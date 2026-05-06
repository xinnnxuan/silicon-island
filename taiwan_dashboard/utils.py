from __future__ import annotations
 
import numpy as np
import pandas as pd
 
 
def fmt_usd(x: float) -> str:
    if x >= 1e12:
        return f"${x / 1e12:,.2f}T"
    if x >= 1e9:
        return f"${x / 1e9:,.2f}B"
    if x >= 1e6:
        return f"${x / 1e6:,.2f}M"
    return f"${x:,.0f}"
 
 
def build_tension_index(years: list[int]) -> pd.DataFrame:
    base = pd.DataFrame({"Year": years})
    base["Tension Index"] = np.interp(base["Year"], [2018, 2020, 2022, 2024], [35, 28, 70, 82])
    base["PHLX SOX (Indexed)"] = np.interp(base["Year"], [2018, 2020, 2021, 2022, 2024], [100, 140, 185, 150, 210])
    base["TSMC (Indexed)"] = np.interp(base["Year"], [2018, 2020, 2022, 2024], [100, 145, 130, 175])
    base["S&P 500 (Indexed)"] = np.interp(base["Year"], [2018, 2020, 2022, 2024], [100, 112, 102, 138])
    return base
