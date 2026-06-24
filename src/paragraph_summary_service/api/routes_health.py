from typing import Annotated

from fastapi import APIRouter, Depends

from paragraph_summary_service.config.settings import Settings, get_settings
from paragraph_summary_service.models.responses import HealthResponse

router = APIRouter()
SettingsDep = Annotated[Settings, Depends(get_settings)]


@router.get("/health", response_model=HealthResponse)
def health(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        provider_default=settings.llm_provider,
        external_provider_calls_enabled=settings.allow_external_provider_calls,
    )
