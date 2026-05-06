from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from plotly_style import (
    ACCENT_RED,
    BORDER,
    DEPENDENCY_COLORSCALE,
    GEO_COAST,
    GEO_FRAME,
    GEO_LAND,
    GEO_OCEAN,
    NAVY,
    TEXT_PRIMARY,
    light_layout,
    style_figure,
)
from story_geo import TW_LAT, TW_LON, add_taiwan_export_arcs, centroid_for_iso3, illustrative_stage_for_iso3


def build_journey_map_figure(
    dest_latest: pd.DataFrame,
    *,
    map_view: str,
    show_arcs: bool = True,
) -> go.Figure:
    """Scatter geo: Taiwan export destinations + optional arc overlays."""
    d = dest_latest.copy()
    if "Country ID" in d.columns:
        d["Story stage"] = d["Country ID"].map(illustrative_stage_for_iso3)

    fig = px.scatter_geo(
        d,
        locations="Country ID",
        size="Exports (USD)",
        color="Share (%)",
        color_continuous_scale=[NAVY, ACCENT_RED],
        hover_name="Country",
        hover_data={"Story stage": True, "Exports (USD)": ":,", "Share (%)": True},
        projection="natural earth",
        title="Taiwanese exports reach every major economy — concentration varies by partner.",
        template="plotly_white",
    )
    light_layout(fig)
    fig.update_layout(
        title=dict(font=dict(color=TEXT_PRIMARY, size=15)),
        margin=dict(l=0, r=0, t=44, b=0),
    )
    fig.update_geos(
        bgcolor=GEO_OCEAN,
        landcolor=GEO_LAND,
        oceancolor=GEO_OCEAN,
        coastlinecolor=GEO_COAST,
        countrycolor=GEO_FRAME,
        framecolor=GEO_FRAME,
        showocean=True,
        showland=True,
    )
    fig.update_coloraxes(
        colorbar=dict(
            title=dict(text="Share (%)", side="right", font=dict(color=TEXT_PRIMARY)),
            tickfont=dict(color=TEXT_PRIMARY),
            outlinecolor=BORDER,
            outlinewidth=1,
            bgcolor="rgba(0,0,0,0)",
        )
    )
    fig.update_traces(
        marker=dict(line=dict(width=0.6, color=BORDER)),
        selector=dict(type="scattergeo"),
    )

    if show_arcs:
        add_taiwan_export_arcs(fig, dest_latest)

    if map_view == "Taiwan focus":
        fig.update_geos(
            center=dict(lat=TW_LAT, lon=TW_LON),
            projection_scale=14,
            showcountries=True,
            countrywidth=0.5,
        )

    return fig


def build_dependency_choropleth_figure(destinations: pd.DataFrame, *, year: int | None = None) -> go.Figure:
    """Choropleth: share of Taiwan exports by destination — diverging urgency scale."""

    if year is None:
        year = int(destinations["Year"].max())
    hover_df = destinations[destinations["Year"] == year].copy()
    fig = px.choropleth(
        hover_df,
        locations="Country ID",
        color="Share (%)",
        hover_name="Country",
        hover_data={"Exports (USD)": ":,", "Share (%)": True},
        title="If Taiwan stops — who feels it first",
        template="plotly_white",
        color_continuous_scale=DEPENDENCY_COLORSCALE,
    )
    style_figure(fig)
    fig.update_layout(
        title=dict(font=dict(color=TEXT_PRIMARY, size=15)),
        coloraxis=dict(colorbar=dict(title=dict(text="Share of Taiwan exports (%)", font=dict(size=11)))),
    )
    fig.update_coloraxes(
        cmin=0,
        cmax=max(hover_df["Share (%)"].max(), 0.01),
        colorbar=dict(
            tickfont=dict(color=TEXT_PRIMARY),
            outlinecolor="#E0E4EF",
        ),
    )

    top3 = hover_df.nlargest(3, "Share (%)")
    for _, row in top3.iterrows():
        cid = str(row.get("Country ID", "")).strip().upper()
        ll = centroid_for_iso3(cid)
        if ll is None:
            continue
        lat, lon = ll
        label = f"{row.get('Country', cid)}<br>{row['Share (%)']:.1f}%"
        fig.add_trace(
            go.Scattergeo(
                lat=[lat],
                lon=[lon],
                mode="markers+text",
                marker=dict(size=10, color=ACCENT_RED, symbol="circle", line=dict(width=1, color="#FFFFFF")),
                text=[label],
                textposition="top center",
                textfont=dict(size=10, color=TEXT_PRIMARY),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    return fig


def build_tsmc_revenue_figure(tsmc_df: pd.DataFrame) -> go.Figure | None:
    """TSMC revenue concentration — leading-edge economics in one firm."""
    if tsmc_df.empty or "Revenue_USD_bn" not in tsmc_df.columns:
        return None
    rev = tsmc_df.dropna(subset=["Revenue_USD_bn"])
    if rev.empty:
        return None
    fig = px.line(
        rev,
        x="Year",
        y="Revenue_USD_bn",
        markers=True,
        title="Foundry revenue concentrates at TSMC — scale that reshapes global allocation.",
        template="plotly_white",
    )
    light_layout(fig)
    fig.update_traces(line=dict(color=ACCENT_RED, width=2.5), marker=dict(color=ACCENT_RED, size=8))
    fig.update_layout(yaxis_title="USD bn", xaxis_title="Year")
    return fig
