"""
Convert Trade Map XLS exports into the format expected by the dashboard.

Usage:
    python convert_trademap.py destinations trademap_destinations.xls
    python convert_trademap.py products    trademap_products_hs2.xls
    python convert_trademap.py products    trademap_products_hs4.xls

Output files are written to:
    Datasets/Destinations/chinese-taipeis-export-destinations-YYYY.csv
    Datasets/Products/chinese-taipeis-exported-products-YYYY.csv

Note: Trade Map XLS files are HTML tables disguised as .xls files.
      This script uses pd.read_html() (requires lxml) to read them.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent
DATA_DIR  = BASE_DIR.parent / "Datasets"
DEST_DIR  = DATA_DIR / "Destinations"
PROD_DIR  = DATA_DIR / "Products"

# ── ISO3 fallback map for common Trade Map country name variants ──────────────
_ISO3_OVERRIDES: dict[str, str] = {
    "China": "CHN",
    "United States of America": "USA",
    "United States": "USA",
    "Hong Kong, China": "HKG",
    "Korea, Republic of": "KOR",
    "South Korea": "KOR",
    "Viet Nam": "VNM",
    "Vietnam": "VNM",
    "Japan": "JPN",
    "Germany": "DEU",
    "Netherlands": "NLD",
    "Singapore": "SGP",
    "United Kingdom": "GBR",
    "Malaysia": "MYS",
    "Thailand": "THA",
    "Philippines": "PHL",
    "India": "IND",
    "Australia": "AUS",
    "France": "FRA",
    "Italy": "ITA",
    "Mexico": "MEX",
    "Canada": "CAN",
    "Indonesia": "IDN",
    "Poland": "POL",
    "Czech Republic": "CZE",
    "Czechia": "CZE",
    "Hungary": "HUN",
    "Belgium": "BEL",
    "Spain": "ESP",
    "Sweden": "SWE",
    "Denmark": "DNK",
    "Finland": "FIN",
    "Norway": "NOR",
    "Austria": "AUT",
    "Switzerland": "CHE",
    "Israel": "ISR",
    "Saudi Arabia": "SAU",
    "United Arab Emirates": "ARE",
    "Brazil": "BRA",
    "Russia": "RUS",
    "Russian Federation": "RUS",
    "Turkey": "TUR",
    "South Africa": "ZAF",
    "World": None,
}


def _get_iso3(name: str) -> str | None:
    if name in _ISO3_OVERRIDES:
        return _ISO3_OVERRIDES[name]
    try:
        import pycountry
        match = pycountry.countries.get(name=name) or pycountry.countries.search_fuzzy(name)[0]
        return match.alpha_3
    except Exception:
        return name[:3].upper()


def _read_trademap_xls(path: Path) -> pd.DataFrame:
    """Read a Trade Map XLS (HTML-disguised) file, returning the data table."""
    try:
        tables = pd.read_html(str(path), encoding="utf-8")
    except Exception as e:
        sys.exit(f"ERROR reading {path.name}: {e}\nMake sure lxml is installed: pip install lxml")

    # The data table is the one with year columns ("Exported value in YYYY")
    for t in sorted(tables, key=lambda x: x.shape[0], reverse=True):
        cols = [str(c) for c in t.columns]
        if any(re.search(r"\b(20\d{2}|19\d{2})\b", c) for c in cols):
            t.columns = [str(c).strip() for c in t.columns]
            return t

    sys.exit(f"ERROR: Could not find a data table with year columns in {path.name}")


def _extract_year_cols(df: pd.DataFrame) -> dict[int, str]:
    """Return {year: column_name} for columns like 'Exported value in 2010'."""
    year_cols = {}
    for col in df.columns:
        m = re.search(r"\b(20\d{2}|19\d{2})\b", col)
        if m:
            year_cols[int(m.group(1))] = col
    return year_cols


def _clean_code(raw: str) -> str:
    """Strip leading apostrophe that Trade Map adds to numeric codes."""
    return raw.lstrip("'").strip()


# HS2 code → Section name mapping
_HS2_SECTION: dict[str, str] = {
    "01-05": "Animal Products",     "06-15": "Vegetable Products",
    "16-24": "Foodstuffs",          "25-27": "Mineral Products",
    "28-38": "Chemical products",   "39-40": "Plastics and articles thereof",
    "41-43": "Raw hides and skins", "44-49": "Wood and articles thereof",
    "50-63": "Textile and articles thereof",
    "64-67": "Footwear and headgear",
    "68-70": "Articles of stone, plaster, cement",
    "71":    "Precious metals",     "72-83": "Base metals and articles thereof",
    "84":    "Machinery",           "85": "Electrical Machinery and Equipment",
    "86-89": "Vehicles other than railway",
    "90-92": "Optical, photo, medical apparatus",
    "93":    "Arms and ammunition", "94-96": "Miscellaneous manufactured articles",
    "97-99": "Works of art",
}


def _hs_to_section(code: str) -> str:
    """Map any HS code (2 or 4 digit) to its section name."""
    digits = re.sub(r"\D", "", code)
    if not digits:
        return "Other"
    num = int(digits[:2])
    for rng, name in _HS2_SECTION.items():
        parts = rng.split("-")
        lo = int(parts[0])
        hi = int(parts[-1])
        if lo <= num <= hi:
            return name
    return "Other"


def convert_destinations(src: Path) -> None:
    print(f"Reading destinations: {src.name}")
    df = _read_trademap_xls(src)

    # Find the importers/country column (first non-year column)
    year_cols = _extract_year_cols(df)
    country_col = df.columns[0]

    if not year_cols:
        sys.exit("ERROR: No year columns found.")

    print(f"  Found years: {sorted(year_cols)}")
    print(f"  Country column: '{country_col}'  ({len(df)} rows)")

    for year, col in sorted(year_cols.items()):
        rows = []
        total_exports = 0.0

        for _, row in df.iterrows():
            country = str(row[country_col]).strip()
            if not country or country.lower() in ("world", "nan", "total"):
                continue
            val_raw = row[col]
            val = pd.to_numeric(str(val_raw).replace(",", "").replace(" ", ""), errors="coerce")
            if pd.isna(val):
                continue
            val_usd = float(val) * 1000  # Trade Map values are in thousands USD
            total_exports += val_usd
            iso3 = _get_iso3(country) or country[:3].upper()
            rows.append({"Country": country, "Country ID": iso3,
                         "Year": year, "Exports (USD)": val_usd})

        if not rows:
            print(f"  Skipping {year} — no data rows.")
            continue

        out = pd.DataFrame(rows)
        out["Share (%)"] = (out["Exports (USD)"] / total_exports * 100).round(3)
        out_path = DEST_DIR / f"chinese-taipeis-export-destinations-{year}.csv"
        if out_path.exists():
            print(f"  SKIP {year} — already exists: {out_path.name}")
            continue
        out.to_csv(out_path, index=False)
        print(f"  Wrote {len(out)} rows → {out_path.name}")


def convert_products(src: Path) -> None:
    print(f"Reading products: {src.name}")
    df = _read_trademap_xls(src)
    year_cols = _extract_year_cols(df)

    if not year_cols:
        sys.exit("ERROR: No year columns found.")

    # Detect code and label columns
    code_col  = next((c for c in df.columns if "code" in c.lower()), df.columns[0])
    label_col = next((c for c in df.columns if "label" in c.lower() or "product" in c.lower()), df.columns[1])

    print(f"  Found years: {sorted(year_cols)}")
    print(f"  Code column: '{code_col}'  Label column: '{label_col}'  ({len(df)} rows)")

    for year, col in sorted(year_cols.items()):
        rows = []
        for _, row in df.iterrows():
            raw_code = str(row[code_col]).strip()
            code = _clean_code(raw_code)
            label = str(row[label_col]).strip()
            # Skip totals / blank
            if not code or code.upper() in ("NAN", "TOTAL") or "TOTAL" in code.upper():
                continue
            val_raw = row[col]
            val = pd.to_numeric(str(val_raw).replace(",", "").replace(" ", ""), errors="coerce")
            if pd.isna(val):
                continue
            val_usd = float(val) * 1000
            section = _hs_to_section(code)
            rows.append({
                "Section ID": 0, "Section": section,
                "HS4 ID": code, "HS4": label,
                "Year": year, "Exports (USD)": val_usd,
            })

        if not rows:
            print(f"  Skipping {year} — no data rows.")
            continue

        out = pd.DataFrame(rows)
        total = out["Exports (USD)"].sum()
        out["Share (%)"] = (out["Exports (USD)"] / total * 100).round(3)
        out_path = PROD_DIR / f"chinese-taipeis-exported-products-{year}.csv"
        if out_path.exists():
            print(f"  SKIP {year} — already exists: {out_path.name}")
            continue
        out.to_csv(out_path, index=False)
        print(f"  Wrote {len(out)} rows → {out_path.name}")


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1].lower()
    src  = Path(sys.argv[2])

    if not src.exists():
        sys.exit(f"ERROR: File not found: {src}")

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    PROD_DIR.mkdir(parents=True, exist_ok=True)

    if mode == "destinations":
        convert_destinations(src)
    elif mode == "products":
        convert_products(src)
    else:
        sys.exit(f"ERROR: Unknown mode '{mode}'. Use 'destinations' or 'products'.")

    print("\nDone. Restart the Streamlit app to load the new files.")


if __name__ == "__main__":
    main()
