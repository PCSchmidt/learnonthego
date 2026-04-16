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
    supported_types = set(detail.get("supported_source_types") or [])
    assert {"md", "pdf", "text", "txt"}.issubset(supported_types)
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
    assert "ENABLE_URL_INGESTION_V1=true" in detail.get("hint", "")


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
    assert isinstance(body.get("citations"), list)
    assert len(body.get("citations") or []) >= 1
    assert body["citations"][0].get("source_uri") == "https://example.com/article"
    assert body.get("source_metadata", {}).get("retrieval_method") == "web_fetch"


def test_v2_rejects_url_when_diagnostics_outcome_not_ready(client, monkeypatch):
    monkeypatch.setenv("ENABLE_URL_INGESTION_V1", "true")
    monkeypatch.setattr(
        lecture_routes,
        "_probe_url_availability",
        lambda uri: {"reachable": True, "status_code": 200},
    )
    monkeypatch.setattr(
        lecture_routes,
        "_fetch_youtube_transcript_text",
        lambda uri, max_chars=8000: (_ for _ in ()).throw(ValueError("No captions")),
    )

    payload = {
        **_base_form(),
        "source_type": "url",
        "source_uri": "https://www.youtube.com/watch?v=abc",
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload)
    detail = _assert_v1a_error(response, "url_not_ready")
    assert "transcript" in detail.get("message", "").lower()


def test_v2_accepts_youtube_url_when_transcript_available(client, monkeypatch):
    monkeypatch.setenv("ENABLE_URL_INGESTION_V1", "true")
    monkeypatch.setattr(
        lecture_routes,
        "_probe_url_availability",
        lambda uri: {"reachable": True, "status_code": 200},
    )
    monkeypatch.setattr(
        lecture_routes,
        "_fetch_youtube_transcript_text",
        lambda uri, max_chars=60000: "YouTube transcript text ready for generation.",
    )

    payload = {
        **_base_form(),
        "source_type": "url",
        "source_uri": "https://www.youtube.com/watch?v=abc",
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["contract_version"] == "v1a"
    assert body["source_type"] == "url"
    assert isinstance(body.get("citations"), list)
    assert len(body.get("citations") or []) >= 1
    assert body.get("source_metadata", {}).get("source_class") == "video"
    assert body.get("source_metadata", {}).get("retrieval_method") == "youtube_transcript"


def test_v2_accepts_podcast_feed_url_when_transcript_available(client, monkeypatch):
    monkeypatch.setenv("ENABLE_URL_INGESTION_V1", "true")
    monkeypatch.setattr(
        lecture_routes,
        "_probe_url_availability",
        lambda uri: {"reachable": True, "status_code": 200},
    )
    monkeypatch.setattr(
        lecture_routes,
        "_fetch_podcast_transcript_text",
        lambda uri, max_chars=60000: "Podcast transcript text ready for generation.",
    )

    payload = {
        **_base_form(),
        "source_type": "url",
        "source_uri": "https://example.com/feed.xml",
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["contract_version"] == "v1a"
    assert body["source_type"] == "url"
    assert isinstance(body.get("citations"), list)
    assert len(body.get("citations") or []) >= 1
    assert body.get("source_metadata", {}).get("source_class") == "podcast"
    assert body.get("source_metadata", {}).get("retrieval_method") == "podcast_feed_transcript"


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
    assert detail.get("field") == "document_text|file|source_uri"


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


def test_v2_rejects_url_fetch_failed_for_web_source(client, monkeypatch):
    monkeypatch.setenv("ENABLE_URL_INGESTION_V1", "true")
    monkeypatch.setattr(
        lecture_routes,
        "_probe_url_availability",
        lambda uri: {"reachable": True, "status_code": 200},
    )
    monkeypatch.setattr(
        lecture_routes,
        "_resolve_url_source_text_v1",
        lambda uri, source_class, max_chars=60000: (_ for _ in ()).throw(ValueError("timeout")),
    )

    payload = {
        **_base_form(),
        "source_type": "url",
        "source_uri": "https://example.com/article",
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload)
    detail = _assert_v1a_error(response, "url_fetch_failed")
    assert "Failed to fetch URL content" in detail.get("message", "")


def test_v2_rejects_empty_url_content_after_resolution(client, monkeypatch):
    monkeypatch.setenv("ENABLE_URL_INGESTION_V1", "true")
    monkeypatch.setattr(
        lecture_routes,
        "_probe_url_availability",
        lambda uri: {"reachable": True, "status_code": 200},
    )
    monkeypatch.setattr(
        lecture_routes,
        "_resolve_url_source_text_v1",
        lambda uri, source_class, max_chars=60000: "   ",
    )

    payload = {
        **_base_form(),
        "source_type": "url",
        "source_uri": "https://example.com/article",
    }

    response = client.post("/api/lectures/generate-document-v2", data=payload)
    detail = _assert_v1a_error(response, "empty_url_content")
    assert "empty text" in detail.get("message", "").lower()


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
