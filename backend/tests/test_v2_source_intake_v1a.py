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


def _base_form() -> dict:
    return {
        "duration": "8",
        "difficulty": "intermediate",
        "llm_provider": "openrouter",
        "tts_provider": "elevenlabs",
        "dry_run": "true",
    }


def _assert_v1a_error(response, expected_code: str) -> dict:
    assert response.status_code == 400
    detail = response.json().get("detail")
    assert isinstance(detail, dict)
    assert detail.get("schema") == "source-intake-error-v1"
    assert detail.get("contract_version") == "v1a"
    assert detail.get("code") == expected_code
    assert detail.get("supported_source_types") == ["md", "pdf", "text", "txt"]
    return detail


def test_v2_accepts_pasted_text_with_source_type(client):
    payload = {
        **_base_form(),
        "source_type": "text",
        "document_text": "This is a pasted text payload for the v1a source contract.",
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["contract_version"] == "v1a"
    assert body["source_type"] == "text"


def test_v2_accepts_txt_file_upload(client):
    payload = {
        **_base_form(),
        "source_type": "txt",
    }
    files = {
        "file": ("notes.txt", b"Plain text notes for source intake testing.", "text/plain"),
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload, files=files)
    assert response.status_code == 200

    body = response.json()
    assert body["contract_version"] == "v1a"
    assert body["source_type"] == "txt"


def test_v2_accepts_md_file_upload(client):
    payload = {
        **_base_form(),
        "source_type": "md",
    }
    files = {
        "file": ("outline.md", b"# Topic\n\n- Point one\n- Point two", "text/markdown"),
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload, files=files)
    assert response.status_code == 200

    body = response.json()
    assert body["contract_version"] == "v1a"
    assert body["source_type"] == "md"


def test_v2_rejects_unsupported_source_type(client):
    payload = {
        **_base_form(),
        "source_type": "url",
        "document_text": "https://example.com/some-article",
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload)
    detail = _assert_v1a_error(response, "unsupported_source_type")
    assert "deferred to the next slice" in detail.get("hint", "")


def test_v2_accepts_ready_url_when_feature_flag_enabled(client, monkeypatch):
    monkeypatch.setenv("ENABLE_URL_INGESTION_V1", "true")
    monkeypatch.setattr(
        lecture_routes,
        "_probe_url_availability",
        lambda uri: {"reachable": True, "status_code": 200},
    )
    monkeypatch.setattr(
        lecture_routes,
        "_fetch_url_source_text",
        lambda uri, max_chars=60000: "Fetched URL text content for dry-run generation.",
    )

    payload = {
        **_base_form(),
        "source_type": "url",
        "source_uri": "https://example.com/article",
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["contract_version"] == "v1a"
    assert body["source_type"] == "url"
    assert body["source"] == "https://example.com/article"


def test_v2_rejects_url_when_diagnostics_outcome_not_ready(client, monkeypatch):
    monkeypatch.setenv("ENABLE_URL_INGESTION_V1", "true")
    monkeypatch.setattr(
        lecture_routes,
        "_probe_url_availability",
        lambda uri: {"reachable": True, "status_code": 200},
    )

    payload = {
        **_base_form(),
        "source_type": "url",
        "source_uri": "https://www.youtube.com/watch?v=abc",
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload)
    detail = _assert_v1a_error(response, "url_not_ready")
    assert "Video transcript ingestion" in detail.get("message", "")


def test_v2_rejects_unsupported_file_extension(client):
    payload = {
        **_base_form(),
    }
    files = {
        "file": (
            "notes.docx",
            b"Not a supported upload type for v1a.",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload, files=files)
    detail = _assert_v1a_error(response, "unsupported_file_extension")
    assert "Unsupported file type" in detail.get("message", "")
    assert ".txt, .md, .pdf" in detail.get("message", "")


def test_v2_rejects_source_type_and_file_mismatch(client):
    payload = {
        **_base_form(),
        "source_type": "pdf",
    }
    files = {
        "file": ("notes.txt", b"Mismatch on purpose.", "text/plain"),
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload, files=files)
    detail = _assert_v1a_error(response, "source_type_input_mismatch")
    assert "does not match uploaded file type" in detail.get("message", "")


def test_v2_rejects_missing_all_sources(client):
    payload = {
        **_base_form(),
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload)
    detail = _assert_v1a_error(response, "invalid_source_input_combination")
    assert detail.get("field") == "document_text|file"


def test_v2_rejects_text_file_too_large(client):
    payload = {
        **_base_form(),
        "source_type": "txt",
    }
    files = {
        "file": ("large.txt", b"a" * (2 * 1024 * 1024 + 1), "text/plain"),
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload, files=files)
    detail = _assert_v1a_error(response, "file_too_large")
    assert detail.get("max_bytes") == 2 * 1024 * 1024


def test_v2_rejects_non_utf8_text_upload(client):
    payload = {
        **_base_form(),
        "source_type": "txt",
    }
    files = {
        "file": ("bad-encoding.txt", b"\xff\xfe\xfa", "text/plain"),
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload, files=files)
    _assert_v1a_error(response, "invalid_text_encoding")


def test_v2_byok_accepts_txt_upload_with_contract(client, monkeypatch):
    async def fake_get_user_api_key(db, user_id, provider):
        return "dummy-key"

    monkeypatch.setattr(lecture_routes, "_get_user_api_key", fake_get_user_api_key)

    payload = {
        **_base_form(),
        "source_type": "txt",
    }
    files = {
        "file": ("notes.txt", b"BYOK text upload for contract check.", "text/plain"),
    }

    response = client.post("/api/lectures/generate-document-v2-byok", data=payload, files=files)
    assert response.status_code == 200

    body = response.json()
    assert body["contract_version"] == "v1a"
    assert body["source_type"] == "txt"
    assert body["key_source"] == "user-encrypted-storage"
