from __future__ import annotations

import re
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import streamlit as st

from config import DEST_DIR, PROD_DIR, DATA_DIR, COUNTRY_DETAIL_DIR, TSMC_DIR

_TRADE_DIR = DATA_DIR / "Trade"


def _tsmc_coerce_number(x: object) -> float:
    """Parse TSMC CSV cells: n/a, ~32, '20–30' ranges, '55 (footnotes)' -> float; else NaN."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return np.nan
    s = str(x).strip()
    if not s or s.lower() in ("n/a", "nan", "-"):
        return np.nan
    s = s.lstrip("~")
    range_m = re.match(r"^\s*([\d.]+)\s*[–\-]\s*([\d.]+)\s*$", s)
    if range_m:
        return (float(range_m.group(1)) + float(range_m.group(2))) / 2.0
    m = re.search(r"([\d.]+)", s)
    if m:
        return float(m.group(1))
    return np.nan


_TSM_COLUMN_RENAME = {
    "Revenue (USD bn)": "Revenue_USD_bn",
    "Revenue (NTD bn)": "Revenue_NTD_bn",
    "Gross Margin %": "Gross_margin_pct",
    "Operating Margin %": "Operating_margin_pct",
    "Net Margin %": "Net_margin_pct",
    "HPC %": "HPC_pct",
    "Smartphone %": "Smartphone_pct",
    "IoT %": "IoT_pct",
    "Automotive %": "Automotive_pct",
    "DCE %": "DCE_pct",
    "Advanced Node %": "Advanced_total_pct",
    "3nm %": "Node_3nm_pct",
    "5nm %": "Node_5nm_pct",
    "7nm %": "Node_7nm_pct",
    "Foundry Share %": "Foundry_market_share_pct",
}

_TSM_COERCE_COLS = (
    "Revenue_USD_bn",
    "Revenue_NTD_bn",
    "Gross_margin_pct",
    "Operating_margin_pct",
    "Net_margin_pct",
    "HPC_pct",
    "Smartphone_pct",
    "IoT_pct",
    "Automotive_pct",
    "DCE_pct",
    "Advanced_total_pct",
    "Node_3nm_pct",
    "Node_5nm_pct",
    "Node_7nm_pct",
    "Foundry_market_share_pct",
)
 
 
@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # ── Destinations ───────────────────────────────────────────────────────
    dest_frames: List[pd.DataFrame] = []
    for file in sorted(DEST_DIR.glob("*.csv")):
        dest_frames.append(pd.read_csv(file))
    destinations = pd.concat(dest_frames, ignore_index=True)
 
    # ── Products ───────────────────────────────────────────────────────────
    prod_frames: List[pd.DataFrame] = []
    for file in sorted(PROD_DIR.glob("*.csv")):
        prod_frames.append(pd.read_csv(file))
    products = pd.concat(prod_frames, ignore_index=True)
 
    # ── Shared cleanup ─────────────────────────────────────────────────────
    for frame in (destinations, products):
        frame["Year"] = frame["Year"].astype(int)
        frame["Exports (USD)"] = pd.to_numeric(frame["Exports (USD)"], errors="coerce").fillna(0)
        frame["Share (%)"] = pd.to_numeric(frame["Share (%)"], errors="coerce").fillna(0)

    # ── Normalise variant country names ────────────────────────────────────
    _COUNTRY_ALIASES = {
        "Hong Kong, China":        "Hong Kong",
        "Korea, Republic of":      "South Korea",
        "United States of America": "United States",
    }
    destinations["Country"] = destinations["Country"].replace(_COUNTRY_ALIASES)
 
    # ── Chip series: derive from products (HS 8542 integrated circuits) ──────
    ic_mask = (
        products["HS4"].str.contains("8542", na=False)
        | products["HS4"].str.lower().str.contains("integrated circuit", na=False)
    )
    ic_df = products[ic_mask]
    if not ic_df.empty:
        chip_series = (
            ic_df.groupby("Year", as_index=False)["Exports (USD)"]
            .sum()
            .rename(columns={"Exports (USD)": "Chip Exports (USD)"})
            .sort_values("Year")
        )
    else:
        chip_series = pd.DataFrame(columns=["Year", "Chip Exports (USD)"])
 
    # ── Trade balance workbook ─────────────────────────────────────────────
    trade_balance = pd.DataFrame()
    trade_book = DATA_DIR / "Value of Exports and Imports.xlsx"
    if trade_book.exists():
        bal_raw = pd.read_excel(trade_book)
        bal_raw.columns = [str(c).strip() for c in bal_raw.columns]
        bal_raw["Year"] = pd.to_numeric(bal_raw["Year"], errors="coerce")
        monthly = bal_raw[bal_raw["Month"].astype(str).str.lower() == "total"].copy()
        trade_balance = monthly[
            ["Year", "Total Exports", "Total Imports", "Trade Surplus (or Deficit)"]
        ].dropna(subset=["Year"])
        for col in ["Total Exports", "Total Imports", "Trade Surplus (or Deficit)"]:
            trade_balance[col] = pd.to_numeric(trade_balance[col], errors="coerce").fillna(0) * 1_000_000
        trade_balance["Year"] = trade_balance["Year"].astype(int)
        trade_balance = trade_balance.sort_values("Year")
 
    # ── Country-level commodity detail ─────────────────────────────────────
    country_detail_frames: List[pd.DataFrame] = []
    if COUNTRY_DETAIL_DIR.exists():
        for file in sorted(COUNTRY_DETAIL_DIR.glob("*.xlsx")):
            try:
                cdf = pd.read_excel(file)
            except Exception:
                continue
            cdf.columns = [str(c).strip() for c in cdf.columns]
            if not {"Year", "ROC Year", "Month"}.issubset(set(cdf.columns)):
                continue
 
            _STEM_ALIASES = {
                "SouthKorea": "South Korea",
                "HongKong": "Hong Kong",
                "ChinaHongKong": "Hong Kong",
                "Irac": "Iraq",
                "Democratic Republic of Timor-Leste": "Timor-Leste",
                "Eastern Europe": None,
                "European Union": None,
            }
            stem = file.stem
            mapped = _STEM_ALIASES.get(stem, stem)
            if mapped is None:
                continue
            cdf["Country"] = mapped
            cdf["Year"] = pd.to_numeric(cdf["Year"], errors="coerce").astype("Int64")
            cdf["ROC Year"] = pd.to_numeric(cdf["ROC Year"], errors="coerce").astype("Int64")
            cdf["Month"] = (
                cdf["Month"]
                .astype(str)
                .str.strip()
                .str.replace("月", "", regex=False)
                .str.replace("⽉", "", regex=False)
                .str.lower()
            )
            cdf["Month"] = np.where(
                cdf["Month"] == "total",
                np.nan,
                pd.to_numeric(cdf["Month"], errors="coerce"),
            )
 
            measure_cols = [c for c in cdf.columns if c not in {"Year", "ROC Year", "Month", "Country"}]
            for col in measure_cols:
                cdf[col] = (
                    cdf[col]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace("－", "0", regex=False)
                    .str.strip()
                )
                cdf[col] = pd.to_numeric(cdf[col], errors="coerce")
                # The Exports by Country XLSX reports values in thousand USD.
                # Normalize to USD to align with other datasets.
                cdf[col] = cdf[col] * 1000
 
            long_df = cdf.melt(
                id_vars=["Country", "Year", "ROC Year", "Month"],
                value_vars=measure_cols,
                var_name="Commodity",
                value_name="Exports",
            )
            country_detail_frames.append(long_df.dropna(subset=["Year", "Exports"]))
 
    country_detail = (
        pd.concat(country_detail_frames, ignore_index=True)
        if country_detail_frames
        else pd.DataFrame()
    )
 
    return destinations, products, chip_series, trade_balance, country_detail
 
 
def semicon_proxy(products: pd.DataFrame) -> pd.DataFrame:
    # HS chapter 85 = Electrical machinery & electronics (includes ICs, semiconductors).
    # Also catch via Section label in case the ID column name varies.
    hs_mask = pd.to_numeric(products.get("HS4 ID", pd.Series(dtype=object)), errors="coerce") == 85
    section_mask = products["Section"].str.lower().str.contains("electrical", na=False)
    return products[hs_mask | section_mask].copy()


def _read_csv_with_encoding_fallback(path: Path) -> pd.DataFrame:
    """Try common encodings for hand-edited CSVs (Excel / Windows / zh-TW)."""
    last_err: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "cp950", "big5", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as e:
            last_err = e
            continue
    if last_err:
        raise last_err
    return pd.read_csv(path)


@st.cache_data
def load_taiwan_gdp() -> pd.DataFrame:
    """Taiwan quarterly GDP (DGBAS) → annual totals in USD bn. Returns [Year, GDP_USD_bn]."""
    p = DATA_DIR / "Taiwan official statistics (MOEA:DGBAS).csv"
    if not p.exists():
        return pd.DataFrame(columns=["Year", "GDP_USD_bn"])
    annual: dict[int, float] = {}
    for encoding in ("cp950", "big5", "utf-8-sig", "latin-1"):
        try:
            import csv as _csv
            with open(p, encoding=encoding) as f:
                rows = list(_csv.reader(f))
            gdp_col = next(
                (i for i, c in enumerate(rows[2]) if "GDP" in c and "U.S" in c and "Per Capita" not in c),
                9,
            )
            for r in rows[3:]:
                if len(r) > gdp_col and "Q" in r[0]:
                    try:
                        year = int(r[0].strip().split()[0])
                        val = float(r[gdp_col].replace(",", ""))
                        annual[year] = annual.get(year, 0.0) + val
                    except (ValueError, IndexError):
                        pass
            break
        except UnicodeDecodeError:
            continue
    if not annual:
        return pd.DataFrame(columns=["Year", "GDP_USD_bn"])
    df = pd.DataFrame({"Year": list(annual.keys()), "GDP_USD_bn": list(annual.values())})
    df["GDP_USD_bn"] = df["GDP_USD_bn"] / 1000  # million → billion
    return df.sort_values("Year")


@st.cache_data
def load_us_taiwan_trade() -> pd.DataFrame:
    """US Census bilateral trade data (US-Taiwan Trade.xlsx).

    Columns: Year, US_Imports_mn, US_Exports_mn, Trade_Balance_mn (USD millions).
    Negative balance = US trade deficit with Taiwan.
    """
    p = DATA_DIR / "US-Taiwan Trade.xlsx"
    if not p.exists():
        return pd.DataFrame(columns=["Year", "US_Imports_mn", "US_Exports_mn", "Trade_Balance_mn"])
    df = pd.read_excel(p)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns={"year": "Year"})
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    df["US_Imports_mn"] = pd.to_numeric(df.get("IYR", pd.Series(dtype=float)), errors="coerce").fillna(0)
    df["US_Exports_mn"] = pd.to_numeric(df.get("EYR", pd.Series(dtype=float)), errors="coerce").fillna(0)
    df["Trade_Balance_mn"] = df["US_Exports_mn"] - df["US_Imports_mn"]
    return df[["Year", "US_Imports_mn", "US_Exports_mn", "Trade_Balance_mn"]].sort_values("Year")


@st.cache_data
def load_taiex() -> pd.DataFrame:
    """TAIEX daily close prices → yearly averages. Returns DataFrame with [Year, TAIEX]."""
    p = DATA_DIR / "Market Data" / "chart_20260401T220618.csv"
    if not p.exists():
        return pd.DataFrame(columns=["Year", "TAIEX"])
    df = pd.read_csv(p, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y", errors="coerce")
    df = df.dropna(subset=["Date"])
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    yearly = df.groupby("Year", as_index=False)["Value"].mean().rename(columns={"Value": "TAIEX"})
    return yearly.sort_values("Year")


@st.cache_data
def load_ic_exports() -> pd.DataFrame:
    """UN Comtrade — Taiwan IC (HS 8542) exports to world, 1997-2024.

    Returns DataFrame with columns [Year, Chip Exports (USD)].
    Falls back to empty DataFrame if Trade/ directory is missing.
    """
    if not _TRADE_DIR.exists():
        return pd.DataFrame(columns=["Year", "Chip Exports (USD)"])
    frames: List[pd.DataFrame] = []
    for f in sorted(_TRADE_DIR.glob("*.csv")):
        try:
            frames.append(pd.read_csv(f))
        except Exception:
            continue
    if not frames:
        return pd.DataFrame(columns=["Year", "Chip Exports (USD)"])
    df = pd.concat(frames, ignore_index=True)
    df["Year"] = pd.to_numeric(df.get("refPeriodId", pd.Series(dtype=object)), errors="coerce")
    df["Chip Exports (USD)"] = pd.to_numeric(df.get("fobvalue", pd.Series(dtype=object)), errors="coerce")
    df = df.dropna(subset=["Year", "Chip Exports (USD)"])
    df = df[df["Chip Exports (USD)"] > 0]
    df["Year"] = df["Year"].astype(int)
    return (
        df.groupby("Year", as_index=False)["Chip Exports (USD)"]
        .sum()
        .sort_values("Year")
    )


@st.cache_data
def load_tsmc_annual_summary() -> pd.DataFrame:
    """TSMC IR-style summary CSV under Datasets/tsmc/ (wide format; tolerates n/a, ~, ranges)."""
    p = TSMC_DIR / "tsmc_wafer_revenue_summary.csv"
    if not p.exists():
        return pd.DataFrame()
    df = _read_csv_with_encoding_fallback(p)
    df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]
    if "Year" not in df.columns:
        return pd.DataFrame()
    df = df.copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    rename = {k: v for k, v in _TSM_COLUMN_RENAME.items() if k in df.columns}
    df = df.rename(columns=rename)
    for col in _TSM_COERCE_COLS:
        if col in df.columns:
            df[col] = df[col].map(_tsmc_coerce_number)
    return df.sort_values("Year")
