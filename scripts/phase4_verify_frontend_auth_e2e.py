#!/usr/bin/env python3
"""Verify production frontend authenticated-flow polish with backend e2e checks.

Checks:
- Deployed frontend bundle exposes key authenticated journey markers.
- Backend authenticated flow works: login -> me -> preview -> confirm -> playback probe.

Outputs a JSON artifact that can be referenced in PROGRESS as release evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_FRONTEND_URL = "https://learnonthego-bice.vercel.app"
DEFAULT_BACKEND_URL = "https://learnonthego-production.up.railway.app"
DEFAULT_ENV_FILE = ".env.walkthrough"


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
    base_url: str,
    path: str,
    method: str = "GET",
    payload: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None,
) -> Tuple[int, Dict[str, Any]]:
    url = f"{base_url.rstrip('/')}{path}"
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


def _request_form(
    base_url: str,
    path: str,
    payload: Dict[str, Any],
    token: Optional[str] = None,
) -> Tuple[int, Dict[str, Any]]:
    url = f"{base_url.rstrip('/')}{path}"
    encoded = urllib.parse.urlencode(payload).encode("utf-8")
    headers: Dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=encoded, headers=headers, method="POST")
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


def _request_status(url: str, token: Optional[str] = None) -> int:
    headers: Dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return response.status
    except urllib.error.HTTPError as err:
        return err.code


class ScriptCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sources: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "script":
            return
        src = dict(attrs).get("src")
        if src:
            self.sources.append(src)


def verify_frontend_markers(frontend_url: str) -> Dict[str, Any]:
    status, html = _request_text(frontend_url)
    collector = ScriptCollector()
    collector.feed(html)

    marker_strings = [
        "LearnOnTheGo",
        "Create Account",
        "Create Premium Lecture",
        "Lecture Player",
        "Settings",
        "Lecture Library",
        "Create New Lecture",
        "Lecture Composer",
    ]

    blobs = [html]
    base = frontend_url.rstrip("/")
    for src in collector.sources[:12]:
        if src.startswith("http://") or src.startswith("https://"):
            script_url = src
        elif src.startswith("/"):
            script_url = f"{base}{src}"
        else:
            script_url = f"{base}/{src}"

        js_status, js_text = _request_text(script_url)
        if js_status == 200 and js_text:
            blobs.append(js_text)

    found = set()
    for blob in blobs:
        for marker in marker_strings:
            if marker in blob:
                found.add(marker)

    missing = [marker for marker in marker_strings if marker not in found]
    return {
        "status_code": status,
        "scripts_discovered": len(collector.sources),
        "found_markers": sorted(found),
        "missing_markers": missing,
        "pass": status == 200 and not missing,
    }


def verify_backend_authenticated_flow(
    backend_url: str,
    email: str,
    password: str,
    token: str,
    openrouter_key: str,
    elevenlabs_key: str,
    paid: bool,
    llm_model: str,
) -> Dict[str, Any]:
    base = backend_url.rstrip("/")
    results: List[Dict[str, Any]] = []

    st_health, _ = _request_json(base, "/health")
    results.append({"step": "health", "status_code": st_health, "pass": st_health == 200})

    auth_token = token.strip() if token else ""
    login_body: Dict[str, Any] = {}
    if not auth_token and email and password:
        st_login, login_body = _request_json(
            base,
            "/api/auth/login",
            method="POST",
            payload={"email": email, "password": password},
        )
        auth_token = login_body.get("access_token") if isinstance(login_body, dict) else ""
        results.append(
            {
                "step": "auth_login",
                "status_code": st_login,
                "pass": st_login == 200 and bool(auth_token),
            }
        )

    if not auth_token:
        temp_email = f"frontend_flow_{int(time.time())}@example.com"
        temp_password = password or "Phase4Pass123!"
        st_register, register_body = _request_json(
            base,
            "/api/auth/register",
            method="POST",
            payload={
                "email": temp_email,
                "password": temp_password,
                "confirm_password": temp_password,
                "full_name": "Frontend Flow Verify",
            },
        )
        results.append({"step": "auth_register_temp", "status_code": st_register, "pass": st_register in (200, 201)})

        st_login_temp, login_temp_body = _request_json(
            base,
            "/api/auth/login",
            method="POST",
            payload={"email": temp_email, "password": temp_password},
        )
        auth_token = login_temp_body.get("access_token") if isinstance(login_temp_body, dict) else ""
        results.append(
            {
                "step": "auth_login_temp",
                "status_code": st_login_temp,
                "pass": st_login_temp == 200 and bool(auth_token),
            }
        )

        if not auth_token:
            return {
                "pass": False,
                "results": results,
                "reason": "auth_login_failed",
                "login_detail": login_body,
                "temp_register_detail": register_body,
                "temp_login_detail": login_temp_body,
            }

    st_me, me_body = _request_json(base, "/api/auth/me", token=auth_token)
    results.append({"step": "auth_me", "status_code": st_me, "pass": st_me == 200 and bool(me_body.get("email"))})

    if paid:
        provider_keys = {
            "openrouter": openrouter_key.strip() if openrouter_key else "",
            "elevenlabs": elevenlabs_key.strip() if elevenlabs_key else "",
        }
        if all(provider_keys.values()):
            for provider, api_key in provider_keys.items():
                st_store, _ = _request_json(
                    base,
                    "/api/api-keys/",
                    method="POST",
                    payload={"provider": provider, "api_key": api_key, "key_name": f"frontend-paid-{provider}"},
                    token=auth_token,
                )
                results.append(
                    {
                        "step": f"store_{provider}",
                        "status_code": st_store,
                        "pass": st_store == 200,
                    }
                )

                st_validate, validate_body = _request_json(
                    base,
                    f"/api/api-keys/{provider}/validate",
                    method="POST",
                    payload={},
                    token=auth_token,
                )
                results.append(
                    {
                        "step": f"validate_{provider}",
                        "status_code": st_validate,
                        "pass": st_validate == 200 and bool(validate_body.get("is_valid")),
                    }
                )
        else:
            results.append(
                {
                    "step": "byok_key_bootstrap",
                    "status_code": None,
                    "pass": False,
                    "detail": "Missing OPENROUTER_API_KEY or ELEVENLABS_API_KEY in env context.",
                }
            )

    preview_payload = {
        "source_type": "text",
        "document_text": "Phase 4 frontend polish verification preview.",
        "duration": 10,
        "difficulty": "intermediate",
        "llm_provider": "openrouter",
        "tts_provider": "elevenlabs",
        "dry_run": True,
    }
    st_preview, preview_body = _request_form(
        base,
        "/api/lectures/generate-document-v2",
        payload=preview_payload,
        token=auth_token,
    )
    results.append(
        {
            "step": "create_preview_dry_run",
            "status_code": st_preview,
            "pass": st_preview == 200 and bool(preview_body.get("dry_run")),
        }
    )

    audio_url = None
    if paid:
        confirm_payload = {
            "source_type": "text",
            "document_text": "Phase 4 frontend polish verification confirm.",
            "duration": 10,
            "difficulty": "intermediate",
            "llm_provider": "openrouter",
            "tts_provider": "elevenlabs",
            "dry_run": False,
        }
        if llm_model.strip():
            confirm_payload["llm_model"] = llm_model.strip()
        st_confirm, confirm_body = _request_form(
            base,
            "/api/lectures/generate-document-v2-byok",
            payload=confirm_payload,
            token=auth_token,
        )
        audio_url = confirm_body.get("audio_url") if isinstance(confirm_body, dict) else None
        results.append(
            {
                "step": "confirm_generation",
                "status_code": st_confirm,
                "pass": st_confirm == 200 and bool(audio_url),
                "has_audio_url": bool(audio_url),
                "detail": confirm_body if st_confirm != 200 else None,
            }
        )

        playback_pass = False
        playback_status: Optional[int] = None
        playback_status_auth: Optional[int] = None
        if audio_url and isinstance(audio_url, str):
            if audio_url.startswith("http://") or audio_url.startswith("https://"):
                probe_url = audio_url
            else:
                probe_url = f"{base}{audio_url if audio_url.startswith('/') else '/' + audio_url}"
            playback_status = _request_status(probe_url)
            if playback_status == 200:
                playback_pass = True
            else:
                playback_status_auth = _request_status(probe_url, token=auth_token)
                playback_pass = playback_status_auth == 200

        results.append(
            {
                "step": "playback_probe",
                "status_code": playback_status,
                "status_code_auth": playback_status_auth,
                "pass": playback_pass,
            }
        )

    by_step = {item["step"]: bool(item["pass"]) for item in results}
    auth_ok = by_step.get("auth_login", False) or by_step.get("auth_login_temp", False)
    flow_pass = (
        by_step.get("health", False)
        and auth_ok
        and by_step.get("auth_me", False)
        and by_step.get("create_preview_dry_run", False)
    )
    if paid:
        flow_pass = flow_pass and by_step.get("confirm_generation", False) and by_step.get("playback_probe", False)

    return {
        "pass": flow_pass,
        "paid": paid,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify frontend authenticated-flow polish and backend e2e checks.")
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE, help="Env file path (default: .env.walkthrough)")
    parser.add_argument("--frontend-url", default=DEFAULT_FRONTEND_URL, help="Frontend base URL")
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND_URL, help="Backend base URL")
    parser.add_argument("--token", default="", help="Optional bearer token for authenticated checks")
    parser.add_argument("--llm-model", default="", help="Optional explicit LLM model ID for paid confirm step")
    parser.add_argument("--paid", action="store_true", help="Require paid confirm + playback probe")
    parser.add_argument(
        "--output",
        default="phase4_frontend_auth_e2e_verification_2026-04-15.json",
        help="Artifact output path",
    )
    args = parser.parse_args()

    load_env_file(args.env_file)

    email = os.getenv("LOTG_EMAIL", "").strip()
    password = os.getenv("LOTG_PASSWORD", "").strip()
    token = args.token.strip() or os.getenv("LOTG_TOKEN", "").strip()
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "").strip()

    frontend = verify_frontend_markers(args.frontend_url)
    backend = verify_backend_authenticated_flow(
        backend_url=args.backend_url,
        email=email,
        password=password,
        token=token,
        openrouter_key=openrouter_key,
        elevenlabs_key=elevenlabs_key,
        paid=args.paid,
        llm_model=args.llm_model,
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
