from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

import plotly.graph_objects as go

from plotly_style import ACCENT_RED, NAVY, light_layout
from utils import fmt_usd

def _country_cards(countries: list, avg_exports: list, shares: list, year: int) -> None:
    """Render per-country stat cards in a responsive flex row."""
    cards = ""
    for ctry, avg, share in zip(countries, avg_exports, shares):
        cards += f"""
        <div style="flex:1;min-width:160px;background:#ffffff;border:1px solid #cbd5e1;
                    border-radius:10px;padding:16px 20px;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
          <div style="font-size:0.78rem;font-weight:600;color:#64748b;
                      text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;
                      white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{ctry}</div>
          <div style="font-size:1.45rem;font-weight:700;color:#1e293b;line-height:1.2;">{avg}</div>
          <div style="font-size:0.8rem;color:#64748b;margin-top:4px;">avg annual exports</div>
          <div style="font-size:0.85rem;font-weight:600;color:#3b82f6;margin-top:8px;">{share:.2f}% of {year} exports</div>
        </div>"""
    st.markdown(
        f'<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:0.75rem;">{cards}</div>',
        unsafe_allow_html=True,
    )


def _light_table(df: pd.DataFrame) -> None:
    """Render a DataFrame as a light-background HTML table."""
    headers = "".join(f'<th style="text-align:left;padding:10px 16px;border-bottom:2px solid #cbd5e1;font-weight:700;color:#1e293b;background:#e2e8f0;">{c}</th>' for c in df.columns)
    rows = ""
    for i, row in df.iterrows():
        bg = "#ffffff" if i % 2 == 0 else "#f1f5f9"
        cells = "".join(f'<td style="padding:10px 16px;border-bottom:1px solid #cbd5e1;color:#1e293b;">{v}</td>' for v in row)
        rows += f'<tr style="background:{bg};">{cells}</tr>'
    html = f"""
    <table style="width:100%;border-collapse:collapse;border-radius:8px;overflow:hidden;border:1px solid #cbd5e1;font-size:0.9rem;font-family:sans-serif;margin-bottom:0.5rem;">
      <thead><tr>{headers}</tr></thead>
      <tbody>{rows}</tbody>
    </table>"""
    st.markdown(html, unsafe_allow_html=True)


_COLORS = [
    "#003087", "#C8102E", "#2e8b57", "#e07b00", "#7b2d8b",
    "#0891b2", "#b45309", "#be185d", "#1d4ed8", "#15803d",
]
def _multi_country_fig(data: pd.DataFrame, title: str, key_col: str = "Country") -> go.Figure:
    """Line chart with distinct color per country, all solid lines."""
    fig = go.Figure()
    for i, (country, grp) in enumerate(data.groupby(key_col)):
        color = _COLORS[i % len(_COLORS)]
        fig.add_trace(go.Scatter(
            x=grp["Year"],
            y=grp["Exports (USD)"],
            name=country,
            mode="lines+markers",
            line=dict(color=color, dash="solid", width=2.5),
            marker=dict(color=color, size=6),
            hovertemplate=f"<b>{country}</b> %{{x}}: $%{{y:,.0f}}<extra></extra>",
        ))
    light_layout(fig)
    fig.update_layout(
        title=title,
        yaxis_title="Exports (USD)",
        xaxis_title="",
        margin=dict(l=0, r=16, t=52, b=40),
        legend=dict(x=1.02, y=1, xanchor="left", yanchor="top"),
        template="plotly_white",
    )
    return fig

_SECTION_LABELS: dict[str, str] = {
    "Machinery": "Industrial Machinery",
    "Electrical Machinery and Equipment": "Electronics & Semiconductors",
    "Optical, photo, medical apparatus": "Optical & Medical Devices",
    "Plastics and articles thereof": "Plastics & Materials",
    "Vehicles other than railway": "Vehicles",
    "Instruments": "Precision Instruments",
    "Base metals and articles thereof": "Base Metals",
    "Chemical products": "Chemicals",
    "Textile and articles thereof": "Textiles",
    "Foodstuffs": "Food & Agriculture",
    "Mineral products": "Mineral Products",
}


def render(
    destinations: pd.DataFrame,
    products: pd.DataFrame,
    trade_balance: pd.DataFrame,
    country_detail: pd.DataFrame,
) -> None:
    st.markdown("Explore Taiwan's trade data by country, product, and year.")

    dest = destinations
    prod = products

    # ── Country explorer ───────────────────────────────────────────────────
    st.subheader("By Destination Country")
    countries = sorted(dest["Country"].unique())
    default_countries = [c for c in ["United States of America", "China"] if c in countries]
    selected_countries = st.multiselect(
        "Select countries",
        countries,
        default=default_countries or countries[:2],
        key="explore_country",
    )

    if not selected_countries:
        st.info("Select at least one country above.")
    else:
        country_data = dest[dest["Country"].isin(selected_countries)].sort_values("Year")
        latest_year = int(dest["Year"].max())

        avgs, shares = [], []
        for ctry in selected_countries:
            ctry_data = country_data[country_data["Country"] == ctry]
            avgs.append(fmt_usd(ctry_data.groupby("Year")["Exports (USD)"].sum().mean()))
            shares.append(ctry_data[ctry_data["Year"] == latest_year]["Share (%)"].sum())
        _country_cards(selected_countries, avgs, shares, latest_year)

        single = len(selected_countries) == 1
        if single:
            fig_country = go.Figure(go.Scatter(
                x=country_data["Year"], y=country_data["Exports (USD)"],
                mode="lines+markers",
                line=dict(color=NAVY, width=2.5),
                marker=dict(color=NAVY, size=6),
                hovertemplate="%{x}: $%{y:,.0f}<extra></extra>",
            ))
            light_layout(fig_country)
            fig_country.update_layout(
                title=f"Taiwan exports to {selected_countries[0]} over time",
                yaxis_title="Exports (USD)", xaxis_title="",
                margin=dict(l=0, r=16, t=52, b=40), showlegend=False,
            )
        else:
            fig_country = _multi_country_fig(country_data, "Taiwan exports over time")
        st.plotly_chart(fig_country, use_container_width=True, theme=None, key="explore_country_trend")

        # ── Country commodity detail (single country only) ─────────────────
        if not country_detail.empty and single:
            selected_country = selected_countries[0]
            detail_countries = sorted(country_detail["Country"].dropna().unique())
            if selected_country in detail_countries:
                detail = country_detail[country_detail["Country"] == selected_country]
                commodity_totals = (
                    detail.groupby("Commodity", as_index=False)["Exports"]
                    .sum()
                    .sort_values("Exports", ascending=False)
                )
                selected_commodities = st.multiselect(
                    "Commodity breakdown",
                    options=commodity_totals["Commodity"].tolist(),
                    default=commodity_totals.head(5)["Commodity"].tolist(),
                    key="explore_commodity",
                )
                if selected_commodities:
                    plot_df = (
                        detail[detail["Commodity"].isin(selected_commodities) & detail["Month"].notna()]
                        .groupby(["Year", "Commodity"], as_index=False)["Exports"]
                        .sum()
                    )
                    fig_detail = px.line(
                        plot_df,
                        x="Year",
                        y="Exports",
                        color="Commodity",
                        markers=True,
                        title=f"{selected_country}: exports by commodity",
                        template="plotly_white",
                        color_discrete_sequence=_COLORS,
                    )
                    light_layout(fig_detail)
                    st.plotly_chart(fig_detail, use_container_width=True, theme=None, key="explore_commodity_trend")

    st.markdown('<div style="margin:3rem 0;"></div>', unsafe_allow_html=True)

    # ── Product explorer ───────────────────────────────────────────────────
    st.subheader("By Product Category")
    section_options = sorted(prod["Section"].dropna().unique())
    selected_section = st.selectbox(
        "Select a product category",
        section_options,
        format_func=lambda s: _SECTION_LABELS.get(s, s),
        key="explore_section",
    )
    all_years = sorted(prod["Year"].unique())
    section_data = (
        prod[prod["Section"] == selected_section]
        .groupby("Year", as_index=False)["Exports (USD)"]
        .sum()
    )
    section_data = (
        pd.DataFrame({"Year": all_years})
        .merge(section_data, on="Year", how="left")
        .fillna(0)
        .sort_values("Year")
    )
    missing_years = section_data[section_data["Exports (USD)"] == 0]["Year"].tolist()

    fig_section = px.bar(
        section_data,
        x="Year",
        y="Exports (USD)",
        title=f"{_SECTION_LABELS.get(selected_section, selected_section)}: exports over time",
        template="plotly_white",
    )
    fig_section.update_traces(marker_color=ACCENT_RED)
    light_layout(fig_section)
    st.plotly_chart(fig_section, use_container_width=True, theme=None, key="explore_section_trend")
    if missing_years:
        st.caption(f"No data in source files for this category in: {', '.join(str(y) for y in missing_years)}.")

    st.markdown('<div style="margin:3rem 0;"></div>', unsafe_allow_html=True)

    # ── Country comparison ─────────────────────────────────────────────────
    st.subheader("Compare Countries")
    default_cmp = [c for c in ["United States of America", "China", "Japan"] if c in countries]
    cmp_countries = st.multiselect(
        "Select countries to compare",
        countries,
        default=default_cmp or countries[:3],
        key="explore_cmp",
    )

    if not cmp_countries:
        st.info("Select at least one country above.")
    else:
        cmp_avgs, cmp_shares = [], []
        for ctry in cmp_countries:
            ctry_series = dest[dest["Country"] == ctry].groupby("Year")["Exports (USD)"].sum()
            cmp_avgs.append(fmt_usd(ctry_series.mean()))
            cmp_shares.append(dest[(dest["Year"] == latest_year) & (dest["Country"] == ctry)]["Share (%)"].sum())
        _country_cards(cmp_countries, cmp_avgs, cmp_shares, latest_year)

        cmp = dest[dest["Country"].isin(cmp_countries)].groupby(
            ["Year", "Country"], as_index=False
        )["Exports (USD)"].sum()
        fig_cmp = _multi_country_fig(cmp, "Export comparison over time")
        st.plotly_chart(fig_cmp, use_container_width=True, theme=None, key="explore_compare")

