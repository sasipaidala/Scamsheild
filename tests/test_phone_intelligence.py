import sqlite3

import pytest

from database.connection import initialize_database
from services.community_reports import submit_report
from services.phone_intelligence import UnconfiguredProvider, lookup_phone


def test_lookup_returns_no_reports_without_inventing_safe_verdict(tmp_path):
    db = tmp_path / "phone.db"
    initialize_database(db)
    normalized, summary, external = lookup_phone(db, "+91 98765-43210")
    assert normalized == "+919876543210"
    assert summary.total_submissions == 0
    assert summary.verified == 0
    assert external.connected is False
    assert external.status == "not_configured"


def test_lookup_counts_community_reports_by_status_and_category(tmp_path):
    db = tmp_path / "phone.db"
    initialize_database(db)
    submit_report(db, "Phone number", "+919876543210", "Financial fraud", "Caller requested an advance transfer.")
    submit_report(db, "Phone number", "+91 98765-43210", "Financial fraud", "Caller asked for payment before service.")
    with sqlite3.connect(db) as connection:
        connection.execute("UPDATE community_reports SET status='verified' WHERE report_id=1")
    _, summary, _ = lookup_phone(db, "+919876543210")
    assert summary.total_submissions == 2
    assert summary.pending_review == 1
    assert summary.verified == 1
    assert summary.categories == (("Financial fraud", 2),)


def test_lookup_rejects_invalid_phone(tmp_path):
    db = tmp_path / "phone.db"
    initialize_database(db)
    with pytest.raises(ValueError):
        lookup_phone(db, "123")


def test_unconfigured_provider_does_not_make_network_claim():
    result = UnconfiguredProvider().lookup("+919876543210")
    assert result.connected is False
    assert result.report_count is None
    assert "configured" in result.explanation.lower()


def test_opentrust_provider_hashes_number_and_parses_reported_response(monkeypatch):
    import hashlib
    import json
    from services.phone_intelligence import OpenTrustProvider

    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({
                "reported": True,
                "report_count": 3,
                "notice": "Merchant observations; not proof of fraud.",
            }).encode()

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("services.phone_intelligence.urlopen", fake_urlopen)
    result = OpenTrustProvider(api_key="test-secret").lookup("+919876543210")

    assert result.connected is True
    assert result.status == "reported"
    assert result.report_count == 3
    assert captured["request"].get_header("Authorization") == "Bearer test-secret"
    body = json.loads(captured["request"].data.decode())
    assert body["phone_sha256"] == hashlib.sha256(b"+919876543210").hexdigest()
    assert body["phone_length"] == 13
    assert "9876543210" not in captured["request"].data.decode()


def test_opentrust_provider_handles_missing_key_without_network(monkeypatch):
    from services.phone_intelligence import OpenTrustProvider

    monkeypatch.delenv("OPENTRUST_API_KEY", raising=False)
    result = OpenTrustProvider().lookup("+919876543210")
    assert result.connected is False
    assert result.status == "not_configured"
    assert "OPENTRUST_API_KEY" in result.explanation


def test_opentrust_provider_reports_empty_result_as_unknown_not_safe(monkeypatch):
    import json
    from services.phone_intelligence import OpenTrustProvider

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"reported": False, "report_count": 0, "notice": "No reports."}).encode()

    monkeypatch.setattr("services.phone_intelligence.urlopen", lambda request, timeout: FakeResponse())
    result = OpenTrustProvider(api_key="test-secret").lookup("+919876543210")
    assert result.connected is True
    assert result.status == "no_reports"
    assert result.spam_label == "No reports found in OpenTrust"
    assert result.report_count == 0
