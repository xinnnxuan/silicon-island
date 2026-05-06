from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from plotly_style import light_layout

# (avg 2024/25 price USD, sensitivity multipliers: 3-month / 1-year / total loss)
_PRODUCTS: dict[str, tuple[int, float, float, float]] = {
    "Phone (iPhone 16 / Galaxy S25)":  (799,   1.22, 1.48, 1.90),
    "Laptop (MacBook Air M3)":         (1099,  1.20, 1.45, 1.85),
    "New Car (US avg. 2024)":          (48000, 1.18, 1.40, 1.75),
    "TV (Samsung 65\" QLED)":          (1299,  1.15, 1.35, 1.65),
    "Refrigerator (mid-range)":        (1200,  1.10, 1.25, 1.48),
    "Washing Machine (front-load)":    (900,   1.08, 1.20, 1.40),
    "Wi-Fi Router (Wi-Fi 6E)":         (180,   1.18, 1.38, 1.72),
    "Hearing Aids (mid-range pair)":   (3000,  1.20, 1.42, 1.78),
    "Glucose Monitor (Dexcom G7)":     (299,   1.15, 1.35, 1.65),
    "Microwave (mid-range)":           (180,   1.06, 1.14, 1.28),
}

_SCENARIOS = ["3-month shortage", "1-year shortage", "Total loss of supply"]
_SCENARIO_IDX = {s: i for i, s in enumerate(_SCENARIOS)}


def render(_destinations: pd.DataFrame, _products: pd.DataFrame, _semi: pd.DataFrame) -> None:
    st.subheader("The Real Cost of Disruption")
    st.caption("Estimated consumer price increases for everyday products under three chip shortage scenarios, modeled on 2020–2022 precedents.")

    rows = []
    for name, vals in _PRODUCTS.items():
        base = vals[0]
        for i, scenario in enumerate(_SCENARIOS):
            factor = vals[i + 1]
            rows.append({
                "Product": name,
                "Scenario": scenario,
                "Price increase (%)": round((factor - 1) * 100, 1),
                "Base price": f"${base:,}",
                "New price": f"${base * factor:,.0f}",
                "Extra cost": f"+${base * (factor - 1):,.0f}",
            })
    price_df = pd.DataFrame(rows)

    # Sort products by total-loss impact so worst-hit are at the top
    order = (
        price_df[price_df["Scenario"] == "Total loss of supply"]
        .sort_values("Price increase (%)")["Product"]
        .tolist()
    )

    fig_price = px.bar(
        price_df,
        x="Product",
        y="Price increase (%)",
        color="Scenario",
        barmode="group",
        title="How much more you'd pay — by disruption severity",
        template="plotly_white",
        category_orders={"Product": list(reversed(order)), "Scenario": _SCENARIOS},
        color_discrete_map={
            "3-month shortage":      "#fca5a5",
            "1-year shortage":       "#ef4444",
            "Total loss of supply":  "#7f1d1d",
        },
        custom_data=["Base price", "New price", "Extra cost"],
    )
    fig_price.update_traces(
        hovertemplate=(
            "<b>%{x}</b> — %{fullData.name}<br>"
            "Price increase: %{y:.0f}%<br>"
            "Base: %{customdata[0]} → %{customdata[1]}<br>"
            "Extra cost: %{customdata[2]}<extra></extra>"
        ),
    )
    light_layout(fig_price)
    fig_price.update_layout(
        yaxis_title="Price increase (%)",
        xaxis_title="",
        legend=dict(x=1.02, y=1, xanchor="left", yanchor="top", title=""),
        margin=dict(l=0, r=40, t=56, b=80),
        height=420,
    )
    st.plotly_chart(fig_price, use_container_width=True, theme=None, key="cost_price_bar")
    st.caption("Illustrative model — chip sensitivity varies by product. Based on 2020–2022 shortage precedents.")



