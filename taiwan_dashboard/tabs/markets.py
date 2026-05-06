from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from config import DATA_DIR
from plotly_style import COLOR_SCALE, DISCRETE, light_layout


def _load_index_csv(name: str) -> pd.DataFrame | None:
    p = Path(DATA_DIR) / "Markets" / f"{name}.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    if "Date" not in df or "Close" not in df:
        return None
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Return"] = df["Close"].pct_change()
    df["Index"] = 100 * df["Close"] / df["Close"].iloc[0]
    return df[["Date", "Close", "Return", "Index"]]


def _load_events() -> pd.DataFrame | None:
    p = Path(DATA_DIR) / "Markets" / "events.csv"
    if not p.exists():
        return None
    ev = pd.read_csv(p)
    if "Date" not in ev or "Label" not in ev or "Severity" not in ev:
        return None
    ev["Date"] = pd.to_datetime(ev["Date"])
    return ev


def _drawdown_after(df: pd.DataFrame, event_date: pd.Timestamp, windows: List[int]) -> Dict[int, float]:
    out: Dict[int, float] = {}
    for w in windows:
        sub = df[(df["Date"] > event_date) & (df["Date"] <= event_date + pd.Timedelta(days=w))]
        if sub.empty:
            out[w] = np.nan
            continue
        # drawdown from event close to min close in window
        start = df.loc[df["Date"] <= event_date, "Close"].iloc[-1]
        min_close = sub["Close"].min()
        out[w] = (min_close / start - 1.0) * 100.0
    return out


def render() -> None:
    st.subheader("Market Reaction Analysis")
    st.write("Overlays and event drawdowns for TAIEX, SOX, and EWT if CSVs are provided.")

    taiex = _load_index_csv("taiex")
    sox = _load_index_csv("sox")
    ewt = _load_index_csv("ewt")
    ev = _load_events()

    if all(x is None for x in [taiex, sox, ewt]):
        st.info(
            "Place CSVs under Datasets/Markets named taiex.csv, sox.csv, ewt.csv with columns [Date, Close]. "
            "Optionally add events.csv with [Date, Label, Severity]."
        )
        return

    # Overlay chart
    frames = []
    if taiex is not None:
        f = taiex.copy(); f["Series"] = "TAIEX"; frames.append(f)
    if sox is not None:
        f = sox.copy(); f["Series"] = "SOX"; frames.append(f)
    if ewt is not None:
        f = ewt.copy(); f["Series"] = "EWT"; frames.append(f)
    overlay = pd.concat(frames, ignore_index=True)

    fig = px.line(overlay, x="Date", y="Index", color="Series", title="Indexed Price Overlays")
    st.plotly_chart(fig, use_container_width=True)

    # Event drawdowns
    if ev is not None:
        rows = []
        for _, e in ev.iterrows():
            d = {"Label": e["Label"], "Severity": e["Severity"]}
            if taiex is not None:
                d.update({f"TAIEX {w}d": _drawdown_after(taiex, e["Date"], [w])[w] for w in [5, 10, 30]})
            if sox is not None:
                d.update({f"SOX {w}d": _drawdown_after(sox, e["Date"], [w])[w] for w in [5, 10, 30]})
            if ewt is not None:
                d.update({f"EWT {w}d": _drawdown_after(ewt, e["Date"], [w])[w] for w in [5, 10, 30]})
            rows.append(d)
        dd = pd.DataFrame(rows)
        st.write("Event Drawdowns (min return within window, %)")
        st.dataframe(dd, use_container_width=True)

        # Scatter: Severity vs 10d drawdown for a selected series
        series_opt = [c for c in dd.columns if c.endswith("10d") and c != "Severity"]
        if series_opt:
            pick = st.selectbox("Series for severity vs drawdown", series_opt, index=0)
            fig2 = px.scatter(
                dd,
                x="Severity",
                y=pick,
                hover_name="Label",
                title=f"Event Severity vs {pick} Drawdown",
                template="plotly_white",
                color="Severity",
                color_continuous_scale=COLOR_SCALE,
            )
            light_layout(fig2)
            st.plotly_chart(fig2, use_container_width=True, theme=None)

