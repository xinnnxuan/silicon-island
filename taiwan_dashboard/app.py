from __future__ import annotations

import streamlit as st

from data_loader import load_data, load_ic_exports, load_taiex, load_taiwan_gdp, load_tsmc_annual_summary, load_us_taiwan_trade, semicon_proxy
from styles import inject_sidebar_styles
from tabs import deep_dive, explore, overview

st.set_page_config(
    page_title="Silicon Island",
    layout="wide",
    initial_sidebar_state="collapsed",
)

_NAV = {
    "story":      "The Story",
    "deep_dive":  "Deep Dive",
    "explore":    "Explore Data",
}


def main() -> None:
    inject_sidebar_styles()

    destinations, products, chip_series_proxy, trade_balance, country_detail = load_data()
    semi = semicon_proxy(products)
    ic_exports = load_ic_exports()
    chip_series = ic_exports if not ic_exports.empty else chip_series_proxy
    tsmc_df = load_tsmc_annual_summary()
    taiex = load_taiex()
    gdp_df = load_taiwan_gdp()
    us_trade = load_us_taiwan_trade()

    section = st.radio(
        "Go to section",
        list(_NAV.keys()),
        format_func=lambda x: _NAV[x],
        horizontal=True,
        key="top_nav_section",
        label_visibility="collapsed",
    )

    match section:
        case "story":
            overview.render(destinations, products, semi, chip_series, country_detail, tsmc_df, gdp_df)
        case "deep_dive":
            deep_dive.render(
                destinations, products, semi, chip_series,
                trade_balance, country_detail, tsmc_df, taiex, us_trade,
            )
        case "explore":
            explore.render(destinations, products, trade_balance, country_detail)


if __name__ == "__main__":
    main()
