import os
from dataclasses import dataclass
from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Request, status
from fastapi.testclient import TestClient

# Ensure JWT validation module can initialize during imports.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest")

import api.api_key_routes as api_key_routes
from auth import get_current_user
from main import app
from models.database import get_async_db


@dataclass
class StoredKey:
    key_name: str
    created_at: datetime
    is_valid: bool = True


class FakeApiKeyService:
    def __init__(self):
        self._keys: dict[tuple[int, str], str] = {}
        self._meta: dict[tuple[int, str], StoredKey] = {}

    async def store_api_key(self, db, user_id, provider, api_key, key_name=None):
        provider_name = provider.value
        key = (user_id, provider_name)
        self._keys[key] = api_key

        existing = self._meta.get(key)
        if existing:
            existing.key_name = key_name or existing.key_name
            existing.is_valid = True
            return existing

        created = StoredKey(
            key_name=key_name or f"{provider_name.title()} API Key",
            created_at=datetime.utcnow(),
            is_valid=True,
        )
        self._meta[key] = created
        return created

    async def get_api_key(self, db, user_id, provider):
        return self._keys.get((user_id, provider.value))

    async def delete_api_key(self, db, user_id, provider):
        key = (user_id, provider.value)
        existed = key in self._keys
        self._keys.pop(key, None)
        self._meta.pop(key, None)
        return existed

    async def get_user_api_keys_status(self, db, user_id):
        return {
            "openrouter": {
                "has_key": bool(self._keys.get((user_id, "openrouter"))),
                "is_valid": bool(self._keys.get((user_id, "openrouter"))),
            },
            "elevenlabs": {
                "has_key": bool(self._keys.get((user_id, "elevenlabs"))),
                "is_valid": bool(self._keys.get((user_id, "elevenlabs"))),
            },
        }


@pytest.fixture
def api_key_client(monkeypatch):
    fake_service = FakeApiKeyService()

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
    monkeypatch.setattr(api_key_routes, "get_api_key_service", lambda: fake_service)

    with TestClient(app) as test_client:
        yield test_client, fake_service

    app.dependency_overrides.clear()


def _auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer smoke-token"}


def test_api_key_add_replace_delete_lifecycle(api_key_client):
    client, fake_service = api_key_client

    status_initial = client.get("/api/api-keys/status", headers=_auth_headers())
    assert status_initial.status_code == 200
    assert status_initial.json()["setup_complete"] is False
    assert set(status_initial.json()["missing_keys"]) == {"openrouter", "elevenlabs"}

    add_openrouter = client.post(
        "/api/api-keys/",
        json={
            "provider": "openrouter",
            "api_key": "sk-or-v1-test-openrouter-123456",
            "key_name": "OR Key v1",
        },
        headers=_auth_headers(),
    )
    assert add_openrouter.status_code == 200
    assert add_openrouter.json()["provider"] == "openrouter"
    assert add_openrouter.json()["key_name"] == "OR Key v1"

    replace_openrouter = client.post(
        "/api/api-keys/",
        json={
            "provider": "openrouter",
            "api_key": "sk-or-v1-test-openrouter-654321",
            "key_name": "OR Key v2",
        },
        headers=_auth_headers(),
    )
    assert replace_openrouter.status_code == 200
    assert replace_openrouter.json()["provider"] == "openrouter"
    assert replace_openrouter.json()["key_name"] == "OR Key v2"

    # Replace should not duplicate records for the same provider.
    assert len([k for k in fake_service._keys.keys() if k[0] == 1 and k[1] == "openrouter"]) == 1

    status_after_one = client.get("/api/api-keys/status", headers=_auth_headers())
    assert status_after_one.status_code == 200
    assert status_after_one.json()["setup_complete"] is False
    assert status_after_one.json()["missing_keys"] == ["elevenlabs"]

    add_elevenlabs = client.post(
        "/api/api-keys/",
        json={
            "provider": "elevenlabs",
            "api_key": "elevenlabs-test-key-123456",
            "key_name": "EL Key v1",
        },
        headers=_auth_headers(),
    )
    assert add_elevenlabs.status_code == 200
    assert add_elevenlabs.json()["provider"] == "elevenlabs"

    status_ready = client.get("/api/api-keys/status", headers=_auth_headers())
    assert status_ready.status_code == 200
    assert status_ready.json()["setup_complete"] is True
    assert status_ready.json()["missing_keys"] == []

    delete_openrouter = client.delete("/api/api-keys/openrouter", headers=_auth_headers())
    assert delete_openrouter.status_code == 200
    assert delete_openrouter.json()["provider"] == "openrouter"

    status_after_delete = client.get("/api/api-keys/status", headers=_auth_headers())
    assert status_after_delete.status_code == 200
    assert status_after_delete.json()["setup_complete"] is False
    assert status_after_delete.json()["missing_keys"] == ["openrouter"]

    delete_openrouter_again = client.delete("/api/api-keys/openrouter", headers=_auth_headers())
    assert delete_openrouter_again.status_code == 404
    assert delete_openrouter_again.json().get("detail") in {
        "No API key found for provider openrouter",
        "Endpoint not found",
    }
