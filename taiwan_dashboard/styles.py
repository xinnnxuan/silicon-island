from __future__ import annotations

import streamlit as st

_PAGE_BG = "#FFFFFF"
_SURFACE = "#F7F8FA"
_TEXT = "#0A0A0A"
_TEXT_MUTED = "#5A5A6A"
_NAVY = "#003087"
_RED = "#C8102E"
_BORDER = "#E0E4EF"
_WARNING_BG = "#FFE5E8"
_LINK = "#003087"

_GLOBAL_CSS = f"""
<style>
  html, body, .stApp, [data-testid="stAppViewContainer"] {{
    background-color: {_PAGE_BG} !important;
  }}
  [data-testid="stHeader"] {{
    background-color: {_PAGE_BG} !important;
  }}
  section.main > div,
  [data-testid="stMain"] > div {{
    background-color: {_PAGE_BG} !important;
  }}
  .main .block-container {{
    background-color: transparent;
    padding-top: 1.25rem;
    max-width: 1200px;
  }}
  [data-testid="stMain"] {{
    color: {_TEXT} !important;
    line-height: 1.7 !important;
  }}
  [data-testid="stMain"] .stMarkdown,
  [data-testid="stMain"] .stMarkdown * {{
    color: {_TEXT} !important;
  }}
  [data-testid="stSidebar"] {{
    display: none !important;
  }}
  [data-testid="collapsedControl"],
  [data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
  }}
  [data-testid="stMain"] [data-testid="stRadio"] [role="radiogroup"] {{
    flex-wrap: wrap !important;
    gap: 0.35rem 1rem !important;
    justify-content: flex-start !important;
  }}
  [data-testid="stMetricValue"],
  [data-testid="stMetricLabel"],
  [data-testid="stMetricDelta"] {{
    color: {_TEXT} !important;
  }}
  .stCaption {{
    color: {_TEXT_MUTED} !important;
    font-style: italic !important;
    font-size: 0.85rem !important;
  }}
  [data-testid="stMain"] label p,
  [data-testid="stMain"] .stRadio label,
  [data-testid="stMain"] .stMultiSelect label p {{
    color: {_TEXT} !important;
  }}
  [data-testid="stAlert"], .stAlert {{
    color: {_TEXT} !important;
  }}
  [data-testid="stMain"] a {{
    color: {_LINK} !important;
    text-decoration: underline;
  }}
  hr {{
    border-color: {_BORDER} !important;
    margin: 2rem 0 !important;
  }}
  [data-testid="stPlotlyChart"],
  [data-testid="stPlotlyChart"] > div,
  .js-plotly-plot .plotly {{
    background-color: {_PAGE_BG} !important;
  }}
  div[data-testid="stVerticalBlockBorderWrapper"]:has(iframe) {{
    margin-bottom: -0.5rem !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
  }}
  div[data-testid="stVerticalBlockBorderWrapper"] iframe {{
    background: transparent !important;
  }}
  [data-testid="stMarkdownContainer"]:has(.td-hero-root) {{
    box-shadow: none !important;
    border: none !important;
    background: transparent !important;
  }}
  [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stMarkdownContainer"] .td-hero-root) {{
    box-shadow: none !important;
    border: none !important;
    background: transparent !important;
  }}

  .td-section-h2 {{
    font-size: clamp(1.65rem, 3vw, 2.05rem);
    font-weight: 700;
    color: {_NAVY};
    margin: 1.75rem 0 0.75rem 0;
    letter-spacing: -0.02em;
  }}
  .td-subtitle {{
    color: {_TEXT_MUTED};
    font-size: 1rem;
    margin: -0.35rem 0 1rem 0;
  }}
  .td-story-transition {{
    font-size: 1.05rem;
    font-style: italic;
    color: {_TEXT_MUTED};
    border-left: 3px solid {_RED};
    padding: 0.65rem 0 0.65rem 1rem;
    margin: 1.25rem 0 1.5rem 0;
    background: {_SURFACE};
    line-height: 1.65;
  }}
  .td-section-kicker {{
    text-align: center;
    font-variant: small-caps;
    letter-spacing: 0.22em;
    font-size: 0.72rem;
    color: {_NAVY};
    margin: 2rem 0 0.35rem 0;
  }}
  .td-section-rule {{
    border-top: 1px solid {_BORDER};
    margin: 0.25rem 0 1.5rem 0;
  }}
  .td-stat-card-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin: 1rem 0 1.5rem 0;
  }}
  .td-stat-card {{
    flex: 1 1 200px;
    background: {_SURFACE};
    border-left: 3px solid {_RED};
    box-shadow: 0 1px 4px rgba(0, 48, 135, 0.08);
    padding: 1rem 1.1rem;
    border-radius: 2px;
  }}
  .td-stat-num {{
    font-size: clamp(1.75rem, 3vw, 2.35rem);
    font-weight: 800;
    color: {_RED};
    line-height: 1.1;
  }}
  .td-stat-cap {{
    font-size: 0.82rem;
    color: {_TEXT_MUTED};
    margin-top: 0.35rem;
    line-height: 1.35;
  }}
  .td-concallout {{
    display: flex;
    align-items: flex-start;
    gap: 1.25rem;
    background: {_SURFACE};
    border-left: 3px solid {_RED};
    box-shadow: 0 1px 4px rgba(0, 48, 135, 0.08);
    padding: 1rem 1.25rem;
    margin: 0.75rem 0 1.25rem 0;
  }}
  .td-concallout-stat {{
    font-size: clamp(2rem, 4vw, 2.75rem);
    font-weight: 800;
    color: {_RED};
    white-space: nowrap;
  }}
  .td-concallout-txt {{
    font-size: 0.95rem;
    color: {_TEXT};
    line-height: 1.55;
    padding-top: 0.35rem;
  }}
  .td-warning-callout {{
    background: {_WARNING_BG};
    border-left: 4px solid {_RED};
    padding: 0.85rem 1rem;
    margin: 0.75rem 0 1rem 0;
    color: {_NAVY};
    font-weight: 600;
    border-radius: 2px;
  }}
  [data-testid="stSlider"] .stSlider > div > div > div {{
    background-color: {_NAVY} !important;
  }}
  [data-baseweb="select"] {{
    background-color: {_PAGE_BG} !important;
  }}
  [data-baseweb="select"] > div,
  [data-baseweb="select"] > div > div {{
    background-color: {_PAGE_BG} !important;
    border-color: {_BORDER} !important;
    color: {_TEXT} !important;
  }}
  [data-baseweb="select"] input,
  [data-baseweb="select"] span {{
    color: {_TEXT} !important;
    background-color: {_PAGE_BG} !important;
  }}
  [data-baseweb="tag"] {{
    background-color: {_NAVY} !important;
    color: #ffffff !important;
  }}
  [data-baseweb="popover"] [role="option"],
  [data-baseweb="menu"] {{
    background-color: {_PAGE_BG} !important;
    color: {_TEXT} !important;
  }}
</style>
"""


def inject_sidebar_styles() -> None:
    """Editorial light theme aligned with plotly_style."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)
