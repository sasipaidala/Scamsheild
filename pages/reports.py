"""Investigation report generation and saved report archive."""
from __future__ import annotations

import streamlit as st

from core.config import Settings
from services.case_management import list_cases
from services.reports import (
    build_case_report, list_saved_reports, render_cases_csv, render_markdown,
    save_report, get_saved_report,
)


def render() -> None:
    database_path = Settings.from_env().database_path
    st.markdown('<div class="ss-eyebrow">MANAGE / REPORTS</div>', unsafe_allow_html=True)
    st.title("Investigation reports")
    st.write("Generate evidence-based reports from saved investigation cases and export a case register.")

    cases = list_cases(database_path)
    reports = list_saved_reports(database_path)
    c1, c2, c3 = st.columns(3)
    c1.metric("Investigation cases", len(cases))
    c2.metric("Saved reports", len(reports))
    c3.metric("Open cases", sum(case["status"] != "Closed" for case in cases))

    st.subheader("Generate a case report")
    if not cases:
        st.info("There are no cases to report yet. Create a case in Investigation Cases first.")
    else:
        labels = {f"{case['case_ref']} · {case['title']} · {case['status']}": case["case_id"] for case in cases}
        with st.form("ss_generate_case_report"):
            selected = st.selectbox("Investigation case", list(labels))
            include_activity = st.checkbox("Include analyst notes and activity history", value=True)
            generate = st.form_submit_button("Generate report", type="primary")
        if generate:
            try:
                report = build_case_report(database_path, labels[selected], include_activity)
                saved = save_report(database_path, report)
                st.session_state["ss_last_generated_report_id"] = saved["report_id"]
                st.success(f"Report {saved['report_ref']} generated and saved.")
            except (ValueError, TypeError) as exc:
                st.error(str(exc))

    last_id = st.session_state.get("ss_last_generated_report_id")
    if last_id:
        saved = get_saved_report(database_path, int(last_id))
        if saved:
            report = saved["payload"]
            st.divider()
            st.subheader("Latest report")
            st.caption(f"{saved['report_ref']} · {saved['case_ref']} · Generated {saved['generated_at']}")
            st.markdown(render_markdown(report))
            st.download_button("Download Markdown report", render_markdown(report),
                               file_name=f"{saved['report_ref'].lower()}.md", mime="text/markdown")
            import json
            st.download_button("Download report JSON", json.dumps(report, ensure_ascii=False, indent=2),
                               file_name=f"{saved['report_ref'].lower()}.json", mime="application/json")

    st.divider()
    st.subheader("Case register export")
    st.write("A CSV summary of saved cases. It does not include full evidence content.")
    st.download_button("Download cases CSV", render_cases_csv(database_path),
                       file_name="scamshield_case_register.csv", mime="text/csv")

    st.subheader("Saved report archive")
    if not reports:
        st.caption("No reports have been generated yet.")
    else:
        st.dataframe([{"Report ID": r["report_ref"], "Case": r["case_ref"],
                       "Type": r["report_type"], "Generated (UTC)": r["generated_at"]}
                      for r in reports], use_container_width=True, hide_index=True)
        archive_options = {f"{r['report_ref']} · {r['case_ref']} · {r['generated_at']}": r["report_id"] for r in reports}
        chosen = st.selectbox("Open saved report", list(archive_options), key="ss_report_archive_select")
        archived = get_saved_report(database_path, archive_options[chosen])
        if archived:
            import json
            payload = archived["payload"]
            st.download_button("Download archived JSON", json.dumps(payload, ensure_ascii=False, indent=2),
                               file_name=f"{archived['report_ref'].lower()}.json", mime="application/json",
                               key=f"download_archived_{archived['report_id']}")
            st.download_button("Download archived Markdown", render_markdown(payload),
                               file_name=f"{archived['report_ref'].lower()}.md", mime="text/markdown",
                               key=f"download_archived_md_{archived['report_id']}")

    st.warning("Reports are snapshots of locally recorded case data, not legal findings or proof of criminal activity. Review content and remove unnecessary personal information before sharing.")
