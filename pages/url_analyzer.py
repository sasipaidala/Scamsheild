"""UI for passive local URL structure analysis."""

from __future__ import annotations

import html
import streamlit as st

from services.url_service import MAX_URL_LENGTH, analyze_url


EXAMPLE_URLS = {
    "Clean structure": "https://example.com/login",
    "HTTP + IP host": "http://192.0.2.1/login",
    "Shortened link": "https://bit.ly/abc123",
    "Embedded credentials": "https://trusted.example@evil.example/login",
}


def _show_examples() -> None:
    st.markdown(
        '<div class="ss-neon-callout"><div class="ss-neon-kicker">QUICK LAB · SAFE EXAMPLES</div>'
        '<div style="color:var(--ss-muted);font-size:.86rem;margin-top:.35rem">'
        'Load a sample into the analyzer to explore how structural indicators are explained. '
        'These examples are parsed locally; no links are opened.</div></div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    for col, (label, sample) in zip(cols, EXAMPLE_URLS.items()):
        if col.button(label, key=f"ss_url_sample_{label}", use_container_width=True):
            st.session_state["ss_url_text"] = sample
            st.session_state.pop("ss_url_analysis_result", None)
            st.rerun()


def render() -> None:
    st.markdown('<div class="ss-eyebrow">ANALYZERS / URL · PASSIVE INSPECTION</div>', unsafe_allow_html=True)
    st.title("URL Analyzer")
    st.write("Inspect a link's visible structure for review indicators. Analysis is local and does not open or fetch the URL.")
    st.warning("This tool does not verify reputation or prove that a URL is malicious or safe. Do not open suspicious links to test them.")

    if "ss_url_prefill" in st.session_state:
        st.session_state["ss_url_text"] = st.session_state.pop("ss_url_prefill")
        st.session_state.pop("ss_url_analysis_result", None)

    _show_examples()
    st.markdown("#### Inspect a URL")
    with st.form("ss_url_analysis_form", clear_on_submit=False):
        url = st.text_input("Suspicious URL", key="ss_url_text", max_chars=MAX_URL_LENGTH, placeholder="https://example.com/login")
        st.caption(f"Maximum {MAX_URL_LENGTH:,} characters. The analyzer may add https:// when no scheme is supplied.")
        submitted = st.form_submit_button("⌁  Analyze URL structure", type="primary", use_container_width=True)

    if submitted:
        try:
            with st.spinner("Parsing URL structure locally…"):
                st.session_state["ss_url_analysis_result"] = analyze_url(url)
        except (TypeError, ValueError) as exc:
            st.session_state.pop("ss_url_analysis_result", None)
            st.error(str(exc))

    result = st.session_state.get("ss_url_analysis_result")
    if result is not None:
        st.markdown("### Structural assessment")
        if result.findings:
            high_attention = [
                finding for finding in result.findings
                if finding.severity.lower().startswith(("high", "critical"))
            ]
            if high_attention:
                st.error(
                    f"🚨 HIGH ATTENTION · {len(high_attention)} high-attention indicator(s) detected "
                    f"({len(result.findings)} total). Review this URL carefully. "
                    "This is not a maliciousness verdict."
                )
            else:
                st.warning(
                    f"{len(result.findings)} structural indicator(s) need review. "
                    "This is not a maliciousness verdict."
                )
        else:
            st.success("No configured structural indicator matched. This does not prove the URL is safe.")
        host_col, scheme_col, finding_col = st.columns(3)
        host_col.metric("Parsed hostname", result.hostname)
        scheme_col.metric("Scheme", result.scheme.upper())
        finding_col.metric("Review indicators", len(result.findings))
        st.markdown(
            '<div class="ss-neon-callout"><div class="ss-neon-kicker">ANALYSIS SNAPSHOT</div>'
            f'<div style="color:var(--ss-text);font-weight:650;overflow-wrap:anywhere;margin-top:.35rem">{html.escape(result.normalized_url)}</div>'
            '<div style="color:var(--ss-subtle);font-size:.75rem;margin-top:.35rem">'
            f'Ruleset {html.escape(result.ruleset_version)} · local parsing only</div></div>',
            unsafe_allow_html=True,
        )
        with st.expander("Parsed URL details"):
            st.write("**Normalized display:**")
            st.code(result.normalized_url, language=None)
            st.write("**Submitted URL:**")
            st.code(result.submitted_url, language=None)
        if result.findings:
            st.markdown("#### Indicators and explanations")
            for index, finding in enumerate(result.findings, 1):
                css_class = "ss-finding-card--high" if finding.severity.lower().startswith("high") else "ss-finding-card--review"
                st.markdown(
                    f'<div class="ss-finding-card {css_class}">'
                    f'<div class="ss-neon-kicker">INDICATOR {index:02d} · {html.escape(finding.severity.upper())}</div>'
                    f'<b>{html.escape(finding.title)}</b>'
                    f'<p>{html.escape(finding.explanation)}</p>'
                    f'<p style="font-size:.72rem;color:var(--ss-subtle)">Rule: <code>{html.escape(finding.rule_id)}</code></p>'
                    '</div>',
                    unsafe_allow_html=True,
                )
        if result.observations:
            with st.expander(f"Additional observations ({len(result.observations)})"):
                for item in result.observations:
                    st.markdown(f"- `{item}`")
        with st.expander("Method and limitations"):
            st.write(f"**Method:** local URL parsing (`{result.ruleset_version}`)")
            st.write(f"**Analyzed at:** {result.analyzed_at}")
            for limitation in result.limitations:
                st.markdown(f"- {limitation}")

    st.markdown(
        '<div class="ss-panel"><div class="ss-panel-title">Safety boundary</div>'
        '<div class="ss-panel-copy">ScamShield only inspects the URL text in this milestone. '
        'It does not make a network request, resolve the hostname, follow redirects, or submit the URL to a third party.</div></div>',
        unsafe_allow_html=True,
    )
