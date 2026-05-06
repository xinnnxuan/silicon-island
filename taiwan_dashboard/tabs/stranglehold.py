from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from plotly_style import DISCRETE, light_layout, with_slider_animation


def render(
    destinations: pd.DataFrame,
    _products: pd.DataFrame,
    _semi: pd.DataFrame,
    chip_series: pd.DataFrame,
    _country_detail: pd.DataFrame | None = None,
) -> None:
    st.subheader("Semiconductor Export Growth")
    st.caption("IC chip exports have outpaced Taiwan's total export growth — semiconductors are increasingly the whole story.")
    total_exports = destinations.groupby("Year", as_index=False)["Exports (USD)"].sum()
    if not chip_series.empty:
        growth = chip_series.merge(total_exports, on="Year", how="left")
        growth = growth.rename(columns={
            "Chip Exports (USD)": "IC Chip Exports",
            "Exports (USD)": "Total Exports",
        })
        fig_chip = px.line(
            growth,
            x="Year",
            y=["IC Chip Exports", "Total Exports"],
            markers=True,
            title="Integrated circuit exports growing faster than Taiwan's total exports",
            template="plotly_white",
            color_discrete_sequence=DISCRETE,
            labels={"value": "USD", "variable": ""},
        )
        light_layout(fig_chip)
        fig_chip.update_layout(
            yaxis_title="USD",
            legend=dict(x=1.02, y=1, xanchor="left", yanchor="top"),
            margin=dict(l=0, r=16, t=52, b=80),
        )
        with_slider_animation(fig_chip, chart_id="stranglehold_chip_line")
        st.plotly_chart(fig_chip, use_container_width=True, theme=None, key="stranglehold_chip_line")
        st.caption("Source: ITC Trade Map, HS 8542 (Electronic Integrated Circuits).")

    else:
        st.info("No TradeData_* files found for long-run semiconductor export trend.")
