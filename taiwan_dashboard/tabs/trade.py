from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

import plotly.graph_objects as go

from plotly_style import ACCENT_RED, DISCRETE, NAVY, light_layout

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
    "Articles of stone, plaster, cement": "Stone & Ceramics",
    "Miscellaneous manufactured articles": "Other Manufactured Goods",
    "Arms and ammunition": "Defense",
    "Works of art": "Art & Collectibles",
}


def _clean_section(s: str) -> str:
    return _SECTION_LABELS.get(s, s)


def render(
    destinations: pd.DataFrame,
    products: pd.DataFrame,
    trade_balance: pd.DataFrame,
    country_detail: pd.DataFrame,
    us_trade: pd.DataFrame,
) -> None:
    st.subheader("Where the Money Flows")
    st.caption("Taiwan's top export destinations, product mix, and bilateral trade relationship with the United States.")

    latest_year = int(destinations["Year"].max())

    # ── Two side-by-side bar charts ────────────────────────────────────────
    col_dest, col_prod = st.columns(2)

    with col_dest:
        top_dest = (
            destinations[destinations["Year"] == latest_year]
            .groupby("Country", as_index=False)["Exports (USD)"]
            .sum()
            .nlargest(12, "Exports (USD)")
            .sort_values("Exports (USD)")
        )
        fig_dest = px.bar(
            top_dest,
            x="Exports (USD)",
            y="Country",
            orientation="h",
            title=f"Top destinations ({latest_year})",
            template="plotly_white",
        )
        fig_dest.update_traces(marker_color=NAVY)
        light_layout(fig_dest)
        fig_dest.update_layout(
            xaxis_title="Exports (USD)",
            yaxis_title="",
            margin=dict(l=0, r=16, t=48, b=40),
        )
        st.plotly_chart(fig_dest, use_container_width=True, theme=None, key="trade_dest_bar")

    with col_prod:
        top_prod = (
            products[products["Year"] == latest_year]
            .groupby("Section", as_index=False)["Exports (USD)"]
            .sum()
            .assign(Section=lambda d: d["Section"].map(_clean_section))
            .nlargest(10, "Exports (USD)")
            .sort_values("Exports (USD)")
        )
        fig_prod = px.bar(
            top_prod,
            x="Exports (USD)",
            y="Section",
            orientation="h",
            title=f"Export mix by product ({latest_year})",
            template="plotly_white",
        )
        fig_prod.update_traces(marker_color=ACCENT_RED)
        light_layout(fig_prod)
        fig_prod.update_layout(
            xaxis_title="Exports (USD)",
            yaxis_title="",
            margin=dict(l=0, r=16, t=48, b=40),
        )
        st.plotly_chart(fig_prod, use_container_width=True, theme=None, key="trade_prod_bar")

    st.caption(f"Source: ITC Trade Map, {latest_year}.")

    # ── Trade balance trend ────────────────────────────────────────────────
    if not trade_balance.empty:
        fig_line = px.line(
            trade_balance,
            x="Year",
            y=["Total Exports", "Total Imports", "Trade Surplus (or Deficit)"],
            markers=True,
            title="Taiwan Exports, Imports, and Trade Balance",
            template="plotly_white",
            color_discrete_sequence=DISCRETE,
        )
        light_layout(fig_line)
        st.plotly_chart(fig_line, use_container_width=True, theme=None, key="trade_balance_line")

    # ── US–Taiwan bilateral trade ──────────────────────────────────────────
    if not us_trade.empty:
        fig_us = go.Figure()
        fig_us.add_trace(go.Scatter(
            x=us_trade["Year"], y=us_trade["US_Imports_mn"],
            name="US imports from Taiwan",
            mode="lines+markers",
            line=dict(color=ACCENT_RED, width=2.5),
            marker=dict(size=5),
            hovertemplate="Year %{x}: $%{y:,.0f}M<extra></extra>",
        ))
        fig_us.add_trace(go.Scatter(
            x=us_trade["Year"], y=us_trade["US_Exports_mn"],
            name="US exports to Taiwan",
            mode="lines+markers",
            line=dict(color=NAVY, width=2.5),
            marker=dict(size=5),
            hovertemplate="Year %{x}: $%{y:,.0f}M<extra></extra>",
        ))
        fig_us.add_trace(go.Bar(
            x=us_trade["Year"],
            y=us_trade["Trade_Balance_mn"],
            name="US trade balance",
            marker_color=[ACCENT_RED if v < 0 else NAVY for v in us_trade["Trade_Balance_mn"]],
            opacity=0.35,
            hovertemplate="Year %{x}: $%{y:,.0f}M<extra></extra>",
        ))
        light_layout(fig_us)
        fig_us.update_layout(
            title="US–Taiwan bilateral trade: America imports far more than it exports",
            yaxis_title="USD millions",
            xaxis_title="",
            margin=dict(l=0, r=16, t=52, b=80),
            legend=dict(x=1.02, y=1, xanchor="left", yanchor="top"),
            barmode="overlay",
        )
        st.plotly_chart(fig_us, use_container_width=True, theme=None, key="us_taiwan_bilateral")
        st.caption("Source: US Census Bureau bilateral trade data. Bars show US trade balance (negative = deficit with Taiwan).")

