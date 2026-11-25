from core.ui_validation import validate_launcher_input


def test_message_input_rejects_empty_content():
    assert validate_launcher_input("Message", "   ") == "Enter a message before continuing."


def test_message_input_accepts_nonempty_content_without_claiming_analysis():
    assert validate_launcher_input("Message", "Please review this message") is None


def test_url_input_rejects_values_over_the_ui_limit():
    error = validate_launcher_input("URL", "x" * 2049)
    assert error == "The url exceeds the 2048 character limit."


def test_phone_input_requires_minimum_length_only():
    error = validate_launcher_input("Phone number", "+91")
    assert error is not None
    assert "Full number validation is not available yet" in error


def test_unknown_input_type_is_rejected():
    assert validate_launcher_input("Email attachment", "file") == "Choose a supported investigation type."
