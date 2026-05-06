from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from plotly_style import ACCENT_RED, NEUTRAL_MUTED, TEXT_PRIMARY, light_layout


def render_fragility_story(_destinations: pd.DataFrame, _products: pd.DataFrame, _semi: pd.DataFrame) -> None:
    st.markdown(
        '<h2 class="td-section-h2">What breaks if it stops</h2>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Based on observed inventory buffers during the 2020–2022 chip shortage. "
        "Timelines are approximate — actual impact depends on each sector's buffer stock."
    )

    sectors = pd.DataFrame([
        {"Sector": "Automotive",          "Months until shortage": 3,  "What happens": "Assembly lines halt; ~$210B revenue lost per quarter",        "Severity": "Critical"},
        {"Sector": "Consumer Electronics","Months until shortage": 5,  "What happens": "Phones, laptops, TVs go out of stock within weeks",            "Severity": "Critical"},
        {"Sector": "Industrial Equipment","Months until shortage": 8,  "What happens": "Factory robots, CNC machines stop shipping",                   "Severity": "Severe"},
        {"Sector": "Telecommunications",  "Months until shortage": 10, "What happens": "5G infrastructure buildout freezes",                           "Severity": "Severe"},
        {"Sector": "Medical Devices",     "Months until shortage": 13, "What happens": "MRI, CT, monitoring equipment production stalls",              "Severity": "Moderate"},
        {"Sector": "Data Centers",        "Months until shortage": 13, "What happens": "GPU/CPU scarcity slows AI and cloud expansion",                "Severity": "Moderate"},
        {"Sector": "Defense / Aerospace", "Months until shortage": 22, "What happens": "Strategic reserves provide buffer — but not indefinitely",     "Severity": "Managed"},
    ])

    _color_map = {"Critical": "#ef4444", "Severe": "#f97316", "Moderate": "#eab308", "Managed": "#22c55e"}
    sectors["Color"] = sectors["Severity"].map(_color_map)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sectors["Months until shortage"],
        y=sectors["Sector"],
        orientation="h",
        marker_color=sectors["Color"],
        customdata=sectors[["What happens", "Severity"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Runway: ~%{x} months<br>"
            "%{customdata[0]}<br>"
            "<i>Severity: %{customdata[1]}</i><extra></extra>"
        ),
    ))

    fig.add_vline(
        x=12,
        line_dash="dash",
        line_color="#94a3b8",
        line_width=1.5,
        annotation_text="1 year",
        annotation_position="top",
        annotation_font=dict(size=11, color="#64748b"),
    )

    light_layout(fig)
    fig.update_layout(
        xaxis=dict(title="Months until shortage hits production", gridcolor="#e2e8f0", range=[0, 26]),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=0, r=40, t=20, b=40),
        showlegend=False,
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True, theme=None, key="story_fragility_chart")
    st.caption(
        "Sources: SIA, McKinsey Global Institute, Alixpartners (automotive shortage analysis). "
        "Defense buffer from CSIS supply chain resilience estimates."
    )


