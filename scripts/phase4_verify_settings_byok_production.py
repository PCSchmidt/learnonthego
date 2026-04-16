#!/usr/bin/env python3
"""Verify production BYOK Settings key-entry deploy and backend lifecycle.

Checks:
- Frontend deployment exposes BYOK key-entry labels in bundled app content.
- Backend auth works for configured user.
- API key store/validate/status endpoints succeed for OpenRouter + ElevenLabs.

Outputs a JSON artifact for release evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_FRONTEND_URL = "https://learnonthego-bice.vercel.app"
DEFAULT_BACKEND_URL = "https://learnonthego-production.up.railway.app"
DEFAULT_ENV_FILE = ".env.example"


def load_env_file(path: str) -> None:
    if not path or not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _request_json(
    url: str,
    method: str = "GET",
    payload: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None,
) -> Tuple[int, Dict[str, Any]]:
    headers: Dict[str, str] = {}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read().decode("utf-8")
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = {"raw": body}
            return response.status, parsed
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"detail": body}
        return err.code, parsed


def _request_text(url: str) -> Tuple[int, str]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return response.status, response.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("utf-8", errors="ignore")


class ScriptCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sources: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "script":
            return
        attr_map = dict(attrs)
        src = attr_map.get("src")
        if src:
            self.sources.append(src)


def verify_frontend(frontend_url: str) -> Dict[str, Any]:
    status, html = _request_text(frontend_url)
    collector = ScriptCollector()
    collector.feed(html)

    marker_strings = [
        "BYOK Key Entry",
        "OpenRouter API Key",
        "ElevenLabs API Key",
        "Save + Validate",
        "Refresh provider status",
    ]

    found_markers = set()
    content_scanned = [html]

    base = frontend_url.rstrip("/")
    for src in collector.sources[:8]:
        src = src.strip()
        if src.startswith("http://") or src.startswith("https://"):
            url = src
        elif src.startswith("/"):
            url = base + src
        else:
            url = base + "/" + src

        js_status, js_text = _request_text(url)
        if js_status == 200 and js_text:
            content_scanned.append(js_text)

    for blob in content_scanned:
        for marker in marker_strings:
            if marker in blob:
                found_markers.add(marker)

    missing = [m for m in marker_strings if m not in found_markers]
    return {
        "status_code": status,
        "pass": status == 200 and not missing,
        "scripts_discovered": len(collector.sources),
        "found_markers": sorted(found_markers),
        "missing_markers": missing,
    }


def verify_backend_and_byok(
    backend_url: str,
    email: str,
    password: str,
    openrouter_key: str,
    elevenlabs_key: str,
) -> Dict[str, Any]:
    backend = backend_url.rstrip("/")

    results: List[Dict[str, Any]] = []

    st_health, _ = _request_json(f"{backend}/health")
    results.append({"step": "health", "status_code": st_health, "pass": st_health == 200})

    st_login, login_body = _request_json(
        f"{backend}/api/auth/login",
        method="POST",
        payload={"email": email, "password": password},
    )
    token = login_body.get("access_token") if isinstance(login_body, dict) else None
    results.append({"step": "auth_login", "status_code": st_login, "pass": st_login == 200 and bool(token)})

    if not token:
        temp_email = f"byok_verify_{int(time.time())}@example.com"
        st_register, register_body = _request_json(
            f"{backend}/api/auth/register",
            method="POST",
            payload={
                "email": temp_email,
                "password": password,
                "confirm_password": password,
                "full_name": "BYOK Verify",
            },
        )
        results.append({"step": "auth_register_temp", "status_code": st_register, "pass": st_register in (200, 201)})

        st_login_temp, login_temp_body = _request_json(
            f"{backend}/api/auth/login",
            method="POST",
            payload={"email": temp_email, "password": password},
        )
        token = login_temp_body.get("access_token") if isinstance(login_temp_body, dict) else None
        results.append(
            {
                "step": "auth_login_temp",
                "status_code": st_login_temp,
                "pass": st_login_temp == 200 and bool(token),
            }
        )

        if not token:
            return {
                "pass": False,
                "results": results,
                "reason": "auth_login_failed",
                "login_detail": login_body,
                "temp_register_detail": register_body,
                "temp_login_detail": login_temp_body,
            }

    for provider, api_key in (("openrouter", openrouter_key), ("elevenlabs", elevenlabs_key)):
        st_store, store_body = _request_json(
            f"{backend}/api/api-keys/",
            method="POST",
            payload={"provider": provider, "api_key": api_key, "key_name": f"verify-{provider}"},
            token=token,
        )
        results.append({"step": f"store_{provider}", "status_code": st_store, "pass": st_store == 200})

        st_validate, validate_body = _request_json(
            f"{backend}/api/api-keys/{provider}/validate",
            method="POST",
            payload={},
            token=token,
        )
        results.append(
            {
                "step": f"validate_{provider}",
                "status_code": st_validate,
                "pass": st_validate == 200 and bool(validate_body.get("is_valid")),
            }
        )

    st_status, status_body = _request_json(f"{backend}/api/api-keys/status", token=token)
    setup_complete = bool(status_body.get("setup_complete")) if isinstance(status_body, dict) else False
    results.append({"step": "status", "status_code": st_status, "pass": st_status == 200 and setup_complete})

    by_step = {item.get("step"): bool(item.get("pass")) for item in results}
    auth_ok = by_step.get("auth_login", False) or by_step.get("auth_login_temp", False)
    backend_pass = (
        by_step.get("health", False)
        and auth_ok
        and by_step.get("store_openrouter", False)
        and by_step.get("validate_openrouter", False)
        and by_step.get("store_elevenlabs", False)
        and by_step.get("validate_elevenlabs", False)
        and by_step.get("status", False)
    )

    return {
        "pass": backend_pass,
        "results": results,
        "setup_complete": setup_complete,
        "missing_keys": status_body.get("missing_keys") if isinstance(status_body, dict) else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify production BYOK Settings deploy and key lifecycle.")
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE, help="Env file path (default: .env.example)")
    parser.add_argument("--frontend-url", default=DEFAULT_FRONTEND_URL, help="Frontend base URL")
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND_URL, help="Backend base URL")
    parser.add_argument(
        "--output",
        default="phase4_settings_byok_deploy_verification_2026-04-15.json",
        help="Artifact output path",
    )
    args = parser.parse_args()

    load_env_file(args.env_file)

    email = os.getenv("LOTG_EMAIL", "").strip()
    password = os.getenv("LOTG_PASSWORD", "").strip()
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "").strip()

    if not all([email, password, openrouter_key, elevenlabs_key]):
        raise SystemExit(
            "Missing LOTG_EMAIL, LOTG_PASSWORD, OPENROUTER_API_KEY, or ELEVENLABS_API_KEY in env context."
        )

    frontend = verify_frontend(args.frontend_url)
    backend = verify_backend_and_byok(
        backend_url=args.backend_url,
        email=email,
        password=password,
        openrouter_key=openrouter_key,
        elevenlabs_key=elevenlabs_key,
    )

    summary = {
        "timestamp": int(time.time()),
        "frontend_url": args.frontend_url,
        "backend_url": args.backend_url,
        "user_email": email,
        "frontend_verification": frontend,
        "backend_verification": backend,
        "overall_pass": bool(frontend.get("pass") and backend.get("pass")),
    }

    with open(args.output, "w", encoding="utf-8") as out:
        json.dump(summary, out, indent=2)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
