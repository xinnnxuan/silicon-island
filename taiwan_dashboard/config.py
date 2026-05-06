from pathlib import Path
 
# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "Datasets"
DEST_DIR = DATA_DIR / "Destinations"
PROD_DIR = DATA_DIR / "Products"
COUNTRY_DETAIL_DIR = DATA_DIR / "Exports by Country:Region and Detailed Commodity Category"
TSMC_DIR = DATA_DIR / "tsmc"
ICON_DIR = BASE_DIR.parent / "icons"
ASSETS_DIR = BASE_DIR / "assets"
 
# ── Colors ─────────────────────────────────────────────────────────────────
RISK_RED = "#FE0000"
SAFE_GREEN = "#16A34A"
TAIWAN_BLUE = "#000095"
NEUTRAL = "#6B7280"
