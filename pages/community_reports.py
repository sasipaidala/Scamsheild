"""Community report submission page. Reports remain private pending moderation."""
from __future__ import annotations

import streamlit as st

from core.config import Settings
from services.community_reports import REPORT_CATEGORIES, submit_report


def render() -> None:
    st.markdown('<div class="ss-eyebrow">INTELLIGENCE / COMMUNITY</div>', unsafe_allow_html=True)
    st.title("Community Reports")
    st.write("Submit information about a suspicious phone number, email address, or URL to help build a carefully moderated community intelligence dataset.")
    st.warning(
        "Reports are allegations, not verified findings. New submissions are stored as pending review and are not shown as confirmed scams. "
        "Do not include OTPs, passwords, bank details, government ID numbers, private conversations, or other sensitive personal information."
    )

    with st.form("ss_community_report_form", clear_on_submit=True):
        identifier_type = st.selectbox("What are you reporting?", ["Phone number", "Email address", "URL"])
        identifier = st.text_input("Phone number / Email address / URL", max_chars=2048,
                                   placeholder="Include country code for phone numbers, e.g. +919876543210")
        category = st.selectbox("Report category", REPORT_CATEGORIES)
        description = st.text_area("What happened?", max_chars=2000, height=140,
                                   placeholder="Describe the contact or incident. Avoid sharing passwords, OTPs, or private data.")
        consent = st.checkbox("I confirm this report is submitted in good faith and does not knowingly contain false or private sensitive information.")
        submitted = st.form_submit_button("Submit report for review", type="primary", use_container_width=True)

    if submitted:
        if not consent:
            st.error("Please confirm the good-faith reporting statement before submitting.")
            return
        try:
            receipt = submit_report(Settings.from_env().database_path, identifier_type, identifier, category, description)
        except (TypeError, ValueError) as exc:
            st.error(str(exc))
            return
        st.success(f"Report submitted for review. Reference: SS-{receipt.report_id:06d}")
        st.info("Status: Pending review. This submission does not establish that the reported identifier is fraudulent.")

    with st.expander("How reports are handled"):
        st.markdown(
            "- Submissions are stored in the local ScamShield database.\n"
            "- New reports receive **Pending review** status.\n"
            "- This milestone does not publish report counts or reputation verdicts.\n"
            "- Moderation, duplicate detection, abuse controls, and public search are separate development tasks."
        )
