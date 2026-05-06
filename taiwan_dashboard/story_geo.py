"""Approximate centroids for Taiwan-export arc overlays (illustrative routing, not vessel paths)."""

from __future__ import annotations

from typing import Tuple

import pandas as pd
import plotly.graph_objects as go

# Taiwan reference point
TW_LAT, TW_LON = 23.55, 121.0

# ISO 3166-1 alpha-3 → (lat, lon) approximate
_CENTROIDS: dict[str, Tuple[float, float]] = {
    "USA": (39.8, -98.6),
    "CHN": (35.9, 104.2),
    "HKG": (22.3, 114.2),
    "JPN": (36.2, 138.25),
    "KOR": (36.5, 127.9),
    "SGP": (1.35, 103.82),
    "DEU": (51.2, 10.45),
    "NLD": (52.13, 5.29),
    "GBR": (54.0, -2.5),
    "VNM": (14.06, 108.28),
    "MYS": (4.21, 101.98),
    "THA": (15.87, 100.99),
    "IND": (20.59, 78.96),
    "AUS": (-25.27, 133.78),
    "FRA": (46.23, 2.21),
    "ITA": (41.87, 12.57),
    "CAN": (56.13, -106.35),
    "MEX": (23.63, -102.55),
    "IDN": (-0.79, 113.92),
    "PHL": (12.88, 121.77),
    "ARE": (23.42, 53.85),
    "SAU": (23.89, 45.08),
    "BRA": (-14.24, -51.93),
    "TUR": (38.96, 35.24),
    "POL": (51.92, 19.15),
    "CZE": (49.82, 15.47),
    "SWE": (60.13, 18.64),
    "ESP": (40.46, -3.75),
    "BEL": (50.5, 4.47),
    "AUT": (47.52, 14.55),
    "CHE": (46.82, 8.23),
    "ISR": (31.05, 34.85),
    "ZAF": (-30.56, 22.94),
    "RUS": (61.52, 105.32),
    "UKR": (48.38, 31.17),
    "NOR": (60.47, 8.47),
    "FIN": (61.92, 25.75),
    "DNK": (56.26, 9.5),
    "IRL": (53.41, -8.24),
    "PRT": (39.4, -8.22),
    "GRC": (39.07, 21.82),
    "NZL": (-40.9, 174.89),
    "CHL": (-35.68, -71.54),
    "ARG": (-38.42, -63.62),
    "EGY": (26.82, 30.8),
    "NGA": (9.08, 8.68),
    "KEN": (-0.02, 37.91),
    "TWN": (TW_LAT, TW_LON),
}


def centroid_for_iso3(iso3: str) -> Tuple[float, float] | None:
    """Return approximate (lat, lon) for map annotations; None if unknown."""
    return _CENTROIDS.get(str(iso3).strip().upper())


def add_taiwan_export_arcs(fig: go.Figure, dest_latest: pd.DataFrame, *, max_routes: int = 18) -> go.Figure:
    """Add great-circle-style polylines from Taiwan to top destinations (by export value)."""
    if dest_latest.empty or "Country ID" not in dest_latest.columns:
        return fig
    top = dest_latest.nlargest(max_routes, "Exports (USD)")
    for _, row in top.iterrows():
        cid = str(row["Country ID"]).strip().upper()
        if cid not in _CENTROIDS:
            continue
        lat1, lon1 = TW_LAT, TW_LON
        lat2, lon2 = _CENTROIDS[cid]
        # Midpoint bump for arc illusion
        mid_lat = (lat1 + lat2) / 2 + abs(lat2 - lat1) * 0.08
        mid_lon = (lon1 + lon2) / 2
        fig.add_trace(
            go.Scattergeo(
                lat=[lat1, mid_lat, lat2],
                lon=[lon1, mid_lon, lon2],
                mode="lines",
                line=dict(width=1, color="rgba(0, 0, 149, 0.4)"),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    return fig


def illustrative_stage_for_iso3(iso3: str) -> str:
    """Conceptual supply-chain stage labels for hover (not from trade statistics)."""
    m = str(iso3).strip().upper()
    if m in ("USA", "CAN", "AUS"):
        return "Materials & design ecosystems (illustrative)"
    if m in ("CHN",):
        return "Refining & manufacturing scale (illustrative)"
    if m in ("JPN", "KOR", "DEU", "NLD", "CHE"):
        return "Equipment, materials & precision industry (illustrative)"
    if m in ("TWN",):
        return "Advanced fabrication (illustrative)"
    return "Trade partner (see export value)"
