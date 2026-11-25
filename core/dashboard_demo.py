"""Synthetic dashboard fixtures used only for development previews."""


def dashboard_demo_allowed(environment: str) -> bool:
    """Allow synthetic dashboard fixtures only in local development mode."""
    return (environment or "").strip().lower() == "development"

# Synthetic data used only to demonstrate dashboard components. Replace with
# repository-backed records after investigation and case persistence exist.
DEMO_METRICS = (
    {"label": "Investigations", "value": "1,284", "change": "+12.8%", "foot": "Illustrative sample volume", "icon": "⌕", "accent": "var(--ss-primary)"},
    {"label": "High-risk findings", "value": "186", "change": "14.5%", "foot": "Share of sample findings", "icon": "⚑", "accent": "var(--ss-danger)"},
    {"label": "Active cases", "value": "36", "change": "8 open", "foot": "Illustrative case queue", "icon": "▣", "accent": "var(--ss-violet)"},
    {"label": "Reports generated", "value": "89", "change": "+6 this week", "foot": "Sample report activity", "icon": "▤", "accent": "var(--ss-success)"},
)

DEMO_CATEGORIES = (
    ("Fake job offers", 82, "var(--ss-primary)"),
    ("Payment / advance-fee", 68, "var(--ss-blue)"),
    ("Account impersonation", 54, "var(--ss-violet)"),
    ("Delivery messages", 39, "var(--ss-warning)"),
    ("Investment promises", 27, "var(--ss-danger)"),
)

DEMO_INVESTIGATIONS = (
    ("Recruitment registration-fee message", "MESSAGE", "High", "Today · 10:42 AM"),
    ("Parcel delivery payment request", "URL", "Medium", "Yesterday · 6:18 PM"),
    ("Account verification warning", "MESSAGE", "High", "Yesterday · 1:06 PM"),
    ("Unsolicited investment invitation", "MESSAGE", "Low", "30 Oct · 11:24 AM"),
)

