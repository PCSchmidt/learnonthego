#!/usr/bin/env python3
"""Phase 4 walkthrough runner with strict paid-request guard.

Default behavior is no-cost validation only.
Paid generation requires BOTH:
- --paid flag
- LOTG_ALLOW_PAID_CHECKS=true
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional, Tuple


DEFAULT_BASE_URL = "https://learnonthego-production.up.railway.app"
DEFAULT_PASSWORD = "Phase4Pass123!"
PAID_GUARD_ENV = "LOTG_ALLOW_PAID_CHECKS"


def _load_env_file(env_file: str) -> None:
    """Load KEY=VALUE pairs from an env file into process environment.

    Existing environment variables are not overwritten.
    """
    if not env_file:
        return

    if not os.path.exists(env_file):
        return

    with open(env_file, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


def _post_json(base_url: str, path: str, payload: Dict[str, Any], token: Optional[str] = None) -> Tuple[int, Dict[str, Any]]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"detail": body}
        return err.code, parsed


def _post_form(base_url: str, path: str, payload: Dict[str, Any], token: Optional[str] = None) -> Tuple[int, Dict[str, Any]]:
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        f"{base_url}{path}",
        data=urllib.parse.urlencode(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"detail": body}
        return err.code, parsed


def _get_json(base_url: str, path: str, token: Optional[str] = None) -> Tuple[int, Dict[str, Any]]:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(f"{base_url}{path}", headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
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


def _check_paid_guard_or_exit() -> None:
    allow_paid = os.getenv(PAID_GUARD_ENV, "false").lower() == "true"
    if not allow_paid:
        raise SystemExit(
            f"Paid mode blocked. Set {PAID_GUARD_ENV}=true explicitly to enable non-dry-run requests."
        )


def run_walkthrough(base_url: str, output_path: str, paid: bool) -> Dict[str, Any]:
    if paid:
        _check_paid_guard_or_exit()

    timestamp = int(time.time())
    email = f"phase4_{timestamp}@example.com"

    results = []

    # No-cost checks first.
    st, health = _get_json(base_url, "/health")
    results.append({"step": "health", "status_code": st, "pass": st == 200})

    st, _ = _post_json(
        base_url,
        "/api/auth/register",
        {
            "email": email,
            "password": DEFAULT_PASSWORD,
            "confirm_password": DEFAULT_PASSWORD,
            "full_name": "Phase4 Runner",
        },
    )
    results.append({"step": "auth_register", "status_code": st, "pass": st in (200, 201)})

    st, login = _post_json(
        base_url,
        "/api/auth/login",
        {"email": email, "password": DEFAULT_PASSWORD},
    )
    token = login.get("access_token") if isinstance(login, dict) else None
    results.append({"step": "auth_login", "status_code": st, "pass": st == 200 and bool(token)})

    st, me = _get_json(base_url, "/api/auth/me", token=token)
    results.append(
        {
            "step": "auth_me",
            "status_code": st,
            "pass": st == 200,
            "email": me.get("email") if isinstance(me, dict) else None,
        }
    )

    dry_payload = {
        "document_text": "Phase 4 no-cost walkthrough check.",
        "duration": "5",
        "difficulty": "intermediate",
        "llm_provider": "openrouter",
        "tts_provider": "openai",
        "dry_run": "true",
    }
    st, dry = _post_form(base_url, "/api/lectures/generate-document-v2", dry_payload, token=token)
    results.append(
        {
            "step": "create_preview_dry_run",
            "status_code": st,
            "pass": st == 200 and isinstance(dry, dict) and dry.get("dry_run") is True,
            "detail": dry.get("detail") if isinstance(dry, dict) else None,
        }
    )

    if paid:
        paid_payload = dict(dry_payload)
        paid_payload["dry_run"] = "false"
        paid_payload["tts_provider"] = "elevenlabs"
        paid_payload["llm_model"] = "openai/gpt-4.1-mini"

        st, generated = _post_form(base_url, "/api/lectures/generate-document-v2-byok", paid_payload, token=token)
        results.append(
            {
                "step": "single_non_dry_run_generation_byok",
                "status_code": st,
                "pass": st == 200 and isinstance(generated, dict) and generated.get("success") is True,
                "detail": generated.get("detail") if isinstance(generated, dict) else None,
            }
        )

    summary = {
        "base_url": base_url,
        "timestamp": timestamp,
        "email": email,
        "paid_mode": paid,
        "guard_env": PAID_GUARD_ENV,
        "results": results,
        "passed_steps": sum(1 for item in results if item.get("pass")),
        "total_steps": len(results),
    }

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(summary, out, indent=2)

    return summary


def run_walkthrough_existing_user(
    base_url: str,
    output_path: str,
    paid: bool,
    email: str,
    password: str,
) -> Dict[str, Any]:
    if paid:
        _check_paid_guard_or_exit()

    results = []

    # No-cost checks first.
    st, health = _get_json(base_url, "/health")
    results.append({"step": "health", "status_code": st, "pass": st == 200})

    st, login = _post_json(
        base_url,
        "/api/auth/login",
        {"email": email, "password": password},
    )
    token = login.get("access_token") if isinstance(login, dict) else None
    results.append({"step": "auth_login", "status_code": st, "pass": st == 200 and bool(token)})

    st, me = _get_json(base_url, "/api/auth/me", token=token)
    results.append(
        {
            "step": "auth_me",
            "status_code": st,
            "pass": st == 200,
            "email": me.get("email") if isinstance(me, dict) else None,
        }
    )

    dry_payload = {
        "document_text": "Phase 4 no-cost walkthrough check.",
        "duration": "5",
        "difficulty": "intermediate",
        "llm_provider": "openrouter",
        "tts_provider": "openai",
        "dry_run": "true",
    }
    st, dry = _post_form(base_url, "/api/lectures/generate-document-v2", dry_payload, token=token)
    results.append(
        {
            "step": "create_preview_dry_run",
            "status_code": st,
            "pass": st == 200 and isinstance(dry, dict) and dry.get("dry_run") is True,
            "detail": dry.get("detail") if isinstance(dry, dict) else None,
        }
    )

    if paid:
        paid_payload = dict(dry_payload)
        paid_payload["dry_run"] = "false"
        paid_payload["tts_provider"] = "elevenlabs"
        paid_payload["llm_model"] = "openai/gpt-4.1-mini"

        st, generated = _post_form(base_url, "/api/lectures/generate-document-v2-byok", paid_payload, token=token)
        results.append(
            {
                "step": "single_non_dry_run_generation_byok",
                "status_code": st,
                "pass": st == 200 and isinstance(generated, dict) and generated.get("success") is True,
                "detail": generated.get("detail") if isinstance(generated, dict) else None,
            }
        )

    summary = {
        "base_url": base_url,
        "timestamp": int(time.time()),
        "email": email,
        "paid_mode": paid,
        "guard_env": PAID_GUARD_ENV,
        "existing_user_mode": True,
        "results": results,
        "passed_steps": sum(1 for item in results if item.get("pass")),
        "total_steps": len(results),
    }

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(summary, out, indent=2)

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 4 walkthrough checks with paid guard.")
    parser.add_argument(
        "--env-file",
        default=".env.walkthrough",
        help="Optional env file for LOTG_* values (default: .env.walkthrough)",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base API URL")
    parser.add_argument("--output", default="phase4_walkthrough_latest.json", help="Output artifact path")
    parser.add_argument("--paid", action="store_true", help="Enable one non-dry-run generation check")
    parser.add_argument(
        "--use-existing-user",
        action="store_true",
        help="Use an existing account for login instead of auto-registering a new account",
    )
    parser.add_argument("--existing-email", help="Existing account email (or LOTG_EMAIL via env)")
    parser.add_argument("--existing-password", help="Existing account password (or LOTG_PASSWORD via env)")
    args = parser.parse_args()

    _load_env_file(args.env_file)

    existing_email = args.existing_email or os.getenv("LOTG_EMAIL")
    existing_password = args.existing_password or os.getenv("LOTG_PASSWORD")

    if args.use_existing_user:
        if not existing_email or not existing_password:
            raise SystemExit(
                "Existing user mode requires --existing-email and --existing-password (or LOTG_EMAIL/LOTG_PASSWORD env vars)."
            )
        summary = run_walkthrough_existing_user(
            base_url=args.base_url.rstrip("/"),
            output_path=args.output,
            paid=args.paid,
            email=existing_email,
            password=existing_password,
        )
    else:
        summary = run_walkthrough(base_url=args.base_url.rstrip("/"), output_path=args.output, paid=args.paid)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
