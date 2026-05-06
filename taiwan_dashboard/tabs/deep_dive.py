from __future__ import annotations

import pandas as pd
import streamlit as st

from tabs import exposure, geopolitics, stranglehold, trade, tsmc
from tabs.scenarios import render_fragility_story


def render(
    destinations: pd.DataFrame,
    products: pd.DataFrame,
    semi: pd.DataFrame,
    chip_series: pd.DataFrame,
    trade_balance: pd.DataFrame,
    country_detail: pd.DataFrame,
    tsmc_df: pd.DataFrame,
    taiex: pd.DataFrame,
    us_trade: pd.DataFrame,
) -> None:
    trade.render(destinations, products, trade_balance, country_detail, us_trade)
    st.markdown('<div style="margin:3rem 0;"></div>', unsafe_allow_html=True)
    stranglehold.render(destinations, products, semi, chip_series, country_detail)
    st.markdown('<div style="margin:3rem 0;"></div>', unsafe_allow_html=True)
    if not tsmc_df.empty:
        tsmc.render(tsmc_df)
        st.markdown('<div style="margin:3rem 0;"></div>', unsafe_allow_html=True)
    exposure.render(destinations, products, country_detail)
    st.markdown('<div style="margin:3rem 0;"></div>', unsafe_allow_html=True)
    render_fragility_story(destinations, products, semi)
    st.markdown('<div style="margin:3rem 0;"></div>', unsafe_allow_html=True)
    geopolitics.render(destinations, taiex)
