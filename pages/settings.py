"""Configurable local workspace preferences and diagnostics."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from core.config import Settings


DEFAULT_PREFERENCES = {
    "ss_density": "Comfortable",
    "ss_reduce_motion": False,
    "ss_show_tooltips": True,
    "ss_confirm_sensitive_actions": True,
    "ss_default_export": "JSON",
}


def _initialize_preferences() -> None:
    for key, value in DEFAULT_PREFERENCES.items():
        st.session_state.setdefault(key, value)


def _sync_settings_theme() -> None:
    st.session_state["ss_theme"] = st.session_state["ss_settings_theme"]
    st.query_params["theme"] = st.session_state["ss_theme"]


def _reset_preferences() -> None:
    """Reset widget-backed preferences before Streamlit instantiates widgets."""
    for key, value in DEFAULT_PREFERENCES.items():
        st.session_state[key] = value
    st.session_state["ss_theme"] = "dark"
    st.session_state["ss_settings_theme"] = "dark"
    st.query_params["theme"] = "dark"


def _preference_payload() -> dict:
    return {
        "product": "ScamShield AI",
        "format_version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "preferences": {
            "theme": st.session_state.get("ss_theme", "dark"),
            "density": st.session_state["ss_density"],
            "reduce_motion": st.session_state["ss_reduce_motion"],
            "show_tooltips": st.session_state["ss_show_tooltips"],
            "confirm_sensitive_actions": st.session_state["ss_confirm_sensitive_actions"],
            "default_export": st.session_state["ss_default_export"],
        },
        "note": "Preferences only; this file does not contain cases, reports, or evidence.",
    }


def render() -> None:
    _initialize_preferences()
    settings = Settings.from_env()

    st.markdown('<div class="ss-eyebrow">WORKSPACE CONTROL</div>', unsafe_allow_html=True)
    st.title("Settings")
    st.caption("Configure how this local ScamShield workspace looks and behaves.")

    appearance, workspace, privacy, data, about = st.tabs(
        ["Appearance", "Workspace", "Privacy & Safety", "Data & Backup", "About"]
    )

    with appearance:
        st.subheader("Visual preferences")
        current_theme = st.session_state.get("ss_theme", "dark")
        st.selectbox(
            "Color theme",
            options=["dark", "light"],
            index=0 if current_theme == "dark" else 1,
            format_func=lambda value: "Dark · Neon green" if value == "dark" else "Light · High contrast",
            key="ss_settings_theme",
            on_change=_sync_settings_theme,
        )
        st.selectbox(
            "Interface density",
            options=["Comfortable", "Compact"],
            key="ss_density",
            help="Compact reduces vertical spacing across the application.",
        )
        st.checkbox(
            "Reduce animations and motion",
            key="ss_reduce_motion",
            help="Disables decorative transitions and animations where possible.",
        )
        st.caption("Theme, density and motion preferences apply across the workspace for this browser session.")

    with workspace:
        st.subheader("Workspace defaults")
        st.selectbox(
            "Default export format",
            options=["JSON", "Markdown"],
            key="ss_default_export",
            help="Saved as a preference for future export workflows. Existing export buttons retain their current formats.",
        )
        st.checkbox(
            "Show contextual guidance",
            key="ss_show_tooltips",
            help="Preference flag for contextual help in supported controls.",
        )
        st.caption("Some defaults are recorded for future workflows; they do not change analyzer scoring or evidence.")

    with privacy:
        st.subheader("Privacy and safety")
        st.checkbox(
            "Require confirmation before sensitive actions",
            key="ss_confirm_sensitive_actions",
            help="Preference for confirmation prompts as destructive actions are introduced.",
        )
        st.info(
            "ScamShield currently runs as a local workspace. These preferences do not create user accounts, "
            "encrypt the database, or change who can access files on this computer."
        )
        st.warning(
            "Do not enter passwords, OTPs, API secrets or unnecessary personal information into investigation notes. "
            "Keep provider keys in the local .env file and out of Git."
        )

    with data:
        st.subheader("Local data and backup")
        database_path = Path(settings.database_path)
        st.text_input("Database location", value=str(database_path), disabled=True)
        if database_path.exists() and database_path.is_file():
            st.download_button(
                "Download database backup",
                data=database_path.read_bytes(),
                file_name=f"scamshield-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db",
                mime="application/octet-stream",
                help="Downloads a copy of the local SQLite database. Store it securely; it may contain investigation data.",
            )
        else:
            st.caption("Database file is not present at the configured location yet.")

        st.download_button(
            "Export preferences (JSON)",
            data=json.dumps(_preference_payload(), indent=2),
            file_name="scamshield-preferences.json",
            mime="application/json",
        )
        st.caption("The preferences export contains settings only, not case records or evidence.")

    with about:
        st.subheader("Workspace information")
        st.write(f"**Application:** {settings.app_name}")
        st.write(f"**Version:** {settings.app_version}")
        st.write(f"**Environment:** {settings.environment}")
        st.write("**Storage:** Local SQLite database")
        st.write("**External threat intelligence:** Not connected unless separately configured and approved.")
        st.caption("No setting on this page changes threat verdicts, risk scores, or the underlying evidence.")

    st.divider()
    st.subheader("Reset preferences")
    st.caption("Reset appearance and workspace preferences to their defaults. This does not delete cases, reports, evidence or the database.")
    st.button(
        "Reset preferences",
        type="secondary",
        on_click=_reset_preferences,
        help="Restore default appearance and workspace preferences without deleting investigation data.",
    )
