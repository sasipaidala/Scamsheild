from core.theme import THEME_TOKENS, normalize_theme, theme_css


def test_unknown_theme_defaults_to_dark():
    assert normalize_theme("neon") == "dark"
    assert normalize_theme(None) == "dark"


def test_both_themes_have_distinct_accessible_palettes():
    assert set(THEME_TOKENS) == {"dark", "light"}
    assert THEME_TOKENS["dark"]["background"] != THEME_TOKENS["light"]["background"]
    assert THEME_TOKENS["dark"]["text"] != THEME_TOKENS["light"]["text"]


def test_theme_css_includes_reduced_motion_support():
    css = theme_css("light")
    assert "color-scheme: light" in css
    assert "prefers-reduced-motion: reduce" in css
    assert "--ss-primary" in css


def test_theme_css_explicitly_styles_streamlit_widget_text_and_popovers():
    light_css = theme_css("light")
    dark_css = theme_css("dark")
    for css in (light_css, dark_css):
        assert '[data-testid="stWidgetLabel"]' in css
        assert '[data-testid="stSelectbox"]' in css
        assert '[data-baseweb="popover"]' in css
        assert "--ss-text" in css
        assert "--ss-surface-elevated" in css
    assert "--ss-text: #18213A" in light_css
    assert "--ss-text: #E0FFE8" in dark_css


def test_theme_css_styles_streamlit_material_icons_for_both_themes():
    dark_css = theme_css("dark")
    light_css = theme_css("light")
    for css in (dark_css, light_css):
        assert '[data-testid="stIconMaterial"]' in css
        assert '.material-symbols-rounded' in css
        assert '[aria-current="page"]' in css
        assert '--ss-icon:' in css
    assert "--ss-icon: #A5C9AE" in dark_css
    assert "--ss-icon: #596783" in light_css
    assert "Premium light workspace" in light_css
    assert "linear-gradient(135deg, #6263DF, #4C4FC5)" in light_css


def test_theme_css_removes_galaxy_and_uses_subtle_cinematic_grid():
    dark_css = theme_css("dark")
    light_css = theme_css("light")
    for css in (dark_css, light_css):
        assert 'id="scamshield-cosmos"' not in css
        assert "linear-gradient(90deg" in css
        assert "prefers-reduced-motion: reduce" in css


def test_neon_theme_tokens_and_interactive_glow_styles_are_present():
    dark_css = theme_css("dark")
    assert THEME_TOKENS["dark"]["primary"] == "#39FF14"
    assert THEME_TOKENS["dark"]["violet"] == "#A3E635"
    assert THEME_TOKENS["dark"]["neon_pink"] == "#4ADE80"
    assert ".ss-neon-callout" in dark_css
    assert "ss-content-enter" in dark_css
    assert "box-shadow: 0 0 0 1px" in dark_css
