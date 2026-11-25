from database.connection import database_connection, initialize_database
from services.case_management import (
    add_case_evidence, add_case_note, create_case, export_case_json,
    get_case, list_cases, update_case_status,
)


def test_create_case_persists_initial_evidence_and_event(tmp_path):
    db = tmp_path / "cases.db"
    initialize_database(db)
    record = create_case(db, "Fake job message", "Message", "Pay registration fee", "WhatsApp message", "High")
    assert record["case_ref"].startswith("SS-")
    assert record["status"] == "Open"
    assert record["priority"] == "High"
    assert record["evidence"][0]["evidence_value"] == "Pay registration fee"
    assert record["events"][0]["event_type"] == "created"


def test_case_status_note_and_evidence_history(tmp_path):
    db = tmp_path / "cases.db"
    initialize_database(db)
    case = create_case(db, "Suspicious domain", "Domain", "example.test")
    case_id = case["case_id"]
    add_case_note(db, case_id, "Matched an imported feed record; review source confidence.")
    add_case_evidence(db, case_id, "URL", "https://example.test/login", "URL Analyzer")
    updated = update_case_status(db, case_id, "In Progress")
    assert updated["status"] == "In Progress"
    assert len(updated["evidence"]) == 2
    assert {event["event_type"] for event in updated["events"]} >= {"created", "note", "evidence_added", "status_changed"}


def test_case_list_filter_and_json_export(tmp_path):
    db = tmp_path / "cases.db"
    initialize_database(db)
    opened = create_case(db, "Open case", "IP address", "192.0.2.10")
    closed = create_case(db, "Closed case", "File hash", "a" * 64)
    update_case_status(db, closed["case_id"], "Closed")
    assert len(list_cases(db, "Open")) == 1
    assert len(list_cases(db, "Closed")) == 1
    exported = export_case_json(db, opened["case_id"])
    assert '"case_ref"' in exported
    assert '192.0.2.10' in exported


def test_case_validation_rejects_empty_title_evidence_and_invalid_status(tmp_path):
    db = tmp_path / "cases.db"
    initialize_database(db)
    try:
        create_case(db, "", "Message", "some text")
        assert False, "empty title should fail"
    except ValueError:
        pass
    try:
        create_case(db, "Missing evidence", "Message", "  ")
        assert False, "empty evidence should fail"
    except ValueError:
        pass
    record = create_case(db, "Valid", "Message", "test")
    try:
        update_case_status(db, record["case_id"], "Unknown")
        assert False, "invalid status should fail"
    except ValueError:
        pass


def test_case_tables_have_foreign_key_cascade(tmp_path):
    db = tmp_path / "cases.db"
    initialize_database(db)
    record = create_case(db, "Delete test", "Message", "text")
    with database_connection(db) as connection:
        connection.execute("DELETE FROM investigation_cases WHERE case_id=?", (record["case_id"],))
        evidence_count = connection.execute("SELECT COUNT(*) FROM case_evidence").fetchone()[0]
        event_count = connection.execute("SELECT COUNT(*) FROM case_events").fetchone()[0]
    assert evidence_count == 0
    assert event_count == 0
