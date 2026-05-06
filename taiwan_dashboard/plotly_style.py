"""Editorial palette: white surface, flag red / navy accents (policy-brief style)."""

from __future__ import annotations

from typing import Any

# Design system
PAGE_BG = "#FFFFFF"
SURFACE = "#F7F8FA"
TEXT_PRIMARY = "#0A0A0A"
TEXT_SECONDARY = "#5A5A6A"
ACCENT_RED = "#C8102E"
NAVY = "#003087"
BORDER = "#E0E4EF"
NEUTRAL_MUTED = "#A0A8BF"
WARNING_BG = "#FFE5E8"
CHINA_DARK = "#8B0000"

# Back-compat aliases used across tabs
TEXT = TEXT_PRIMARY
BLUE = NAVY
RED = ACCENT_RED
FABRIC_YELLOW = "#E8734A"
FABRIC_YIELD = FABRIC_YELLOW  # legacy typo alias

# Generic blue→red scale (maps, etc.)
COLOR_SCALE = [NAVY, ACCENT_RED]

# Dependency choropleth: white → orange → red (urgency)
DEPENDENCY_COLORSCALE = [
    [0.0, "#FFFFFF"],
    [0.35, "#FFD4B8"],
    [0.65, "#E8734A"],
    [1.0, "#C8102E"],
]

DISCRETE = [NAVY, ACCENT_RED, "#1a4a8c", "#d64545", "#003087", "#C8102E", NEUTRAL_MUTED, "#5a6a8a"]

GEO_LAND = "#E8ECF4"
GEO_OCEAN = "#F5F7FB"
GEO_COAST = "#C5CCD8"
GEO_FRAME = BORDER


def light_layout(fig: Any) -> Any:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=PAGE_BG,
        plot_bgcolor=PAGE_BG,
        font=dict(color=TEXT_PRIMARY),
        title_font=dict(color=TEXT_PRIMARY),
    )
    return fig


def _has_geo_trace(fig: Any) -> bool:
    for tr in fig.data:
        t = getattr(tr, "type", "") or ""
        if t in ("choropleth", "scattergeo"):
            return True
    return False


def _has_map_trace(fig: Any) -> bool:
    for tr in fig.data:
        if getattr(tr, "type", "") in ("scattermap", "scattermapbox"):
            return True
    return False


def style_figure(fig: Any) -> Any:
    light_layout(fig)
    if _has_geo_trace(fig):
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
    if _has_map_trace(fig):
        try:
            fig.update_mapboxes(style="carto-positron")
        except Exception:
            try:
                fig.update_layout(mapbox_style="carto-positron")
            except Exception:
                pass
    return fig


def sankey_node_colors(n: int) -> list[str]:
    return [DISCRETE[i % len(DISCRETE)] for i in range(n)]


def imshow_blue_red_scale() -> list[list]:
    return [[0.0, NAVY], [1.0, ACCENT_RED]]


SLIDER_CHART_DURATION_MS = 1200


def with_slider_animation(fig: Any, *, chart_id: str, duration_ms: int = SLIDER_CHART_DURATION_MS) -> Any:
    fig.update_layout(
        transition=dict(duration=int(duration_ms), easing="cubic-in-out"),
        uirevision=chart_id,
    )
    return fig
