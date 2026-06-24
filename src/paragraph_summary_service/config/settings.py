from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Paragraph Summary Service"
    app_version: str = "0.1.1"
    llm_provider: str = "mock"
    allow_external_provider_calls: bool = False
    summary_db_path: Path = Path(".local/paragraph_summary.sqlite")
    summary_artifact_dir: Path = Path("output/paragraph_summaries")
    max_records_per_request: int = Field(default=1000, ge=1)
    max_record_chars: int = Field(default=20_000, ge=100)
    max_total_chars: int = Field(default=5_000_000, ge=1000)
    max_upload_bytes: int = Field(default=5_000_000, ge=1000)
    token_chars_per_token: int = Field(default=4, ge=1)
    redaction_version: str = "basic_redaction_v1"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash-lite"
    gemini_input_tpm_limit: int = 250_000
    gemini_safe_input_token_target: int = 225_000
    gemini_requests_per_minute: int = 1
    gemini_timeout_seconds: float = 90.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
