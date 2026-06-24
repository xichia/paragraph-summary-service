from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from paragraph_summary_service.config.settings import Settings, get_settings
from paragraph_summary_service.storage.repositories import SummaryRepository

router = APIRouter()
SettingsDep = Annotated[Settings, Depends(get_settings)]


@router.get("/artifacts/{artifact_id}")
def get_artifact(artifact_id: str, settings: SettingsDep) -> FileResponse:
    path = SummaryRepository(settings.summary_db_path).get_artifact_path(artifact_id)
    if path is None or not path.exists():
        raise HTTPException(status_code=404, detail="artifact not found")
    return FileResponse(path, media_type="application/x-ndjson", filename=path.name)
