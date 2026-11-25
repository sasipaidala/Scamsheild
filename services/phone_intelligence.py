"""Phone reputation lookups using ScamShield reports and optional licensed providers.

No external provider is queried unless an explicit adapter is configured. Pending
community reports are allegations and are never represented as verified findings.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from database.connection import database_connection
from services.community_reports import normalize_identifier


@dataclass(frozen=True, slots=True)
class CommunityPhoneSummary:
    total_submissions: int
    pending_review: int
    verified: int
    rejected: int
    duplicate: int
    categories: tuple[tuple[str, int], ...]
    latest_report_at: str | None


@dataclass(frozen=True, slots=True)
class ProviderResult:
    provider_name: str
    connected: bool
    status: str
    spam_label: str | None = None
    report_count: int | None = None
    explanation: str | None = None


class PhoneReputationProvider(Protocol):
    def lookup(self, e164_number: str) -> ProviderResult: ...


class UnconfiguredProvider:
    """Safe default: no network call and no fabricated provider result."""

    def lookup(self, e164_number: str) -> ProviderResult:
        return ProviderResult(
            provider_name="External intelligence",
            connected=False,
            status="not_configured",
            explanation="No authorized phone-reputation provider is configured.",
        )


class OpenTrustProvider:
    """OpenTrust India merchant-community lookup using privacy-preserving hashes.

    OpenTrust requires an approved merchant account and an API key. The API
    returns merchant-submitted observations, not independently proven fraud.
    """

    endpoint = "https://opentrust.in/api/v1/lookups"

    def __init__(self, api_key: str | None = None, timeout: float = 8.0):
        self.api_key = (api_key if api_key is not None else os.getenv("OPENTRUST_API_KEY", "")).strip()
        self.timeout = timeout

    def lookup(self, e164_number: str) -> ProviderResult:
        if not self.api_key:
            return ProviderResult(
                provider_name="OpenTrust", connected=False, status="not_configured",
                explanation="OpenTrust API key is missing. Configure OPENTRUST_API_KEY after your account is approved.",
            )

        # OpenTrust's documented Indian-number hash format is SHA-256 of +91XXXXXXXXXX.
        digest = hashlib.sha256(e164_number.encode("utf-8")).hexdigest()
        payload = json.dumps({"phone_sha256": digest, "phone_length": len(e164_number)}).encode("utf-8")
        request = Request(
            self.endpoint, data=payload, method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ScamShield/0.3",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code in (401, 403):
                detail = "OpenTrust rejected the API key or account access. Check approval and credentials."
            elif exc.code == 429:
                detail = "OpenTrust rate limit reached. Try again later."
            elif exc.code == 402:
                detail = "OpenTrust lookup allowance is exhausted or unavailable."
            else:
                detail = f"OpenTrust returned HTTP {exc.code}."
            return ProviderResult("OpenTrust", False, "provider_error", explanation=detail)
        except (URLError, TimeoutError, OSError):
            return ProviderResult("OpenTrust", False, "unavailable", explanation="OpenTrust could not be reached. No external verdict was produced.")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return ProviderResult("OpenTrust", False, "invalid_response", explanation="OpenTrust returned an unreadable response.")

        try:
            count = int(data.get("report_count", 0))
            reported = bool(data.get("reported", count > 0))
        except (AttributeError, TypeError, ValueError):
            return ProviderResult("OpenTrust", False, "invalid_response", explanation="OpenTrust response did not contain the expected reputation fields.")

        notice = str(data.get("notice") or "Reports are unverified merchant observations, not proof of fraud.")
        return ProviderResult(
            provider_name="OpenTrust", connected=True,
            status="reported" if reported or count > 0 else "no_reports",
            spam_label="Community reports found" if reported or count > 0 else "No reports found in OpenTrust",
            report_count=count, explanation=notice,
        )


def lookup_community_phone(database_path: str | Path, phone_number: str) -> CommunityPhoneSummary:
    normalized = normalize_identifier("Phone number", phone_number)
    with database_connection(database_path) as connection:
        rows = connection.execute(
            """SELECT status, category, COUNT(*) AS amount, MAX(created_at) AS latest
               FROM community_reports
               WHERE identifier_type = 'Phone number' AND normalized_identifier = ?
               GROUP BY status, category""",
            (normalized,),
        ).fetchall()

    status_counts = {key: 0 for key in ("pending_review", "verified", "rejected", "duplicate")}
    categories: dict[str, int] = {}
    latest: str | None = None
    total = 0
    for row in rows:
        status = str(row["status"])
        amount = int(row["amount"])
        status_counts[status] = status_counts.get(status, 0) + amount
        total += amount
        if status in {"pending_review", "verified"}:
            categories[str(row["category"])] = categories.get(str(row["category"]), 0) + amount
        value = row["latest"]
        if value and (latest is None or value > latest):
            latest = str(value)

    return CommunityPhoneSummary(
        total_submissions=total,
        pending_review=status_counts["pending_review"],
        verified=status_counts["verified"],
        rejected=status_counts["rejected"],
        duplicate=status_counts["duplicate"],
        categories=tuple(sorted(categories.items(), key=lambda item: (-item[1], item[0]))),
        latest_report_at=latest,
    )


def lookup_phone(database_path: str | Path, phone_number: str,
                 provider: PhoneReputationProvider | None = None) -> tuple[str, CommunityPhoneSummary, ProviderResult]:
    normalized = normalize_identifier("Phone number", phone_number)
    community = lookup_community_phone(database_path, normalized)
    external = (provider or OpenTrustProvider()).lookup(normalized)
    return normalized, community, external
