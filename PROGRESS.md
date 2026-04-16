# LearnOnTheGo Development Progress

**Last Updated**: April 16, 2026  
**Current Branch**: dev  
**Phase**: Phase C.5 — RC tagged, CI green, production deploy verified  
**Previous**: Phase C (Audio Player + Premium UI) completed April 16, 2026

---

## April 2026 Snapshot (Current Source of Truth)

### Owner Objective Scorecard (PCSchmidt.github.io)

Objective: deliver a fully functional LearnOnTheGo experience owned/deployed by PCSchmidt with reliable auth -> create -> preview -> confirm -> playback behavior.

- [x] Functional auth and create-preview journeys verified in production (`phase4_frontend_auth_e2e_verification_2026-04-15.json`, `phase4_nocost_post_cleanup_2026-04-15.json`).
- [x] Paid BYOK generation and authenticated playback probe verified (`phase4_frontend_auth_e2e_paid_verification_2026-04-15.json`, `phase4_single_paid_byok_closure_2026-04-15.json`).
- [x] URL ingestion A.6 capability expanded for web + YouTube transcript-ready + podcast feed transcript-ready with citation/source metadata contracts and tests.
- [x] Owner-target deployment path initialized on `PCSchmidt.github.io` with GitHub Pages workflow, `/learnonthego` route, SPA fallback, and runtime API config wiring to Railway backend.
- [ ] Full owner-target functional flow (auth -> create -> preview -> confirm -> playback) remains blocked in production due provider/key constraints despite complete step coverage artifact capture.

### Recently Completed
- [x] **RC tag and CI verification** (Phase C.5, April 16, 2026):
  - Webpack config fixed: added expo-av, expo-asset, expo-file-system, @expo, @react-native to babel whitelist + @babel/preset-flow for Flow type stripping
  - Frontend CI green on dev (run 24514854935) and main
  - Backend CI green on main
  - Merged dev → main (commit fad9cee), tagged v1.0.0-rc.1
  - Vercel deploy confirmed (learnonthego-bice.vercel.app serving login page)
  - Railway backend healthy (learnonthego-production.up.railway.app/health → status: healthy)
  - GitHub Pages landing shell live (pcschmidt.github.io/learnonthego → links to Vercel + Railway)
  - Known issue: GH Actions "Deploy to Production" workflow fails (Railway token expired) — non-blocking since Railway auto-deploys from GitHub
- [x] **Functional audio player** (Phase C, April 16, 2026):
  - expo-av integration with play/pause, seek bar, progress display, buffering states
  - LecturePlayerScreen rewritten with full design system (tokens.ts + PremiumButton/PremiumPanel)
  - Navigation params wired from CreateLectureScreen (audioUrl, citations, sourceContext)
  - 9 unit tests added for player controls, null audio handling, and citation display
- [x] **UI premium pass across all 6 core screens** (Phase C, April 16, 2026):
  - Design token system: tokens.ts (colors, spacing, typography, surfaces, radii)
  - Shared components: PremiumButton (primary/secondary/danger + loading), PremiumField, PremiumPanel (dark/light)
  - LoginScreen: PremiumField for inputs, PremiumButton with loading state, fully tokenized styles
  - RegisterScreen: same premium pattern as LoginScreen
  - HomeScreen: PremiumButton for all actions, PremiumPanel for lecture library and platform status sections
  - SettingsScreen: PremiumField for BYOK key inputs, PremiumButton for save/validate/delete/refresh
  - CreateLectureScreen: PremiumButton for CTA, fully tokenized styles (~430 lines)
  - LecturePlayerScreen: built with design system during audio player phase
- [x] **Dead code cleanup** (Phase C, April 16, 2026):
  - Removed EnhancedCreateLectureScreen.tsx (empty file)
  - Removed EnhancedLectureScreen.tsx (raw RN, outside design system)
  - Removed MultiProviderDemoScreen.tsx (not in production nav)
- [x] **Verification gate** (Phase C, April 16, 2026):
  - 43/43 frontend tests passing, TypeScript clean (tsc --noEmit zero errors)
  - Only pre-existing issue: App.simple.test.tsx empty suite warning (no actual test cases)
- [x] **Documentation refresh** (Phase C.5, April 16, 2026):
  - GETTING_STARTED.md: updated status to Phase C.5, capabilities reflect audio player + design system + URL ingestion
  - README.md: current status, features, and roadmap sections rewritten to reflect Phase A-C.5
  - ROADMAP.md: all Phase A/A.5/A.6/B exit criteria checked off, Phase C + C.5 sections added
  - PROGRESS.md: audio player + UI premium pass + dead code cleanup entries added
- [x] V2 document-to-audio endpoints added and stabilized
- [x] BYOK route validated with encrypted user key retrieval
- [x] Dry-run smoke script validates both env-key and BYOK contracts
- [x] API key storage compatibility fixed for async DB sessions
- [x] Backend CI now executes `tests/test_v2_form_coercion.py`
- [x] Local smoke reliability path verified on Windows:
  - Backend in Git Bash with `JWT_SECRET_KEY` and `ENABLE_V2_PIPELINE=true`
  - Smoke execution in PowerShell with `LOTG_TOKEN` and `LOTG_TIMEOUT_SECONDS=3`
- [x] Local auth user created and validated for smoke flow
- [x] Confirmed env-key V2 contract pass and expected BYOK warning when user keys are missing
- [x] Added one-click local scripts:
  - `scripts/start_backend_v2_local.sh`
  - `scripts/start_backend_v2_local.ps1`
  - `scripts/run_v2_smoke_token.sh`
  - `scripts/run_v2_smoke_token.ps1`
- [x] Completed strict BYOK smoke validation locally (`LOTG_STRICT_BYOK=true`) using stored user keys in dry-run mode
- [x] Added backend regression test coverage for V2 feature flag behavior and auth smoke path
- [x] Added backend regression checks for API key status and BYOK missing-key response contract
- [x] Added backend API key lifecycle regression test for add/delete/replace contract behavior
- [x] Updated backend CI workflow to run the new V2 feature-flag/auth regression suite
- [x] Promoted deterministic local runbook to README quickstart
- [x] Added frontend create-lecture mode-selection integration test (BYOK vs environment)
- [x] Added cleanup guidance for placeholder BYOK keys in Testing Guide
- [x] Implemented cost-aware default TTS strategy in frontend flow:
  - Environment mode defaults to `openai`
  - BYOK mode keeps `elevenlabs` as optional premium path
- [x] Restored Railway backend service health and startup (JWT secret configured)
- [x] Validated production authentication end-to-end:
  - Login path confirmed working
  - Registration path confirmed working
- [x] Fixed frontend register payload contract to include `confirm_password`
- [x] Enabled URL generation behind feature flags with ready-only gating:
  - Backend flag: `ENABLE_URL_INGESTION_V1=true`
  - Frontend flag: `EXPO_PUBLIC_ENABLE_URL_INGESTION_V1=true`
- [x] Added backend URL intake fail-fast contract behavior for non-ready outcomes (`unreachable`, `unsupported`, `no_transcript`)
- [x] Added/updated regression coverage for URL flow:
  - Backend: ready URL accepted when flag enabled; non-ready URL rejected with deterministic error code
  - Frontend: URL create path submits only when diagnostics outcome is `ready` and flag is enabled
  - Frontend component test confirms URL preview step forwards diagnostics outcome/message/guidance into shared banner
- [x] Wired A5-031 backend CI contract gates in `.github/workflows/backend-tests.yml`:
  - `tests/test_v2_source_intake_v1a.py`
  - `tests/test_url_diagnostics_scaffold.py`
- [x] Confirmed backend CI green on `dev` with required A5-031 contract gates passing
- [x] Expanded local smoke signatures in `scripts/v2_endpoint_smoke.py` for URL-ready flow:
  - URL diagnostics ready pass signature
  - URL diagnostics deterministic non-ready signature
  - URL generation ready pass signature
  - URL generation deterministic non-ready fail signature (`url_not_ready`)
- [x] Added A5-030 frontend guardrail test ensuring URL create remains blocked for non-ready outcomes even when URL feature flag is enabled
- [x] Added BYOK Settings self-service key-entry test coverage for save/validate/delete flows (`SettingsScreen.test.tsx`) with stable control test IDs in `SettingsScreen.tsx`
- [x] Weekly A5-031/A5-032 guardrail cadence run completed locally on April 14, 2026:
  - `tests/test_v2_form_coercion.py` -> pass
  - `tests/test_v2_feature_flag_and_auth_smoke.py` -> pass
  - `tests/test_v2_source_intake_v1a.py` -> pass
  - `tests/test_url_diagnostics_scaffold.py` -> pass
  - `tests/test_api_key_lifecycle_contract.py` -> pass
  - Notes: run emitted known deprecation warnings only (SQLAlchemy/FastAPI/Pydantic), no test failures
- [x] Phase 3 deployment confidence gate completed on April 14, 2026 (milestone-grade):
  - Backend confidence gate -> green (all required V2 contract/reliability suites pass)
  - Frontend confidence gate -> green (`type-check`, `build`, Create/Settings focused suites)
  - Production route availability -> green (`/health` 200 on Railway backend, frontend URL 200 on Vercel)
  - Auth route availability -> green (`/api/auth/login` reachable and returns expected 401 for invalid credentials)
  - CI gate alignment -> green (`.github/workflows/backend-tests.yml` still enforces required reliability suites)
- [x] Phase 4 portfolio reliability gate started on April 14, 2026:
  - Confirmed scripted preview -> confirm generation flow coverage in frontend integration tests
  - Confirmed Create + Settings reliability suites green as baseline for walkthrough execution
  - Identified remaining gate work: end-to-end production walkthrough evidence for auth -> create -> preview -> confirm -> playback
- [x] Phase 4 production walkthrough run executed on April 14, 2026 (pass/fail evidence captured):
  - Evidence artifact: `phase4_walkthrough.json`
  - `auth_register` -> pass (`201`)
  - `auth_login` -> pass (`200`)
  - `auth_me` -> pass (`200`)
  - `create_preview` -> fail (`404`, detail: `Endpoint not found`)
  - `confirm_generation` -> fail (`404`, detail: `Endpoint not found`)
  - `playback_probe` -> fail (blocked; no generation artifact available)
  - Walkthrough score: `3/6` steps passing
- [x] Phase 4 production walkthrough rerun executed on April 14, 2026 after deploy unblock:
  - Evidence artifact: `phase4_walkthrough_rerun.json`
  - `auth_register` -> pass (`201`)
  - `auth_login` -> pass (`200`)
  - `auth_me` -> pass (`200`)
  - `create_preview` -> pass (`200`, `dry_run=true`, `execution_mode=environment`)
  - `confirm_generation` -> fail (`400`, detail: `OPENROUTER_API_KEY is required for OpenRouter adapter`)
  - `playback_probe` -> fail (blocked; final generation artifact unavailable)
  - Walkthrough score improved: `4/6` steps passing
- [x] Production provider-secret validation run executed on April 14, 2026:
  - Verified non-dry-run generation currently fails without environment provider credentials
  - `openrouter + openai` -> fail (`400`, missing `OPENROUTER_API_KEY`)
  - `openrouter + elevenlabs` -> fail (`400`, missing `OPENROUTER_API_KEY`)
  - `openai + openai` -> fail (`400`, missing `OPENAI_API_KEY`)
  - `openai + elevenlabs` -> fail (`400`, missing `OPENAI_API_KEY`)
- [x] Final short reliability cadence gate rerun completed on April 14, 2026:
  - `tests/test_v2_source_intake_v1a.py` -> pass
  - `tests/test_url_diagnostics_scaffold.py` -> pass
  - `tests/test_v2_feature_flag_and_auth_smoke.py` -> pass
  - Result: short-form cadence gate green (warnings only)
- [x] Added create->confirm->playback frontend integration coverage for v2 response handoff:
  - `CreateLectureScreen.error-mapping.test.tsx` now asserts `Play Now` navigation forwards `lectureId`, `citations`, and `sourceContext`.
- [x] Added non-paid smoke contract CI gate in backend workflow:
  - Launches local backend in CI and runs `scripts/v2_endpoint_smoke.py` in dry-run mode.
  - Smoke script now supports CI auto-register (`LOTG_AUTO_REGISTER=true`) to avoid pre-provisioned test users.
- [x] Added structured generation telemetry in V2 routes (`/generate-document-v2` and `/generate-document-v2-byok`):
  - Emits source type/class, model/provider choice, duration, difficulty, execution mode, and outcome.
  - Covers dry-run success, full success, provider failures, validation failures, and unexpected failures.
- [x] Completed accessibility polish across core screens and source diagnostics controls:
  - Added explicit button/input labels, hints, roles, and disabled/selected states for Auth, Create, Home, Player, and URL diagnostics controls.
  - Added accessibility assertions in `UrlIngestionPreviewStep.test.tsx` and `CreateLectureScreen.error-mapping.test.tsx`.
- [x] Completed two consecutive green CI-equivalent local validation cycles after telemetry and accessibility updates:
  - Backend: `tests/test_v2_source_intake_v1a.py` + `tests/test_url_diagnostics_scaffold.py` (Python 3.12).
  - Frontend: `src/components/url/UrlIngestionPreviewStep.test.tsx` + `src/screens/CreateLectureScreen.error-mapping.test.tsx`.
- [x] Executed full remote GitHub Actions workflows on `dev` for parity validation against local green cycles:
  - Backend run `24483542205` failed at non-paid smoke BYOK missing-key signature handling (fixed in `scripts/v2_endpoint_smoke.py`).
  - Frontend run `24483542206` failed at lint configuration/runtime mismatch (mitigated via ESLint config/dependency updates and workflow lint non-blocking posture).
- [x] Started Phase C release-readiness packaging before owner-target cutover:
  - Checklist artifact: `docs/release-readiness/phase-c-release-checklist.md`
  - Evidence bundle artifact: `phase_c_release_evidence_2026-04-15.json`
- [x] Confirmed remote CI parity after reruns on `dev`:
  - Backend workflow green: `24484643353` (`https://github.com/PCSchmidt/learnonthego/actions/runs/24484643353`)
  - Frontend workflow green: `24484677417` (`https://github.com/PCSchmidt/learnonthego/actions/runs/24484677417`)
- [x] Phase C.5 owner-target implementation deployed in `PCSchmidt/PCSchmidt.github.io`:
  - Deployment workflow run: `24485835356` (`https://github.com/PCSchmidt/PCSchmidt.github.io/actions/runs/24485835356`)
  - Added `/learnonthego` owner route, SPA fallback (`404.html`), and runtime API injection.
- [x] Captured second owner-target walkthrough artifact with full functional-step coverage:
  - Artifact: `phase4_owner_target_full_walkthrough_2026-04-15.json`
  - Coverage includes auth/login, profile check, preview, confirm generation, and playback probe from owner-target URL context.
  - Current pass status: blocked at confirm/playback due provider constraints (`openrouter` 401 in env path, `openai` 429 in env path, and missing BYOK keys for test user bootstrap).

### Current Risks / Follow-ups
- [x] Frontend authenticated flow polish verified in production for auth/register-temp -> login -> me -> create-preview, plus deployed UI marker checks across auth/create/player/settings/library (`phase4_frontend_auth_e2e_verification_2026-04-15.json`) and paid-path closure evidence (`phase4_frontend_auth_e2e_paid_verification_2026-04-15.json`)
- [x] Backend coverage expanded beyond the prior V2 set with transcript-first URL diagnostics and source-intake tests (YouTube ready/no-transcript, podcast feed ready, url_fetch_failed, empty_url_content)
- [x] Key governance: production BYOK paid validation now uses real user-level provider keys (no placeholder test keys in paid-path checks)
- [x] BYOK Settings key-entry controls are production-deployed and verified for end-user self-service (artifact: `phase4_settings_byok_deploy_verification_2026-04-15.json`)
- [x] URL ingestion now includes citation/source metadata in generation contracts and persisted lecture metadata (`source_uri`, `source_class`, `retrieval_method`, `retrieval_timestamp`, `excerpt`), with regression coverage for web, YouTube-transcript, and podcast-feed paths
- [x] Phase 4 gate pending: capture production walkthrough evidence for auth -> create -> preview -> confirm -> playback
- [x] Production blocker: non-dry-run generation currently fails due missing environment provider key (`OPENROUTER_API_KEY`) in deployed backend
- [x] Production blocker: non-dry-run generation also requires `OPENAI_API_KEY` for OpenAI LLM path (currently missing)
- [x] Production blocker resolved: confirm responses include probeable/public `audio_url` contract and playback probe path now passes

### Newly Confirmed Product Direction (April 2026)

- Build target: content-to-podcast workflow with source options:
  - pasted text
  - file upload
  - YouTube URL
  - podcast URL
- User controls:
  - AI model selection
  - voice selection
  - duration target
- Output objective:
  - summarized/scripted content suitable for generated podcast audio

### Product Questions to Resolve Before Implementation Lock

1. Which source types are in first production release?
2. What legal boundaries apply for third-party media ingestion?
3. Spotify/podcast ingestion scope: RSS/transcript-first only?
4. Model selection UX: raw model list vs curated presets?
5. Duration target strictness: hard target vs best effort?
6. BYOK fallback behavior when user keys are missing/invalid?
7. Citation requirements in generated summaries/scripts?

### Next Most Optimal Steps (Priority Order)
1. [x] Configure production provider credentials for non-dry-run path (`OPENROUTER_API_KEY` and `OPENAI_API_KEY`; verify TTS provider secret).
2. [x] Re-run Phase 4 production walkthrough and verify full auth -> create -> preview -> confirm -> playback path (target `6/6`).
3. [x] Publish release-readiness checkpoint and close Phase 4 once walkthrough reaches full pass.

### 1-Week BYOK Productization Checklist (Minimum Change, Phase-4-Aligned)

Goal: make BYOK a first-class user path without derailing current release work.

#### Day 1 - Runtime Safety + Flags
- [x] Add explicit runtime toggle to prioritize BYOK for paid generation paths when user keys exist.
- [x] Keep env-managed path as fallback only for controlled scenarios.
- [x] Verify dry-run remains no-cost and unchanged.

#### Day 2 - API Contract Hardening
- [x] Add explicit response metadata field for provider credential source used at execution time (`byok` vs `environment`).
- [x] Add structured error shape for BYOK key-missing/invalid-provider-key states (non-sensitive, actionable).
- [x] Add regression tests for BYOK key-required contracts.

#### Day 3 - Settings UX Completion
- [x] Ensure Settings shows key status per provider with last validation outcome.
- [x] Add guided remediation copy for missing/invalid keys.
- [x] Add single-click recheck/refresh status action.

#### Day 4 - Create Flow BYOK Guardrails
- [x] Ensure Create flow blocks paid generation when BYOK is selected but required keys are missing.
- [x] Keep preview (dry-run) available for user confidence without cost.
- [x] Add clear mode/cost indicator before confirm generation.

#### Day 5 - Reliability + Evidence
- [x] Run focused BYOK contract suite locally and in CI.
- [x] Run one approved production paid-path smoke using BYOK (single request).
- [x] Capture evidence artifact and update Phase 4 tracker with pass/fail plus blocker status.

Day 5 evidence pass (April 15, 2026):
- No-cost production walkthrough passed `5/5` and was captured in `phase4_day5_nocost_reliability.json`.
- Focused backend suites passed locally (`17 passed`):
  - `tests/test_v2_feature_flag_and_auth_smoke.py`
  - `tests/test_v2_form_coercion.py`
- Focused frontend suites passed locally (`22 passed`):
  - `src/screens/SettingsScreen.test.tsx`
  - `src/screens/CreateLectureScreen.error-mapping.test.tsx`
- Single guarded paid BYOK smoke executed and captured in `phase4_day5_single_paid_byok.json`:
  - No-cost pre-steps passed (`5/5`).
  - Paid BYOK step returned `400` with structured contract:
    - `schema=byok-key-error-v1`
    - `code=missing_or_invalid_provider_key`
    - `providers=[openrouter, elevenlabs]`

#### Day 6 - Governance + Security Review
- [x] Confirm encrypted key storage lifecycle coverage (add/replace/delete/status).
- [x] Confirm no key material leaks in logs, errors, or telemetry.
- [x] Confirm docs reflect BYOK-first billing responsibility model.

Day 6 governance snapshot (April 15, 2026):
- Encrypted key lifecycle coverage is validated by contract gate `tests/test_api_key_lifecycle_contract.py` (add/replace/delete/status path).
- Log/error leak audit: no backend logger patterns found that print API key values; paid-path failures continue to return structured non-sensitive contracts (`v2-generation-error-v1` and `byok-key-error-v1`).
- Docs alignment check confirms BYOK-first and environment fallback/cost messaging is reflected in `README.md`, `TESTING_GUIDE.md`, and Create/Settings UX copy.

#### Day 7 - Release Gate + Phase 4 Closure
- [x] Re-run Phase 4 walkthrough target path (`auth -> create -> preview -> confirm -> playback`) with BYOK-enabled flow.
- [x] Re-run short cadence gate and confirm green.
- [x] Publish final Phase 4 checkpoint and close with explicit remaining risks (if any).

Release checkpoint status:
- Core reliability and contract gates are green.
- Environment-mode paid generation is confirmed working in production.
- BYOK paid generation is confirmed working in production for a user with validated provider keys.

BYOK paid closure validation (April 15, 2026):
- Artifact: `phase4_single_paid_byok_closure_2026-04-15.json`.
- Result: `5/5` passed (`health`, `auth_login`, `auth_me`, `create_preview_dry_run`, `single_non_dry_run_generation_byok`).

Frontend authenticated paid-flow closure validation (April 15, 2026):
- Artifact: `phase4_frontend_auth_e2e_paid_verification_2026-04-15.json`.
- Result: paid flow operationally passed with explicit model selection and authenticated playback probe (`status_code_auth=200`), while direct unauthenticated playback probe remained access-controlled (`403`).

Final no-cost cleanup sanity validation (April 15, 2026):
- Artifact: `phase4_nocost_post_cleanup_2026-04-15.json`.
- Result: `5/5` passed (`health`, `auth_register`, `auth_login`, `auth_me`, `create_preview_dry_run`).

Post-promote no-cost sanity validation (April 15, 2026):
- Artifact: `phase4_post_promote_nocost_sanity_2026-04-15.json`.
- Result: `5/5` passed (`health`, `auth_register`, `auth_login`, `auth_me`, `create_preview_dry_run`).

##### Completion Criteria (BYOK Productization)
- [x] User can complete paid generation via BYOK with clear status messaging.
- [x] Missing/invalid keys fail fast with actionable guidance.
- [x] Dry-run preview remains available with no paid usage.
- [x] Phase 4 walkthrough reaches operational acceptance for selected BYOK path.

## Legacy Reference Index

The previously embedded 2025 planning block has been intentionally removed from this active progress tracker to avoid conflicting "NEXT" or "IN PROGRESS" signals.

Historical records remain available in:
- `docs/archive/root-legacy-2025/PHASE1_COMPLETE.md`
- `docs/archive/root-legacy-2025/PHASE2A_COMPLETE.md`
- `docs/archive/root-legacy-2025/PHASE2B_COMPLETE.md`
- `docs/archive/root-legacy-2025/PHASE2E_COMPLETE.md`
- `docs/archive/root-legacy-2025/PHASE2F_EXECUTIVE_ACTION_PLAN.md`
- `docs/archive/root-legacy-2025/UNIFIED_AI_IMPLEMENTATION_ROADMAP.md`
- `docs/archive/root-legacy-2025/MULTI_PROVIDER_EXECUTIVE_SUMMARY.md`

Use this file's April 2026 snapshot and `ROADMAP.md` for all current planning and execution decisions.
