"""Static regression checks for the settings workspace."""
from pathlib import Path


def test_settings_page_exposes_expected_preference_sections_and_controls():
    source = (Path(__file__).parents[1] / "pages" / "settings.py").read_text(encoding="utf-8")
    for label in (
        "Appearance", "Workspace", "Privacy & Safety", "Data & Backup", "About",
        "Interface density", "Reduce animations and motion", "Default export format",
        "Download database backup", "Export preferences (JSON)", "Reset preferences",
    ):
        assert label in source


def test_settings_page_warns_about_local_storage_and_secrets():
    source = (Path(__file__).parents[1] / "pages" / "settings.py").read_text(encoding="utf-8")
    assert "local workspace" in source.lower()
    assert "OTP" in source
    assert "does not delete cases" in source


def test_global_shell_applies_density_and_motion_preferences():
    source = (Path(__file__).parents[1] / "app.py").read_text(encoding="utf-8")
    assert 'st.session_state.get("ss_density", "Comfortable")' in source
    assert 'st.session_state.get("ss_reduce_motion", False)' in source
    assert "animation-duration: .01ms" in source
