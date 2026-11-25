"""Truecaller-style phone spam lookup, grounded in available evidence."""
from __future__ import annotations

import streamlit as st

from core.config import Settings
from services.phone_intelligence import lookup_phone


def render() -> None:
    st.markdown('<div class="ss-eyebrow">ANALYZERS / PHONE REPUTATION</div>', unsafe_allow_html=True)
    st.title("Phone Intelligence")
    st.write("Check whether a phone number has been reported to ScamShield and review any connected, authorized reputation intelligence.")
    st.info("A community report is an allegation, not proof. A number with no reports is not automatically safe.")

    with st.form("ss_phone_lookup_form"):
        phone = st.text_input("Phone number", placeholder="+919876543210", max_chars=32)
        submitted = st.form_submit_button("Check number", type="primary", use_container_width=True)

    if not submitted:
        st.caption("Enter the full number with country code. Example: +919876543210")
        return
    try:
        normalized, community, external = lookup_phone(Settings.from_env().database_path, phone)
    except (TypeError, ValueError) as exc:
        st.error(str(exc))
        return

    st.subheader(f"Lookup: {normalized}")
    if community.total_submissions == 0:
        st.success("No ScamShield community reports found")
        st.caption("This only means this local ScamShield database has no matching reports. It is not a safe-number verdict.")
    else:
        st.warning("Community reports found — review their status before drawing a conclusion")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total submissions", community.total_submissions)
        c2.metric("Pending review", community.pending_review)
        c3.metric("Verified reports", community.verified)
        if community.categories:
            st.markdown("**Reported categories**")
            for category, count in community.categories:
                st.write(f"• {category}: {count}")
        if community.latest_report_at:
            st.caption(f"Latest matching report: {community.latest_report_at} (UTC)")
        if community.rejected or community.duplicate:
            st.caption(f"Excluded from active reputation summary: {community.rejected} rejected · {community.duplicate} duplicate")

    st.divider()
    st.subheader("External reputation intelligence")
    if external.connected:
        st.write(f"Provider: {external.provider_name}")
        if external.status == "reported":
            st.warning("OpenTrust community reports found")
        else:
            st.info("No matching reports found in OpenTrust")
        if external.spam_label:
            st.write(f"Provider result: {external.spam_label}")
        if external.report_count is not None:
            st.metric("OpenTrust report count", external.report_count)
        st.caption(external.explanation or "Reports are community observations, not proof of fraud.")
    else:
        st.warning("OpenTrust external lookup unavailable")
        st.caption(external.explanation or "No external lookup was completed.")
        st.caption("Community lookup in ScamShield remains available independently.")

    st.divider()
    st.caption("ScamShield does not identify the subscriber or reveal their live location. Reputation results depend on the coverage and reliability of connected sources.")
