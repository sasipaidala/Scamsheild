import json

import pytest

from database.connection import database_connection, initialize_database
from services.case_management import add_case_note, create_case
from services.reports import (
    build_case_report, get_saved_report, list_saved_reports, render_cases_csv,
    render_markdown, save_report,
)


def test_report_build_save_and_retrieve_snapshot(tmp_path):
    db = tmp_path / "reports.db"
    initialize_database(db)
    case = create_case(db, "Suspicious recruitment message", "Message", "Pay a registration fee", "Unsolicited job offer", "High")
    add_case_note(db, case["case_id"], "Fee request requires further verification.")
    report = build_case_report(db, case["case_id"])
    assert report["case"]["case_ref"] == case["case_ref"]
    assert len(report["evidence"]) == 1
    assert any("not proof" in item for item in report["limitations"])
    saved = save_report(db, report)
    restored = get_saved_report(db, saved["report_id"])
    assert restored["payload"]["report_ref"] == report["report_ref"]
    assert len(list_saved_reports(db)) == 1


def test_report_can_exclude_activity_but_preserve_evidence(tmp_path):
    db = tmp_path / "reports.db"
    initialize_database(db)
    case = create_case(db, "URL review", "URL", "https://example.test/login")
    report = build_case_report(db, case["case_id"], include_activity=False)
    assert report["activity"] == []
    assert report["evidence"][0]["evidence_value"] == "https://example.test/login"


def test_markdown_report_contains_scope_evidence_and_limitations(tmp_path):
    db = tmp_path / "reports.db"
    initialize_database(db)
    case = create_case(db, "Test case", "IP address", "192.0.2.20")
    text = render_markdown(build_case_report(db, case["case_id"]))
    assert "## Case summary" in text
    assert "192.0.2.20" in text
    assert "## Limitations" in text


def test_case_csv_exports_register_without_evidence_content(tmp_path):
    db = tmp_path / "reports.db"
    initialize_database(db)
    create_case(db, "CSV test", "Message", "private evidence payload")
    csv_text = render_cases_csv(db)
    assert "case_ref,title,status,priority" in csv_text
    assert "CSV test" in csv_text
    assert "private evidence payload" not in csv_text


def test_missing_case_report_raises(tmp_path):
    db = tmp_path / "reports.db"
    initialize_database(db)
    with pytest.raises(ValueError, match="Case was not found"):
        build_case_report(db, 999)


def test_migration_five_preserves_case_and_creates_report_table(tmp_path):
    db = tmp_path / "reports.db"
    initialize_database(db)
    case = create_case(db, "Migration check", "Message", "test")
    with database_connection(db) as connection:
        version = connection.execute("SELECT MAX(version) FROM schema_migrations").fetchone()[0]
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert version == 6
    assert "generated_reports" in tables
    assert case["case_ref"]
