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
from services.pipeline_errors import PipelineExecutionError


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
    assert isinstance(body.get("metadata"), dict)
    policy = body["metadata"].get("duration_policy")
    assert isinstance(policy, dict)
    assert policy.get("schema") == "duration-best-effort-v1"
    assert policy.get("target_duration_minutes") == 8
    assert isinstance(policy.get("estimated_duration_minutes"), (int, float))
    assert isinstance(policy.get("within_tolerance"), bool)
    assert policy.get("status") in {"within_tolerance", "under_target", "over_target"}


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


def test_v2_env_route_prefers_byok_for_paid_when_toggle_enabled(auth_client, monkeypatch):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")
    monkeypatch.setattr(lecture_routes, "_byok_priority_for_paid_enabled", lambda: True)

    async def fake_get_user_api_key(db, user_id, provider):
        return "test-user-key"

    captured = {}

    class StubPipeline:
        async def run(self, **kwargs):
            captured.update(kwargs)
            return {
                "title": "t",
                "script": "s",
                "audio_url": "https://example.com/a.mp3",
                "audio_duration": 100,
                "word_count": 10,
                "estimated_duration": 1,
                "sources": [],
                "llm_provider": kwargs.get("llm_provider"),
                "tts_provider": kwargs.get("tts_provider"),
                "audio_metadata": {},
            }

    monkeypatch.setattr(lecture_routes, "_get_user_api_key", fake_get_user_api_key)
    monkeypatch.setattr(lecture_routes, "create_document_pipeline_v2", lambda: StubPipeline())

    response = auth_client.post(
        "/api/lectures/generate-document-v2",
        data=_v2_payload(dry_run="false"),
        headers={"Authorization": "Bearer smoke-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["execution_mode"] == "byok"
    assert body["key_source"] == "user-encrypted-storage"
    assert body.get("metadata", {}).get("credential_source") == "byok"
    assert captured.get("llm_api_key") == "test-user-key"
    assert captured.get("tts_api_key") == "test-user-key"


def test_v2_env_route_dry_run_stays_environment_when_toggle_enabled(auth_client, monkeypatch):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")
    monkeypatch.setattr(lecture_routes, "_byok_priority_for_paid_enabled", lambda: True)

    response = auth_client.post(
        "/api/lectures/generate-document-v2",
        data=_v2_payload(dry_run="true"),
        headers={"Authorization": "Bearer smoke-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["execution_mode"] == "environment"
    assert body["key_source"] == "environment"


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
    assert isinstance(body.get("metadata"), dict)
    assert body["metadata"].get("credential_source") == expected_execution_mode
    policy = body["metadata"].get("duration_policy")
    assert isinstance(policy, dict)
    assert policy.get("schema") == "duration-best-effort-v1"
    assert policy.get("target_duration_minutes") == 8
    assert isinstance(policy.get("estimated_duration_minutes"), (int, float))
    assert isinstance(policy.get("within_tolerance"), bool)


def test_v2_requires_auth_header(auth_client, monkeypatch):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")

    response = auth_client.post("/api/lectures/generate-document-v2", data=_v2_payload())

    assert response.status_code == 401
    assert response.json().get("detail") == "Could not validate credentials"


def test_v2_final_generation_surfaces_provider_stage_error(auth_client, monkeypatch):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")

    class FakePipeline:
        async def run(self, **kwargs):
            raise PipelineExecutionError(
                stage="llm_generate",
                provider="openrouter",
                message="LLM provider request failed with HTTP 429",
                status_code=429,
                retryable=True,
                cause_type="HTTPStatusError",
            )

    monkeypatch.setattr(lecture_routes, "create_document_pipeline_v2", lambda: FakePipeline())

    response = auth_client.post(
        "/api/lectures/generate-document-v2",
        data=_v2_payload(dry_run="false"),
        headers={"Authorization": "Bearer smoke-token"},
    )

    assert response.status_code == 502
    detail = response.json().get("detail", {})
    assert detail.get("schema") == "v2-generation-error-v1"
    assert detail.get("code") == "provider_execution_failed"
    assert detail.get("stage") == "llm_generate"
    assert detail.get("provider") == "openrouter"
    assert detail.get("execution_mode") == "environment"
    assert detail.get("provider_http_status") == 429
    assert detail.get("retryable") is True


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
    detail = response.json().get("detail", {})
    assert detail.get("schema") == "byok-key-error-v1"
    assert detail.get("code") == "missing_or_invalid_provider_key"
    assert detail.get("execution_mode") == "byok"
    assert set(detail.get("providers", [])) == {"openrouter", "elevenlabs"}


def test_v2_byok_unsupported_provider_contract(auth_client, monkeypatch):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")

    bad_payload = _v2_payload()
    bad_payload["llm_provider"] = "openai"

    response = auth_client.post(
        "/api/lectures/generate-document-v2-byok",
        data=bad_payload,
        headers={"Authorization": "Bearer smoke-token"},
    )

    assert response.status_code == 400
    detail = response.json().get("detail", {})
    assert detail.get("schema") == "byok-key-error-v1"
    assert detail.get("code") == "unsupported_provider"
    assert detail.get("execution_mode") == "byok"
    assert detail.get("providers") == ["openai"]
