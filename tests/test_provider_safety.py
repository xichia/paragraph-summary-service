import pytest

from paragraph_summary_service.config.settings import Settings
from paragraph_summary_service.models.domain import ProviderParagraphRequest
from paragraph_summary_service.prompts.templates import get_template
from paragraph_summary_service.providers.base import ProviderNotEnabledError
from paragraph_summary_service.providers.gemini import GeminiProvider
from paragraph_summary_service.providers.mock import MockProvider
from paragraph_summary_service.providers.registry import get_provider


def _provider_record() -> ProviderParagraphRequest:
    return ProviderParagraphRequest("r1", "ref", "Text.", "sha256:x", 48)


def test_gemini_provider_requires_explicit_opt_in(tmp_path):
    settings = Settings(
        summary_db_path=tmp_path / "db.sqlite",
        summary_artifact_dir=tmp_path / "out",
        allow_external_provider_calls=False,
        gemini_api_key="fake",
    )
    provider = GeminiProvider(settings)
    with pytest.raises(ProviderNotEnabledError):
        provider.generate_paragraph_summaries(
            records=[_provider_record()],
            template=get_template("paragraph_sentence_batch_v1"),
            model=provider.default_model,
        )


def test_default_provider_is_mock_with_external_calls_disabled(tmp_path):
    settings = Settings(
        summary_db_path=tmp_path / "db.sqlite",
        summary_artifact_dir=tmp_path / "out",
    )

    provider = get_provider(settings.llm_provider, settings)

    assert settings.llm_provider == "mock"
    assert settings.allow_external_provider_calls is False
    assert isinstance(provider, MockProvider)


def test_gemini_provider_requires_api_key_even_when_enabled(tmp_path):
    settings = Settings(
        summary_db_path=tmp_path / "db.sqlite",
        summary_artifact_dir=tmp_path / "out",
        allow_external_provider_calls=True,
        gemini_api_key=None,
    )
    provider = GeminiProvider(settings)

    with pytest.raises(ProviderNotEnabledError):
        provider.generate_paragraph_summaries(
            records=[_provider_record()],
            template=get_template("paragraph_sentence_batch_v1"),
            model=provider.default_model,
        )


def test_gemini_provider_uses_real_path_after_explicit_opt_in(tmp_path, monkeypatch):
    calls = {}

    class FakeGeminiResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "candidates": [
                    {"content": {"parts": [{"text": _gemini_json_response()}]}}
                ],
                "usageMetadata": {
                    "promptTokenCount": 3,
                    "candidatesTokenCount": 2,
                    "totalTokenCount": 5,
                },
            }

    def fake_post(url, json, timeout):
        calls["url"] = url
        calls["payload"] = json
        calls["timeout"] = timeout
        return FakeGeminiResponse()

    monkeypatch.setattr("paragraph_summary_service.providers.gemini.httpx.post", fake_post)
    settings = Settings(
        summary_db_path=tmp_path / "db.sqlite",
        summary_artifact_dir=tmp_path / "out",
        allow_external_provider_calls=True,
        gemini_api_key="fake-test-key",
    )
    provider = GeminiProvider(settings)

    result = provider.generate_paragraph_summaries(
        records=[_provider_record()],
        template=get_template("paragraph_sentence_batch_v1"),
        model=provider.default_model,
    )

    assert "fake-test-key" in calls["url"]
    assert calls["timeout"] == settings.gemini_timeout_seconds
    assert calls["payload"]["generationConfig"]["temperature"] == 0.0
    assert result.results[0].summary == "Text."
    assert result.usage.total_tokens == 5


def _gemini_json_response() -> str:
    return '{"summaries":[{"record_id":"r1","summary":"Text.","status":"completed"}]}'
