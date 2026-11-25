"""Streamlit interface for the local message-indicator analyzer."""

from __future__ import annotations

import streamlit as st

from services.message_service import MAX_MESSAGE_LENGTH, analyze_message
from services.email_service import analyze_email, MAX_EMAIL_FIELD_LENGTH, MAX_HEADERS_LENGTH


def _render_result(result) -> None:
    st.markdown('<div class="ss-section-gap-small"></div>', unsafe_allow_html=True)
    st.subheader("Analysis assessment")

    if result.risk_level == "Critical":
        st.error(f"{result.assessment} · Review this message carefully")
    elif result.risk_level == "High":
        st.error(f"{result.assessment} · Several concerning indicators were found")
    elif result.risk_level == "Moderate":
        st.warning(f"{result.assessment} · Verify the context independently")
    elif result.risk_level == "Low":
        st.info(f"{result.assessment} · Limited indicators were found")
    elif result.risk_level == "Insufficient evidence":
        st.info("Insufficient evidence · Provide more context for a meaningful review")
    else:
        st.info("No significant indicators detected · This is not proof of safety")

    score_col, category_col, breadth_col = st.columns(3)
    with score_col:
        score_text = "Not scored" if result.indicator_score is None else f"{result.indicator_score}/100"
        st.metric("Heuristic indicator score", score_text)
    with category_col:
        st.metric("Primary pattern", result.primary_category)
    with breadth_col:
        st.metric("Matched indicators", len(result.findings))
    st.caption("The score is a transparent rule-weight total, not a statistical probability or a verdict.")

    st.markdown(f"**Evidence breadth:** {result.indicator_breadth}")
    if result.findings:
        st.markdown("#### Supporting indicators")
        for index, finding in enumerate(result.findings, start=1):
            with st.expander(f"{index}. {finding.title} · {finding.severity}", expanded=index == 1):
                st.write(finding.explanation)
                st.caption("Matched excerpt from the submitted message")
                st.code(finding.excerpt, language=None)
                st.caption(f"Rule: `{finding.rule_id}` · Weight: {finding.weight} points")
    else:
        st.markdown(
            '<div class="ss-panel"><div class="ss-panel-title">No configured indicator matched</div>'
            '<div class="ss-panel-copy">This message may still be deceptive. The detector can only identify patterns it has explicit rules for.</div></div>',
            unsafe_allow_html=True,
        )

    if result.observations:
        st.markdown("#### Additional observations")
        for observation in result.observations:
            if observation == "url_present":
                st.write("A URL-like string is present. Its destination and reputation were not checked.")
            elif observation == "phone_number_like_text_present":
                st.write("A phone-number-like string is present. Ownership and reputation were not checked.")

    st.markdown("#### Recommended precautions")
    for recommendation in result.recommendations:
        st.markdown(f"- {recommendation}")

    with st.expander("Analysis method and limitations"):
        st.write(f"**Method:** local heuristic rules (`{result.ruleset_version}`)")
        st.write(f"**Selected message language:** {result.language_selected}")
        st.write(f"**Analyzed at:** {result.analyzed_at}")
        for limitation in result.limitations:
            st.markdown(f"- {limitation}")


def _render_message_mode() -> None:
    st.markdown('<div class="ss-eyebrow">ANALYZERS / MESSAGE</div>', unsafe_allow_html=True)
    st.title("Message Analyzer")
    st.write(
        "Review SMS, emails and chat messages for combinations of social-engineering "
        "indicators. Analysis runs locally with explainable rules."
    )
    st.warning(
        "This is an initial heuristic detector, not a definitive scam classifier. "
        "It does not contact external services and does not save the submitted message."
    )

    if "ss_message_prefill" in st.session_state:
        st.session_state["ss_message_text"] = st.session_state.pop("ss_message_prefill")
        st.session_state.pop("ss_message_analysis_result", None)

    with st.form("ss_message_analysis_form", clear_on_submit=False):
        message = st.text_area(
            "Suspicious message",
            key="ss_message_text",
            height=220,
            max_chars=MAX_MESSAGE_LENGTH,
            placeholder="Paste the complete SMS, email or chat message here...",
        )
        st.caption(f"Maximum {MAX_MESSAGE_LENGTH:,} characters. Current length: {len(message)}")
        language = st.selectbox(
            "Message language",
            ["English", "Telugu", "Hindi", "Not sure"],
            key="ss_message_language",
        )
        submitted = st.form_submit_button("Analyze message", type="primary", use_container_width=True)

    if submitted:
        try:
            result = analyze_message(message, language)
            st.session_state["ss_message_analysis_result"] = result
        except (TypeError, ValueError) as exc:
            st.error(str(exc))

    result = st.session_state.get("ss_message_analysis_result")
    if result is not None:
        _render_result(result)

    with st.expander("Try a synthetic test example"):
        st.caption("These examples are fictional test inputs, not real scam reports.")
        examples = {
            "Fake job fee request": (
                "Congratulations, you have been selected for a work from home job. "
                "Pay the registration fee of Rs 999 today to secure your offer."
            ),
            "OTP request": (
                "Your bank account will be blocked today. Please send your OTP immediately "
                "to verify your account."
            ),
            "Preventive safety message": (
                "Never share your OTP or password with anyone. Your bank will never ask "
                "you to send an OTP in a message."
            ),
        }
        example_choice = st.selectbox("Select a test message", ["Choose an example", *examples.keys()])
        if example_choice != "Choose an example":
            st.code(examples[example_choice], language=None)
            st.caption("Copy the example into the message field above and run the analyzer.")


def _render_email_result(result) -> None:
    st.subheader("Email analysis assessment")
    if result.risk_level == "High attention":
        st.error("High attention · Review the sender, routing and content carefully")
    elif result.risk_level == "Needs review":
        st.warning("Needs review · Indicators require independent verification")
    else:
        st.info("No configured indicators detected · This is not proof of safety")

    first, second, third = st.columns(3)
    first.metric("Email assessment", result.risk_level)
    second.metric("Extracted URLs", len(result.urls))
    third.metric("Email-specific indicators", len(result.findings))

    st.markdown("#### Sender and routing")
    st.write(f"**From:** {result.sender or 'Not provided'}")
    st.write(f"**Reply-To:** {result.reply_to or 'Not provided'}")
    if result.sender_reply_to_mismatch:
        st.warning("The From and Reply-To domains differ. This is a warning signal, not proof of spoofing.")

    if result.findings:
        st.markdown("#### Email indicators")
        for item in result.findings:
            with st.expander(f"{item.title} · {item.severity}", expanded=True):
                st.write(item.explanation)

    if result.urls:
        st.markdown("#### Extracted links — not opened")
        for url in result.urls:
            st.code(url, language=None)

    st.markdown("#### Message-content analysis")
    _render_result(result.message_analysis)

    st.markdown("#### Email authentication headers")
    if not result.authentication_available:
        st.info("Unavailable · No raw Authentication-Results header was supplied.")
    elif result.authentication:
        for mechanism, status in result.authentication.items():
            st.write(f"**{mechanism}:** {status} *(reported by supplied header; not independently verified)*")
    else:
        st.warning("A header was supplied, but no recognizable SPF/DKIM/DMARC status was extracted.")

    st.markdown("#### Recommended precautions")
    for item in result.recommendations:
        st.markdown(f"- {item}")
    with st.expander("Analysis method and limitations"):
        for item in result.limitations:
            st.markdown(f"- {item}")

def _render_email_mode() -> None:
    st.markdown('<div class="ss-eyebrow">ANALYZERS / EMAIL</div>', unsafe_allow_html=True)
    st.subheader("Email Spam Analysis")
    st.write("Inspect sender details, reply routing, message content, embedded links and optional authentication headers.")
    st.warning("Local heuristics only. ScamShield does not contact the sender, open links, inspect attachments, query DNS, or independently validate email authentication.")

    with st.form("ss_email_analysis_form", clear_on_submit=False):
        sender = st.text_input("Sender email address (From)", max_chars=MAX_EMAIL_FIELD_LENGTH, key="ss_email_sender")
        display_name = st.text_input("Sender display name (optional)", max_chars=MAX_EMAIL_FIELD_LENGTH, key="ss_email_display_name")
        reply_to = st.text_input("Reply-To address (optional)", max_chars=MAX_EMAIL_FIELD_LENGTH, key="ss_email_reply_to")
        subject = st.text_input("Email subject", max_chars=MAX_EMAIL_FIELD_LENGTH, key="ss_email_subject")
        body = st.text_area("Email body", height=220, max_chars=MAX_EMAIL_FIELD_LENGTH, key="ss_email_body")
        with st.expander("Advanced: raw email headers (optional)"):
            headers = st.text_area("Paste headers only", height=160, max_chars=MAX_HEADERS_LENGTH, key="ss_email_headers", help="Include Authentication-Results if available. Do not paste passwords, session cookies, or private tokens.")
        submitted = st.form_submit_button("Analyze email", type="primary", use_container_width=True)

    if submitted:
        try:
            result = analyze_email(sender, subject, body, reply_to, display_name, headers)
            st.session_state["ss_email_analysis_result"] = result
        except (TypeError, ValueError) as exc:
            st.error(str(exc))
    result = st.session_state.get("ss_email_analysis_result")
    if result is not None:
        _render_email_result(result)

def render() -> None:
    st.markdown('<div class="ss-eyebrow">ANALYZERS / MESSAGE & EMAIL</div>', unsafe_allow_html=True)
    st.title("Message Analyzer")
    mode = st.radio("Analysis type", ["SMS / Message Analysis", "Email Spam Analysis"], horizontal=True, key="ss_message_analysis_mode")
    if mode == "Email Spam Analysis":
        _render_email_mode()
    else:
        _render_message_mode()
