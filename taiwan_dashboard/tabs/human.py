from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from plotly_style import ACCENT_RED, DISCRETE, NAVY, TEXT_PRIMARY, light_layout


def render_human_story(destinations: pd.DataFrame, products: pd.DataFrame, semi: pd.DataFrame) -> None:
    """Closing emotional layer: workforce facts + legible quality-of-life proxies."""
    st.markdown(
        '<h2 class="td-section-h2">73,000 engineers. One island. The whole world watching.</h2>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Factories run on precision labor and migration choices as much as on capital equipment."
    )

    years = sorted(destinations["Year"].unique())
    latest_year = years[-1]
    semi_latest = semi[semi["Year"] == latest_year]["Exports (USD)"].sum()
    total_latest = products[products["Year"] == latest_year]["Exports (USD)"].sum()
    workforce_share = min(100, (semi_latest / max(total_latest, 1)) * 100 * 0.75)

    st.markdown(
        f"""
<div class="td-stat-card-row">
  <div class="td-stat-card">
    <div class="td-stat-num">73,000</div>
    <div class="td-stat-cap">TSMC employees (public ballpark)</div>
  </div>
  <div class="td-stat-card">
    <div class="td-stat-num">$68,000</div>
    <div class="td-stat-cap">Average engineer salary (proxy)</div>
  </div>
  <div class="td-stat-card">
    <div class="td-stat-num">{workforce_share:.1f}%</div>
    <div class="td-stat-cap">Semiconductor-linked workforce (proxy)</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Trend charts below are illustrative models, not empirical data. "
        "For primary statistics see Taiwan DGBAS and World Bank."
    )

    people = pd.DataFrame({
        "Year": years,
        "GDP per capita (USD, proxy)": np.linspace(25000, 38000, len(years)),
        "Life expectancy": np.linspace(79.5, 81.3, len(years)),
        "Education index (proxy)": np.linspace(0.79, 0.86, len(years)),
    })

    def _spark(y_col: str, title: str) -> go.Figure:
        fig = go.Figure(
            go.Scatter(
                x=people["Year"],
                y=people[y_col],
                mode="lines+markers",
                line=dict(color=NAVY, width=2),
                marker=dict(size=6, color=NAVY),
            )
        )
        light_layout(fig)
        fig.update_layout(
            title=dict(text=title, font=dict(size=13, color=TEXT_PRIMARY)),
            height=240,
            margin=dict(l=40, r=16, t=40, b=40),
            xaxis=dict(title="", showgrid=True, gridcolor="#E0E4EF"),
            yaxis=dict(title="", showgrid=True, gridcolor="#E0E4EF"),
            showlegend=False,
        )
        return fig

    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(
            _spark("GDP per capita (USD, proxy)", "Income per capita trends upward."),
            use_container_width=True,
            theme=None,
            key="story_human_gdp",
        )
        st.caption("*GDP per capita (USD, proxy) — higher productivity, higher stakes.*")
    with c2:
        st.plotly_chart(
            _spark("Life expectancy", "Longevity reflects public health and welfare."),
            use_container_width=True,
            theme=None,
            key="story_human_life",
        )
        st.caption("*Life expectancy — a coarse read on living standards over time.*")
    with c3:
        st.plotly_chart(
            _spark("Education index (proxy)", "Skills compound across generations."),
            use_container_width=True,
            theme=None,
            key="story_human_edu",
        )
        st.caption("*Education index (proxy) — normalized skill depth, not enrollment alone.*")

    talent = pd.DataFrame({
        "Country": ["USA", "Japan", "Singapore", "Germany", "China"],
        "Taiwanese Talent Outflow": [8000, 4200, 2600, 1900, 3000],
        "Foreign Talent Inflow to Taiwan": [6500, 2200, 2100, 1500, 1800],
    })
    fig_talent = px.bar(
        talent,
        x="Country",
        y=["Taiwanese Talent Outflow", "Foreign Talent Inflow to Taiwan"],
        barmode="group",
        title="Talent crosses borders in both directions — the net shape shifts policy debates.",
        template="plotly_white",
        color_discrete_sequence=[NAVY, ACCENT_RED],
    )
    light_layout(fig_talent)
    fig_talent.update_layout(title_font=dict(size=15, color=TEXT_PRIMARY))
    st.plotly_chart(fig_talent, use_container_width=True, theme=None, key="story_human_talent")
    st.caption("Approximate estimates — see NSTC talent reports and OECD migration statistics for primary data.")


def render(destinations: pd.DataFrame, products: pd.DataFrame, semi: pd.DataFrame) -> None:
    st.subheader("The Human Side")
    st.write("Behind every wafer and shipment are workers, households, and social choices.")

    years = sorted(destinations["Year"].unique())
    people = pd.DataFrame({
        "Year": years,
        "GDP per capita (USD, proxy)": np.linspace(25000, 38000, len(years)),
        "Life expectancy": np.linspace(79.5, 81.3, len(years)),
        "Education index (proxy)": np.linspace(0.79, 0.86, len(years)),
    })

    c1, c2, c3 = st.columns(3)
    with c1:
        f1 = go.Figure(
            go.Scatter(
                x=people["Year"],
                y=people["GDP per capita (USD, proxy)"],
                mode="lines+markers",
                line=dict(color=NAVY, width=2),
            )
        )
        light_layout(f1)
        f1.update_layout(height=240, title="GDP per capita (USD, proxy)", showlegend=False)
        st.plotly_chart(f1, use_container_width=True, theme=None)
    with c2:
        f2 = go.Figure(
            go.Scatter(x=people["Year"], y=people["Life expectancy"], mode="lines+markers", line=dict(color=NAVY, width=2))
        )
        light_layout(f2)
        f2.update_layout(height=240, title="Life expectancy", showlegend=False)
        st.plotly_chart(f2, use_container_width=True, theme=None)
    with c3:
        f3 = go.Figure(
            go.Scatter(
                x=people["Year"],
                y=people["Education index (proxy)"],
                mode="lines+markers",
                line=dict(color=NAVY, width=2),
            )
        )
        light_layout(f3)
        f3.update_layout(height=240, title="Education index (proxy)", showlegend=False)
        st.plotly_chart(f3, use_container_width=True, theme=None)

    talent = pd.DataFrame({
        "Country": ["USA", "Japan", "Singapore", "Germany", "China"],
        "Taiwanese Talent Outflow": [8000, 4200, 2600, 1900, 3000],
        "Foreign Talent Inflow to Taiwan": [6500, 2200, 2100, 1500, 1800],
    })
    fig_talent = px.bar(
        talent,
        x="Country",
        y=["Taiwanese Talent Outflow", "Foreign Talent Inflow to Taiwan"],
        barmode="group",
        title="Talent flows (country-level approximation)",
        template="plotly_white",
        color_discrete_sequence=DISCRETE[:2],
    )
    light_layout(fig_talent)
    st.plotly_chart(fig_talent, use_container_width=True, theme=None)

    latest_year = years[-1]
    semi_latest = semi[semi["Year"] == latest_year]["Exports (USD)"].sum()
    total_latest = products[products["Year"] == latest_year]["Exports (USD)"].sum()
    workforce_share = min(100, (semi_latest / max(total_latest, 1)) * 100 * 0.75)
    s1, s2, s3 = st.columns(3)
    s1.metric("TSMC employees", "73,000")
    s2.metric("Avg Engineer Salary (proxy)", "$68,000")
    s3.metric("Workforce in semiconductor-linked sectors", f"{workforce_share:.1f}%")

    identity = pd.DataFrame({
        "Year": [2000, 2005, 2010, 2015, 2020, 2024],
        "Taiwanese Identity %": [37, 45, 52, 60, 66, 69],
        "Chinese Identity %": [25, 18, 12, 8, 5, 3],
        "Both %": [38, 37, 36, 32, 29, 28],
    })
    fig_id = px.line(
        identity,
        x="Year",
        y=["Taiwanese Identity %", "Chinese Identity %", "Both %"],
        markers=True,
        title="Survey-based identity labels shift slowly — and shape how risk is discussed at home.",
        template="plotly_white",
        color_discrete_sequence=DISCRETE,
    )
    light_layout(fig_id)
    fig_id.update_layout(title_font=dict(size=15, color=TEXT_PRIMARY))
    st.plotly_chart(fig_id, use_container_width=True, theme=None)
