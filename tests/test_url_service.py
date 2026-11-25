from datetime import datetime
import json

import pytest

from services.url_service import MAX_URL_LENGTH, RULESET_VERSION, analyze_url


def test_basic_url_parses_without_claiming_safe():
    result = analyze_url("https://example.com/login")
    assert result.hostname == "example.com"
    assert result.scheme == "https"
    assert "no_configured_structural_indicators" in result.observations
    assert any("not proven safe" in item for item in result.limitations)


def test_url_without_scheme_gets_https_for_parsing():
    result = analyze_url("example.com/path")
    assert result.scheme == "https"
    assert result.normalized_url == "https://example.com/path"


def test_userinfo_is_flagged_without_network_access():
    result = analyze_url("https://trusted.example@evil.example/login")
    assert result.hostname == "evil.example"
    assert any(f.rule_id == "userinfo_present" for f in result.findings)


def test_ip_literal_host_is_flagged_for_review():
    result = analyze_url("http://192.0.2.1/sign-in")
    ids = {f.rule_id for f in result.findings}
    assert "ip_literal_host" in ids
    assert "unencrypted_http" in ids


def test_shortener_domain_is_an_indicator_not_a_verdict():
    result = analyze_url("https://bit.ly/abc123")
    assert any(f.rule_id == "shortener_domain" for f in result.findings)
    assert "verdict" in " ".join(result.limitations)


def test_nonstandard_port_and_long_hostname_indicators():
    result = analyze_url("https://" + "a" * 65 + ".example:8443/")
    ids = {f.rule_id for f in result.findings}
    assert "long_hostname" in ids
    assert "nonstandard_port" in ids


def test_invalid_scheme_is_rejected():
    with pytest.raises(ValueError, match="Only HTTP and HTTPS"):
        analyze_url("javascript:alert(1)")


def test_missing_host_is_rejected():
    with pytest.raises(ValueError, match="valid hostname"):
        analyze_url("https:///path")


def test_empty_and_oversized_urls_are_rejected():
    with pytest.raises(ValueError, match="Enter a URL"):
        analyze_url("  ")
    with pytest.raises(ValueError, match="character limit"):
        analyze_url("a" * (MAX_URL_LENGTH + 1))


def test_control_characters_are_rejected():
    with pytest.raises(ValueError, match="control characters"):
        analyze_url("https://example.com/\nlogin")


def test_result_is_json_friendly_and_has_aware_timestamp():
    result = analyze_url("https://example.com/?next=%2Faccount")
    json.dumps(result.to_dict(), ensure_ascii=False)
    assert result.ruleset_version == RULESET_VERSION
    assert datetime.fromisoformat(result.analyzed_at).tzinfo is not None


def test_analysis_contains_no_external_reputation_claim():
    result = analyze_url("https://example.com")
    text = " ".join(result.limitations).lower()
    assert "not" in text and "reputation" in text
