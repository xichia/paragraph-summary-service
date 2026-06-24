from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from paragraph_summary_service.config.settings import Settings, get_settings
from paragraph_summary_service.models.requests import ParagraphRecordInput, ParagraphSummaryRequest
from paragraph_summary_service.models.responses import ParagraphSummaryArtifactResponse
from paragraph_summary_service.services.paragraph_summarise import ParagraphSummaryService
from paragraph_summary_service.splitters.lightweight import split_uploaded_text

router = APIRouter()
SettingsDep = Annotated[Settings, Depends(get_settings)]
UploadField = Annotated[UploadFile, File()]
ProviderForm = Annotated[str, Form()]
ModelForm = Annotated[str | None, Form()]
TemplateVersionForm = Annotated[str, Form()]
MaxSummaryTokensForm = Annotated[int, Form()]


@router.post("/paragraph-summaries", response_model=ParagraphSummaryArtifactResponse)
def paragraph_summaries(
    request: ParagraphSummaryRequest,
    settings: SettingsDep,
) -> ParagraphSummaryArtifactResponse:
    return ParagraphSummaryService(settings).summarise_request(request).response


@router.post("/paragraph-summaries/from-file", response_model=ParagraphSummaryArtifactResponse)
async def paragraph_summaries_from_file(
    file: UploadField,
    settings: SettingsDep,
    provider: ProviderForm = "mock",
    model: ModelForm = None,
    template_version: TemplateVersionForm = "paragraph_sentence_batch_v1",
    max_summary_tokens_per_record: MaxSummaryTokensForm = 48,
) -> ParagraphSummaryArtifactResponse:
    filename = file.filename or "upload.txt"
    if not filename.lower().endswith((".txt", ".md")):
        raise HTTPException(status_code=400, detail="only .txt and .md uploads are supported")
    raw = await file.read()
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="upload exceeds configured size limit")
    text = raw.decode("utf-8", errors="replace")
    document_id, records = split_uploaded_text(
        filename=filename,
        content=text,
        content_type=file.content_type or "text/plain",
    )
    if not records:
        raise HTTPException(status_code=400, detail="file did not contain paragraph-like text")
    request = ParagraphSummaryRequest(
        document_id=document_id,
        records=[
            ParagraphRecordInput(
                record_id=record.record_id,
                source_ref=record.source_ref,
                text=record.text,
                checksum=record.checksum,
                metadata=record.metadata,
                provenance=record.provenance,
            )
            for record in records
        ],
        provider=provider,
        model=model,
        template_version=template_version,
        max_summary_tokens_per_record=max_summary_tokens_per_record,
    )
    return ParagraphSummaryService(settings).summarise_request(request).response
