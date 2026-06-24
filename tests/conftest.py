from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SUMMARY_DB_PATH", str(tmp_path / "paragraph_summary.sqlite"))
    monkeypatch.setenv("SUMMARY_ARTIFACT_DIR", str(tmp_path / "artifacts"))
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("ALLOW_EXTERNAL_PROVIDER_CALLS", "false")
    from paragraph_summary_service.config import settings as settings_module

    settings_module.get_settings.cache_clear()
    app_module = importlib.import_module("paragraph_summary_service.api.app")
    app = app_module.create_app()
    with TestClient(app) as test_client:
        yield test_client
    settings_module.get_settings.cache_clear()
