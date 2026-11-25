"""Generate and persist evidence-based investigation report snapshots."""
from __future__ import annotations

import csv
import io
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from database.connection import database_connection
from services.case_management import get_case, list_cases


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_case_report(database_path: str | Path, case_id: int, include_activity: bool = True) -> dict[str, Any]:
    case = get_case(database_path, case_id)
    if case is None:
        raise ValueError("Case was not found.")
    events = case["events"] if include_activity else []
    return {
        "report_ref": "RPT-" + secrets.token_hex(4).upper(),
        "generated_at": _now(),
        "report_type": "Investigation case report",
        "scope": "Snapshot of the selected local investigation case and its recorded evidence.",
        "case": {key: case[key] for key in ("case_ref", "title", "status", "priority", "description", "created_at", "updated_at")},
        "evidence": case["evidence"],
        "activity": events,
        "limitations": [
            "This report contains records saved in this ScamShield workspace only.",
            "An imported threat-intelligence match is a source-reported indicator, not proof that a person or organization committed fraud.",
            "No external provider lookup or independent forensic verification is implied unless explicitly recorded in the case evidence.",
            "Evidence completeness and accuracy depend on the information supplied by the investigator.",
        ],
    }


def save_report(database_path: str | Path, report: dict[str, Any]) -> dict[str, Any]:
    payload = json.dumps(report, ensure_ascii=False, sort_keys=True)
    with database_connection(database_path) as connection:
        cursor = connection.execute(
            "INSERT INTO generated_reports(report_ref, case_ref, report_type, generated_at, payload_json) VALUES (?, ?, ?, ?, ?)",
            (report["report_ref"], report["case"]["case_ref"], report["report_type"], report["generated_at"], payload),
        )
        report_id = int(cursor.lastrowid)
    return get_saved_report(database_path, report_id)  # type: ignore[return-value]


def get_saved_report(database_path: str | Path, report_id: int) -> dict[str, Any] | None:
    with database_connection(database_path) as connection:
        row = connection.execute("SELECT * FROM generated_reports WHERE report_id=?", (int(report_id),)).fetchone()
    if row is None:
        return None
    result = dict(row)
    result["payload"] = json.loads(result.pop("payload_json"))
    return result


def list_saved_reports(database_path: str | Path, limit: int = 200) -> tuple[dict[str, Any], ...]:
    safe_limit = max(1, min(int(limit), 1000))
    with database_connection(database_path) as connection:
        rows = connection.execute(
            "SELECT report_id, report_ref, case_ref, report_type, generated_at FROM generated_reports ORDER BY generated_at DESC LIMIT ?",
            (safe_limit,),
        ).fetchall()
    return tuple(dict(row) for row in rows)


def render_markdown(report: dict[str, Any]) -> str:
    case = report["case"]
    lines = [
        f"# {report['report_type']}", "", f"**Report:** {report['report_ref']}  ",
        f"**Generated (UTC):** {report['generated_at']}  ", f"**Case:** {case['case_ref']} — {case['title']}", "",
        "## Case summary", f"- Status: {case['status']}", f"- Priority: {case['priority']}",
        f"- Created: {case['created_at']}", f"- Last updated: {case['updated_at']}", "",
        "## Description", case["description"] or "No description recorded.", "", "## Evidence",
    ]
    if report["evidence"]:
        for item in report["evidence"]:
            lines.extend([f"### {item['evidence_type']} — {item['created_at']}", f"Source: {item['source']}", "```text", item["evidence_value"], "```", ""])
    else:
        lines.append("No evidence recorded.")
    lines.extend(["## Activity history", ""])
    if report["activity"]:
        for event in report["activity"]:
            lines.append(f"- {event['created_at']} · {event['event_type']}: {event['details']}")
    else:
        lines.append("Activity history omitted or unavailable.")
    lines.extend(["", "## Limitations"])
    lines.extend(f"- {item}" for item in report["limitations"])
    return "\n".join(lines) + "\n"


def render_cases_csv(database_path: str | Path) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=["case_ref", "title", "status", "priority", "evidence_count", "created_at", "updated_at"])
    writer.writeheader()
    for case in list_cases(database_path):
        writer.writerow({key: case.get(key, "") for key in writer.fieldnames})
    return output.getvalue()
