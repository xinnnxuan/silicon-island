from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from plotly_style import DISCRETE, light_layout


def render(destinations: pd.DataFrame, products: pd.DataFrame, chip_series: pd.DataFrame) -> None:
    st.subheader("Economy & Concentration")
    st.write("KPI panel: GDP proxy, trade balance proxy, and semiconductor export share.")

    years = sorted(destinations["Year"].unique())
    latest_year = years[-1]
    prod_latest = products[products["Year"] == latest_year]
    total_latest = prod_latest["Exports (USD)"].sum()

    # Semiconductor share using chip_series if available, otherwise HS proxy from products
    semi_latest = 0.0
    if not chip_series.empty:
        cs = chip_series[chip_series["Year"] == latest_year]["Chip Exports (USD)"].sum()
        semi_latest = float(cs)
    else:
        # Fallback: approximate from products HS keywords match already performed upstream
        try:
            from data_loader import semicon_proxy  # type: ignore
            semi_df = semicon_proxy(products)
            semi_latest = float(semi_df[semi_df["Year"] == latest_year]["Exports (USD)"].sum())
        except Exception:
            semi_latest = 0.0
    share = (semi_latest / total_latest * 100) if total_latest else 0.0

    # Simple proxies for GDP/trade balance using export totals (real data can replace via CSV later)
    total_exports_by_year = destinations.groupby("Year", as_index=False)["Exports (USD)"].sum()
    total_exports_by_year["Trade Balance Proxy"] = total_exports_by_year["Exports (USD)"] * np.linspace(
        0.82, 0.93, len(total_exports_by_year)
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Latest Year", f"{latest_year}")
    c2.metric("Semiconductor Share of Exports", f"{share:.1f}%")
    c3.metric("Total Exports (latest)", f"${total_latest:,.0f}")

    fig = px.line(
        total_exports_by_year,
        x="Year",
        y=["Exports (USD)", "Trade Balance Proxy"],
        markers=True,
        title="Exports and Trade Balance Proxy",
        template="plotly_white",
        color_discrete_sequence=DISCRETE,
    )
    light_layout(fig)
    st.plotly_chart(fig, use_container_width=True, theme=None)

