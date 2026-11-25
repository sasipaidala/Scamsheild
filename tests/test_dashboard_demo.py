from pathlib import Path

from core.dashboard_demo import (
    DEMO_CATEGORIES,
    DEMO_INVESTIGATIONS,
    DEMO_METRICS,
    dashboard_demo_allowed,
)


def test_dashboard_demo_records_are_separate_preview_fixtures():
    fixture_source = (Path(__file__).parents[1] / "core" / "dashboard_demo.py").read_text(encoding="utf-8")
    page_source = (Path(__file__).parents[1] / "pages" / "overview.py").read_text(encoding="utf-8")
    assert "Synthetic data used only" in fixture_source
    assert "DEMONSTRATION DATA" in page_source
    assert "not real investigations" in page_source
    assert len(DEMO_METRICS) == 4
    assert len(DEMO_CATEGORIES) >= 4
    assert len(DEMO_INVESTIGATIONS) >= 3


def test_demo_visualization_categories_use_percentages_in_range():
    assert all(0 <= percentage <= 100 for _, percentage, _ in DEMO_CATEGORIES)



def test_demo_dashboard_is_allowed_only_in_development():
    assert dashboard_demo_allowed("development") is True
    assert dashboard_demo_allowed("test") is False
    assert dashboard_demo_allowed("production") is False
    assert dashboard_demo_allowed("PRODUCTION") is False
