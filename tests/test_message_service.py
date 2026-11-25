"""Regression tests for the local, explainable message analyzer."""

from datetime import datetime
import json

import pytest

from services.message_service import MAX_MESSAGE_LENGTH, RULESET_VERSION, analyze_message


def test_otp_disclosure_request_is_high_risk_and_explained():
    result = analyze_message("Please send your OTP to verify your account.", "English")

    assert result.risk_level == "High"
    assert result.indicator_score is not None and result.indicator_score >= 50
    assert any(finding.rule_id == "credential_request" for finding in result.findings)
    assert any("Do not share an OTP" in item for item in result.recommendations)


def test_otp_prevention_advice_does_not_trigger_credential_request():
    message = "Never share your OTP or password with anyone. Your bank will never ask for it."
    result = analyze_message(message, "English")

    assert result.risk_level == "No significant indicators detected"
    assert result.indicator_score == 0
    assert not result.findings


def test_job_offer_with_registration_fee_triggers_combined_pattern():
    message = (
        "Congratulations, you have been selected for a work from home job. "
        "Pay the registration fee of Rs 999 today to secure your offer."
    )
    result = analyze_message(message, "English")

    rule_ids = {finding.rule_id for finding in result.findings}
    assert {"advance_fee", "job_offer"}.issubset(rule_ids)
    assert result.risk_level == "High"
    assert result.primary_category == "Possible fake-job / advance-fee pattern"


def test_urgency_alone_is_not_classified_as_critical():
    result = analyze_message("Please respond immediately to confirm the meeting time.")

    assert result.risk_level == "Low"
    assert result.indicator_score == 10
    assert len(result.findings) == 1


def test_telugu_advance_fee_phrase_is_detected_as_a_limited_heuristic():
    result = analyze_message("మీ ఉద్యోగం కోసం రిజిస్ట్రేషన్ ఫీజు ముందుగా చెల్లించండి.", "Telugu")

    assert any(finding.rule_id == "advance_fee" for finding in result.findings)
    assert result.language_selected == "Telugu"
    assert any("not been validated" in item for item in result.limitations)


def test_hindi_advance_fee_phrase_is_detected_as_a_limited_heuristic():
    result = analyze_message("नौकरी पाने के लिए पंजीकरण शुल्क पहले जमा करें।", "Hindi")

    assert any(finding.rule_id == "advance_fee" for finding in result.findings)
    assert result.language_selected == "Hindi"


def test_benign_message_without_matches_is_not_declared_safe():
    result = analyze_message(
        "Hello, our office meeting is scheduled for tomorrow at 10 AM. Please bring the project notes."
    )

    assert result.assessment == "No significant indicators detected"
    assert result.indicator_score == 0
    assert "does not prove the message is safe" in result.indicator_breadth


def test_short_message_returns_insufficient_evidence():
    result = analyze_message("Hello")

    assert result.risk_level == "Insufficient evidence"
    assert result.indicator_score is None


def test_url_in_message_is_observation_not_a_malicious_url_finding():
    result = analyze_message("Please review https://example.com for tomorrow's meeting details.")

    assert "url_present" in result.observations
    assert not result.findings
    assert result.indicator_score == 0
    assert any("URL has not been checked" in item for item in result.recommendations)


def test_empty_and_oversized_messages_are_rejected():
    with pytest.raises(ValueError, match="Enter a message"):
        analyze_message("   ")
    with pytest.raises(ValueError, match="character limit"):
        analyze_message("x" * (MAX_MESSAGE_LENGTH + 1))


def test_invalid_language_is_rejected():
    with pytest.raises(ValueError, match="Choose English, Telugu, Hindi"):
        analyze_message("Please verify this message", "French")


def test_unicode_normalization_and_zero_width_characters_are_handled():
    result = analyze_message("Please send your O\u200bTP to verify your account.", "English")

    assert any(finding.rule_id == "credential_request" for finding in result.findings)


def test_result_includes_version_and_timezone_aware_timestamp():
    result = analyze_message("Please share your OTP now.")

    assert result.ruleset_version == RULESET_VERSION
    timestamp = datetime.fromisoformat(result.analyzed_at)
    assert timestamp.tzinfo is not None


def test_analysis_result_can_be_converted_to_json_friendly_dictionary():
    result = analyze_message("Please send your OTP now.")
    payload = result.to_dict()

    assert payload["ruleset_version"] == RULESET_VERSION
    assert isinstance(payload["findings"], tuple)
    assert payload["findings"][0]["rule_id"] == "credential_request"
    json.dumps(payload, ensure_ascii=False)



def test_account_pressure_and_kyc_claim_are_detected():
    result = analyze_message("Your bank account is blocked. Update KYC immediately.")

    assert any(finding.rule_id == "account_threat" for finding in result.findings)
    assert result.risk_level == "Moderate"


def test_direct_payment_request_is_detected_without_claiming_external_verification():
    result = analyze_message("Pay now to release your parcel from the delivery center.")

    assert any(finding.rule_id == "payment_request" for finding in result.findings)
    assert any("independently verify" in item for item in result.recommendations)


def test_off_platform_migration_is_a_low_weight_indicator():
    result = analyze_message("Contact us on WhatsApp to continue the conversation.")

    assert any(finding.rule_id == "off_platform_migration" for finding in result.findings)
    assert result.risk_level == "Low"


def test_unusually_attractive_investment_promise_is_detected():
    result = analyze_message("Double your money with 100% guaranteed returns.")

    assert any(finding.rule_id == "unrealistic_offer" for finding in result.findings)
    assert result.risk_level == "Low"
