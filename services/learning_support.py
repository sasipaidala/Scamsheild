"""Local persistence for security-awareness progress and help requests."""
from __future__ import annotations

import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from database.connection import database_connection

TOPICS = {
    "Phishing and suspicious links": {
        "level": "Beginner", "minutes": 5,
        "summary": "Recognize deceptive messages and inspect links without opening them.",
        "content": [
            "Treat unexpected messages that demand urgent action as suspicious, especially when they ask you to sign in, pay, or share information.",
            "Check the registered domain carefully. A familiar brand name in a subdomain or URL path does not make the actual domain trustworthy.",
            "Do not open unknown links to test them. Copy the address safely into ScamShield's passive URL analyzer or use an approved reputation service.",
            "Navigate to important services using a saved bookmark or an address you type yourself, rather than a message link.",
        ],
        "quiz": [("A message says your account will close in 10 minutes and links to a login page. What is the safest action?", ["Open it quickly", "Use the official app/site independently", "Reply with your password"], 1, "Urgency is a pressure tactic. Verify through a known official channel.")],
    },
    "OTP, passwords and account security": {
        "level": "Beginner", "minutes": 4,
        "summary": "Protect credentials, recovery codes and one-time passwords.",
        "content": [
            "Never share an OTP, password, PIN, recovery code or authenticator approval with another person. Legitimate support staff should not ask you to disclose them.",
            "Use a unique password for every important account and a password manager to generate and store strong passwords.",
            "Enable multi-factor authentication where available. Prefer phishing-resistant passkeys or security keys when supported.",
            "If you disclose a credential, change it from the official website or app, revoke active sessions, and secure the recovery email and phone account.",
        ],
        "quiz": [("A caller claims to be bank support and asks you to read an OTP. What should you do?", ["Share it if they know your name", "Share only the first digits", "Do not share; end the call and contact the bank independently"], 2, "An OTP can authorize access or transactions. Never disclose it.")],
    },
    "Fake jobs and recruitment scams": {
        "level": "Intermediate", "minutes": 5,
        "summary": "Check job offers, recruiter identity and suspicious fees.",
        "content": [
            "Be cautious when a recruiter guarantees selection without a credible interview or offers unusually high pay for simple work.",
            "Do not pay registration, interview, training, equipment-release or refundable security fees to obtain a job. Verify any claimed fee directly with the employer through its official domain.",
            "Check whether the vacancy appears on the employer's official careers page and whether the recruiter uses a verifiable company email address.",
            "Do not send identity documents, bank details or selfies with documents until the employer and purpose are independently verified.",
        ],
        "quiz": [("A work-from-home offer asks for a refundable enrollment fee before sharing the job details. Best response?", ["Pay a small amount", "Decline payment and verify through the employer's official careers channel", "Send ID first"], 1, "Upfront fees are a major warning sign. Independent verification matters.")],
    },
    "Payment and UPI fraud": {
        "level": "Intermediate", "minutes": 5,
        "summary": "Avoid collect-request, QR-code and impersonation traps.",
        "content": [
            "Entering a UPI PIN or approving a collect request generally authorizes money to leave your account; it is not a way to receive money.",
            "Do not scan a QR code or approve a payment request to receive a refund, prize or incoming transfer.",
            "Verify payment status inside your bank or payment app. Screenshots and SMS messages can be forged.",
            "If money is lost in India, contact your bank/payment provider immediately and report promptly through the national cybercrime helpline 1930 or cybercrime.gov.in.",
        ],
        "quiz": [("Someone says you must enter your UPI PIN to receive a refund. What should you do?", ["Enter the PIN", "Decline; receiving money does not require sharing your UPI PIN", "Send them an OTP"], 1, "A UPI PIN authorizes a debit. Do not enter it to receive money.")],
    },
    "Impersonation and social engineering": {
        "level": "Intermediate", "minutes": 4,
        "summary": "Verify people and requests before taking sensitive actions.",
        "content": [
            "Scammers may impersonate employers, banks, delivery companies, government agencies, friends or family.",
            "A familiar display name, profile photo or caller ID is not proof of identity.",
            "For unusual money or data requests, contact the person using a separate, previously known channel. Do not use contact details supplied in the suspicious message.",
            "Pause when a request involves secrecy, urgency, remote-access software, gift cards, cryptocurrency or bypassing normal procedures.",
        ],
        "quiz": [("A manager messages from a new number asking for an urgent confidential transfer. What should you do?", ["Transfer immediately", "Verify through a known company channel", "Send your banking login"], 1, "Use an independent, trusted channel to confirm unusual requests.")],
    },
}

CATEGORIES = ("Bug or technical issue", "Report a security concern", "Account or access help", "Feature request", "Other")
PRIORITIES = ("Low", "Normal", "High")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_awareness_progress(database_path: str | Path) -> dict[str, dict[str, Any]]:
    with database_connection(database_path) as conn:
        rows = conn.execute("SELECT topic, score, completed_at FROM awareness_progress ORDER BY completed_at DESC").fetchall()
    return {row["topic"]: dict(row) for row in rows}


def save_awareness_progress(database_path: str | Path, topic: str, score: int) -> dict[str, Any]:
    if topic not in TOPICS:
        raise ValueError("Unknown awareness topic.")
    if not isinstance(score, int) or not 0 <= score <= 100:
        raise ValueError("Score must be between 0 and 100.")
    completed_at = _now()
    with database_connection(database_path) as conn:
        conn.execute("""INSERT INTO awareness_progress(topic, score, completed_at) VALUES (?, ?, ?)
            ON CONFLICT(topic) DO UPDATE SET score=excluded.score, completed_at=excluded.completed_at""", (topic, score, completed_at))
    return {"topic": topic, "score": score, "completed_at": completed_at}


def create_support_ticket(database_path: str | Path, category: str, subject: str, description: str,
                          email: str = "", priority: str = "Normal") -> dict[str, Any]:
    category, subject, description, email = (v.strip() for v in (category, subject, description, email))
    if category not in CATEGORIES:
        raise ValueError("Choose a valid support category.")
    if priority not in PRIORITIES:
        raise ValueError("Choose a valid priority.")
    if not subject or len(subject) > 120:
        raise ValueError("Subject is required and must be 120 characters or fewer.")
    if not description or len(description) > 4000:
        raise ValueError("Description is required and must be 4,000 characters or fewer.")
    if any(ord(c) < 32 and c not in "\n\r\t" for c in subject + description):
        raise ValueError("Text contains unsupported control characters.")
    if email and (len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email)):
        raise ValueError("Enter a valid email address or leave it blank.")
    ref = "SS-HELP-" + secrets.token_hex(3).upper()
    created_at = _now()
    with database_connection(database_path) as conn:
        conn.execute("INSERT INTO support_tickets(ticket_ref, category, subject, description, contact_email, priority, status, created_at) VALUES (?, ?, ?, ?, ?, ?, 'Open', ?)",
                     (ref, category, subject, description, email, priority, created_at))
    return {"ticket_ref": ref, "category": category, "subject": subject, "description": description,
            "contact_email": email, "priority": priority, "status": "Open", "created_at": created_at}


def list_support_tickets(database_path: str | Path, limit: int = 100) -> tuple[dict[str, Any], ...]:
    with database_connection(database_path) as conn:
        rows = conn.execute("SELECT ticket_ref, category, subject, priority, status, created_at FROM support_tickets ORDER BY created_at DESC LIMIT ?", (max(1, min(int(limit), 500)),)).fetchall()
    return tuple(dict(row) for row in rows)
