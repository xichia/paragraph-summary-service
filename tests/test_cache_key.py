from paragraph_summary_service.cache.keys import build_cache_key, sha256_text


def test_text_hash_normalizes_trailing_whitespace():
    assert sha256_text("hello\n") == sha256_text("hello")


def test_cache_key_changes_with_template():
    common = {
        "input_text_hash": sha256_text("hello"),
        "summary_style": "paragraph_sentence",
        "provider": "mock",
        "model": "mock-deterministic-v1",
        "redaction_version": "v1",
        "max_summary_tokens": 48,
    }
    one = build_cache_key(template_version="a", **common)
    two = build_cache_key(template_version="b", **common)
    assert one != two
