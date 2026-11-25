"""Import-based threat intelligence with strict normalization and provenance.

No network requests are made. Indicators are only as trustworthy as their
stated source; importing a feed does not independently verify its claims.
"""
from __future__ import annotations

import csv
import hashlib
import ipaddress
import io
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from database.connection import database_connection

MAX_FEED_BYTES = 5 * 1024 * 1024
MAX_FEED_ROWS = 50_000
MAX_INDICATOR_LENGTH = 2048
INDICATOR_TYPES = ("domain", "ip", "url", "hash")
HASH_LENGTHS = {32: "MD5", 40: "SHA-1", 64: "SHA-256", 128: "SHA-512"}


@dataclass(frozen=True, slots=True)
class ImportSummary:
    inserted: int
    updated: int
    skipped: int
    errors: tuple[str, ...]


def normalize_indicator(indicator_type: str, value: str) -> str:
    if indicator_type not in INDICATOR_TYPES:
        raise ValueError("Indicator type must be domain, ip, url, or hash.")
    if not isinstance(value, str):
        raise TypeError("Indicator must be text.")
    raw = value.strip()
    if not raw or len(raw) > MAX_INDICATOR_LENGTH:
        raise ValueError("Indicator is empty or exceeds the length limit.")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in raw):
        raise ValueError("Indicator contains control characters.")

    if indicator_type == "ip":
        try:
            return str(ipaddress.ip_address(raw))
        except ValueError as exc:
            raise ValueError("Enter a valid IPv4 or IPv6 address.") from exc

    if indicator_type == "hash":
        compact = raw.lower()
        if not re.fullmatch(r"[0-9a-f]+", compact) or len(compact) not in HASH_LENGTHS:
            raise ValueError("Hash must be a 32, 40, 64, or 128 character hexadecimal digest.")
        return compact

    if indicator_type == "url":
        candidate = raw if re.match(r"(?i)^https?://", raw) else "https://" + raw
        try:
            parts = urlsplit(candidate)
            _ = parts.port
            host = parts.hostname
        except ValueError as exc:
            raise ValueError("Enter a valid HTTP or HTTPS URL.") from exc
        if parts.scheme.lower() not in {"http", "https"} or not host or parts.username is not None or parts.password is not None:
            raise ValueError("Only HTTP(S) URLs with a valid hostname and no embedded credentials are accepted.")
        if any(ch.isspace() for ch in raw):
            raise ValueError("URL cannot contain spaces.")
        normalized_host = _normalize_domain(host)
        port = parts.port
        netloc = normalized_host if port is None else f"{normalized_host}:{port}"
        return urlunsplit((parts.scheme.lower(), netloc, parts.path or "/", parts.query, ""))

    return _normalize_domain(raw)


def _normalize_domain(value: str) -> str:
    candidate = value.strip().rstrip(".").lower()
    if not candidate or "/" in candidate or "@" in candidate or any(ch.isspace() for ch in candidate):
        raise ValueError("Enter a valid domain name without a path or credentials.")
    try:
        candidate = candidate.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError("Domain name could not be normalized.") from exc
    if len(candidate) > 253 or "." not in candidate:
        raise ValueError("Enter a fully qualified domain name.")
    labels = candidate.split(".")
    if any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label) for label in labels):
        raise ValueError("Domain contains an invalid label.")
    return candidate


def import_csv(database_path: str | Path, csv_bytes: bytes, source_name: str,
               source_url: str = "") -> ImportSummary:
    if not isinstance(csv_bytes, bytes):
        raise TypeError("Feed content must be bytes.")
    if len(csv_bytes) > MAX_FEED_BYTES:
        raise ValueError("Feed exceeds the 5 MB import limit.")
    source_name = source_name.strip() if isinstance(source_name, str) else ""
    if not source_name or len(source_name) > 120:
        raise ValueError("Enter a source name (maximum 120 characters).")
    source_url = source_url.strip() if isinstance(source_url, str) else ""
    if len(source_url) > 500 or any(ord(ch) < 32 for ch in source_url):
        raise ValueError("Source URL is invalid or too long.")
    try:
        text = csv_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded.") from exc
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV must include a header row.")
    fields = {name.strip().lower() for name in reader.fieldnames if name}
    if "indicator" not in fields or not ({"type", "indicator_type"} & fields):
        raise ValueError("CSV requires 'indicator' and 'type' (or 'indicator_type') columns.")

    inserted = updated = skipped = 0
    errors: list[str] = []
    now = datetime.now(timezone.utc).isoformat()
    with database_connection(database_path) as connection:
        for row_number, row in enumerate(reader, start=2):
            if row_number - 1 > MAX_FEED_ROWS:
                raise ValueError(f"Feed exceeds the {MAX_FEED_ROWS:,} row limit.")
            normalized_row = {(key or "").strip().lower(): (value or "").strip() for key, value in row.items()}
            kind = normalized_row.get("type") or normalized_row.get("indicator_type") or ""
            indicator = normalized_row.get("indicator", "")
            try:
                normalized = normalize_indicator(kind.lower(), indicator)
                confidence_raw = normalized_row.get("confidence", "")
                confidence = int(confidence_raw) if confidence_raw else None
                if confidence is not None and not 0 <= confidence <= 100:
                    raise ValueError("confidence must be between 0 and 100")
                values = (
                    kind.lower(), indicator, normalized, source_name, source_url,
                    normalized_row.get("threat_type") or normalized_row.get("threat type") or "Unspecified",
                    confidence, normalized_row.get("first_seen", ""),
                    normalized_row.get("last_seen", ""), normalized_row.get("expires_at", ""),
                    normalized_row.get("description", ""), now,
                )
                existing = connection.execute(
                    "SELECT indicator_id FROM threat_indicators WHERE indicator_type=? AND normalized_value=? AND source_name=?",
                    (kind.lower(), normalized, source_name),
                ).fetchone()
                connection.execute(
                    """INSERT INTO threat_indicators
                    (indicator_type, indicator_value, normalized_value, source_name, source_url,
                     threat_type, confidence, first_seen, last_seen, expires_at, description, imported_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(indicator_type, normalized_value, source_name) DO UPDATE SET
                    indicator_value=excluded.indicator_value, source_url=excluded.source_url,
                    threat_type=excluded.threat_type, confidence=excluded.confidence,
                    first_seen=excluded.first_seen, last_seen=excluded.last_seen,
                    expires_at=excluded.expires_at, description=excluded.description,
                    imported_at=excluded.imported_at""",
                    values,
                )
                if existing:
                    updated += 1
                else:
                    inserted += 1
            except (ValueError, TypeError) as exc:
                skipped += 1
                if len(errors) < 20:
                    errors.append(f"Row {row_number}: {exc}")
    return ImportSummary(inserted, updated, skipped, tuple(errors))


def lookup_indicator(database_path: str | Path, indicator_type: str, value: str) -> tuple[dict, ...]:
    normalized = normalize_indicator(indicator_type, value)
    with database_connection(database_path) as connection:
        rows = connection.execute(
            """SELECT indicator_type, indicator_value, source_name, source_url, threat_type,
            confidence, first_seen, last_seen, expires_at, description, imported_at
            FROM threat_indicators WHERE indicator_type=? AND normalized_value=?
            ORDER BY confidence DESC, imported_at DESC""",
            (indicator_type, normalized),
        ).fetchall()
    return tuple(dict(row) for row in rows)


def list_indicators(database_path: str | Path, limit: int = 500) -> tuple[dict, ...]:
    safe_limit = max(1, min(int(limit), 2000))
    with database_connection(database_path) as connection:
        rows = connection.execute(
            """SELECT indicator_type, indicator_value, source_name, threat_type,
            confidence, first_seen, last_seen, expires_at, imported_at
            FROM threat_indicators ORDER BY imported_at DESC LIMIT ?""", (safe_limit,)
        ).fetchall()
    return tuple(dict(row) for row in rows)


def indicator_count(database_path: str | Path) -> int:
    with database_connection(database_path) as connection:
        return int(connection.execute("SELECT COUNT(*) FROM threat_indicators").fetchone()[0])
