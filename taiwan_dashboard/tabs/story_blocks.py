from __future__ import annotations

import streamlit.components.v1 as components

from plotly_style import BLUE, FABRIC_YELLOW, PAGE_BG, TEXT_PRIMARY

TEXT = TEXT_PRIMARY


def render_convergence() -> None:
    """Micro-section: globe → Taiwan → cleanroom (CSS metaphor)."""
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <style>
    html, body {{ margin:0; padding:0; background:{PAGE_BG}; }}
    .box {{
      font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
      max-width: 720px;
      margin: 0 auto;
      padding: 1.5rem 1rem 1.25rem 1rem;
      text-align: center;
      box-sizing: border-box;
    }}
    .headline {{
      font-size: clamp(1.4rem, 4vw, 2rem);
      font-weight: 800;
      color: {TEXT};
      letter-spacing: -0.02em;
      margin: 0 0 1rem 0;
    }}
    .seq {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      flex-wrap: wrap;
      font-size: clamp(1.5rem, 5vw, 2.25rem);
      margin-top: 0.25rem;
    }}
    .earth {{
      width: 2.25rem;
      height: 2.25rem;
      border-radius: 50%;
      background: radial-gradient(circle at 32% 28%, #93c5fd 0%, #3b82f6 45%, #1e3a8a 100%);
      border: 1px solid #60a5fa;
      animation: pulse 3.2s ease-in-out infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 0.65; transform: scale(1); }}
      50% {{ opacity: 1; transform: scale(1.08); }}
    }}
    .arrow {{
      color: #6b7280;
      font-weight: 300;
      font-size: 1.25rem;
    }}
    .tw {{
      display: inline-block;
      padding: 0.15rem 0.55rem;
      border-radius: 6px;
      background: linear-gradient(135deg, #1e3a8a 0%, #172554 100%);
      border: 1px solid {BLUE};
      color: #ffffff;
      font-size: 0.85rem;
      font-weight: 700;
      letter-spacing: 0.08em;
    }}
    .clean {{
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: {FABRIC_YELLOW};
      margin-top: 0.85rem;
    }}
  </style>
</head>
<body>
  <div class="box">
    <p class="headline">Everything converges here.</p>
    <div class="seq">
      <span class="earth" title="Global"></span>
      <span class="arrow">&#8594;</span>
      <span class="tw">TAIWAN</span>
      <span class="arrow">&#8594;</span>
      <span class="clean">Cleanroom</span>
    </div>
  </div>
</body>
</html>"""
    components.html(page, width=1400, height=220, scrolling=False)


def render_final_takeaway() -> None:
    """Closing fullscreen-style block."""
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <style>
    html, body {{ margin:0; padding:0; background:{PAGE_BG}; }}
    .fin {{
      font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
      min-height: 320px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
      padding: 2.5rem 1.5rem;
      box-sizing: border-box;
      border-top: 1px solid #e5e7eb;
      border-bottom: 1px solid #e5e7eb;
      margin: 0.5rem 0 0 0;
    }}
    .fin p {{
      margin: 0 0 0.85rem 0;
      max-width: 28rem;
      font-size: clamp(1.05rem, 2.8vw, 1.35rem);
      font-weight: 500;
      line-height: 1.55;
      color: {TEXT};
    }}
    .fin .muted {{
      color: #6b7280;
      font-weight: 400;
      font-size: clamp(0.95rem, 2.4vw, 1.12rem);
    }}
    .fin .last {{
      margin-top: 1.25rem;
      font-size: clamp(0.88rem, 2.2vw, 1rem);
      color: {BLUE};
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <div class="fin">
    <p>This started as sand.</p>
    <p>It became the most complex manufacturing process ever created.</p>
    <p>And today&#8212;<br/><span class="muted">it holds the modern world together.</span></p>
    <p class="last">If it stops&#8212;everything feels it.</p>
  </div>
</body>
</html>"""
    components.html(page, width=1400, height=420, scrolling=False)
