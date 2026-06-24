from paragraph_summary_service.config.settings import Settings
from paragraph_summary_service.providers.base import (
    ParagraphSummaryProvider,
    ProviderNotEnabledError,
)
from paragraph_summary_service.providers.gemini import GeminiProvider
from paragraph_summary_service.providers.mock import MockProvider


def get_provider(provider_name: str, settings: Settings) -> ParagraphSummaryProvider:
    normalized = provider_name.lower().strip()
    if normalized == "mock":
        return MockProvider(settings)
    if normalized == "gemini":
        return GeminiProvider(settings)
    raise ProviderNotEnabledError(f"provider is not registered: {provider_name}")


def resolve_model(provider: ParagraphSummaryProvider, requested_model: str | None) -> str:
    return requested_model or provider.default_model
