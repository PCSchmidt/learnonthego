#!/usr/bin/env python3
"""Lightweight smoke test for V2 lecture endpoints using dry-run mode.

This script validates response contracts for both V2 endpoints without invoking
paid LLM/TTS generation.
"""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


BASE_URL = os.getenv("LOTG_BASE_URL", "http://localhost:8000").rstrip("/")
EMAIL = os.getenv("LOTG_EMAIL")
PASSWORD = os.getenv("LOTG_PASSWORD")
TOKEN = os.getenv("LOTG_TOKEN")
STRICT_BYOK = os.getenv("LOTG_STRICT_BYOK", "false").lower() == "true"
REQUEST_TIMEOUT_SECONDS = float(os.getenv("LOTG_TIMEOUT_SECONDS", "8"))


class SmokeError(Exception):
    pass


def post_json(path: str, payload: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    return _read_response(req)


def post_form(path: str, payload: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"
    body = urllib.parse.urlencode(payload).encode("utf-8")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    return _read_response(req)


def get_path(path: str) -> Dict[str, Any]:
    req = urllib.request.Request(f"{BASE_URL}{path}", method="GET")
    return _read_response(req)


def _read_response(req: urllib.request.Request) -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            raw = response.read().decode("utf-8")
            return {"ok": True, "status": response.status, "data": json.loads(raw)}
    except urllib.error.HTTPError as err:
        raw = err.read().decode("utf-8")
        data: Dict[str, Any]
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"detail": raw}
        return {"ok": False, "status": err.code, "data": data}
    except (urllib.error.URLError, TimeoutError, socket.timeout) as err:
        raise SmokeError(
            f"Network error calling {req.full_url} (timeout={REQUEST_TIMEOUT_SECONDS}s): {err}"
        )


def verify_backend_reachable() -> None:
    health = get_path("/health")
    if not health["ok"]:
        raise SmokeError(
            f"Backend preflight failed at /health ({health['status']}): {health['data']}"
        )


def get_access_token() -> str:
    if TOKEN:
        return TOKEN

    if not EMAIL or not PASSWORD:
        raise SmokeError(
            "Set LOTG_TOKEN or both LOTG_EMAIL and LOTG_PASSWORD to authenticate smoke tests."
        )

    login_payload = {"email": EMAIL, "password": PASSWORD}
    response = post_json("/api/auth/login", login_payload)
    if not response["ok"]:
        raise SmokeError(f"Login failed ({response['status']}): {response['data']}")

    token = response["data"].get("access_token")
    if not token:
        raise SmokeError("Login response did not include access_token")

    return token


def validate_success_contract(name: str, data: Dict[str, Any], expected_key_source: str) -> None:
    required_top = ["success", "dry_run", "title", "script", "llm", "audio", "key_source"]
    missing_top = [k for k in required_top if k not in data]
    if missing_top:
        raise SmokeError(f"{name}: missing top-level keys: {missing_top}")

    if data.get("success") is not True:
        raise SmokeError(f"{name}: success is not true")

    if data.get("dry_run") is not True:
        raise SmokeError(f"{name}: dry_run is not true")

    if data.get("key_source") != expected_key_source:
        raise SmokeError(
            f"{name}: expected key_source={expected_key_source}, got {data.get('key_source')}"
        )

    llm = data.get("llm", {})
    audio = data.get("audio", {})

    for key in ["provider", "model", "usage"]:
        if key not in llm:
            raise SmokeError(f"{name}: llm.{key} missing")

    for key in ["provider", "model", "file_path", "bytes_written", "metadata"]:
        if key not in audio:
            raise SmokeError(f"{name}: audio.{key} missing")


def main() -> int:
    print(f"Using base URL: {BASE_URL} (timeout={REQUEST_TIMEOUT_SECONDS}s)")
    print("Checking backend health...")
    verify_backend_reachable()

    print("Authenticating...")
    token = get_access_token()

    shared_form = {
        "document_text": "Dry-run smoke test document about machine learning fundamentals.",
        "duration": 8,
        "difficulty": "intermediate",
        "llm_provider": "openrouter",
        "tts_provider": "elevenlabs",
        "dry_run": "true",
    }

    print("Checking env-key V2 endpoint...")
    env_result = post_form("/api/lectures/generate-document-v2", shared_form, token=token)
    if not env_result["ok"]:
        raise SmokeError(
            f"env-key endpoint failed ({env_result['status']}): {env_result['data']}"
        )
    validate_success_contract("env-key endpoint", env_result["data"], "environment")
    print("PASS: /api/lectures/generate-document-v2 contract validated")

    print("Checking BYOK V2 endpoint...")
    byok_result = post_form("/api/lectures/generate-document-v2-byok", shared_form, token=token)
    if byok_result["ok"]:
        validate_success_contract("byok endpoint", byok_result["data"], "user-encrypted-storage")
        print("PASS: /api/lectures/generate-document-v2-byok contract validated")
    else:
        detail = str(byok_result["data"].get("detail", ""))
        missing_keys_error = byok_result["status"] == 400 and "Missing valid API keys" in detail
        if missing_keys_error and not STRICT_BYOK:
            print("WARN: BYOK endpoint reachable but user keys missing; contract test skipped.")
        else:
            raise SmokeError(
                f"byok endpoint failed ({byok_result['status']}): {byok_result['data']}"
            )

    print("V2 smoke test completed successfully.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SmokeError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
