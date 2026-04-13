import os
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

# Ensure JWT validation module can initialize during imports.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest")

from auth import get_current_user
from main import app
from models.database import get_async_db
import api.lecture_routes as lecture_routes


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("ENABLE_V2_PIPELINE", "true")

    async def override_current_user():
        return SimpleNamespace(id=1)

    async def override_async_db():
        return None

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_async_db] = override_async_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_generate_document_v2_coerces_form_types(client):
    response = client.post(
        "/api/lectures/generate-document-v2",
        data={
            "document_text": "Typed form coercion regression check",
            "duration": "8",
            "difficulty": "intermediate",
            "llm_provider": "openrouter",
            "tts_provider": "elevenlabs",
            "dry_run": "true",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is True
    assert body["duration"] == 8
    assert isinstance(body["duration"], int)


def test_generate_document_v2_byok_coerces_form_types(client, monkeypatch):
    async def fake_get_user_api_key(db, user_id, provider):
        return "dummy-key"

    monkeypatch.setattr(lecture_routes, "_get_user_api_key", fake_get_user_api_key)

    response = client.post(
        "/api/lectures/generate-document-v2-byok",
        data={
            "document_text": "Typed form coercion regression check",
            "duration": "8",
            "difficulty": "intermediate",
            "llm_provider": "openrouter",
            "tts_provider": "elevenlabs",
            "dry_run": "true",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is True
    assert body["duration"] == 8
    assert isinstance(body["duration"], int)
    assert body["key_source"] == "user-encrypted-storage"
