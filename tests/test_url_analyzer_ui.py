from pathlib import Path


def test_url_analyzer_has_clickable_local_examples_and_local_feedback():
    source = (Path(__file__).parents[1] / "pages" / "url_analyzer.py").read_text(encoding="utf-8")
    assert '"Clean structure": "https://example.com/login"' in source
    assert '"HTTP + IP host": "http://192.0.2.1/login"' in source
    assert '"Shortened link": "https://bit.ly/abc123"' in source
    assert '"Embedded credentials": "https://trusted.example@evil.example/login"' in source
    assert 'st.spinner("Parsing URL structure locally…")' in source
    assert "st.rerun()" in source


def test_high_attention_url_findings_render_a_red_error_banner():
    source = (Path(__file__).parents[1] / "pages" / "url_analyzer.py").read_text(encoding="utf-8")
    assert 'finding.severity.lower().startswith(("high", "critical"))' in source
    assert 'st.error(' in source
    assert "HIGH ATTENTION" in source
