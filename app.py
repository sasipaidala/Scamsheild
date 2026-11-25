"""ScamShield AI application entry point — functional interface milestone."""

from __future__ import annotations

import logging

import streamlit as st

from components.navigation import build_navigation, initialize_theme_state
from core.config import Settings
from core.theme import theme_css
from database.connection import initialize_database


def configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    settings = Settings.from_env()
    configure_logging(settings)

    st.set_page_config(
        page_title=settings.app_name,
        page_icon="🛡",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    initialize_database(settings.database_path)
    selected_theme = initialize_theme_state()
    st.markdown(theme_css(selected_theme), unsafe_allow_html=True)
    density = st.session_state.get("ss_density", "Comfortable")
    reduce_motion = st.session_state.get("ss_reduce_motion", False)
    preference_css = "<style>"
    if density == "Compact":
        preference_css += """
        [data-testid="stMainBlockContainer"] { padding-top: 1rem; padding-bottom: 1.5rem; }
        [data-testid="stVerticalBlock"] { gap: .65rem; }
        .ss-panel { padding: 1rem; }
        """
    if reduce_motion:
        preference_css += """
        *, *::before, *::after {
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: .01ms !important;
            scroll-behavior: auto !important;
        }
        """
    preference_css += "</style>"
    st.markdown(preference_css, unsafe_allow_html=True)

    page = build_navigation()
    page.run()


if __name__ == "__main__":
    main()
