"""Persistent investigation case register and case detail workspace."""
from __future__ import annotations

import streamlit as st

from core.config import Settings
from services.threat_intelligence import lookup_indicator
from services.case_management import (
    CASE_PRIORITIES, CASE_STATUSES, EVIDENCE_TYPES, add_case_evidence,
    add_case_note, export_case_json, get_case, list_cases, update_case_status,
)


def render() -> None:
    database_path = Settings.from_env().database_path
    st.markdown('<div class="ss-eyebrow">MANAGE / CASES</div>', unsafe_allow_html=True)
    st.title("Investigation cases")
    st.write("A persistent case register for evidence, analyst notes and status history.")

    cases = list_cases(database_path)
    metric_cols = st.columns(3)
    metric_cols[0].metric("Total cases", len(cases))
    metric_cols[1].metric("Open / in progress", sum(c["status"] != "Closed" for c in cases))
    metric_cols[2].metric("Closed", sum(c["status"] == "Closed" for c in cases))

    if not cases:
        st.info("No investigation cases have been created yet. Use New Investigation to open the first case.")
        return

    st.subheader("Case register")
    filter_status = st.selectbox("Filter by status", ["All", *CASE_STATUSES], key="ss_case_filter")
    visible = [c for c in cases if filter_status == "All" or c["status"] == filter_status]
    st.dataframe(
        [{"Case ID": c["case_ref"], "Title": c["title"], "Status": c["status"],
          "Priority": c["priority"], "Evidence": c["evidence_count"], "Updated": c["updated_at"]}
         for c in visible],
        use_container_width=True, hide_index=True,
    )
    if not visible:
        st.caption("No cases match this filter.")
        return

    options = {f"{c['case_ref']} · {c['title']}": c["case_id"] for c in visible}
    selected_label = st.selectbox("Open case", list(options), key="ss_case_selected")
    record = get_case(database_path, options[selected_label])
    if record is None:
        st.error("This case could not be loaded. Refresh the page and try again.")
        return

    st.divider()
    st.subheader(f"{record['case_ref']} — {record['title']}")
    st.caption(f"Created {record['created_at']} · Last updated {record['updated_at']}")
    left, right = st.columns(2)
    with left:
        new_status = st.selectbox("Status", CASE_STATUSES, index=CASE_STATUSES.index(record["status"]), key=f"status_{record['case_id']}")
    with right:
        st.text_input("Priority", value=record["priority"], disabled=True, key=f"priority_{record['case_id']}")
    if st.button("Save status", key=f"save_status_{record['case_id']}"):
        try:
            update_case_status(database_path, record["case_id"], new_status)
            st.success("Case status updated.")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

    if record["description"]:
        st.markdown("**Case description**")
        st.write(record["description"])

    st.markdown("**Evidence**")
    if record["evidence"]:
        for item in record["evidence"]:
            with st.expander(f"{item['evidence_type']} · {item['created_at']}"):
                st.code(item["evidence_value"], language=None)
                st.caption(f"Source: {item['source']}")
                indicator_type = {"URL": "url", "Domain": "domain", "IP address": "ip", "File hash": "hash"}.get(item["evidence_type"])
                if indicator_type:
                    try:
                        matches = lookup_indicator(database_path, indicator_type, item["evidence_value"])
                    except (ValueError, TypeError):
                        matches = ()
                    if matches:
                        st.warning(f"{len(matches)} exact match(es) in imported threat intelligence")
                        for match in matches:
                            st.markdown(f"**{match['threat_type']}** · Source: {match['source_name']} · Source confidence: {match['confidence'] if match['confidence'] is not None else 'Not supplied'}")
                            if match["source_url"]:
                                st.caption(f"Source reference: {match['source_url']}")
                    else:
                        st.caption("No exact match in the imported IOC inventory. This is not proof the indicator is safe.")
    else:
        st.caption("No evidence attached.")

    with st.expander("Add evidence"):
        with st.form(f"add_evidence_{record['case_id']}"):
            evidence_type = st.selectbox("Evidence type", EVIDENCE_TYPES, key=f"ev_type_{record['case_id']}")
            evidence_value = st.text_area("Evidence content", max_chars=10000, key=f"ev_value_{record['case_id']}")
            evidence_source = st.text_input("Source / context", value="User added", max_chars=120, key=f"ev_source_{record['case_id']}")
            add_evidence = st.form_submit_button("Attach evidence")
        if add_evidence:
            try:
                add_case_evidence(database_path, record["case_id"], evidence_type, evidence_value, evidence_source)
                st.success("Evidence attached to case.")
                st.rerun()
            except (ValueError, TypeError) as exc:
                st.error(str(exc))

    with st.expander("Add analyst note"):
        with st.form(f"add_note_{record['case_id']}"):
            note = st.text_area("Note", max_chars=2000, key=f"note_{record['case_id']}")
            add_note = st.form_submit_button("Save note")
        if add_note:
            try:
                add_case_note(database_path, record["case_id"], note)
                st.success("Note saved to case history.")
                st.rerun()
            except (ValueError, TypeError) as exc:
                st.error(str(exc))

    st.markdown("**Activity history**")
    for event in record["events"]:
        st.caption(f"{event['created_at']} · {event['event_type'].replace('_', ' ').title()}")
        st.write(event["details"])

    st.download_button(
        "Export case as JSON", data=export_case_json(database_path, record["case_id"]),
        file_name=f"{record['case_ref'].lower()}.json", mime="application/json",
    )
    st.warning("Case evidence is stored locally in the configured SQLite database. Avoid storing passwords, OTPs, payment-card data or unrelated personal information.")
