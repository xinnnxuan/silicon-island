from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from plotly_style import ACCENT_RED, TEXT_PRIMARY, light_layout

# Canonical display order (≥8 industries, proxy mapping from section labels).
_INDUSTRY_ORDER: list[str] = [
    "Technology",
    "Consumer Electronics",
    "Automotive",
    "Defense",
    "Telecom",
    "Medical Devices",
    "Industrial Equipment",
    "Aerospace",
]

def _industry_for_section(section: str) -> str:
    """Map trade `Section` strings into one of eight proxy industries."""
    s = (section or "").lower()

    explicit = {
        "Electrical Machinery and Equipment": "Technology & Semiconductors",
        "Machinery": "Industrial Equipment",
        "Optical, photo, medical apparatus": "Medical Devices",
        "Plastics and articles thereof": "Industrial Equipment",
        "Vehicles other than railway": "Automotive",
        "Instruments": "Medical Devices",
    }
    if section in explicit:
        return explicit[section]

    if any(k in s for k in ("854", "semiconductor", "integrated circuit", "electrical machinery")):
        return "Technology"
    if any(k in s for k in ("computer", "office machine", "electronic")):
        return "Consumer Electronics"
    if any(k in s for k in ("vehicle", "automotive", "aircraft", "spacecraft")):
        return "Aerospace" if "air" in s or "space" in s else "Automotive"
    if any(k in s for k in ("weapon", "military", "defense", "ordnance")):
        return "Defense"
    if any(k in s for k in ("telecom", "telephone", "transmission", "radio", "tv")):
        return "Telecom"
    if any(k in s for k in ("medical", "pharmaceutical", "optical", "surgical", "dental", "orthopedic")):
        return "Medical Devices"
    if any(k in s for k in ("industrial", "machine", "pump", "turbine", "mechanical", "plastics and")):
        return "Industrial Equipment"
    if "iron" in s or "steel" in s or "metal" in s or "chemical" in s:
        return "Industrial Equipment"
    return "Technology"


def build_industry_exposure_figure(products: pd.DataFrame, *, latest_year: int | None = None) -> go.Figure:
    """Horizontal bars: industry exposure index from product sections (latest year)."""
    if latest_year is None:
        latest_year = int(products["Year"].max())
    sec = (
        products[products["Year"] == latest_year]
        .groupby("Section", as_index=False)["Exports (USD)"]
        .sum()
        .sort_values("Exports (USD)", ascending=False)
    )
    sec["Industry"] = sec["Section"].map(_industry_for_section)
    industry = sec.groupby("Industry", as_index=False)["Exports (USD)"].sum()
    industry["Exposure Index"] = 100 * industry["Exports (USD)"] / industry["Exports (USD)"].sum()

    merged = industry[["Industry", "Exposure Index"]].copy()
    merged = merged[merged["Exposure Index"] > 0].sort_values("Exposure Index", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=merged["Exposure Index"],
            y=merged["Industry"],
            orientation="h",
            marker=dict(color=ACCENT_RED, line=dict(width=0)),
            hovertemplate="%{y}: %{x:.1f}% of Taiwan's exports<extra></extra>",
        )
    )
    light_layout(fig)
    fig.update_layout(
        title=dict(
            text="Semiconductors & electronics make up the majority of Taiwan's export exposure.",
            font=dict(size=15, color=TEXT_PRIMARY),
        ),
        xaxis=dict(title="Share of Taiwan's classified exports (%)", gridcolor="#E0E4EF", zeroline=False),
        yaxis=dict(title="", automargin=True),
        margin=dict(l=0, r=16, t=48, b=48),
        showlegend=False,
        bargap=0.35,
    )
    return fig


def render(_destinations: pd.DataFrame, products: pd.DataFrame, country_detail: pd.DataFrame) -> None:
    st.subheader("Which Industries Are Most Exposed")
    st.caption("Semiconductor content as a share of final product cost — the higher the bar, the more vulnerable that sector is to a Taiwan supply disruption.")

    fig = build_industry_exposure_figure(products)
    st.plotly_chart(fig, use_container_width=True, theme=None)

