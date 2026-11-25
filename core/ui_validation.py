"""Small interface-level validation helpers; these do not perform threat analysis."""

from __future__ import annotations

MAX_LENGTHS = {
    "Message": 5000,
    "URL": 2048,
    "Phone number": 32,
}


def validate_launcher_input(input_kind: str, value: str) -> str | None:
    """Validate only that an interface field is present and within its size limit."""
    if input_kind not in MAX_LENGTHS:
        return "Choose a supported investigation type."

    cleaned = (value or "").strip()
    if not cleaned:
        return f"Enter a {input_kind.lower()} before continuing."

    if len(cleaned) > MAX_LENGTHS[input_kind]:
        return f"The {input_kind.lower()} exceeds the {MAX_LENGTHS[input_kind]} character limit."

    if input_kind == "Phone number" and len(cleaned) < 5:
        return "Enter at least 5 characters for the phone number. Full number validation is not available yet."

    return None
