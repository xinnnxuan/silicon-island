from __future__ import annotations

import base64
import html

import streamlit as st

from config import ASSETS_DIR, BASE_DIR, ICON_DIR

_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def _taiwan_flag_map_data_uri() -> str | None:
    """Load taiwan-flag-map* from assets/, public/, icons/, or project parent."""
    search_dirs = [ASSETS_DIR, BASE_DIR / "public", ICON_DIR, BASE_DIR.parent]
    stems = ("taiwan-flag-map", "taiwan_flag_map", "Taiwan-flag-map")

    def encode(path) -> str:
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{_MIME[path.suffix.lower()]};base64,{b64}"

    for directory in search_dirs:
        if not directory.is_dir():
            continue
        for stem in stems:
            for ext in _MIME:
                p = directory / f"{stem}{ext}"
                if p.is_file():
                    return encode(p)
            for p in sorted(directory.glob(f"{stem}.*")):
                if p.suffix.lower() in _MIME:
                    return encode(p)
        for p in sorted(directory.glob("taiwan-flag-map*")):
            if p.suffix.lower() in _MIME:
                return encode(p)
        for p in sorted(directory.glob("taiwan_flag_map*")):
            if p.suffix.lower() in _MIME:
                return encode(p)
        for name in ("TAIWAN.png", "Taiwan.png", "taiwan.png"):
            p = directory / name
            if p.is_file():
                return encode(p)
    return None


def render(
    metric_1: str,
    label_1: str,
) -> None:
    flag_uri = _taiwan_flag_map_data_uri()

    if flag_uri:
        safe_uri = html.escape(flag_uri, quote=True)
        st.markdown(
            f"""
<div style="position:relative; width:100%; line-height:0; overflow:hidden;">
  <img
    src="{safe_uri}"
    alt="Taiwan flag map"
    style="width:100%; height:auto; display:block; max-height:520px; object-fit:contain; transform:translateX(-7%);"
  />
  <div style="
    position: absolute;
    top: 28%;
    left: 0;
    right: 0;
    text-align: center;
    pointer-events: none;
    line-height: normal;
  ">
    <div style="
      font-size: clamp(2.8rem, 9vw, 5.5rem);
      font-weight: 900;
      letter-spacing: 0.06em;
      color: #000000;
      line-height: 1;
      text-shadow: 0 0 24px rgba(255,255,255,0.85), 0 0 10px rgba(255,255,255,0.7);
    ">TAIWAN</div>
    <div style="
      font-size: clamp(0.85rem, 2.5vw, 1.15rem);
      color: #000000;
      margin-top: 0.5rem;
      letter-spacing: 0.18em;
      font-weight: 600;
      text-transform: uppercase;
      text-shadow: 0 0 16px rgba(255,255,255,0.9), 0 0 8px rgba(255,255,255,0.75);
    ">How one island became the world's most critical supply chain</div>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("## TAIWAN")

    # ── 3 KPIs ────────────────────────────────────────────────────────────────
    st.markdown(
        f"""
<div style="display:flex;align-items:flex-start;width:100%;margin:3.5rem 0 3.5rem 0;">
  <div style="flex:1;text-align:center;">
    <div style="font-size:clamp(2.4rem,5vw,3.2rem);font-weight:900;color:#C8102E;line-height:1;">{metric_1}</div>
    <div style="font-size:1rem;font-weight:700;color:#5A5A6A;margin-top:0.45rem;text-transform:uppercase;letter-spacing:0.05em;">{label_1}</div>
  </div>
  <div style="flex:1;text-align:center;">
    <div style="font-size:clamp(2.4rem,5vw,3.2rem);font-weight:900;color:#C8102E;line-height:1;">~90%</div>
    <div style="font-size:1rem;font-weight:700;color:#5A5A6A;margin-top:0.45rem;text-transform:uppercase;letter-spacing:0.05em;">TSMC share of leading-edge chips</div>
  </div>
  <div style="flex:1;text-align:center;">
    <div style="font-size:clamp(2.4rem,5vw,3.2rem);font-weight:900;color:#C8102E;line-height:1;">$90B</div>
    <div style="font-size:1rem;font-weight:700;color:#5A5A6A;margin-top:0.45rem;text-transform:uppercase;letter-spacing:0.05em;">TSMC revenue (2024)</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

