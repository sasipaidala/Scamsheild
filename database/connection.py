"""SQLite connection and versioned schema initialization."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA_VERSION = 6

MIGRATIONS: tuple[tuple[int, str], ...] = (
    (
        1,
        """
        CREATE TABLE IF NOT EXISTS app_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_app_settings_updated_at
            ON app_settings(updated_at);
        """,
    ),
    (
        2,
        """
        CREATE TABLE IF NOT EXISTS community_reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier_type TEXT NOT NULL CHECK (identifier_type IN ('Phone number', 'Email address', 'URL')),
            identifier_value TEXT NOT NULL,
            normalized_identifier TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending_review'
                CHECK (status IN ('pending_review', 'verified', 'rejected', 'duplicate')),
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_community_reports_identifier
            ON community_reports(identifier_type, normalized_identifier);
        CREATE INDEX IF NOT EXISTS idx_community_reports_status_created
            ON community_reports(status, created_at);
        """,
    ),
    (
        3,
        """
        CREATE TABLE IF NOT EXISTS threat_indicators (
            indicator_id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_type TEXT NOT NULL CHECK (indicator_type IN ('domain', 'ip', 'url', 'hash')),
            indicator_value TEXT NOT NULL,
            normalized_value TEXT NOT NULL,
            source_name TEXT NOT NULL,
            source_url TEXT NOT NULL DEFAULT '',
            threat_type TEXT NOT NULL DEFAULT 'Unspecified',
            confidence INTEGER CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 100)),
            first_seen TEXT NOT NULL DEFAULT '',
            last_seen TEXT NOT NULL DEFAULT '',
            expires_at TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            imported_at TEXT NOT NULL,
            UNIQUE(indicator_type, normalized_value, source_name)
        );
        CREATE INDEX IF NOT EXISTS idx_threat_indicators_lookup
            ON threat_indicators(indicator_type, normalized_value);
        CREATE INDEX IF NOT EXISTS idx_threat_indicators_source
            ON threat_indicators(source_name, imported_at);
        """,
    ),
    (
        4,
        """
        CREATE TABLE IF NOT EXISTS investigation_cases (
            case_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_ref TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Closed')),
            priority TEXT NOT NULL DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_cases_status_updated ON investigation_cases(status, updated_at);
        CREATE TABLE IF NOT EXISTS case_evidence (
            evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
            evidence_type TEXT NOT NULL CHECK (evidence_type IN ('Message', 'Email', 'URL', 'Domain', 'IP address', 'File hash')),
            evidence_value TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'User added',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_case_evidence_case ON case_evidence(case_id, created_at);
        CREATE TABLE IF NOT EXISTS case_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL REFERENCES investigation_cases(case_id) ON DELETE CASCADE,
            event_type TEXT NOT NULL CHECK (event_type IN ('created', 'status_changed', 'note', 'evidence_added')),
            details TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_case_events_case ON case_events(case_id, created_at);
        """,
    ),
    (
        5,
        """
        CREATE TABLE IF NOT EXISTS generated_reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_ref TEXT NOT NULL UNIQUE,
            case_ref TEXT NOT NULL,
            report_type TEXT NOT NULL,
            generated_at TEXT NOT NULL,
            payload_json TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_generated_reports_case_date
            ON generated_reports(case_ref, generated_at);
        """,
    ),
    (
        6,
        """
        CREATE TABLE IF NOT EXISTS awareness_progress (
            topic TEXT PRIMARY KEY,
            score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
            completed_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS support_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_ref TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            contact_email TEXT NOT NULL DEFAULT '',
            priority TEXT NOT NULL DEFAULT 'Normal' CHECK (priority IN ('Low', 'Normal', 'High')),
            status TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Resolved', 'Closed')),
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_support_tickets_created ON support_tickets(created_at);
        """,
    ),
)


def connect(database_path: str | Path) -> sqlite3.Connection:
    """Open a SQLite connection with safe defaults for local development."""
    raw_path = str(database_path)
    if raw_path != ":memory:":
        path = Path(raw_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        raw_path = str(path)

    connection = sqlite3.connect(raw_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    if raw_path != ":memory:":
        connection.execute("PRAGMA journal_mode = WAL")
    return connection


@contextmanager
def database_connection(database_path: str | Path) -> Iterator[sqlite3.Connection]:
    """Yield a connection and close it reliably."""
    connection = connect(database_path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database(database_path: str | Path) -> None:
    """Apply all unapplied migrations without deleting existing data."""
    with database_connection(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        current_row = connection.execute(
            "SELECT COALESCE(MAX(version), 0) AS version FROM schema_migrations"
        ).fetchone()
        current_version = int(current_row["version"])

        if current_version > SCHEMA_VERSION:
            raise RuntimeError(
                "Database schema is newer than this application version. "
                "Update the application before opening this database."
            )

        for version, migration_sql in MIGRATIONS:
            if version <= current_version:
                continue
            connection.executescript(migration_sql)
            connection.execute(
                "INSERT INTO schema_migrations(version) VALUES (?)", (version,)
            )
