"""Local email phishing-indicator analysis; no network calls or persistence."""
from __future__ import annotations

import re
from dataclasses import dataclass
from email import policy
from email.parser import Parser
from email.utils import parseaddr
from urllib.parse import urlsplit

from services.message_service import MAX_MESSAGE_LENGTH, analyze_message

MAX_EMAIL_FIELD_LENGTH = 5000
MAX_HEADERS_LENGTH = 20000
_URL_RE = re.compile(r"(?i)\b(?:https?://|www\.)[^\s<>()\[\]{}\"']+")
_EMAIL_RE = re.compile(r"^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$")


@dataclass(frozen=True, slots=True)
class EmailFinding:
    code: str
    title: str
    severity: str
    explanation: str


@dataclass(frozen=True, slots=True)
class EmailAnalysisResult:
    risk_level: str
    sender: str
    reply_to: str
    sender_reply_to_mismatch: bool
    urls: tuple[str, ...]
    findings: tuple[EmailFinding, ...]
    message_analysis: object
    authentication: dict[str, str]
    authentication_available: bool
    recommendations: tuple[str, ...]
    limitations: tuple[str, ...]


def _domain(address: str) -> str:
    _, parsed = parseaddr(address or "")
    if not parsed and "@" in address:
        parsed = address.strip()
    if not _EMAIL_RE.match(parsed):
        return ""
    return parsed.rsplit("@", 1)[1].lower().rstrip(".")


def _auth_results(raw_headers: str) -> tuple[dict[str, str], bool]:
    if not raw_headers.strip():
        return {}, False
    parsed = Parser(policy=policy.default).parsestr(raw_headers, headersonly=True)
    values = parsed.get_all("Authentication-Results", [])
    if not values:
        return {}, False
    # Only read explicit authserv-id results; never infer from missing fields.
    joined = " ".join(str(value) for value in values).lower()
    statuses: dict[str, str] = {}
    for mechanism in ("spf", "dkim", "dmarc"):
        match = re.search(rf"\b{mechanism}\s*=\s*(pass|fail|softfail|neutral|none|temperror|permerror)\b", joined)
        if match:
            statuses[mechanism.upper()] = match.group(1)
    return statuses, True


def analyze_email(
    sender_email: str,
    subject: str,
    body: str,
    reply_to: str = "",
    display_name: str = "",
    raw_headers: str = "",
) -> EmailAnalysisResult:
    """Analyze supplied email fields using local heuristics only.

    Raw authentication headers are user-supplied text and are not cryptographically
    verified by this function. A displayed pass/fail is therefore reported as
    header-claimed, not independently validated.
    """
    fields = {"Sender email": sender_email, "Subject": subject, "Email body": body,
              "Reply-To": reply_to, "Display name": display_name}
    for label, value in fields.items():
        if not isinstance(value, str):
            raise TypeError(f"{label} must be text.")
        if len(value) > MAX_EMAIL_FIELD_LENGTH:
            raise ValueError(f"{label} exceeds the {MAX_EMAIL_FIELD_LENGTH} character limit.")
    if not sender_email.strip() and not subject.strip() and not body.strip():
        raise ValueError("Enter at least a sender, subject or email body.")
    if len(raw_headers) > MAX_HEADERS_LENGTH:
        raise ValueError(f"Raw headers exceed {MAX_HEADERS_LENGTH} characters.")

    findings: list[EmailFinding] = []
    sender_domain = _domain(sender_email)
    reply_domain = _domain(reply_to)
    mismatch = bool(sender_domain and reply_domain and sender_domain != reply_domain)
    if sender_email.strip() and not sender_domain:
        findings.append(EmailFinding("invalid_sender", "Sender address format is unusual", "Review",
                                     "The sender field does not parse as a conventional email address. This may be a formatting issue, not proof of spoofing."))
    if reply_to.strip() and not reply_domain:
        findings.append(EmailFinding("invalid_reply_to", "Reply-To address format is unusual", "Review",
                                     "The Reply-To field does not parse as a conventional email address."))
    if mismatch:
        findings.append(EmailFinding("reply_to_mismatch", "Sender and Reply-To domains differ", "High attention",
                                     f"The visible sender domain is {sender_domain}, while replies are directed to {reply_domain}. This can be legitimate, but verify the relationship independently."))

    combined = f"{subject}\n{body}".strip()
    if len(combined) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Subject and email body combined exceed the {MAX_MESSAGE_LENGTH} character limit.")
    if display_name and sender_domain:
        name = display_name.lower().strip()
        domain_root = sender_domain.split(".")[0]
        if any(term in name for term in ("bank", "support", "security", "payroll", "microsoft", "google", "amazon")) and not any(term in domain_root for term in ("bank", "support", "security", "payroll", "microsoft", "google", "amazon")):
            findings.append(EmailFinding("display_name_domain", "Display name may not align with sender domain", "Review",
                                         "A recognizable organization-style display name is paired with a domain that does not visibly contain that organization name. Display names are easy to forge; this is only a prompt to verify."))

    message_result = analyze_message(combined if combined else "Email sender details supplied for review.", "Not sure")
    if message_result.risk_level in {"High", "Critical"}:
        findings.append(EmailFinding("body_high_risk", "Email content contains multiple high-concern message indicators", "High attention",
                                     "The subject/body triggered the existing message analyzer. Review its matched excerpts below."))
    elif message_result.findings:
        findings.append(EmailFinding("body_indicators", "Email content contains social-engineering indicators", "Review",
                                     "The subject/body triggered one or more local message rules. Review the supporting indicators below."))

    urls = tuple(dict.fromkeys(match.rstrip(".,;:!?)\"'") for match in _URL_RE.findall(combined)))
    if urls:
        findings.append(EmailFinding("urls_present", "Email contains embedded URL(s)", "Review",
                                     "The links were extracted for inspection but were not opened, resolved, or checked against a threat-intelligence provider."))

    authentication, auth_available = _auth_results(raw_headers)
    if auth_available and not authentication:
        findings.append(EmailFinding("auth_results_unparsed", "Authentication-Results header supplied, but no SPF/DKIM/DMARC status parsed", "Review",
                                     "The provided header did not contain a recognizable SPF, DKIM or DMARC result."))
    for mechanism, status in authentication.items():
        if status not in {"pass", "none"}:
            findings.append(EmailFinding(f"{mechanism.lower()}_{status}", f"Header reports {mechanism} {status}", "High attention" if status in {"fail", "permerror"} else "Review",
                                         "This status is copied from user-supplied Authentication-Results text and has not been independently verified."))

    if any(item.severity == "High attention" for item in findings):
        risk = "High attention"
    elif findings:
        risk = "Needs review"
    else:
        risk = "No configured indicators detected"

    recommendations = ["Do not reply, open links, download attachments or provide credentials until you verify the sender independently."]
    if mismatch:
        recommendations.append("Contact the organization using contact details from its official website, not the Reply-To address.")
    if urls:
        recommendations.append("Copy each URL into ScamShield's URL Analyzer; do not visit it just to test it.")
    if not auth_available:
        recommendations.append("SPF/DKIM/DMARC status is unavailable because no Authentication-Results header was supplied.")
    elif not authentication:
        recommendations.append("No SPF/DKIM/DMARC status could be extracted from the supplied headers; do not assume authentication passed.")
    recommendations.append("Preserve the original email, including full headers, if reporting is necessary.")

    limitations = (
        "This is local heuristic analysis, not a definitive phishing classifier or proof of sender identity.",
        "No DNS, MX, SPF, DKIM, DMARC, URL reputation, attachment or external threat-intelligence lookup is performed; embedded URLs are not opened.",
        "Authentication-Results values are copied from user-supplied headers and can be forged; they are not independently validated.",
        "A clean result does not prove an email or sender is safe. Legitimate services may use third-party sending and Reply-To domains.",
        "Submitted email content is analyzed in memory only and is not sent to external services or saved by this module.",
    )
    return EmailAnalysisResult(risk, sender_email.strip(), reply_to.strip(), mismatch, urls, tuple(findings),
                               message_result, authentication, auth_available, tuple(recommendations), limitations)
