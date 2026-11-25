"""Privacy-conscious intake for user-submitted community scam reports.

Submissions are unverified allegations. This module stores them as pending review
and never exposes them as confirmed fraud intelligence.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from database.connection import database_connection

MAX_DESCRIPTION_LENGTH = 2000
MAX_IDENTIFIER_LENGTH = 2048
REPORT_CATEGORIES = (
    "Phishing",
    "Financial fraud",
    "Fake job offer",
    "OTP or credential theft",
    "Impersonation",
    "Investment scam",
    "Lottery or prize scam",
    "Spam marketing",
    "Other",
)


@dataclass(frozen=True, slots=True)
class ReportReceipt:
    report_id: int
    status: str
    created_at: str


def normalize_identifier(identifier_type: str, value: str) -> str:
    if identifier_type not in {"Phone number", "Email address", "URL"}:
        raise ValueError("Choose a supported report type.")
    if not isinstance(value, str):
        raise TypeError("Enter the identifier as text.")
    value = value.strip()
    if not value:
        raise ValueError("Enter the phone number, email address, or URL.")
    if len(value) > MAX_IDENTIFIER_LENGTH:
        raise ValueError("The identifier is too long.")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError("The identifier contains unsupported control characters.")

    if identifier_type == "Phone number":
        compact = re.sub(r"[\s().-]", "", value)
        if not re.fullmatch(r"\+?[0-9]{7,15}", compact):
            raise ValueError("Enter a phone number with 7–15 digits, optionally starting with + and country code.")
        return compact

    if identifier_type == "Email address":
        if value.count("@") != 1 or len(value) > 254:
            raise ValueError("Enter a valid email address.")
        local, domain = value.rsplit("@", 1)
        if (not local or len(local) > 64 or not domain or "." not in domain
                or domain.startswith(".") or domain.endswith(".")
                or any(ch.isspace() for ch in value)):
            raise ValueError("Enter a valid email address.")
        return value.casefold()

    explicit_scheme = re.match(r"^([A-Za-z][A-Za-z0-9+.-]*):", value)
    if explicit_scheme and explicit_scheme.group(1).lower() not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs can be reported.")
    candidate = value if re.match(r"(?i)^https?://", value) else "https://" + value
    try:
        parts = urlsplit(candidate)
        _ = parts.port
    except ValueError as exc:
        raise ValueError("Enter a valid HTTP or HTTPS URL or domain.") from exc
    if parts.scheme not in {"http", "https"} or not parts.hostname or any(ch.isspace() for ch in value):
        raise ValueError("Enter a valid HTTP or HTTPS URL or domain.")
    if parts.username is not None or parts.password is not None:
        # Keep the original evidence, but don't silently interpret credentials as a host.
        pass
    return candidate.rstrip("/").casefold()


def submit_report(database_path: str | Path, identifier_type: str, identifier: str,
                  category: str, description: str) -> ReportReceipt:
    normalized = normalize_identifier(identifier_type, identifier)
    if category not in REPORT_CATEGORIES:
        raise ValueError("Choose a valid report category.")
    if not isinstance(description, str):
        raise TypeError("Enter a description as text.")
    description = description.strip()
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise ValueError(f"Description must be {MAX_DESCRIPTION_LENGTH} characters or fewer.")
    if len(description) < 10:
        raise ValueError("Add at least 10 characters describing what happened.")

    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with database_connection(database_path) as connection:
        cursor = connection.execute(
            """INSERT INTO community_reports
               (identifier_type, identifier_value, normalized_identifier, category,
                description, status, created_at)
               VALUES (?, ?, ?, ?, ?, 'pending_review', ?)""",
            (identifier_type, identifier.strip(), normalized, category, description, created_at),
        )
        report_id = int(cursor.lastrowid)
    return ReportReceipt(report_id=report_id, status="pending_review", created_at=created_at)
