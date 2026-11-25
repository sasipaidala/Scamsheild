"""Create a persistent investigation case with its initial evidence item."""
from __future__ import annotations

import streamlit as st

from core.config import Settings
from services.case_management import CASE_PRIORITIES, EVIDENCE_TYPES, create_case


def get_page_link(name: str):
    from components.navigation import get_page_link as resolve_page_link
    return resolve_page_link(name)


def render() -> None:
    st.markdown('<div class="ss-eyebrow">WORKSPACE / INTAKE</div>', unsafe_allow_html=True)
    st.title("New investigation")
    st.write("Create a case record and preserve its initial evidence for later review.")

    with st.form("ss_intake_form", clear_on_submit=True):
        title = st.text_input("Case title", max_chars=120, placeholder="e.g. Suspected fake recruitment message")
        evidence_type = st.selectbox("Evidence type", EVIDENCE_TYPES, key="ss_intake_kind")
        if evidence_type == "Message":
            evidence_value = st.text_area("Suspicious message", height=180, max_chars=10000, placeholder="Paste the message. Remove passwords, OTPs and unrelated personal details.")
        elif evidence_type == "Email":
            evidence_value = st.text_area("Email content / headers", height=180, max_chars=10000, placeholder="Paste relevant sender, subject, body or sanitized headers.")
        elif evidence_type == "URL":
            evidence_value = st.text_input("Suspicious URL", max_chars=2048, placeholder="https://example.com/path")
        else:
            evidence_value = st.text_input(f"{evidence_type} value", max_chars=2048, placeholder="Enter the indicator value")
        priority = st.selectbox("Priority", CASE_PRIORITIES, index=1)
        description = st.text_area("Case description / context", max_chars=2000, height=100, placeholder="Where was it received? What happened? Avoid secrets.")
        submitted = st.form_submit_button("Create investigation case", type="primary", use_container_width=True)

    if submitted:
        try:
            record = create_case(
                Settings.from_env().database_path, title, evidence_type,
                evidence_value, description, priority,
            )
            st.success(f"Case {record['case_ref']} created and saved locally.")
            st.page_link(get_page_link("cases"), label="Open Investigation Cases", icon=":material/folder_open:")
            st.caption("No external service was contacted. The evidence is stored in your local SQLite database.")
        except (ValueError, TypeError) as exc:
            st.error(str(exc))

    st.markdown('<div class="ss-section-gap-small"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ss-panel"><div class="ss-panel-title">Evidence handling</div>'
        '<div class="ss-panel-copy">Only submit evidence you are authorized to retain. Remove passwords, OTPs, payment-card data and unrelated personal information. '
        'URLs are stored as text; ScamShield does not open them or follow redirects during case intake.</div></div>',
        unsafe_allow_html=True,
    )
