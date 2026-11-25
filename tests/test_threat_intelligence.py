import sqlite3

import pytest

from database.connection import SCHEMA_VERSION, initialize_database
from services.threat_intelligence import (
    import_csv, indicator_count, list_indicators, lookup_indicator, normalize_indicator,
)


def test_normalize_domain_and_ip_and_hash():
    assert normalize_indicator("domain", "EXAMPLE.COM.") == "example.com"
    assert normalize_indicator("ip", "2001:0db8::1") == "2001:db8::1"
    assert normalize_indicator("hash", "A" * 64) == "a" * 64


def test_normalize_url_strips_fragment_and_normalizes_host():
    assert normalize_indicator("url", "HTTP://Example.COM/login#top") == "http://example.com/login"


@pytest.mark.parametrize("kind,value", [
    ("domain", "localhost"),
    ("domain", "https://example.com"),
    ("ip", "999.1.1.1"),
    ("hash", "not-a-hash"),
    ("url", "javascript:alert(1)"),
    ("url", "https://user:pass@example.com/login"),
])
def test_invalid_indicators_are_rejected(kind, value):
    with pytest.raises(ValueError):
        normalize_indicator(kind, value)


def test_import_and_exact_lookup_preserve_source_provenance(tmp_path):
    db = tmp_path / "ti.db"
    initialize_database(db)
    feed = b"indicator,type,threat_type,confidence,first_seen,description\nexample.com,domain,phishing,85,2026-11-01,Credential theft host\n"
    summary = import_csv(db, feed, "Unit Test Feed", "https://feed.example/docs")
    assert (summary.inserted, summary.updated, summary.skipped) == (1, 0, 0)
    matches = lookup_indicator(db, "domain", "EXAMPLE.COM")
    assert len(matches) == 1
    assert matches[0]["source_name"] == "Unit Test Feed"
    assert matches[0]["confidence"] == 85
    assert matches[0]["source_url"] == "https://feed.example/docs"
    assert indicator_count(db) == 1


def test_duplicate_import_updates_same_source_record(tmp_path):
    db = tmp_path / "dedupe.db"
    initialize_database(db)
    first = b"indicator,type,confidence\nexample.com,domain,40\n"
    second = b"indicator,type,confidence\nexample.com,domain,90\n"
    assert import_csv(db, first, "Feed").inserted == 1
    result = import_csv(db, second, "Feed")
    assert result.updated == 1
    assert indicator_count(db) == 1
    assert lookup_indicator(db, "domain", "example.com")[0]["confidence"] == 90


def test_same_indicator_from_different_sources_is_retained(tmp_path):
    db = tmp_path / "sources.db"
    initialize_database(db)
    feed = b"indicator,type\nexample.com,domain\n"
    import_csv(db, feed, "Feed A")
    import_csv(db, feed, "Feed B")
    assert len(lookup_indicator(db, "domain", "example.com")) == 2


def test_bad_rows_are_skipped_with_error_and_valid_rows_saved(tmp_path):
    db = tmp_path / "partial.csv.db"
    initialize_database(db)
    feed = b"indicator,type,confidence\nexample.com,domain,80\nnot-valid,ip,20\n"
    result = import_csv(db, feed, "Mixed Feed")
    assert result.inserted == 1
    assert result.skipped == 1
    assert "Row 3" in result.errors[0]


def test_csv_requires_type_and_indicator_headers(tmp_path):
    db = tmp_path / "bad-header.db"
    initialize_database(db)
    with pytest.raises(ValueError, match="requires"):
        import_csv(db, b"value,kind\nexample.com,domain\n", "Feed")


def test_migration_three_is_versioned_and_creates_ioc_table(tmp_path):
    db = tmp_path / "migration.db"
    initialize_database(db)
    with sqlite3.connect(db) as connection:
        version = connection.execute("SELECT MAX(version) FROM schema_migrations").fetchone()[0]
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert version == SCHEMA_VERSION == 6
    assert "threat_indicators" in tables
