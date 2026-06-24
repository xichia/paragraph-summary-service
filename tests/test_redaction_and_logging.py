from paragraph_summary_service.safety.logging import sanitize_log_fields
from paragraph_summary_service.safety.redaction import redact_metadata, redact_text


def test_redaction_hooks():
    redacted = redact_text("Email jane@example.com and token sk-abcdefghijklmnopqrstuvwxyz123456")
    assert "jane@example.com" not in redacted
    assert "sk-abcdefghijklmnopqrstuvwxyz123456" not in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_SECRET]" in redacted


def test_log_sanitizer_removes_text_field():
    fields = sanitize_log_fields({"text": "secret raw paragraph", "record_id": "r1"})
    assert fields["text"] == "[REDACTED]"
    assert fields["record_id"] == "r1"


def test_metadata_redaction_removes_raw_text_fields():
    raw_text = "Original paragraph body with jane@example.com."
    metadata = {
        "nested": {"paragraph_text": raw_text},
        "note": f"copied: {raw_text}",
        "page": 1,
        "text": raw_text,
    }

    redacted = redact_metadata(metadata, raw_text=raw_text)

    assert redacted == {
        "nested": {"paragraph_text": "[REDACTED]"},
        "note": "copied: [REDACTED]",
        "page": 1,
        "text": "[REDACTED]",
    }
