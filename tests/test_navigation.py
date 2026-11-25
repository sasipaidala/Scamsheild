"""Regression checks for the complete, uniquely routed product navigation."""

import ast
from pathlib import Path


def _page_route_paths() -> list[str]:
    source_path = Path(__file__).parents[1] / "components" / "navigation.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    page_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "st"
        and node.func.attr == "Page"
    ]

    paths = []
    for call in page_calls:
        path_keyword = next(
            (keyword for keyword in call.keywords if keyword.arg == "url_path"),
            None,
        )
        assert path_keyword is not None, "Every page must declare url_path explicitly"
        assert isinstance(path_keyword.value, ast.Constant)
        assert isinstance(path_keyword.value.value, str)
        paths.append(path_keyword.value.value)
    return paths


def test_navigation_has_thirteen_unique_product_routes_including_public_home():
    paths = _page_route_paths()
    expected = {
        "",
        "overview",
        "new-investigation",
        "message-analyzer",
        "url-analyzer",
                "cases",
        "community-reports",
        "threat-intelligence",
        "security-awareness",
        "reports",
        "settings",
        "help",
    }
    assert len(paths) == 12
    assert len(paths) == len(set(paths))
    assert set(paths) == expected


def test_awareness_and_help_routes_use_implemented_pages():
    source_path = Path(__file__).parents[1] / "components" / "navigation.py"
    source = source_path.read_text(encoding="utf-8")
    assert "security_awareness_page.render" in source
    assert "help_center_page.render" in source



def test_message_analyzer_route_uses_the_real_analysis_page_not_placeholder():
    source_path = Path(__file__).parents[1] / "components" / "navigation.py"
    source = source_path.read_text(encoding="utf-8")
    assert "from pages import cases, landing, message_analyzer, new_investigation, overview, settings" in source
    assert "message_analyzer.render" in source


def test_threat_intelligence_route_uses_implemented_page():
    source_path = Path(__file__).parents[1] / "components" / "navigation.py"
    source = source_path.read_text(encoding="utf-8")
    assert "threat_intelligence_page.render" in source
    assert "Threat Intelligence" in source


def test_phone_intelligence_is_out_of_navigation_scope():
    source_path = Path(__file__).parents[1] / "components" / "navigation.py"
    source = source_path.read_text(encoding="utf-8")
    assert "phone_intelligence" not in source
