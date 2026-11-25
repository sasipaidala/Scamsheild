import pytest
from database.connection import initialize_database
from services.learning_support import (
    TOPICS, create_support_ticket, get_awareness_progress,
    list_support_tickets, save_awareness_progress,
)


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "learning.db"
    initialize_database(path)
    return path


def test_all_awareness_topics_have_content_and_quiz():
    assert len(TOPICS) >= 5
    for topic in TOPICS.values():
        assert topic["content"]
        assert topic["quiz"]


def test_awareness_progress_persists_and_updates(db):
    save_awareness_progress(db, "Phishing and suspicious links", 100)
    save_awareness_progress(db, "Phishing and suspicious links", 0)
    progress = get_awareness_progress(db)
    assert progress["Phishing and suspicious links"]["score"] == 0


def test_awareness_rejects_invalid_topic_and_score(db):
    with pytest.raises(ValueError):
        save_awareness_progress(db, "unknown", 100)
    with pytest.raises(ValueError):
        save_awareness_progress(db, next(iter(TOPICS)), 101)


def test_support_ticket_is_persisted_without_exposing_description_in_list(db):
    ticket = create_support_ticket(db, "Bug or technical issue", "Page error", "The page failed to load", "user@example.com")
    assert ticket["status"] == "Open"
    rows = list_support_tickets(db)
    assert rows[0]["ticket_ref"] == ticket["ticket_ref"]
    assert "description" not in rows[0]


def test_support_ticket_validation(db):
    with pytest.raises(ValueError):
        create_support_ticket(db, "Other", "", "description")
    with pytest.raises(ValueError):
        create_support_ticket(db, "Other", "Subject", "Description", "not-an-email")
