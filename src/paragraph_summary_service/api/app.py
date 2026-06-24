from __future__ import annotations

from fastapi import FastAPI

from paragraph_summary_service.api.errors import (
    key_error_handler,
    provider_error_handler,
    request_limit_error_handler,
)
from paragraph_summary_service.api.routes_artifacts import router as artifacts_router
from paragraph_summary_service.api.routes_health import router as health_router
from paragraph_summary_service.api.routes_paragraph_summaries import router as paragraph_router
from paragraph_summary_service.config.settings import get_settings
from paragraph_summary_service.providers.base import ProviderError
from paragraph_summary_service.safety.limits import RequestLimitError


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.add_exception_handler(ProviderError, provider_error_handler)
    app.add_exception_handler(RequestLimitError, request_limit_error_handler)
    app.add_exception_handler(KeyError, key_error_handler)
    app.include_router(health_router)
    app.include_router(paragraph_router)
    app.include_router(artifacts_router)
    return app

