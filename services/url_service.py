"""Passive URL structure analysis. This module never performs network requests."""

from __future__ import annotations

import ipaddress
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from urllib.parse import unquote, urlsplit

MAX_URL_LENGTH = 2048
RULESET_VERSION = "url-structure-0.1.0"
_SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "ow.ly", "buff.ly", "cutt.ly", "rb.gy"}


@dataclass(frozen=True)
class UrlFinding:
    rule_id: str
    title: str
    severity: str
    explanation: str


@dataclass(frozen=True)
class UrlAnalysis:
    submitted_url: str
    normalized_url: str
    hostname: str
    scheme: str
    findings: tuple[UrlFinding, ...]
    observations: tuple[str, ...]
    analyzed_at: str
    ruleset_version: str
    limitations: tuple[str, ...]

    def to_dict(self) -> dict:
        result = asdict(self)
        result["findings"] = [asdict(item) for item in self.findings]
        return result


def analyze_url(value: str) -> UrlAnalysis:
    """Inspect URL syntax locally; never resolve DNS, open, or fetch the URL."""
    if not isinstance(value, str):
        raise TypeError("Enter a URL as text.")
    submitted = value.strip()
    if not submitted:
        raise ValueError("Enter a URL to analyze.")
    if len(submitted) > MAX_URL_LENGTH:
        raise ValueError(f"The URL exceeds the {MAX_URL_LENGTH} character limit.")
    if any(ord(char) < 32 or ord(char) == 127 for char in submitted):
        raise ValueError("The URL contains control characters. Remove them and try again.")
    explicit_scheme = re.match(r"^([A-Za-z][A-Za-z0-9+.-]*):", submitted)
    if explicit_scheme and explicit_scheme.group(1).lower() not in {"http", "https"}:
        # A host:port value is not a URI scheme; reject other explicit schemes.
        remainder = submitted[len(explicit_scheme.group(0)):]
        if not remainder.isdigit() and not remainder.startswith("/"):
            raise ValueError("Only HTTP and HTTPS URLs can be analyzed.")
    candidate = submitted if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", submitted) else "https://" + submitted
    try:
        parts = urlsplit(candidate)
        scheme = parts.scheme.lower()
        hostname = parts.hostname or ""
        port = parts.port
    except ValueError as exc:
        raise ValueError("The URL has an invalid host or port format.") from exc
    if scheme not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs can be analyzed.")
    if not hostname:
        raise ValueError("Enter a URL with a valid hostname, such as example.com.")
    if any(char.isspace() for char in submitted):
        raise ValueError("The URL contains spaces. Check the copied address before analyzing it.")

    host_ascii = hostname.rstrip(".").lower()
    try:
        host_ascii = host_ascii.encode("idna").decode("ascii")
    except UnicodeError:
        host_ascii = hostname.lower()

    findings: list[UrlFinding] = []
    observations: list[str] = []

    if parts.username is not None or parts.password is not None:
        findings.append(UrlFinding("userinfo_present", "Credentials embedded before the hostname", "High attention", "The URL contains user-information syntax before the host. This can make the actual destination less obvious; verify the hostname carefully."))
    try:
        ipaddress.ip_address(host_ascii.strip("[]"))
        findings.append(UrlFinding("ip_literal_host", "IP address used as the host", "Review", "The destination is written as an IP address rather than a domain name. This is not inherently malicious, but it deserves context checking."))
    except ValueError:
        pass
    if host_ascii.startswith("xn--") or ".xn--" in host_ascii:
        findings.append(UrlFinding("idn_punycode", "Internationalized domain encoding present", "Review", "The hostname contains punycode. Internationalized domains can be legitimate, but visually similar characters can also be abused."))
    if host_ascii in _SHORTENERS:
        findings.append(UrlFinding("shortener_domain", "Known URL-shortener domain", "Review", "This hostname is commonly used to shorten links. The final destination has not been resolved or checked."))
    if len(host_ascii) > 60:
        findings.append(UrlFinding("long_hostname", "Unusually long hostname", "Review", "The hostname is unusually long. Length alone does not establish malicious intent."))
    if host_ascii.count(".") >= 4:
        findings.append(UrlFinding("many_subdomains", "Multiple hostname labels", "Review", "The hostname has several dot-separated labels. Check the registrable domain; attackers can place brand-like words in subdomains."))
    if port is not None and port not in {80, 443}:
        findings.append(UrlFinding("nonstandard_port", "Non-standard web port", "Review", f"The URL specifies port {port}. Non-standard ports can be legitimate, but should be expected for the service."))
    if re.search(r"%[0-9a-fA-F]{2}", parts.path + parts.query + parts.fragment):
        observations.append("percent_encoding_present")
    decoded = unquote(parts.path + "?" + parts.query + "#" + parts.fragment)
    if decoded != parts.path + "?" + parts.query + "#" + parts.fragment:
        observations.append("percent_encoded_content_present")
    if "@" in submitted:
        observations.append("at_symbol_present_in_input")
    if scheme == "http":
        findings.append(UrlFinding("unencrypted_http", "HTTP rather than HTTPS", "Review", "The URL uses HTTP, so transport encryption is not indicated by the URL. Some legitimate sites still use HTTP; do not enter sensitive information."))
    if not findings:
        observations.append("no_configured_structural_indicators")

    display_url = f"{scheme}://{host_ascii}"
    if port is not None:
        display_url += f":{port}"
    display_url += parts.path or "/"
    if parts.query:
        display_url += "?" + parts.query
    if parts.fragment:
        display_url += "#" + parts.fragment

    return UrlAnalysis(
        submitted_url=submitted,
        normalized_url=display_url,
        hostname=host_ascii,
        scheme=scheme,
        findings=tuple(findings),
        observations=tuple(observations),
        analyzed_at=datetime.now(timezone.utc).isoformat(),
        ruleset_version=RULESET_VERSION,
        limitations=(
            "This is passive URL-structure analysis only; the URL was not opened, fetched, resolved, or checked against reputation feeds.",
            "Findings are review indicators, not a verdict or probability. A URL with no findings is not proven safe.",
            "Redirect destinations, DNS records, page content, certificate state, domain age, and current threat intelligence were not checked.",
        ),
    )
