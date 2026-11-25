"""Persistent investigation case records and evidence history."""
from __future__ import annotations

import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from database.connection import database_connection

CASE_STATUSES = ("Open", "In Progress", "Closed")
CASE_PRIORITIES = ("Low", "Medium", "High", "Critical")
EVIDENCE_TYPES = ("Message", "Email", "URL", "Domain", "IP address", "File hash")
MAX_TITLE = 120
MAX_DESCRIPTION = 2000
MAX_EVIDENCE = 10000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _clean_text(value: str, field: str, limit: int, required: bool = False) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field} must be text.")
    value = value.strip()
    if required and not value:
        raise ValueError(f"{field} is required.")
    if len(value) > limit:
        raise ValueError(f"{field} must be {limit} characters or fewer.")
    if any(ord(ch) < 32 and ch not in "\n\r\t" for ch in value):
        raise ValueError(f"{field} contains unsupported control characters.")
    return value


def create_case(database_path: str | Path, title: str, evidence_type: str,
                evidence_value: str, description: str = "", priority: str = "Medium") -> dict[str, Any]:
    title = _clean_text(title, "Case title", MAX_TITLE, True)
    description = _clean_text(description, "Description", MAX_DESCRIPTION)
    evidence_value = _clean_text(evidence_value, "Evidence", MAX_EVIDENCE, True)
    if evidence_type not in EVIDENCE_TYPES:
        raise ValueError("Unsupported evidence type.")
    if priority not in CASE_PRIORITIES:
        raise ValueError("Unsupported case priority.")
    case_ref = "SS-" + secrets.token_hex(4).upper()
    now = _now()
    with database_connection(database_path) as connection:
        cursor = connection.execute(
            """INSERT INTO investigation_cases
            (case_ref, title, status, priority, description, created_at, updated_at)
            VALUES (?, ?, 'Open', ?, ?, ?, ?)""",
            (case_ref, title, priority, description, now, now),
        )
        case_id = int(cursor.lastrowid)
        connection.execute(
            """INSERT INTO case_evidence
            (case_id, evidence_type, evidence_value, source, created_at)
            VALUES (?, ?, ?, 'User submission', ?)""",
            (case_id, evidence_type, evidence_value, now),
        )
        connection.execute(
            "INSERT INTO case_events(case_id, event_type, details, created_at) VALUES (?, 'created', ?, ?)",
            (case_id, f"Case created with {evidence_type} evidence.", now),
        )
    return get_case(database_path, case_id)


def list_cases(database_path: str | Path, status: str | None = None, limit: int = 500) -> tuple[dict[str, Any], ...]:
    safe_limit = max(1, min(int(limit), 2000))
    query = """SELECT c.*, (SELECT COUNT(*) FROM case_evidence e WHERE e.case_id=c.case_id) AS evidence_count
               FROM investigation_cases c"""
    params: list[Any] = []
    if status and status in CASE_STATUSES:
        query += " WHERE c.status=?"
        params.append(status)
    query += " ORDER BY c.updated_at DESC LIMIT ?"
    params.append(safe_limit)
    with database_connection(database_path) as connection:
        rows = connection.execute(query, params).fetchall()
    return tuple(dict(row) for row in rows)


def get_case(database_path: str | Path, case_id: int) -> dict[str, Any] | None:
    with database_connection(database_path) as connection:
        case = connection.execute(
            "SELECT * FROM investigation_cases WHERE case_id=?", (int(case_id),)
        ).fetchone()
        if case is None:
            return None
        result = dict(case)
        result["evidence"] = [dict(row) for row in connection.execute(
            "SELECT * FROM case_evidence WHERE case_id=? ORDER BY created_at DESC, evidence_id DESC", (int(case_id),)
        ).fetchall()]
        result["events"] = [dict(row) for row in connection.execute(
            "SELECT * FROM case_events WHERE case_id=? ORDER BY created_at DESC, event_id DESC", (int(case_id),)
        ).fetchall()]
    return result


def update_case_status(database_path: str | Path, case_id: int, status: str) -> dict[str, Any]:
    if status not in CASE_STATUSES:
        raise ValueError("Unsupported case status.")
    now = _now()
    with database_connection(database_path) as connection:
        exists = connection.execute("SELECT 1 FROM investigation_cases WHERE case_id=?", (int(case_id),)).fetchone()
        if not exists:
            raise ValueError("Case was not found.")
        connection.execute("UPDATE investigation_cases SET status=?, updated_at=? WHERE case_id=?", (status, now, int(case_id)))
        connection.execute("INSERT INTO case_events(case_id, event_type, details, created_at) VALUES (?, 'status_changed', ?, ?)", (int(case_id), f"Status changed to {status}.", now))
    return get_case(database_path, case_id)


def add_case_note(database_path: str | Path, case_id: int, note: str) -> dict[str, Any]:
    note = _clean_text(note, "Note", MAX_DESCRIPTION, True)
    now = _now()
    with database_connection(database_path) as connection:
        exists = connection.execute("SELECT 1 FROM investigation_cases WHERE case_id=?", (int(case_id),)).fetchone()
        if not exists:
            raise ValueError("Case was not found.")
        connection.execute("INSERT INTO case_events(case_id, event_type, details, created_at) VALUES (?, 'note', ?, ?)", (int(case_id), note, now))
        connection.execute("UPDATE investigation_cases SET updated_at=? WHERE case_id=?", (now, int(case_id)))
    return get_case(database_path, case_id)


def add_case_evidence(database_path: str | Path, case_id: int, evidence_type: str,
                      evidence_value: str, source: str = "User added") -> dict[str, Any]:
    if evidence_type not in EVIDENCE_TYPES:
        raise ValueError("Unsupported evidence type.")
    evidence_value = _clean_text(evidence_value, "Evidence", MAX_EVIDENCE, True)
    source = _clean_text(source, "Evidence source", 120, True)
    now = _now()
    with database_connection(database_path) as connection:
        exists = connection.execute("SELECT 1 FROM investigation_cases WHERE case_id=?", (int(case_id),)).fetchone()
        if not exists:
            raise ValueError("Case was not found.")
        connection.execute("INSERT INTO case_evidence(case_id, evidence_type, evidence_value, source, created_at) VALUES (?, ?, ?, ?, ?)", (int(case_id), evidence_type, evidence_value, source, now))
        connection.execute("UPDATE investigation_cases SET updated_at=? WHERE case_id=?", (now, int(case_id)))
        connection.execute("INSERT INTO case_events(case_id, event_type, details, created_at) VALUES (?, 'evidence_added', ?, ?)", (int(case_id), f"Added {evidence_type} evidence from {source}.", now))
    return get_case(database_path, case_id)


def export_case_json(database_path: str | Path, case_id: int) -> str:
    record = get_case(database_path, case_id)
    if record is None:
        raise ValueError("Case was not found.")
    return json.dumps(record, ensure_ascii=False, indent=2)
