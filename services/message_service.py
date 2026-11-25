"""Local, explainable message scam-indicator analysis.

This module performs no network requests, does not call an AI provider, and does
not persist submitted content. Rules are heuristics, not a calibrated fraud
probability or a definitive determination that a sender is malicious.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Pattern

MAX_MESSAGE_LENGTH = 5000
RULESET_VERSION = "message-rules-0.1.0"
SUPPORTED_LANGUAGE_LABELS = {"English", "Telugu", "Hindi", "Not sure"}


@dataclass(frozen=True, slots=True)
class _Rule:
    rule_id: str
    title: str
    category: str
    severity: str
    weight: int
    explanation: str
    patterns: tuple[Pattern[str], ...]


def _patterns(*expressions: str) -> tuple[Pattern[str], ...]:
    return tuple(re.compile(expression, re.IGNORECASE | re.UNICODE) for expression in expressions)


_RULES: tuple[_Rule, ...] = (
    _Rule(
        rule_id="credential_request",
        title="Request for an OTP, password or security code",
        category="Credential harvesting",
        severity="High-severity indicator",
        weight=50,
        explanation=(
            "The message appears to ask the recipient to disclose or enter a sensitive "
            "authentication secret. Legitimate organizations should not ask a person "
            "to disclose an OTP, password, PIN or CVV in a message reply."
        ),
        patterns=_patterns(
            r"\b(?:share|send|provide|tell|reveal|forward|reply\s+with|enter|type)\s+(?:(?:me|us)\s+)?(?:your\s+)?(?:otp|one[- ]time\s+password|verification\s+code|passcode|password|upi\s+pin|pin|cvv)\b",
            r"\b(?:we\s+need|need|asking\s+for|requesting)\s+(?:your\s+)?(?:otp|one[- ]time\s+password|verification\s+code|passcode|password|upi\s+pin|cvv)\b",
            r"(?:ओटीपी|एक\s*बार\s*का\s*पासवर्ड|पासवर्ड|सत्यापन\s*कोड).{0,24}(?:भेजें|बताएं|बताइए|साझा\s*करें|दें|लिखें)",
            r"(?:ఓటీపీ|ఓటిపి|otp|పాస్‌వర్డ్|పాస్వర్డ్|ధృవీకరణ\s*కోడ్).{0,28}(?:పంపండి|చెప్పండి|షేర్\s*చేయండి|తెలియజేయండి|ఇవ్వండి)",
        ),
    ),
    _Rule(
        rule_id="advance_fee",
        title="Advance or registration fee requested",
        category="Advance-fee request",
        severity="High indicator",
        weight=34,
        explanation=(
            "The message connects a payment with registration, processing, training, "
            "interview, security or joining. An upfront fee request deserves independent "
            "verification, especially when linked to a job, prize or account benefit."
        ),
        patterns=_patterns(
            r"(?:pay|send|transfer|deposit|submit).{0,55}(?:registration|processing|application|security|training|interview|joining|verification|refundable)\s+(?:fee|charge|deposit|amount)",
            r"(?:registration|processing|application|security|training|interview|joining)\s+(?:fee|charge|deposit).{0,45}(?:required|must\s+be\s+paid|pay\s+now|before|to\s+(?:proceed|confirm|secure))",
            r"(?:upfront|advance)\s+(?:payment|fee|deposit).{0,35}(?:job|work|offer|registration|selection|application)?",
            r"(?:नौकरी|जॉब|भर्ती|रजिस्ट्रेशन|पंजीकरण|प्रोसेसिंग|सुरक्षा|ट्रेनिंग).{0,28}(?:फीस|शुल्क).{0,35}(?:जमा\s*करें|भुगतान\s*करें|पहले|देना\s*होगा)",
            r"(?:ఉద్యోగం|జాబ్|నమోదు|రిజిస్ట్రేషన్|ప్రాసెసింగ్|సెక్యూరిటీ|ట్రైనింగ్).{0,28}(?:ఫీజు|రుసుము).{0,35}(?:చెల్లించండి|ముందుగా|చెల్లించాలి)",
        ),
    ),
    _Rule(
        rule_id="account_threat",
        title="Account restriction or KYC pressure",
        category="Account pressure / possible impersonation",
        severity="Moderate indicator",
        weight=22,
        explanation=(
            "The message uses an account, card, wallet or KYC restriction/update claim. "
            "Such notices can be legitimate or fraudulent; verify by opening the official "
            "app or website yourself rather than using a message link."
        ),
        patterns=_patterns(
            r"(?:bank|account|wallet|upi|card|kyc).{0,55}(?:blocked|suspended|deactivated|frozen|will\s+be\s+closed|verify|update\s+kyc)",
            r"(?:blocked|suspended|deactivated|frozen|will\s+be\s+closed).{0,55}(?:bank|account|wallet|upi|card|kyc)",
            r"(?:खाता|बैंक\s*खाता|कार्ड|वॉलेट|केवाईसी).{0,45}(?:बंद|ब्लॉक|निलंबित|अपडेट|सत्यापित)",
            r"(?:ఖాతా|బ్యాంక్\s*ఖాతా|కార్డ్|వాలెట్|కేవైసీ|kyc).{0,45}(?:బ్లాక్|నిలిపి|మూసి|అప్‌డేట్|ధృవీకరించ)",
        ),
    ),
    _Rule(
        rule_id="payment_request",
        title="Direct request to transfer or release money",
        category="Payment request",
        severity="High indicator",
        weight=22,
        explanation=(
            "The message asks for money to be transferred, paid or released. A payment "
            "request is not proof of fraud, but unexpected requests should be verified "
            "through a separately obtained, trusted contact channel."
        ),
        patterns=_patterns(
            r"\b(?:pay\s+now|send\s+(?:the\s+)?money|transfer\s+(?:the\s+)?(?:money|amount)|scan\s+(?:the\s+)?qr\s+(?:code\s+)?to\s+pay|pay\s+to\s+claim|pay\s+to\s+release)\b",
            r"\b(?:upi\s+id|payment\s+qr).{0,35}(?:pay|transfer|send|deposit)\b",
            r"(?:पैसे|राशि|भुगतान).{0,30}(?:भेजें|ट्रांसफर|जमा|अभी\s*करें)",
            r"(?:డబ్బు|మొత్తం|చెల్లింపు).{0,30}(?:పంపండి|ట్రాన్స్‌ఫర్|జమ|ఇప్పుడే\s*చెల్లించండి)",
        ),
    ),
    _Rule(
        rule_id="unrealistic_offer",
        title="Unusually attractive job or financial promise",
        category="Employment or investment promise",
        severity="Moderate indicator",
        weight=20,
        explanation=(
            "The message combines an unusually attractive earning, job or return promise. "
            "Check the organization, role, terms and compensation through independently "
            "verified channels."
        ),
        patterns=_patterns(
            r"\b(?:double\s+(?:your\s+)?money|100\s*%\s*(?:guaranteed\s+)?returns?|guaranteed\s+(?:profit|income|returns?)|risk[- ]free\s+(?:profit|investment)|earn\s+[₹$€]?\s*\d[\d,.]*\s*(?:per|a)\s*day|\bno\s+experience\b.{0,45}\b(?:high\s+salary|earn|salary)\b)",
            r"\b(?:work\s+from\s+home|part[- ]time\s+job|remote\s+job).{0,70}(?:earn|salary|income|per\s+day|daily\s+profit|no\s+experience)",
            r"(?:घर\s*बैठे\s*कमाएं|रोज़ाना\s*कमाएं|गारंटीड\s*रिटर्न|पैसा\s*दोगुना)",
            r"(?:ఇంటి\s*నుంచి\s*పని|రోజుకు\s*సంపాదించండి|గ్యారంటీ\s*లాభం|డబ్బు\s*రెట్టింపు)",
        ),
    ),
    _Rule(
        rule_id="job_offer",
        title="Unsolicited job or recruitment approach",
        category="Employment approach",
        severity="Low indicator",
        weight=12,
        explanation=(
            "The message contains a recruitment or job-selection approach. This is only "
            "context; legitimate recruiters also use these terms. It becomes more concerning "
            "when combined with upfront fees, unrealistic promises or sensitive-data requests."
        ),
        patterns=_patterns(
            r"\b(?:job\s+offer|you\s+(?:have\s+been\s+)?selected\s+for\s+(?:the\s+)?job|job\s+vacancy|hiring\s+now|recruitment\s+team|work\s+from\s+home\s+job|part[- ]time\s+job)\b",
            r"(?:नौकरी\s*का\s*ऑफर|आपका\s*चयन|भर्ती\s*चल\s*रही|वर्क\s*फ्रॉम\s*होम)",
            r"(?:ఉద్యోగ\s*ఆఫర్|మీరు\s*ఎంపికయ్యారు|రిక్రూట్‌మెంట్|వర్క్\s*ఫ్రమ్\s*హోమ్)",
        ),
    ),
    _Rule(
        rule_id="urgency_pressure",
        title="Urgency or threat of immediate consequences",
        category="Urgency / coercive pressure",
        severity="Low indicator",
        weight=10,
        explanation=(
            "The message pressures the recipient to act quickly or threatens a consequence. "
            "Urgency alone is common in legitimate notices and is not enough to establish fraud."
        ),
        patterns=_patterns(
            r"\b(?:act\s+now|immediately|urgent(?:ly)?|today\s+only|final\s+warning|last\s+chance|within\s+\d+\s*(?:minutes?|hours?)|else\s+your\s+account|before\s+it\s+expires)\b",
            r"(?:तुरंत|अभी\s*करें|आज\s*ही|अंतिम\s*चेतावनी|जल्दी\s*करें|खाता\s*बंद\s*हो जाएगा)",
            r"(?:వెంటనే|ఇప్పుడే|ఈరోజే|చివరి\s*హెచ్చరిక|త్వరగా\s*చేయండి|ఖాతా\s*మూసివేయబడుతుంది)",
        ),
    ),
    _Rule(
        rule_id="off_platform_migration",
        title="Request to move the conversation to another channel",
        category="Off-platform contact request",
        severity="Low indicator",
        weight=8,
        explanation=(
            "The sender asks the recipient to continue on a separate messaging platform. "
            "This can be normal, but it can also reduce visibility and make verification harder."
        ),
        patterns=_patterns(
            r"\b(?:contact|message|chat|call|join|continue)\s+(?:me|us)?\s*(?:on|via|through)\s+(?:whats\s*app|whatsapp|telegram|signal)\b",
            r"\b(?:move|shift|continue)\s+(?:this|the\s+conversation|our\s+chat)\s+to\s+(?:whats\s*app|whatsapp|telegram)\b",
        ),
    ),
)

_URL_PATTERN = re.compile(r"(?i)\b(?:https?://|www\.)[^\s<>()\[\]{}]+")
_PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d[\d .()\-]{7,}\d)(?!\w)")
_PROTECTIVE_PREFIX = re.compile(
    r"(?:\bnever\b|\bdon['’]?t\b|\bdo\s+not\b|\bshould\s+not\b|\bmust\s+not\b|\bavoid\b|कभी\s*भी\s*न|नहीं\s*करें|చేయవద్దు|చేయకండి)\W*(?:[\w’'-]+\W*){0,5}$",
    re.IGNORECASE | re.UNICODE,
)


@dataclass(frozen=True, slots=True)
class MessageFinding:
    rule_id: str
    title: str
    category: str
    severity: str
    weight: int
    excerpt: str
    explanation: str


@dataclass(frozen=True, slots=True)
class MessageAnalysisResult:
    assessment: str
    risk_level: str
    indicator_score: int | None
    indicator_breadth: str
    primary_category: str
    findings: tuple[MessageFinding, ...]
    observations: tuple[str, ...]
    recommendations: tuple[str, ...]
    limitations: tuple[str, ...]
    language_selected: str
    ruleset_version: str
    analyzed_at: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation of the analysis result."""
        return asdict(self)


def _normalize_message(message: str) -> str:
    normalized = unicodedata.normalize("NFKC", message)
    normalized = re.sub(r"[\u200b-\u200f\ufeff]", "", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _is_protective_context(text: str, start: int) -> bool:
    sentence_start = max(
        text.rfind(".", 0, start),
        text.rfind("!", 0, start),
        text.rfind("?", 0, start),
        text.rfind(";", 0, start),
        text.rfind("\n", 0, start),
    ) + 1
    prefix = text[sentence_start:start].strip()
    return bool(_PROTECTIVE_PREFIX.search(prefix))


def _match_rule(rule: _Rule, text: str) -> MessageFinding | None:
    for pattern in rule.patterns:
        match = pattern.search(text)
        if match is None:
            continue
        if _is_protective_context(text, match.start()):
            continue
        excerpt = match.group(0).strip()
        if len(excerpt) > 180:
            excerpt = excerpt[:177].rstrip() + "..."
        return MessageFinding(
            rule_id=rule.rule_id,
            title=rule.title,
            category=rule.category,
            severity=rule.severity,
            weight=rule.weight,
            excerpt=excerpt,
            explanation=rule.explanation,
        )
    return None


def _risk_assessment(findings: tuple[MessageFinding, ...], text_length: int) -> tuple[str, str, int | None, str]:
    if not findings:
        if text_length < 20:
            return (
                "Insufficient evidence",
                "Insufficient evidence",
                None,
                "The submitted content is too short to assess meaningfully.",
            )
        return (
            "No significant indicators detected",
            "No significant indicators detected",
            0,
            "No configured heuristic rule matched. This does not prove the message is safe.",
        )

    by_id = {finding.rule_id for finding in findings}
    score = sum(finding.weight for finding in findings)
    score += 12 if {"credential_request", "urgency_pressure"}.issubset(by_id) else 0
    score += 16 if {"advance_fee", "job_offer"}.issubset(by_id) else 0
    score += 12 if "account_threat" in by_id and ({"credential_request", "payment_request"} & by_id) else 0
    score = min(score, 100)

    if score >= 75:
        assessment = risk_level = "Critical"
    elif score >= 50:
        assessment = risk_level = "High"
    elif score >= 25:
        assessment = risk_level = "Moderate"
    else:
        assessment = risk_level = "Low"

    if len(findings) >= 3:
        breadth = "Multiple different indicator types were found."
    elif len(findings) == 2:
        breadth = "Two different indicator types were found."
    else:
        breadth = "One indicator type was found; context is important."
    return assessment, risk_level, score, breadth


def _primary_category(findings: tuple[MessageFinding, ...]) -> str:
    ids = {finding.rule_id for finding in findings}
    if "credential_request" in ids:
        return "Credential or OTP request"
    if "advance_fee" in ids and "job_offer" in ids:
        return "Possible fake-job / advance-fee pattern"
    if "advance_fee" in ids:
        return "Advance-fee request"
    if "account_threat" in ids:
        return "Account pressure / possible impersonation"
    if "unrealistic_offer" in ids or "job_offer" in ids:
        return "Employment or financial promise"
    if "payment_request" in ids:
        return "Payment request"
    if findings:
        return "Social-engineering indicators"
    return "No prominent pattern identified"


def _recommendations(findings: tuple[MessageFinding, ...], observations: tuple[str, ...]) -> tuple[str, ...]:
    ids = {finding.rule_id for finding in findings}
    recommendations: list[str] = []
    if "credential_request" in ids:
        recommendations.append("Do not share an OTP, password, PIN or CVV in a message or phone call.")
    if "advance_fee" in ids or "job_offer" in ids:
        recommendations.append("Verify the recruiter and vacancy using the employer's independently located official website; be cautious about upfront fees.")
    if "account_threat" in ids:
        recommendations.append("Open the bank or service's official app yourself, or contact support using a number from an official source.")
    if "payment_request" in ids:
        recommendations.append("Do not transfer money until you independently verify the request and recipient.")
    if "off_platform_migration" in ids:
        recommendations.append("Keep the original conversation and verify the sender before moving to another messaging channel.")
    if "url_present" in observations:
        recommendations.append("Do not open the embedded link based on this message alone; the URL has not been checked by the URL analyzer.")
    if not recommendations:
        recommendations.append("If the message is unexpected, verify it through a separate trusted channel before taking action.")
    recommendations.append("Preserve the original message and sender details if you need to report the incident.")
    return tuple(recommendations)


def analyze_message(message: str, language: str = "Not sure") -> MessageAnalysisResult:
    """Analyze text using local pattern rules and return an explainable assessment.

    The score is an uncalibrated heuristic indicator score, not a probability.
    Submitted content is not sent to external services or stored by this function.
    """
    if not isinstance(message, str):
        raise TypeError("Message content must be text.")
    if language not in SUPPORTED_LANGUAGE_LABELS:
        raise ValueError("Choose English, Telugu, Hindi or Not sure for the message language.")

    cleaned = _normalize_message(message)
    if not cleaned:
        raise ValueError("Enter a message before running the analysis.")
    if len(cleaned) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Message exceeds the {MAX_MESSAGE_LENGTH} character limit.")

    findings = tuple(
        finding
        for rule in _RULES
        if (finding := _match_rule(rule, cleaned)) is not None
    )

    observations: list[str] = []
    if _URL_PATTERN.search(cleaned):
        observations.append("url_present")
    if _PHONE_PATTERN.search(cleaned):
        observations.append("phone_number_like_text_present")

    assessment, risk_level, score, breadth = _risk_assessment(findings, len(cleaned))
    recommendations = _recommendations(findings, tuple(observations))
    limitations = (
        "Local phrase and pattern rules only; no AI model or external threat-intelligence provider was queried.",
        "English, Telugu and Hindi have initial phrase coverage, but multilingual detection has not been validated on a representative dataset and may miss mixed-language or unusual wording.",
        "The indicator score is not a calibrated probability and is not proof that a message or sender is fraudulent.",
        "A clean result means only that these configured rules did not match; it does not establish that the message is safe.",
        "The analysis result is held only in the current Streamlit session; it is not saved to the database in this milestone.",
    )

    return MessageAnalysisResult(
        assessment=assessment,
        risk_level=risk_level,
        indicator_score=score,
        indicator_breadth=breadth,
        primary_category=_primary_category(findings),
        findings=findings,
        observations=tuple(observations),
        recommendations=recommendations,
        limitations=limitations,
        language_selected=language,
        ruleset_version=RULESET_VERSION,
        analyzed_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
