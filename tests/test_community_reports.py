import sqlite3
import pytest

from database.connection import SCHEMA_VERSION, initialize_database
from services.community_reports import normalize_identifier, submit_report


def test_phone_normalization():
    assert normalize_identifier("Phone number", "+91 98765-43210") == "+919876543210"


def test_email_normalization():
    assert normalize_identifier("Email address", "Abuse@Example.COM") == "abuse@example.com"


def test_invalid_phone_rejected():
    with pytest.raises(ValueError):
        normalize_identifier("Phone number", "12345")


def test_invalid_url_rejected():
    with pytest.raises(ValueError):
        normalize_identifier("URL", "javascript:alert(1)")


def test_report_is_persisted_as_pending_review(tmp_path):
    db = tmp_path / "reports.db"
    initialize_database(db)
    receipt = submit_report(db, "Email address", "Fraud@Example.com", "Phishing", "Received a fake login link by email.")
    assert receipt.report_id > 0
    assert receipt.status == "pending_review"
    with sqlite3.connect(db) as connection:
        row = connection.execute("SELECT normalized_identifier, status FROM community_reports").fetchone()
    assert row == ("fraud@example.com", "pending_review")


def test_database_migration_is_versioned_and_idempotent(tmp_path):
    db = tmp_path / "migration.db"
    initialize_database(db)
    initialize_database(db)
    with sqlite3.connect(db) as connection:
        version = connection.execute("SELECT MAX(version) FROM schema_migrations").fetchone()[0]
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert version == SCHEMA_VERSION == 6
    assert "community_reports" in tables
