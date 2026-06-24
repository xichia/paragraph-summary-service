from __future__ import annotations

import re
from typing import Any

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")
API_KEY_RE = re.compile(r"\b(?:sk|AIza|ghp|xoxb|xoxp|key|token)[-_A-Za-z0-9]{12,}\b", re.I)
LONG_SECRET_RE = re.compile(r"\b[A-Za-z0-9_\-]{32,}\b")
RAW_TEXT_METADATA_KEYS = {
    "body",
    "content",
    "paragraph_text",
    "prompt",
    "raw_text",
    "source_text",
    "text",
}


def redact_text(text: str) -> str:
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    redacted = PHONE_RE.sub("[REDACTED_PHONE]", redacted)
    redacted = API_KEY_RE.sub("[REDACTED_SECRET]", redacted)
    redacted = LONG_SECRET_RE.sub("[REDACTED_SECRET]", redacted)
    return redacted


def redact_metadata(metadata: dict[str, Any], *, raw_text: str) -> dict[str, Any]:
    return {
        key: _redact_metadata_field(key, value, raw_text=raw_text)
        for key, value in metadata.items()
    }


def _redact_metadata_field(key: str, value: Any, *, raw_text: str) -> Any:
    if key.lower() in RAW_TEXT_METADATA_KEYS:
        return "[REDACTED]"
    return _redact_metadata_value(value, raw_text=raw_text)


def _redact_metadata_value(value: Any, *, raw_text: str) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _redact_metadata_field(str(key), nested, raw_text=raw_text)
            for key, nested in value.items()
        }
    if isinstance(value, list):
        return [_redact_metadata_value(item, raw_text=raw_text) for item in value]
    if isinstance(value, str):
        stripped_raw_text = raw_text.strip()
        if stripped_raw_text and stripped_raw_text in value:
            value = value.replace(stripped_raw_text, "[REDACTED]")
        return redact_text(value)
    return value
