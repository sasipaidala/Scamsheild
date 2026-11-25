import pytest

from services.email_service import analyze_email


def test_sender_reply_to_domain_mismatch_is_flagged():
    result = analyze_email(
        "billing@company.example", "Invoice", "Please review the invoice.",
        reply_to="collect@unrelated.example"
    )
    assert result.sender_reply_to_mismatch
    assert any(item.code == "reply_to_mismatch" for item in result.findings)
    assert result.risk_level in {"Needs review", "High attention"}


def test_otp_and_urgent_email_body_triggers_content_indicator():
    result = analyze_email(
        "security@example.com", "Urgent account warning",
        "Your account will be blocked today. Send your OTP immediately."
    )
    assert any(item.code == "body_high_risk" for item in result.findings)
    assert result.message_analysis.findings


def test_urls_are_extracted_but_never_claimed_checked():
    result = analyze_email(
        "notice@example.com", "Review now", "Visit https://example.test/login for details."
    )
    assert result.urls == ("https://example.test/login",)
    assert any(item.code == "urls_present" for item in result.findings)
    assert any("not opened" in item or "not opened" in item.lower() for item in result.limitations)


def test_authentication_header_statuses_are_reported_as_unverified():
    headers = """From: Security <security@example.com>\nAuthentication-Results: mx.example; spf=pass; dkim=fail; dmarc=fail\n"""
    result = analyze_email("security@example.com", "Notice", "Please review.", raw_headers=headers)
    assert result.authentication == {"SPF": "pass", "DKIM": "fail", "DMARC": "fail"}
    assert any("not been independently verified" in item.explanation for item in result.findings)


def test_missing_authentication_headers_are_unavailable_not_pass():
    result = analyze_email("person@example.com", "Hello", "Meeting at 10 AM")
    assert result.authentication_available is False
    assert result.authentication == {}
    assert any("unavailable" in item.lower() for item in result.recommendations)


def test_authentication_results_header_without_status_is_not_assumed_pass():
    result = analyze_email("person@example.com", "Hello", "Meeting at 10 AM",
                           raw_headers="Authentication-Results: mx.example; auth=none\n")
    assert result.authentication_available is True
    assert result.authentication == {}
    assert any(item.code == "auth_results_unparsed" for item in result.findings)


def test_invalid_sender_format_is_flagged_as_review_not_spoofing():
    result = analyze_email("not-an-email", "Hello", "Please see attached.")
    assert any(item.code == "invalid_sender" for item in result.findings)
    assert result.risk_level == "Needs review"


def test_empty_input_and_oversized_fields_are_rejected():
    with pytest.raises(ValueError, match="Enter at least"):
        analyze_email("", "", "")
    with pytest.raises(ValueError, match="character limit"):
        analyze_email("a@example.com", "x" * 5001, "Body")


def test_auth_header_size_is_limited():
    with pytest.raises(ValueError, match="Raw headers exceed"):
        analyze_email("a@example.com", "Subject", "Body", raw_headers="x" * 20001)


def test_subject_and_body_combined_length_is_limited():
    with pytest.raises(ValueError, match="combined exceed"):
        analyze_email("a@example.com", "s" * 3000, "b" * 2500)
