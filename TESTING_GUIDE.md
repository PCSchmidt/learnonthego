# LearnOnTheGo Testing Guide

Last updated: April 13, 2026

This guide reflects the current validated testing path for the V2 lecture pipeline and BYOK architecture.

## Test Strategy

- Fast contract validation first (`dry_run=true`)
- BYOK contract validation second (`LOTG_STRICT_BYOK=true`)
- Focused regression guard in CI (`tests/test_v2_form_coercion.py`)
- Required BYOK key-management gate in CI (`tests/test_api_key_lifecycle_contract.py`) for add/replace/delete contract proof

## Prerequisites

- Backend running locally (default: `http://localhost:8000`)
- `JWT_SECRET_KEY` set before backend startup
- `ENABLE_V2_PIPELINE=true` set before backend startup (required for V2 routes)
- Test user account available
- For strict BYOK checks: user has valid provider keys stored via `POST /api/api-keys/`

### Recommended Windows Run Pattern (stable)

- Start backend in Git Bash.
- Run smoke in PowerShell with short timeout.

Backend (Git Bash):

```bash
cd /c/Users/pchri/Documents/AIEngineeringProjects/learnonthego/backend
JWT_SECRET_KEY=local-dev-jwt-secret ENABLE_V2_PIPELINE=true \
c:/Users/pchri/Documents/AIEngineeringProjects/.venv/Scripts/python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Smoke (PowerShell token path):

```powershell
Set-Location "C:\Users\pchri\Documents\AIEngineeringProjects\learnonthego"
$env:LOTG_TOKEN = "<jwt-token>"
$env:LOTG_TIMEOUT_SECONDS = "3"
& "C:\Users\pchri\Documents\AIEngineeringProjects\.venv\Scripts\python.exe" -u scripts\v2_endpoint_smoke.py
```

## 1) V2 Smoke Test (No Paid Generation)

Validates endpoint contracts without calling paid model/voice generation.

```bash
LOTG_BASE_URL=http://localhost:8000 \
LOTG_EMAIL=your-email@example.com \
LOTG_PASSWORD=your-password \
python scripts/v2_endpoint_smoke.py
```

Expected result:
- `PASS: /api/lectures/generate-document-v2 contract validated`
- BYOK endpoint either passes or warns if keys are missing.

## 2) Strict BYOK Contract Validation

Requires stored user-level OpenRouter and ElevenLabs keys.

For local dry-run contract testing, non-production placeholder keys are acceptable because paid generation is not invoked.

```bash
LOTG_BASE_URL=http://localhost:8000 \
LOTG_EMAIL=your-email@example.com \
LOTG_PASSWORD=your-password \
LOTG_STRICT_BYOK=true \
python scripts/v2_endpoint_smoke.py
```

Expected result:
- `PASS: /api/lectures/generate-document-v2 contract validated`
- `PASS: /api/lectures/generate-document-v2-byok contract validated`
- `V2 smoke test completed successfully.`

One-click strict run:

```powershell
$env:LOTG_TOKEN = "<jwt-token>"
.\scripts\run_v2_smoke_token.ps1 -StrictByok
```

```bash
export LOTG_TOKEN="<jwt-token>"
export LOTG_STRICT_BYOK=true
./scripts/run_v2_smoke_token.sh
```

Cleanup test keys after dry-run validation:

```powershell
$headers = @{ Authorization = "Bearer $env:LOTG_TOKEN" }
Invoke-RestMethod -Method Delete -Uri "http://localhost:8000/api/api-keys/openrouter" -Headers $headers
Invoke-RestMethod -Method Delete -Uri "http://localhost:8000/api/api-keys/elevenlabs" -Headers $headers
```

```bash
curl -X DELETE "http://localhost:8000/api/api-keys/openrouter" -H "Authorization: Bearer $LOTG_TOKEN"
curl -X DELETE "http://localhost:8000/api/api-keys/elevenlabs" -H "Authorization: Bearer $LOTG_TOKEN"
```

## 3) Backend Regression Test

Covers form coercion for typed V2 params so string form values do not regress into runtime type failures.

```bash
cd backend
python -m pytest tests/test_v2_form_coercion.py -q
```

Expected result:
- `2 passed`

## 4) CI Validation

Backend workflow now includes the V2 coercion regression test on push/PR for `dev` and `main`.

Reviewer gate note:
- `tests/test_api_key_lifecycle_contract.py` is the required BYOK key-management contract gate.
- This is the canonical evidence for API key add/replace/delete behavior.

Workflow file:
- `.github/workflows/backend-tests.yml`

## Troubleshooting

- `401 Could not validate credentials`:
  - Ensure `LOTG_TOKEN` is unset if you want email/password login in smoke script.
  - Verify `JWT_SECRET_KEY` matches the running backend process.

- BYOK endpoint says keys are missing:
  - Store keys using `POST /api/api-keys/` as the same authenticated user.
  - Re-run strict smoke after key storage.

- Smoke passes env endpoint but not BYOK in strict mode:
  - Confirm both providers are present (`openrouter`, `elevenlabs`) and marked valid.

## Historical Notes

Older cost-free/mock-mode-only guidance from 2025 was replaced by this current V2-focused guide. Historical session and dated status files are archived under `docs/archive/`.
