from typing import Any

SENSITIVE_FIELD_NAMES = {"text", "prompt", "api_key", "authorization", "password", "secret"}


def sanitize_log_fields(fields: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, value in fields.items():
        clean[key] = "[REDACTED]" if key.lower() in SENSITIVE_FIELD_NAMES else value
    return clean
