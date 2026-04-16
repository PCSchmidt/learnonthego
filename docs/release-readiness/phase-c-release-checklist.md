# Phase C Release Readiness Checklist

Owner: PCSchmidt
Date: 2026-04-15
Scope: Pre-cutover packaging before Phase C.5 owner-target deployment to PCSchmidt.github.io

## 1) Authentication Readiness

- [x] Login flow works with valid credentials.
- [x] Register flow supports new account creation.
- [x] Existing-user walkthrough path validated.
- [ ] Password reset flow has production-safe email delivery validation.
- [ ] Session expiry and refresh behavior documented for web playback probes.

Evidence:
- phase4_frontend_auth_e2e_verification_2026-04-15.json
- phase4_frontend_auth_e2e_paid_verification_2026-04-15.json
- phase4_walkthrough_rerun.json

## 2) Lecture Generation Readiness

- [x] V2 env generation contract validated.
- [x] URL diagnostics ready/non-ready contracts validated.
- [x] URL ingestion generation contract validated (ready pass + non-ready deterministic fail).
- [x] BYOK generation contract validated for configured-key paths.
- [x] Production telemetry emits source/model/duration/outcome for env and BYOK routes.
- [ ] CI backend smoke gate green on latest dev commit.

Evidence:
- phase4_nocost_validation.json
- phase4_nocost_post_deploy.json
- phase4_single_paid_post_deploy.json
- phase4_single_paid_post_day2_byok.json

## 3) Playback Readiness

- [x] Create -> confirm -> player handoff covered by integration test.
- [x] Source context and citations rendered on player screen.
- [x] Paid auth walkthrough includes playback probe check.
- [ ] Production playback controls (seek/speed/download) remain roadmap scope, not release-blocking for current RC.

Evidence:
- phase4_playback_probe_contract_validation.json
- phase4_frontend_auth_e2e_paid_verification_2026-04-15.json

## 4) Key Management Readiness

- [x] BYOK key lifecycle contract gate in backend CI.
- [x] Settings routing from create flow for provider guidance.
- [x] Env fallback messaging and mode toggles surfaced in UI.
- [ ] BYOK strict-mode smoke remains optional in CI until secrets strategy is finalized.

Evidence:
- phase4_settings_byok_deploy_verification_2026-04-15.json
- phase4_single_paid_byok_closure_2026-04-15.json

## 5) CI and Release Discipline

- [x] Two consecutive local CI-equivalent validation cycles completed.
- [x] Remote dev workflows executed for parity check.
- [ ] Remote dev workflows green on latest parity-fix commit.
- [ ] Release candidate tag and notes created.

## 6) Cutover Preconditions for Phase C.5

- [ ] GitHub Pages workflow and routing fallback validated in owner target repo.
- [ ] Production API base URL confirmed for GitHub Pages build.
- [ ] Owner-target smoke artifact captured from PCSchmidt.github.io.

## Open Risks (As of 2026-04-15)

1. Frontend lint debt remains high; lint step is non-blocking while type-check and focused parity tests stay enforced.
2. Backend smoke BYOK strict validation depends on runtime key availability and remains optional in non-paid CI mode.
3. Full frontend test suite has intermittent act-warning related instability; focused parity suite is currently the required gate.
