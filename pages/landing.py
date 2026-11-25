"""Public ScamShield AI landing page for the functional-interface milestone."""

from __future__ import annotations

import streamlit as st

from components.cinematic_experience import render_cinematic_experience
from components.brand import render_brand
from core.ui_validation import validate_launcher_input


def get_page_link(name: str):
    """Resolve page references at render time to avoid navigation import cycles."""
    from components.navigation import get_page_link as resolve_page_link

    return resolve_page_link(name)


def _render_navbar() -> None:
    left, middle, right = st.columns([1.6, 4.2, 1.4], vertical_alignment="center")
    with left:
        render_brand(compact=True)
    with middle:
        st.markdown(
            '<nav class="ss-public-nav" aria-label="Main navigation">'
            '<a href="#features">Features</a>'
            '<a href="#how-it-works">How it works</a>'
            '<a href="#trust">Trust &amp; safety</a>'
            '<a href="#about">About</a>'
            '</nav>',
            unsafe_allow_html=True,
        )
    with right:
        st.page_link(
            get_page_link("overview"),
            label="Open workspace",
            icon=":material/arrow_forward:",
            use_container_width=True,
        )
    st.markdown('<div class="ss-public-nav-divider"></div>', unsafe_allow_html=True)


def _render_hero() -> None:
    left, right = st.columns([1.15, 0.85], gap="large", vertical_alignment="center")
    with left:
        st.markdown(
            '<div class="ss-eyebrow">DIGITAL SAFETY, WITH EVIDENCE</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="ss-hero-title">Your first line of defense against digital scams.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="ss-hero-copy">Bring suspicious messages, links and phone numbers into one evidence-led workspace. '
            'Local message analysis is available now; URL and phone analysis are being built next.</div>',
            unsafe_allow_html=True,
        )
        cta_one, cta_two = st.columns([1.2, 1], gap="small")
        with cta_one:
            st.page_link(
                get_page_link("new_investigation"),
                label="Start investigation",
                icon=":material/search:",
                use_container_width=True,
            )
        with cta_two:
            st.markdown('<a class="ss-secondary-cta" href="#features">Explore features</a>', unsafe_allow_html=True)
        st.markdown(
            '<div class="ss-hero-footnote"><span class="ss-status-dot"></span>'
            ' Local-first foundation · External intelligence not connected</div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="ss-preview-shell">
              <div class="ss-preview-topbar">
                <span class="ss-preview-dots"><i></i><i></i><i></i></span>
                <span class="ss-preview-label">SCAMSHIELD WORKSPACE</span>
                <span class="ss-preview-live">ILLUSTRATIVE</span>
              </div>
              <div class="ss-preview-body">
                <div class="ss-preview-kicker">INVESTIGATION PREVIEW</div>
                <div class="ss-preview-heading">Evidence before assumptions.</div>
                <div class="ss-preview-input">
                  <span class="ss-preview-input-icon">⌕</span>
                  <span>Review a suspicious message, link or number</span>
                </div>
                <div class="ss-preview-grid">
                  <div class="ss-preview-chip"><b>01</b><span>Message indicators</span><em>Local rules active</em></div>
                  <div class="ss-preview-chip"><b>02</b><span>URL structure</span><em>Planned</em></div>
                  <div class="ss-preview-chip"><b>03</b><span>Phone intelligence</span><em>Planned</em></div>
                </div>
                <div class="ss-preview-assessment">
                  <div><span class="ss-preview-assessment-label">ASSESSMENT</span><strong>Awaiting evidence</strong></div>
                  <span class="ss-preview-neutral">NOT ANALYZED</span>
                </div>
              </div>
              <div class="ss-preview-foot">Concept preview · No live scan or threat lookup has run</div>
            </div>
            """,
            unsafe_allow_html=True,
        )



def _render_hero_actions() -> None:
    """Keep the cinematic calls to action native to Streamlit for reliable navigation."""
    st.markdown(
        '<div class="ss-cinematic-actions-heading">SCAMSHIELD AI <span>·</span> DETECT THE SIGNAL. STOP THE SCAM.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <style>
    .ss-cinematic-actions-heading{margin:.45rem 0 1rem;text-align:center;color:#39ff14;font:800 .67rem/1.5 ui-monospace,monospace;letter-spacing:.18em}
    div[data-testid="stHorizontalBlock"] .ss-cinematic-action-primary button{background:linear-gradient(110deg,#39ff14,#83ffad)!important;color:#041007!important;border:1px solid #39ff14!important;font-weight:800!important;min-height:3rem;box-shadow:0 0 24px #39ff1425}
    div[data-testid="stHorizontalBlock"] .ss-cinematic-action-secondary button{background:#0a1710!important;color:#b7ffd1!important;border:1px solid #28613a!important;font-weight:700!important;min-height:3rem}
    @media(max-width:640px){.ss-cinematic-actions-heading{letter-spacing:.08em;font-size:.6rem}}
    </style>
    """, unsafe_allow_html=True)
    left, right = st.columns([1, 1], gap="medium")
    with left:
        st.markdown('<div class="ss-cinematic-action-primary">', unsafe_allow_html=True)
        st.page_link(get_page_link("new_investigation"), label="Start the Investigation", icon=":material/travel_explore:", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="ss-cinematic-action-secondary">', unsafe_allow_html=True)
        st.page_link(get_page_link("overview"), label="Open Security Workspace", icon=":material/dashboard:", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def _render_launcher() -> None:
    st.markdown('<div class="ss-section-kicker">QUICK START</div>', unsafe_allow_html=True)
    st.subheader("What would you like to investigate?")
    st.caption("Message analysis is available using local heuristic rules. URL and phone checks are still in development.")

    input_kind = st.radio(
        "Choose an investigation type",
        options=["Message", "URL", "Phone number"],
        horizontal=True,
        key="ss_landing_input_kind",
        label_visibility="collapsed",
    )

    with st.form("ss_landing_launcher", clear_on_submit=False):
        value = ""
        if input_kind == "Message":
            value = st.text_area(
                "Suspicious message",
                placeholder="Paste the SMS, email or chat message here...",
                height=120,
                max_chars=5000,
            )
            st.selectbox("Message language", ["English", "Telugu", "Hindi", "Not sure"], key="ss_landing_message_language")
        elif input_kind == "URL":
            value = st.text_input(
                "Suspicious URL",
                placeholder="https://example.com/path",
                max_chars=2048,
            )
            st.caption("The website will not be opened or fetched by this form.")
        else:
            phone_col, country_col = st.columns([1.7, 1])
            with phone_col:
                value = st.text_input(
                    "Phone number",
                    placeholder="+91 98765 43210",
                    max_chars=32,
                )
            with country_col:
                st.selectbox("Country", ["India (+91)", "United States (+1)", "United Kingdom (+44)", "Other"], key="ss_landing_phone_country")
        submitted = st.form_submit_button("Continue", type="primary", use_container_width=True)

    if submitted:
        error = validate_launcher_input(input_kind, value)
        if error:
            st.error(error)
        elif input_kind == "Message":
            st.session_state["ss_message_prefill"] = value.strip()
            st.success("Your message passed basic input checks. Continue to the local message analyzer.")
            st.page_link(
                get_page_link("message_analyzer"),
                label="Analyze this message",
                icon=":material/arrow_forward:",
            )
            st.caption("The message is not sent to an external provider or saved to the database.")
        else:
            st.warning(
                "The input passed basic length checks only. URL analysis and phone-number "
                "validation are not available yet. Nothing was saved or sent to an external provider."
            )
            st.page_link(
                get_page_link("new_investigation"),
                label="Open the investigation workspace",
                icon=":material/arrow_forward:",
            )


def _render_features() -> None:
    st.markdown('<div id="features"></div>', unsafe_allow_html=True)
    st.markdown('<div class="ss-section-kicker">CAPABILITIES</div>', unsafe_allow_html=True)
    st.header("One workspace. Multiple evidence types.")
    st.write("The product is designed to bring common digital-safety checks into one transparent workflow.")
    features = [
        ("01", "Message analysis", "Identify combinations of social-engineering indicators in suspicious messages.", "Local heuristic rules active"),
        ("02", "URL investigation", "Inspect URL structure and, later, consult approved reputation sources.", "In development"),
        ("03", "Phone intelligence", "Normalize phone numbers and present only authorized, attributable findings.", "Planned"),
        ("04", "Evidence correlation", "Review possible relationships between cases with supporting evidence.", "Planned"),
        ("05", "Explainable assessment", "Show what contributed to an assessment and what could not be verified.", "Planned"),
        ("06", "Investigation reports", "Organize findings and export a clear record when case storage is available.", "Planned"),
    ]
    for row_start in range(0, len(features), 3):
        cols = st.columns(3, gap="medium")
        for col, item in zip(cols, features[row_start : row_start + 3]):
            number, title, description, status = item
            with col:
                st.markdown(
                    f'<div class="ss-feature-card"><div class="ss-feature-number">{number}</div>'
                    f'<div class="ss-feature-title">{title}</div>'
                    f'<div class="ss-feature-copy">{description}</div>'
                    f'<div class="ss-feature-status">{status}</div></div>',
                    unsafe_allow_html=True,
                )


def _render_workflow() -> None:
    st.markdown('<div id="how-it-works"></div>', unsafe_allow_html=True)
    st.markdown('<div class="ss-section-kicker">WORKFLOW</div>', unsafe_allow_html=True)
    st.header("A clear process, from input to evidence.")
    steps = [
        ("01", "Submit", "Choose a message, URL or phone number."),
        ("02", "Validate", "Check that the submitted input is in an acceptable format."),
        ("03", "Analyze", "Run appropriate local detection logic."),
        ("04", "Verify", "Consult permitted sources when configured."),
        ("05", "Correlate", "Review related evidence without overstating a match."),
        ("06", "Understand", "Read the findings, uncertainty and safe next steps."),
    ]
    columns = st.columns(3, gap="medium")
    for index, (number, title, description) in enumerate(steps):
        with columns[index % 3]:
            st.markdown(
                f'<div class="ss-step-card"><span>{number}</span><b>{title}</b><p>{description}</p></div>',
                unsafe_allow_html=True,
            )


def _render_trust() -> None:
    st.markdown('<div id="trust"></div>', unsafe_allow_html=True)
    st.markdown('<div class="ss-section-kicker">TRUST &amp; TRANSPARENCY</div>', unsafe_allow_html=True)
    st.header("A warning is not a verdict.")
    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        st.write(
            "ScamShield AI is intended to help people assess suspicious digital activity. "
            "It must distinguish technical findings, external-source reports, community "
            "allegations, heuristic warnings and AI-generated explanations."
        )
    with right:
        for item in [
            "A risk score is not proof of criminal activity.",
            "Community reports can be inaccurate or outdated.",
            "An unavailable source is not a clean result.",
            "Private evidence is not sent to third parties by this foundation interface.",
        ]:
            st.markdown(f'<div class="ss-trust-row"><span>✓</span>{item}</div>', unsafe_allow_html=True)


def render() -> None:
    _render_navbar()
    render_cinematic_experience()
    st.markdown("<div class='ss-cinematic-cta-note'>SCAMSHIELD AI · DETECT THE SIGNAL. STOP THE SCAM.</div>", unsafe_allow_html=True)
    _render_hero_actions()
    st.markdown('<div class="ss-section-gap"></div>', unsafe_allow_html=True)
    _render_launcher()
    st.markdown('<div class="ss-section-gap"></div>', unsafe_allow_html=True)
    _render_features()
    st.markdown('<div class="ss-section-gap"></div>', unsafe_allow_html=True)
    _render_workflow()
    st.markdown('<div class="ss-section-gap"></div>', unsafe_allow_html=True)
    _render_trust()
    st.markdown('<div id="about" class="ss-footer">'
                '<b>ScamShield AI</b> · Detect the Signal. Stop the Scam. '
                '<span>Local development release · External intelligence not connected</span></div>',
                unsafe_allow_html=True)
