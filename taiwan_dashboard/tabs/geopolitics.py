from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from plotly_style import ACCENT_RED, NAVY, light_layout

_EVENT_CARDS = [
    (
        "2021 Chip Shortage",
        "Global chip scarcity exposed how much of the world runs on Taiwan-made silicon. "
        "Semiconductor equities rallied while auto and consumer electronics stocks lagged.",
        "~4–6 months",
    ),
    (
        "2022 Pelosi Visit",
        "China launched its largest-ever military exercises around Taiwan. "
        "Volatility spiked across Asia tech; markets repriced geopolitical risk for the region.",
        "~2–3 months",
    ),
    (
        "2024 Earthquake",
        "A 7.4-magnitude quake near Hualien briefly halted TSMC production lines. "
        "Foundry-dependent names saw short-term risk repricing before operations resumed.",
        "~3–5 weeks",
    ),
]

_TENSION_PERIODS = [
    (1995, 1996, "1995–96 Strait Crisis<br>China missile tests"),
    (2002, 2005, "Cross-strait tensions<br>Chen Shui-bian era"),
    (2016, 2016, "DPP election win;<br>Beijing freezes dialogue"),
    (2020, 2024, "Peak escalation:<br>COVID, Pelosi, PLA drills"),
]

_KEY_EVENTS = [
    (1996, "1996 Strait Crisis"),
    (2016, "DPP wins election"),
    (2022, "Pelosi visit / PLA exercises"),
]


def render(destinations: pd.DataFrame, taiex: pd.DataFrame) -> None:
    st.subheader("Geopolitical Tensions & Market Reactions")
    st.caption("Taiwan's stock market has absorbed every major cross-strait shock and kept climbing — but each event reprices risk for global chip supply chains.")

    # ── Decide data source: TAIEX if available, else exports ──────────────
    if not taiex.empty:
        plot_df = taiex.rename(columns={"TAIEX": "Value"})
        y_label = "TAIEX (yearly avg)"
        line_title = "Taiwan's stock market has recovered from every geopolitical shock"
        caption = (
            "TAIEX = Taiwan Weighted Stock Index, yearly average. "
            "Shaded bands = documented periods of elevated cross-strait tension. "
            "Source: Taiwan Stock Exchange."
        )
        hover = "Year %{x}: %{y:,.0f}<extra></extra>"
    else:
        exp = destinations.groupby("Year", as_index=False)["Exports (USD)"].sum().sort_values("Year")
        plot_df = exp.rename(columns={"Exports (USD)": "Value"})
        y_label = "Total Exports (USD)"
        line_title = "Taiwan's exports grew through every geopolitical shock"
        caption = "Shaded bands = documented periods of elevated cross-strait tension. Sources: Taiwan Strait Crisis (1995–96), MND reports, Council on Foreign Relations."
        hover = "Year %{x}: $%{y:,.0f}<extra></extra>"

    y_min = plot_df["Value"].min()
    y_max = plot_df["Value"].max()
    data_min = int(plot_df["Year"].min())
    data_max = int(plot_df["Year"].max())

    fig = go.Figure()

    # Shaded tension bands
    for x0, x1, label in _TENSION_PERIODS:
        if x1 < data_min or x0 > data_max:
            continue
        fig.add_vrect(
            x0=x0, x1=x1 + 0.9,
            fillcolor=ACCENT_RED,
            opacity=0.08,
            layer="below",
            line_width=0,
        )
        fig.add_annotation(
            x=(x0 + x1) / 2,
            y=y_max * 1.01,
            text=label,
            showarrow=False,
            yanchor="bottom",
            font=dict(size=9, color=ACCENT_RED),
            align="center",
        )

    # Event markers
    for year, _ in _KEY_EVENTS:
        if year < data_min or year > data_max:
            continue
        fig.add_vline(
            x=year,
            line_dash="dot",
            line_color=ACCENT_RED,
            opacity=0.6,
            line_width=1.5,
        )

    # Main line
    fig.add_trace(
        go.Scatter(
            x=plot_df["Year"],
            y=plot_df["Value"],
            mode="lines+markers",
            line=dict(color=NAVY, width=2.5),
            marker=dict(color=NAVY, size=5),
            hovertemplate=hover,
        )
    )

    light_layout(fig)
    fig.update_layout(
        title=line_title,
        yaxis_title=y_label,
        xaxis_title="",
        margin=dict(l=0, r=16, t=52, b=40),
        showlegend=False,
        yaxis=dict(range=[y_min * 0.85, y_max * 1.12]),
    )
    st.plotly_chart(fig, use_container_width=True, theme=None, key="geo_exports_line")
    st.caption(caption)

    # ── Event cards ────────────────────────────────────────────────────────
    cols = st.columns(3)
    for i, (evt, desc, rec) in enumerate(_EVENT_CARDS):
        with cols[i]:
            st.markdown(f"**{evt}**")
            st.write(desc)
            st.caption(f"Market recovery window: {rec}")
