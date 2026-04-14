import os
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Request, status
from fastapi.testclient import TestClient

# Ensure JWT validation module can initialize during imports.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest")

from auth import get_current_user
from main import app
from models.database import get_async_db
import api.lecture_routes as lecture_routes
import api.api_key_routes as api_key_routes


@pytest.fixture
def auth_client(monkeypatch):
    async def override_current_user(request: Request):
        auth_header = request.headers.get("Authorization", "")
        if auth_header != "Bearer smoke-token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return SimpleNamespace(id=1)

    async def override_async_db():
        return None

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_async_db] = override_async_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _v2_payload(*, dry_run: str = "true") -> dict:
    return {
        "document_text": "Feature flag and auth smoke regression",
        "duration": "8",
        "difficulty": "intermediate",
        "llm_provider": "openrouter",
        "llm_model": "openai/gpt-4.1-mini",
        "tts_provider": "elevenlabs",
        "dry_run": dry_run,
    }


def test_v2_endpoint_disabled_returns_404(auth_client, monkeypatch):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "false")

    response = auth_client.post(
        "/api/lectures/generate-document-v2",
        data=_v2_payload(),
        headers={"Authorization": "Bearer smoke-token"},
    )

    assert response.status_code == 404
    # main.py registers a global 404 handler, so exact endpoint detail may be normalized.
    assert response.json().get("detail") in {
        "V2 pipeline is disabled. Set ENABLE_V2_PIPELINE=true to enable.",
        "Endpoint not found",
    }


def test_v2_endpoint_enabled_returns_contract(auth_client, monkeypatch):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")

    response = auth_client.post(
        "/api/lectures/generate-document-v2",
        data=_v2_payload(),
        headers={"Authorization": "Bearer smoke-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["dry_run"] is True
    assert body["key_source"] == "environment"
    assert body["execution_mode"] == "environment"


def test_v2_preview_dry_run_response_shape_contract(auth_client, monkeypatch):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")

    response = auth_client.post(
        "/api/lectures/generate-document-v2",
        data=_v2_payload(),
        headers={"Authorization": "Bearer smoke-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["dry_run"] is True
    assert body["execution_mode"] == "environment"
    assert isinstance(body["script"], str)
    assert body["script"]
    assert isinstance(body.get("preview_script"), dict)
    assert {"title", "content", "duration_minutes", "difficulty"}.issubset(body["preview_script"].keys())
    assert isinstance(body.get("summary"), str)
    assert isinstance(body.get("llm"), dict)
    assert {"provider", "model", "usage"}.issubset(body["llm"].keys())
    assert isinstance(body.get("audio"), dict)
    assert {"provider", "model", "file_path", "bytes_written", "metadata"}.issubset(body["audio"].keys())
    assert isinstance(body.get("script_sections"), list)
    assert isinstance(body.get("citations"), list)


def test_v2_byok_endpoint_enabled_returns_contract(auth_client, monkeypatch):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")

    async def fake_get_user_api_key(db, user_id, provider):
        return "dummy-api-key-for-tests"

    monkeypatch.setattr(lecture_routes, "_get_user_api_key", fake_get_user_api_key)

    response = auth_client.post(
        "/api/lectures/generate-document-v2-byok",
        data=_v2_payload(),
        headers={"Authorization": "Bearer smoke-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["dry_run"] is True
    assert body["key_source"] == "user-encrypted-storage"
    assert body["execution_mode"] == "byok"


@pytest.mark.parametrize(
    "endpoint,expected_key_source,expected_execution_mode",
    [
        ("/api/lectures/generate-document-v2", "environment", "environment"),
        ("/api/lectures/generate-document-v2-byok", "user-encrypted-storage", "byok"),
    ],
)
def test_v2_endpoints_echo_llm_model_in_dry_run_contract(
    auth_client,
    monkeypatch,
    endpoint,
    expected_key_source,
    expected_execution_mode,
):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")

    async def fake_get_user_api_key(db, user_id, provider):
        return "dummy-api-key-for-tests"

    monkeypatch.setattr(lecture_routes, "_get_user_api_key", fake_get_user_api_key)

    response = auth_client.post(
        endpoint,
        data=_v2_payload(),
        headers={"Authorization": "Bearer smoke-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["dry_run"] is True
    assert body["key_source"] == expected_key_source
    assert body["execution_mode"] == expected_execution_mode
    assert body["llm"]["model"] == "openai/gpt-4.1-mini"


@pytest.mark.parametrize(
    "endpoint,expected_execution_mode",
    [
        ("/api/lectures/generate-document-v2", "environment"),
        ("/api/lectures/generate-document-v2-byok", "byok"),
    ],
)
def test_v2_final_generation_contract_includes_execution_mode(
    auth_client,
    monkeypatch,
    endpoint,
    expected_execution_mode,
):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")

    async def fake_get_user_api_key(db, user_id, provider):
        return "dummy-api-key-for-tests"

    monkeypatch.setattr(lecture_routes, "_get_user_api_key", fake_get_user_api_key)

    class FakePipeline:
        async def run(self, **kwargs):
            return {
                "title": "Mocked final generation",
                "script": "Final generated script",
                "llm": {
                    "provider": kwargs.get("llm_provider"),
                    "model": kwargs.get("llm_model") or "mock-model",
                    "usage": {"prompt_tokens": 10, "completion_tokens": 20},
                },
                "audio": {
                    "provider": kwargs.get("tts_provider"),
                    "model": "mock-tts",
                    "file_path": "mock.wav",
                    "bytes_written": 1234,
                    "metadata": {},
                },
            }

    monkeypatch.setattr(lecture_routes, "create_document_pipeline_v2", lambda: FakePipeline())

    response = auth_client.post(
        endpoint,
        data=_v2_payload(dry_run="false"),
        headers={"Authorization": "Bearer smoke-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["execution_mode"] == expected_execution_mode
    assert body["title"] == "Mocked final generation"
    assert body["script"] == "Final generated script"
    assert isinstance(body.get("summary"), str)
    assert isinstance(body.get("script_sections"), list)
    assert len(body["script_sections"]) >= 1
    assert {"id", "heading", "content"}.issubset(body["script_sections"][0].keys())
    assert isinstance(body.get("citations"), list)


def test_v2_requires_auth_header(auth_client, monkeypatch):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")

    response = auth_client.post("/api/lectures/generate-document-v2", data=_v2_payload())

    assert response.status_code == 401
    assert response.json().get("detail") == "Could not validate credentials"


def test_api_key_status_reports_missing_required_keys(auth_client, monkeypatch):
    class FakeApiKeyService:
        async def get_api_key(self, db, user_id, provider):
            return None

    monkeypatch.setattr(api_key_routes, "get_api_key_service", lambda: FakeApiKeyService())

    response = auth_client.get(
        "/api/api-keys/status",
        headers={"Authorization": "Bearer smoke-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["can_generate_lectures"] is False
    assert body["setup_complete"] is False
    assert set(body["missing_keys"]) == {"openrouter", "elevenlabs"}


def test_v2_byok_missing_keys_contract(auth_client, monkeypatch):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")

    async def fake_get_user_api_key(db, user_id, provider):
        return None

    monkeypatch.setattr(lecture_routes, "_get_user_api_key", fake_get_user_api_key)

    response = auth_client.post(
        "/api/lectures/generate-document-v2-byok",
        data=_v2_payload(),
        headers={"Authorization": "Bearer smoke-token"},
    )

    assert response.status_code == 400
    detail = response.json().get("detail", "")
    assert "Missing valid API keys for:" in detail
    assert "openrouter" in detail
    assert "elevenlabs" in detail
