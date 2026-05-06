from __future__ import annotations

import streamlit as st


def story_transition(text: str) -> None:
    st.markdown(
        f'<p class="td-story-transition">{text}</p>',
        unsafe_allow_html=True,
    )


def section_kicker(text: str) -> None:
    st.markdown(
        f'<p class="td-section-kicker">{text}</p>',
        unsafe_allow_html=True,
    )
