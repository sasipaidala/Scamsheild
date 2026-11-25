"""Import-based IOC intelligence workspace. No external network lookups."""
from __future__ import annotations

import streamlit as st

from core.config import Settings
from services.threat_intelligence import (
    INDICATOR_TYPES, import_csv, indicator_count, list_indicators, lookup_indicator,
)


def render() -> None:
    database_path = Settings.from_env().database_path
    st.markdown('<div class="ss-eyebrow">INTELLIGENCE / IOC WORKSPACE</div>', unsafe_allow_html=True)
    st.title("Threat Intelligence")
    st.write("Search and manage indicators from threat feeds you explicitly import. Every result retains its source attribution.")
    st.info("Import-based mode · No live provider is connected. ScamShield does not fetch, resolve, or open submitted indicators.")

    total = indicator_count(database_path)
    a, b, c = st.columns(3)
    a.metric("Imported indicators", f"{total:,}")
    b.metric("Supported IOC types", "4")
    c.metric("Live feeds", "0")

    lookup_tab, import_tab, inventory_tab = st.tabs(["IOC Lookup", "Import Feed", "Indicator Inventory"])
    with lookup_tab:
        st.subheader("Search an indicator")
        with st.form("ss_ioc_lookup_form"):
            kind = st.selectbox("Indicator type", INDICATOR_TYPES, format_func=lambda x: x.upper())
            value = st.text_input("Indicator value", placeholder="example.com, 203.0.113.10, URL or file hash")
            submitted = st.form_submit_button("Search local intelligence", type="primary")
        if submitted:
            try:
                st.session_state["ss_ioc_lookup_result"] = lookup_indicator(database_path, kind, value)
                st.session_state["ss_ioc_lookup_query"] = value
            except (TypeError, ValueError) as exc:
                st.session_state.pop("ss_ioc_lookup_result", None)
                st.error(str(exc))
        if "ss_ioc_lookup_result" in st.session_state:
            results = st.session_state["ss_ioc_lookup_result"]
            if results:
                st.warning(f"{len(results)} matching source record(s) found. Review source and context; a feed match is not a final verdict.")
                for item in results:
                    with st.container(border=True):
                        st.markdown(f"**{item['threat_type']}** · `{item['indicator_type']}`")
                        st.code(item["indicator_value"], language=None)
                        st.write(f"Source: **{item['source_name']}**")
                        if item["source_url"]:
                            st.code(item["source_url"], language=None)
                        st.write(f"Confidence supplied by source: {item['confidence'] if item['confidence'] is not None else 'Not provided'}")
                        st.caption(f"First seen: {item['first_seen'] or 'Not provided'} · Last seen: {item['last_seen'] or 'Not provided'} · Imported: {item['imported_at']}")
                        if item["description"]:
                            st.write(item["description"])
            else:
                st.success("No match in your imported intelligence records. This does not mean the indicator is safe.")

    with import_tab:
        st.subheader("Import a CSV threat feed")
        st.write("Accepted columns: `indicator`, `type` (or `indicator_type`), and optional `threat_type`, `confidence`, `first_seen`, `last_seen`, `expires_at`, `description`.")
        source_name = st.text_input("Feed / source name", max_chars=120, placeholder="e.g. Internal SOC feed")
        source_url = st.text_input("Source reference URL (optional)", max_chars=500, placeholder="https://source.example/feed-documentation")
        uploaded = st.file_uploader("Upload UTF-8 CSV", type=["csv"], max_upload_size=5)
        if st.button("Import indicators", type="primary", disabled=not (source_name.strip() and uploaded is not None)):
            try:
                summary = import_csv(database_path, uploaded.getvalue(), source_name, source_url)
                st.success(f"Import complete: {summary.inserted} inserted, {summary.updated} updated, {summary.skipped} skipped.")
                for error in summary.errors:
                    st.caption(error)
                st.rerun()
            except (TypeError, ValueError) as exc:
                st.error(str(exc))
        st.caption("Only import feeds you are authorized to use. Source claims are stored as supplied and are not independently verified.")
        st.download_button(
            "Download CSV template",
            data="indicator,type,threat_type,confidence,first_seen,last_seen,expires_at,description\nexample.com,domain,phishing,70,,,,Example record - replace before use\n",
            file_name="scamshield_ioc_template.csv",
            mime="text/csv",
        )

    with inventory_tab:
        st.subheader("Recently imported indicators")
        records = list_indicators(database_path)
        if records:
            st.dataframe(records, use_container_width=True, hide_index=True)
        else:
            st.caption("No indicators imported yet. Inventory will populate after a feed is imported.")

    with st.expander("Method, provenance and limitations"):
        st.markdown("- Lookup is exact-match against the local SQLite indicator inventory.\n- Source name, optional reference URL and feed-supplied metadata are retained.\n- Confidence values are source-supplied, not calculated by ScamShield.\n- Expiration dates are stored but not automatically interpreted as proof of current validity.\n- No DNS resolution, URL fetching, malware detonation, or live provider lookup occurs.\n- A missing match is not a clean bill of health.")
