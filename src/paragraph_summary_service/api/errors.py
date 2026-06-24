from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from paragraph_summary_service.models.responses import ErrorDetail
from paragraph_summary_service.providers.base import ProviderError
from paragraph_summary_service.safety.limits import RequestLimitError


async def provider_error_handler(request: Request, exc: ProviderError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": ErrorDetail(code=exc.error_code, message=str(exc)).model_dump()},
    )


async def request_limit_error_handler(request: Request, exc: RequestLimitError) -> JSONResponse:
    return JSONResponse(
        status_code=413,
        content={"error": ErrorDetail(code="REQUEST_TOO_LARGE", message=str(exc)).model_dump()},
    )


async def key_error_handler(request: Request, exc: KeyError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": ErrorDetail(code="UNKNOWN_TEMPLATE", message=str(exc)).model_dump()},
    )
