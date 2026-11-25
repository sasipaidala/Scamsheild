"""Centralized Streamlit page registry and branded sidebar navigation."""

from __future__ import annotations

import streamlit as st

from components.brand import render_brand
from core.theme import normalize_theme
from pages import cases, landing, message_analyzer, new_investigation, overview, settings
from pages import community_reports, url_analyzer, reports as reports_page_module, threat_intelligence as threat_intelligence_page, security_awareness as security_awareness_page, help_center as help_center_page


_PAGE_LINKS: dict[str, object] = {}


def get_page_link(name: str):
    """Return a registered Streamlit page for use by in-page navigation links."""
    if name not in _PAGE_LINKS:
        raise KeyError(f"Unknown ScamShield page link: {name}")
    return _PAGE_LINKS[name]


def _sync_theme_to_url() -> None:
    """Keep the selected theme in the URL so a refresh preserves this choice."""
    st.query_params["theme"] = st.session_state["ss_theme"]


def initialize_theme_state() -> str:
    """Initialize theme state from URL once per Streamlit browser session."""
    if "ss_theme" not in st.session_state:
        st.session_state["ss_theme"] = normalize_theme(st.query_params.get("theme"))
    return normalize_theme(st.session_state["ss_theme"])


def build_navigation():
    """Register all product destinations and render the custom sidebar."""
    home_page = st.Page(
        landing.render,
        title="Home",
        icon=":material/home:",
        url_path="",
        default=True,
    )
    overview_page = st.Page(
        overview.render,
        title="Overview",
        icon=":material/dashboard:",
        url_path="overview",
    )
    investigation_page = st.Page(
        new_investigation.render,
        title="New Investigation",
        icon=":material/travel_explore:",
        url_path="new-investigation",
    )
    message_page = st.Page(
        message_analyzer.render,
        title="Message Analyzer",
        icon=":material/mark_email_unread:",
        url_path="message-analyzer",
    )
    url_page = st.Page(
        url_analyzer.render,
        title="URL Analyzer",
        icon=":material/link:",
        url_path="url-analyzer",
    )
    cases_page = st.Page(
        cases.render,
        title="Investigation Cases",
        icon=":material/folder_open:",
        url_path="cases",
    )
    community_page = st.Page(
        community_reports.render,
        title="Community Reports",
        icon=":material/groups:",
        url_path="community-reports",
    )
    threat_page = st.Page(
        threat_intelligence_page.render,
        title="Threat Intelligence",
        icon=":material/manage_search:",
        url_path="threat-intelligence",
    )
    awareness_page = st.Page(
        security_awareness_page.render,
        title="Security Awareness",
        icon=":material/school:",
        url_path="security-awareness",
    )
    reports_page = st.Page(
        reports_page_module.render,
        title="Reports",
        icon=":material/description:",
        url_path="reports",
    )
    settings_page = st.Page(
        settings.render,
        title="Settings",
        icon=":material/settings:",
        url_path="settings",
    )
    help_page = st.Page(
        help_center_page.render,
        title="Help",
        icon=":material/help_outline:",
        url_path="help",
    )

    _PAGE_LINKS.clear()
    _PAGE_LINKS.update({
        "home": home_page,
        "overview": overview_page,
        "new_investigation": investigation_page,
        "message_analyzer": message_page,
        "url_analyzer": url_page,
        "cases": cases_page,
        "community_reports": community_page,
        "threat_intelligence": threat_page,
        "security_awareness": awareness_page,
        "reports": reports_page,
        "settings": settings_page,
        "help": help_page,
    })

    all_pages = [
        home_page,
        overview_page,
        investigation_page,
        message_page,
        url_page,
        cases_page,
        community_page,
        threat_page,
        awareness_page,
        reports_page,
        settings_page,
        help_page,
    ]
    current_page = st.navigation(all_pages, position="hidden")

    with st.sidebar:
        render_brand(compact=False)
        st.markdown(
            '<div class="ss-status"><span class="ss-status-dot"></span>'
            'Local workspace · message analysis enabled</div>',
            unsafe_allow_html=True,
        )
        st.divider()

        st.caption("PUBLIC")
        st.page_link(home_page, label="Home", icon=":material/home:")

        st.caption("WORKSPACE")
        st.page_link(overview_page, label="Overview", icon=":material/dashboard:")
        st.page_link(
            investigation_page,
            label="New Investigation",
            icon=":material/travel_explore:",
        )

        st.caption("ANALYZERS")
        st.page_link(message_page, label="Message Analyzer", icon=":material/mark_email_unread:")
        st.page_link(url_page, label="URL Analyzer", icon=":material/link:")

        st.caption("INTELLIGENCE")
        st.page_link(threat_page, label="Threat Intelligence", icon=":material/manage_search:")
        st.page_link(community_page, label="Community Reports", icon=":material/groups:")

        st.caption("MANAGE")
        st.page_link(cases_page, label="Investigation Cases", icon=":material/folder_open:")
        st.page_link(reports_page, label="Reports", icon=":material/description:")

        st.caption("LEARN & SUPPORT")
        st.page_link(
            awareness_page,
            label="Security Awareness",
            icon=":material/school:",
        )
        st.page_link(help_page, label="Help", icon=":material/help_outline:")

        st.divider()
        st.caption("PREFERENCES")
        st.page_link(settings_page, label="Settings", icon=":material/settings:")
        st.selectbox(
            "Theme",
            options=["dark", "light"],
            format_func=lambda value: "Dark mode" if value == "dark" else "Light mode",
            key="ss_theme",
            on_change=_sync_theme_to_url,
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("SCAMSHIELD AI · v0.3.0")
        st.caption("External intelligence: not connected")
        st.caption("Unfinished modules are marked as planned.")

    return current_page
