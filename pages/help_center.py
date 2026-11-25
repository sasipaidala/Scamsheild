"""Product help, troubleshooting and locally recorded support requests."""
from __future__ import annotations

import streamlit as st

from core.config import Settings
from services.learning_support import CATEGORIES, PRIORITIES, create_support_ticket, list_support_tickets

FAQS = [
    ("Does a low risk score prove a message is safe?", "No. ScamShield uses indicators and available evidence. A low score or no match is not proof of legitimacy."),
    ("Does Threat Intelligence perform live internet lookups?", "The current IOC workspace uses indicators imported from files. A result only reflects the imported sources and their coverage; it is not a global clean bill of health."),
    ("Does URL Analyzer open submitted links?", "No. The local URL analyzer inspects URL structure. Do not open suspicious links just to test them."),
    ("Are support requests sent to a support team?", "Not currently. Requests are saved in this local SQLite workspace. There is no email delivery, hosted ticket queue or staff notification integration."),
    ("Where is my data stored?", "By default, records are stored in the SQLite database configured by SCAMSHIELD_DATABASE_PATH. Back up the database securely and restrict access to the machine and folder."),
    ("Can I upload passwords, OTPs or full bank details as evidence?", "No. Remove passwords, OTPs, full card/account numbers, access tokens and unrelated personal data before recording evidence."),
]


def render() -> None:
    db = Settings.from_env().database_path
    st.markdown('<div class="ss-eyebrow">DOCUMENTATION · SUPPORT</div>', unsafe_allow_html=True)
    st.title("Help & Support")
    st.write("Find guidance for using ScamShield, troubleshoot common issues, or record a support request.")

    search = st.text_input("Search help articles", placeholder="e.g. URL analysis, database, risk score")
    matches = [(q, a) for q, a in FAQS if not search or search.lower() in (q + " " + a).lower()]
    st.subheader("Frequently asked questions")
    if matches:
        for question, answer in matches:
            with st.expander(question):
                st.write(answer)
    else:
        st.info("No matching help article. Try a shorter search term or submit a support request.")

    with st.expander("Troubleshooting"):
        st.markdown("""
        - **Application will not start:** activate the project virtual environment and run `pip install -r requirements.txt`.
        - **Missing Python module:** install the declared project dependencies, then rerun the application.
        - **Database locked:** close duplicate ScamShield processes and check that the database folder is writable.
        - **Imported CSV rejected:** check the template/required columns, encoding and indicator type values; remove malformed rows.
        - **Data missing after restart:** confirm that `SCAMSHIELD_DATABASE_PATH` points to the same database file each time.
        """)

    st.divider()
    st.subheader("Submit a support request")
    st.warning("This is a local ticket register only. It does not send email, notify a support team or provide a response SLA. Do not include passwords, OTPs, API keys or full financial identifiers.")
    with st.form("support_request_form", clear_on_submit=True):
        category = st.selectbox("Category", CATEGORIES)
        subject = st.text_input("Subject", max_chars=120)
        description = st.text_area("Describe the issue", max_chars=4000, height=140)
        email = st.text_input("Contact email (optional)", max_chars=254)
        priority = st.selectbox("Priority", PRIORITIES, index=1)
        submitted = st.form_submit_button("Save support request", type="primary")
    if submitted:
        try:
            ticket = create_support_ticket(db, category, subject, description, email, priority)
            st.success(f"Request saved locally. Reference: {ticket['ticket_ref']}")
        except ValueError as exc:
            st.error(str(exc))

    st.divider()
    st.subheader("Recent local requests")
    tickets = list_support_tickets(db, limit=20)
    if not tickets:
        st.caption("No support requests have been recorded in this workspace.")
    else:
        st.dataframe(list(tickets), use_container_width=True, hide_index=True)
