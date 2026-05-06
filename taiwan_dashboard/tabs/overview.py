from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from plotly_style import NAVY, light_layout
from tabs import chip_process, destination_choropleth, hero
from tabs.story_blocks import render_final_takeaway
from tabs.story_ui import story_transition
from utils import fmt_usd


def render(
    destinations: pd.DataFrame,
    products: pd.DataFrame,
    semi: pd.DataFrame,
    chip_series: pd.DataFrame,
    _country_detail: pd.DataFrame,
    _tsmc_df: pd.DataFrame,
    gdp_df: pd.DataFrame,
) -> None:
    latest_year = destinations["Year"].max()
    dest_latest = destinations[destinations["Year"] == latest_year]
    prod_latest = products[products["Year"] == latest_year]
    semi_latest = semi[semi["Year"] == latest_year]

    world_total = dest_latest["Exports (USD)"].sum()
    semi_total = semi_latest["Exports (USD)"].sum()
    semi_share = 100 * semi_total / max(prod_latest["Exports (USD)"].sum(), 1)
    over_1pct_countries = (dest_latest["Share (%)"] >= 1).sum()
    chip_latest = chip_series[chip_series["Year"] == latest_year]["Chip Exports (USD)"].sum()

    yr = int(latest_year) if pd.notna(latest_year) else None
    yr_s = str(yr) if yr is not None else "latest year"

    # ── 1. Hook ────────────────────────────────────────────────────────────────
    hero.render(
        f"{semi_share:.1f}%",
        "Semiconductor proxy share of exports",
    )

    # ── 2. Taiwan's economic rise ──────────────────────────────────────────────
    if not gdp_df.empty:
        st.markdown('<h2 class="td-section-h2">An island that built an economy on silicon</h2>', unsafe_allow_html=True)
        fig_gdp = go.Figure()
        fig_gdp.add_trace(go.Scatter(
            x=gdp_df["Year"],
            y=gdp_df["GDP_USD_bn"],
            mode="lines+markers",
            line=dict(color=NAVY, width=2.5),
            marker=dict(color=NAVY, size=5),
            hovertemplate="Year %{x}: $%{y:.0f}B<extra></extra>",
        ))
        light_layout(fig_gdp)
        fig_gdp.update_layout(
            title="Taiwan's GDP has grown nearly 6× since 1990",
            yaxis_title="GDP (USD billion)",
            xaxis_title="",
            margin=dict(l=0, r=16, t=52, b=40),
            showlegend=False,
        )
        st.plotly_chart(fig_gdp, use_container_width=True, theme=None, key="story_gdp")
        st.caption("Source: Taiwan DGBAS (Directorate-General of Budget, Accounting and Statistics). Annual sum of quarterly GDP.")

        story_transition("That growth was built on one thing: making the chips the world runs on.")

    # ── 3. How it's made ───────────────────────────────────────────────────────
    st.markdown('<h2 class="td-section-h2">How a chip is made</h2>', unsafe_allow_html=True)
    chip_process.render(destinations)

    story_transition("Fabrication concentrates in one place — and one company. Who can't afford for that to stop?")

    # ── 4. Who depends on it ───────────────────────────────────────────────────
    st.markdown('<h2 class="td-section-h2">Who depends on it</h2>', unsafe_allow_html=True)
    st.caption("Share of Taiwan's exports by destination — press ▶ to animate · drag to pan · scroll to zoom.")

    destination_choropleth.render(destinations, height=520)

    story_transition("Every major economy is downstream. Dive into Deep Dive to see what breaks — and what it costs you.")

    # ── 5. No one is close ─────────────────────────────────────────────────────
    st.markdown('<h2 class="td-section-h2">No one is close</h2>', unsafe_allow_html=True)
    st.caption(
        "When each company first achieved mass production at each chip node. "
        "Smaller nm = more powerful chips. TSMC has led every generation."
    )

    _timeline = pd.DataFrame([
        {"Company": "TSMC",    "Node": "28nm", "Year": 2011, "Detail": "Apple A6 · industry-leading at launch"},
        {"Company": "TSMC",    "Node": "14nm", "Year": 2015, "Detail": "16nm FinFET — first FinFET in mobile chips"},
        {"Company": "TSMC",    "Node": "7nm",  "Year": 2018, "Detail": "Apple A12 · iPhone XS"},
        {"Company": "TSMC",    "Node": "5nm",  "Year": 2020, "Detail": "Apple A14 · iPhone 12"},
        {"Company": "TSMC",    "Node": "3nm",  "Year": 2022, "Detail": "Apple A17 · iPhone 15 Pro"},
        {"Company": "TSMC",    "Node": "2nm",  "Year": 2025, "Detail": "Volume production began"},
        {"Company": "Samsung", "Node": "28nm", "Year": 2012, "Detail": "Exynos 4 series"},
        {"Company": "Samsung", "Node": "14nm", "Year": 2015, "Detail": "Exynos 7420 · Galaxy S6"},
        {"Company": "Samsung", "Node": "7nm",  "Year": 2019, "Detail": "Exynos 9825 · 1 yr after TSMC"},
        {"Company": "Samsung", "Node": "5nm",  "Year": 2021, "Detail": "Exynos 2100 · 1 yr after TSMC"},
        {"Company": "Samsung", "Node": "3nm",  "Year": 2024, "Detail": "Exynos 2400 · yield issues delayed mass production"},
        {"Company": "Samsung", "Node": "2nm",  "Year": 2026, "Detail": "Targeted — not yet in production"},
        {"Company": "Intel",   "Node": "28nm", "Year": 2012, "Detail": "22nm FinFET (≈28nm equivalent) · Ivy Bridge"},
        {"Company": "Intel",   "Node": "14nm", "Year": 2014, "Detail": "Broadwell — but stuck here for 5 years"},
        {"Company": "Intel",   "Node": "7nm",  "Year": 2023, "Detail": "Intel 4 (≈7nm equivalent) · 5 yrs after TSMC"},
        {"Company": "Intel",   "Node": "3nm",  "Year": 2024, "Detail": "Intel 3"},
        {"Company": "Intel",   "Node": "2nm",  "Year": 2025, "Detail": "Intel 18A — limited samples only"},
        {"Company": "SMIC",    "Node": "28nm", "Year": 2015, "Detail": "Mainstream production — no restrictions"},
        {"Company": "SMIC",    "Node": "14nm", "Year": 2019, "Detail": "First advanced node"},
        {"Company": "SMIC",    "Node": "7nm",  "Year": 2023, "Detail": "No EUV access · low volume · US export-controlled"},
    ])

    _colors = {"TSMC": "#ef4444", "Samsung": "#3b82f6", "Intel": "#8b5cf6", "SMIC": "#94a3b8"}
    _node_order = ["28nm", "14nm", "7nm", "5nm", "3nm", "2nm"]

    _fig_tl = go.Figure()
    for company, grp in _timeline.groupby("Company"):
        _fig_tl.add_trace(go.Scatter(
            x=grp["Node"],
            y=grp["Year"],
            mode="markers",
            name=company,
            marker=dict(size=12, color=_colors[company], symbol="circle",
                        line=dict(color="white", width=1.5)),
            customdata=grp["Detail"].values,
            hovertemplate="<b>%{meta}</b> · %{x}<br>%{y}<br><i>%{customdata}</i><extra></extra>",
            meta=company,
        ))

    light_layout(_fig_tl)
    _fig_tl.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=_node_order, title="Chip node"),
        yaxis=dict(title="Year of first mass production", range=[2009.5, 2027]),
        margin=dict(l=0, r=80, t=50, b=90),
        height=340,
        legend=dict(x=1.02, y=1, xanchor="left", yanchor="top"),
    )
    st.plotly_chart(_fig_tl, use_container_width=True, theme=None, key="story_gap")
    st.caption("Sources: TSMC, Samsung, Intel IR disclosures. SMIC 7nm uses DUV multi-patterning without EUV.")

    story_transition("The world has finally woken up to this concentration risk. Here's what's being done about it.")

    # ── 6. What's being done ───────────────────────────────────────────────────
    st.markdown('<h2 class="td-section-h2">What\'s being done about it</h2>', unsafe_allow_html=True)
    st.caption("Governments and companies are racing to diversify chip production — but it will take a decade.")

    _initiatives = [
        ("🇺🇸 US CHIPS Act", "2022", "$52B in subsidies to build domestic fabs. TSMC Arizona, Intel Ohio, Samsung Texas all announced. First wafers expected 2026–2028."),
        ("🇯🇵 Japan Rapidus", "2023", "Japan's government-backed fab targeting 2nm chips by 2027. IBM partnership for process technology. $3.5B+ committed."),
        ("🇪🇺 EU Chips Act", "2023", "€43B target to double Europe's share of global chip production from 9% to 20% by 2030. TSMC Dresden fab under construction."),
        ("🇮🇳 India Semiconductor Mission", "2024", "$10B incentive scheme. Tata Group building first fab. Micron assembly and test plant underway in Gujarat."),
    ]

    cols = st.columns(4)
    for i, (title, year, desc) in enumerate(_initiatives):
        with cols[i]:
            st.markdown(f"**{title}**")
            st.caption(f"Announced {year}")
            st.write(desc)

    st.markdown(
        """<div style="border-left:3px solid #C8102E;padding:0.65rem 1rem;margin:1.25rem 0;
        background:#F7F8FA;font-size:0.95rem;color:#0A0A0A;line-height:1.6;">
        Even with all of this investment, analysts estimate the world will remain heavily dependent
        on Taiwan for leading-edge chips through at least <strong>2035</strong>.
        The gap is structural, not just financial.
        </div>""",
        unsafe_allow_html=True,
    )


