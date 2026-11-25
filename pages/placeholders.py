"""Honest navigation placeholders for ScamShield AI modules not yet implemented."""

from __future__ import annotations

import streamlit as st


def _render_placeholder(*, section: str, title: str, description: str, milestone: str) -> None:
    st.markdown(
        f'<div class="ss-eyebrow">{section}</div>',
        unsafe_allow_html=True,
    )
    st.title(title)
    st.write(description)
    st.info(
        "This module is a navigation placeholder in the Phase 1 foundation. "
        "It does not process submissions, query external services, save records, "
        "or generate investigation results."
    )
    st.caption(f"Planned implementation: {milestone}")


def message_analyzer() -> None:
    _render_placeholder(
        section="ANALYZERS",
        title="Message Analyzer",
        description=(
            "Review suspicious SMS, emails, and chat messages for social-engineering "
            "indicators. The explainable detection pipeline will be added in the analysis milestone."
        ),
        milestone="Phase 3 · Message detection and evidence explanations",
    )


def url_analyzer() -> None:
    _render_placeholder(
        section="ANALYZERS",
        title="URL Analyzer",
        description=(
            "Inspect URL structure and identify potentially suspicious characteristics. "
            "This foundation page does not open, fetch, or check submitted URLs."
        ),
        milestone="Phase 3 · Passive URL parsing and safe local checks",
    )


def phone_intelligence() -> None:
    _render_placeholder(
        section="ANALYZERS",
        title="Phone Intelligence",
        description=(
            "Review phone-number format and, when authorized sources are configured, "
            "reputation findings. No number lookup or caller identity data is available yet."
        ),
        milestone="Phase 3 · Number validation and approved provider adapters",
    )


def community_reports() -> None:
    _render_placeholder(
        section="INTELLIGENCE",
        title="Community Reports",
        description=(
            "A future space for carefully moderated, privacy-conscious community reports. "
            "No reports can be submitted or viewed in this foundation release."
        ),
        milestone="Phase 4 · Backend, persistence, moderation, and abuse controls",
    )


def threat_intelligence() -> None:
    _render_placeholder(
        section="INTELLIGENCE",
        title="Threat Intelligence",
        description=(
            "View findings from approved threat-intelligence providers when integrations "
            "are configured. No external intelligence provider is currently connected."
        ),
        milestone="Phase 3 and Phase 4 · Authorized provider integrations",
    )


def security_awareness() -> None:
    _render_placeholder(
        section="LEARN & SUPPORT",
        title="Security Awareness",
        description=(
            "Practical guidance about phishing, fake job offers, OTP theft, impersonation, "
            "and other common scam patterns will be organized here."
        ),
        milestone="Phase 2 · Public content and awareness experience",
    )


def reports() -> None:
    _render_placeholder(
        section="MANAGE",
        title="Reports",
        description=(
            "Downloadable investigation reports will appear here after analysis records "
            "and case storage are implemented. No reports are available yet."
        ),
        milestone="Phase 4 · Case persistence and PDF/JSON exports",
    )


def help_center() -> None:
    _render_placeholder(
        section="LEARN & SUPPORT",
        title="Help & Support",
        description=(
            "Find product guidance, safe-use information, and troubleshooting resources. "
            "The help center content is not yet available."
        ),
        milestone="Phase 2 · Help content and support navigation",
    )
