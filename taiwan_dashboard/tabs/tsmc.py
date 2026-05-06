from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import TSMC_DIR
from plotly_style import ACCENT_RED, BLUE, NAVY, NEUTRAL_MUTED, TEXT_PRIMARY, light_layout

_PLATFORM_LABELS = {
    "HPC": "High-Performance Computing",
    "Smartphone": "Smartphones",
    "IoT": "Internet of Things",
    "Automotive": "Automotive",
    "DCE": "Digital Consumer Electronics",
}

_PLATFORM_STYLES: dict[str, tuple[str, str]] = {
    "High-Performance Computing": ("#003087", "solid"),
    "Smartphones":                ("#C8102E", "solid"),
    "Internet of Things":         ("#2e8b57", "solid"),
    "Automotive":                 ("#e07b00", "solid"),
    "Digital Consumer Electronics": ("#7b2d8b", "solid"),
}


def render(tsmc_df: pd.DataFrame) -> None:
    st.subheader("TSMC: The World's Most Critical Manufacturer")
    st.caption("Revenue, platform mix, and foundry market share — one company that no global tech supply chain can route around.")

    if tsmc_df.empty:
        st.info(
            f"Add `tsmc_wafer_revenue_summary.csv` in `{TSMC_DIR}` next to your annual report PDF backups."
        )
        return

    # ── Revenue + Advanced node side-by-side ─────────────────────────────
    c1, c2 = st.columns(2)

    rev = tsmc_df.dropna(subset=["Revenue_USD_bn"]) if "Revenue_USD_bn" in tsmc_df.columns else pd.DataFrame()
    if not rev.empty:
        fig_rev = px.line(
            rev,
            x="Year",
            y="Revenue_USD_bn",
            markers=True,
            title="Annual revenue has more than tripled since 2016",
            template="plotly_white",
        )
        fig_rev.update_traces(line=dict(color=NAVY, width=2.5), marker=dict(color=NAVY, size=6))
        fig_rev.update_layout(yaxis_title="Revenue (USD bn)", xaxis_title="")
        light_layout(fig_rev)
        c1.plotly_chart(fig_rev, use_container_width=True, theme=None)
        c1.caption("Source: TSMC Investor Relations annual reports.")
    else:
        c1.info("No Revenue (USD bn) data available.")

    adv = tsmc_df.dropna(subset=["Advanced_total_pct"]) if "Advanced_total_pct" in tsmc_df.columns else pd.DataFrame()
    if not adv.empty:
        fig_adv = px.line(
            adv,
            x="Year",
            y="Advanced_total_pct",
            markers=True,
            title="Advanced nodes now dominate wafer revenue",
            template="plotly_white",
        )
        fig_adv.update_traces(line=dict(color=ACCENT_RED, width=2.5), marker=dict(color=ACCENT_RED, size=6))
        fig_adv.update_layout(yaxis_title="Share of wafer revenue (%)", xaxis_title="")
        light_layout(fig_adv)
        c2.plotly_chart(fig_adv, use_container_width=True, theme=None)
        c2.caption("Advanced nodes = 7nm and below. Competitors are 3–5 years behind at leading edge.")
    else:
        c2.info("No Advanced Node % data available.")

    # ── Platform mix ──────────────────────────────────────────────────────
    platform_cols = [c for c in ("HPC_pct", "Smartphone_pct", "IoT_pct", "Automotive_pct", "DCE_pct") if c in tsmc_df.columns]
    if platform_cols and tsmc_df[platform_cols].notna().any().any():
        plat = tsmc_df[["Year"] + platform_cols].dropna(how="all", subset=platform_cols).dropna(subset=["Year"])
        long = plat.melt(id_vars="Year", var_name="Platform", value_name="pct").dropna(subset=["pct"])
        long["Platform"] = (
            long["Platform"]
            .str.replace("_pct", "", regex=False)
            .map(lambda x: _PLATFORM_LABELS.get(x, x))
        )
        fig_plat = go.Figure()
        for platform, grp in long.groupby("Platform"):
            color, dash = _PLATFORM_STYLES.get(platform, ("#555555", "solid"))
            fig_plat.add_trace(
                go.Scatter(
                    x=grp["Year"],
                    y=grp["pct"],
                    mode="lines+markers",
                    name=platform,
                    line=dict(color=color, dash=dash, width=2.5),
                    marker=dict(color=color, size=7),
                    hovertemplate=f"<b>{platform}</b><br>Year %{{x}}: %{{y:.1f}}%<extra></extra>",
                )
            )
        fig_plat.update_layout(
            title="Every major industry runs on TSMC chips",
            yaxis_title="Share of revenue (%)",
            xaxis_title="",
            legend=dict(x=1.02, y=1, xanchor="left", yanchor="top", title=""),
            margin=dict(l=0, r=16, t=52, b=80),
            template="plotly_white",
        )
        light_layout(fig_plat)
        st.plotly_chart(fig_plat, use_container_width=True, theme=None)
        st.caption("HPC includes AI accelerators (NVIDIA, AMD, Apple Silicon). Source: TSMC Investor Relations.")

    # ── Foundry competitive landscape (TrendForce estimates) ─────────────
    _FOUNDRY_SHARE = {
        "TSMC":             [52.0, 54.0, 53.0, 56.0, 59.0, 61.0],
        "Samsung":          [18.0, 17.0, 18.0, 16.0, 13.0, 11.0],
        "GlobalFoundries":  [ 8.0,  7.5,  7.0,  6.5,  6.0,  5.4],
        "UMC":              [ 6.5,  6.8,  7.0,  6.9,  6.3,  6.1],
        "SMIC":             [ 4.0,  4.8,  5.3,  5.8,  6.0,  6.2],
    }
    _FOUNDRY_YEARS = [2019, 2020, 2021, 2022, 2023, 2024]
    _FOUNDRY_COLORS = {
        "TSMC":            "#003087",
        "Samsung":         "#C8102E",
        "GlobalFoundries": "#e07b00",
        "UMC":             "#2e8b57",
        "SMIC":            "#7b2d8b",
    }
    fig_comp = go.Figure()
    for company, shares in _FOUNDRY_SHARE.items():
        fig_comp.add_trace(
            go.Scatter(
                x=_FOUNDRY_YEARS,
                y=shares,
                mode="lines+markers",
                name=company,
                line=dict(color=_FOUNDRY_COLORS[company], width=2.5),
                marker=dict(color=_FOUNDRY_COLORS[company], size=7),
                hovertemplate=f"<b>{company}</b> %{{x}}: %{{y}}%<extra></extra>",
            )
        )
    light_layout(fig_comp)
    fig_comp.update_layout(
        title="TSMC holds more market share than all competitors combined",
        yaxis_title="Share of global foundry revenue (%)",
        xaxis_title="",
        legend=dict(x=1.02, y=1, xanchor="left", yanchor="top", title=""),
        margin=dict(l=0, r=16, t=52, b=80),
        yaxis=dict(range=[0, 70]),
    )
    st.plotly_chart(fig_comp, use_container_width=True, theme=None)
    st.caption("Source: TrendForce estimates. Pure-play + IDM foundry revenue basis.")


    # ── Raw data ──────────────────────────────────────────────────────────
    with st.expander("Raw data — TSMC annual metrics"):
        show_cols = [c for c in tsmc_df.columns if c != "Year"]
        st.dataframe(tsmc_df[["Year"] + show_cols], use_container_width=True, hide_index=True)
