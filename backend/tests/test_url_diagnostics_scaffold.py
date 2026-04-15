import os
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Request, status
from fastapi.testclient import TestClient

# Ensure JWT validation module can initialize during imports.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest")

from auth import get_current_user
from main import app
import api.lecture_routes as lecture_routes


@pytest.fixture
def auth_client():
    async def override_current_user(request: Request):
        auth_header = request.headers.get("Authorization", "")
        if auth_header != "Bearer smoke-token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return SimpleNamespace(id=1)

    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _headers() -> dict:
    return {"Authorization": "Bearer smoke-token"}


def test_url_diagnostics_requires_auth(auth_client):
    response = auth_client.post("/api/lectures/url-diagnostics-v1", data={"source_uri": "https://example.com"})

    assert response.status_code == 401
    assert response.json().get("detail") == "Could not validate credentials"


def test_url_diagnostics_reports_unreachable(auth_client, monkeypatch):
    monkeypatch.setattr(
        lecture_routes,
        "_probe_url_availability",
        lambda uri: {"reachable": False, "status_code": None, "error": "timeout"},
    )

    response = auth_client.post(
        "/api/lectures/url-diagnostics-v1",
        data={"source_uri": "https://example.com/article"},
        headers=_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["schema"] == "url-diagnostics-v1"
    assert body["outcome"] == "unreachable"
    assert body["diagnostics"]["code"] == "unreachable"


def test_url_diagnostics_reports_no_transcript_for_video(auth_client, monkeypatch):
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

    response = auth_client.post(
        "/api/lectures/url-diagnostics-v1",
        data={"source_uri": "https://www.youtube.com/watch?v=abc"},
        headers=_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["source_class"] == "video"
    assert body["outcome"] == "no_transcript"
    assert body["diagnostics"]["code"] == "no_transcript"


def test_url_diagnostics_reports_ready_for_youtube_with_transcript(auth_client, monkeypatch):
    monkeypatch.setattr(
        lecture_routes,
        "_probe_url_availability",
        lambda uri: {"reachable": True, "status_code": 200},
    )
    monkeypatch.setattr(
        lecture_routes,
        "_fetch_youtube_transcript_text",
        lambda uri, max_chars=8000: "Transcript snippet",
    )

    response = auth_client.post(
        "/api/lectures/url-diagnostics-v1",
        data={"source_uri": "https://www.youtube.com/watch?v=abc"},
        headers=_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["source_class"] == "video"
    assert body["outcome"] == "ready"
    assert body["diagnostics"]["code"] == "ready"


def test_url_diagnostics_reports_unsupported_for_podcast(auth_client, monkeypatch):
    monkeypatch.setattr(
        lecture_routes,
        "_probe_url_availability",
        lambda uri: {"reachable": True, "status_code": 200},
    )

    response = auth_client.post(
        "/api/lectures/url-diagnostics-v1",
        data={"source_uri": "https://open.spotify.com/episode/xyz"},
        headers=_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["source_class"] == "podcast"
    assert body["outcome"] == "unsupported"
    assert body["diagnostics"]["code"] == "unsupported"


def test_url_diagnostics_reports_ready_for_podcast_feed_with_transcript(auth_client, monkeypatch):
    monkeypatch.setattr(
        lecture_routes,
        "_probe_url_availability",
        lambda uri: {"reachable": True, "status_code": 200},
    )
    monkeypatch.setattr(
        lecture_routes,
        "_fetch_podcast_transcript_text",
        lambda uri, max_chars=8000: "Episode transcript",
    )

    response = auth_client.post(
        "/api/lectures/url-diagnostics-v1",
        data={"source_uri": "https://example.com/feed.xml"},
        headers=_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["source_class"] == "podcast"
    assert body["outcome"] == "ready"
    assert body["diagnostics"]["code"] == "ready"


def test_url_diagnostics_reports_ready_for_web_page(auth_client, monkeypatch):
    monkeypatch.setattr(
        lecture_routes,
        "_probe_url_availability",
        lambda uri: {"reachable": True, "status_code": 200},
    )

    response = auth_client.post(
        "/api/lectures/url-diagnostics-v1",
        data={"source_uri": "https://example.com/post"},
        headers=_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["source_class"] == "web"
    assert body["outcome"] == "ready"
    assert body["diagnostics"]["code"] == "ready"
