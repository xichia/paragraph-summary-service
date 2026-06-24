from paragraph_summary_service.config.settings import Settings
from paragraph_summary_service.models.domain import ProviderParagraphRequest
from paragraph_summary_service.prompts.templates import get_template
from paragraph_summary_service.providers.mock import MockProvider


def test_mock_provider_is_deterministic(tmp_path):
    settings = Settings(
        summary_db_path=tmp_path / "db.sqlite",
        summary_artifact_dir=tmp_path / "out",
    )
    provider = MockProvider(settings)
    records = [
        ProviderParagraphRequest(
            "r1",
            "paragraph 1",
            "Alpha beta. Gamma delta.",
            "sha256:x",
            48,
        )
    ]
    template = get_template("paragraph_sentence_batch_v1")

    first = provider.generate_paragraph_summaries(
        records=records,
        template=template,
        model=provider.default_model,
    )
    second = provider.generate_paragraph_summaries(
        records=records,
        template=template,
        model=provider.default_model,
    )

    assert first == second
    assert first.results[0].summary == "Alpha beta."
