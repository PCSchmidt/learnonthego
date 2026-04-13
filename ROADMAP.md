# LearnOnTheGo 2026 Execution Roadmap

Document Version: 2.0  
Last Updated: April 12, 2026  
Status: Active

## Current Baseline

Backend and validation baseline already achieved:

- V2 document endpoints are in place and stable (`/api/lectures/generate-document-v2`, `/api/lectures/generate-document-v2-byok`)
- Dry-run smoke script validates env-key and BYOK response contracts
- BYOK user key storage path is fixed and tested
- Backend CI runs the V2 form coercion regression test

Primary gap now is productized frontend user journey and broader reliability coverage.

## Phase A (Now): Frontend End-to-End V2 Integration

Goal: deliver one complete authenticated user flow from sign-in to generated audio playback using the V2 backend path.

Target window: 1-2 weeks

### Checklist

- [ ] Wire frontend generate flow to `/api/lectures/generate-document-v2` as default
- [ ] Add BYOK key-status UI and key setup guidance using `/api/api-keys` endpoints
- [ ] Add strict handling for missing-key responses from BYOK endpoint
- [ ] Add generation state UX: idle, submitting, processing, success, failure
- [ ] Add playback handoff from successful generation to player screen
- [ ] Add PDF upload path parity with text input path
- [ ] Validate auth session continuity through generation and playback
- [ ] Run smoke script in strict mode before each frontend milestone merge

### Exit Criteria

- [ ] A user can sign in, submit text, and play generated output end-to-end
- [ ] A user with configured BYOK keys can pass strict BYOK smoke validation
- [ ] Frontend error states are explicit for auth failure, key-missing, and validation errors
- [ ] No manual backend hotfixes are needed to demo the core flow

## Phase B (Next): Reliability and Test Coverage Expansion

Goal: convert current backend stability into repeatable, CI-enforced reliability across core flows.

Target window: 1-2 weeks after Phase A

### Checklist

- [ ] Add backend tests for API key storage/retrieval with async DB session path
- [ ] Add backend tests for BYOK missing-key, unsupported provider, and success responses
- [ ] Add backend tests for non-dry-run guardrails (input validation and failure contracts)
- [ ] Add frontend integration tests for create/generate/playback states
- [ ] Add a CI step for smoke test contract checks in non-paid mode
- [ ] Track and fix flaky tests until two consecutive clean CI runs on `dev`

### Exit Criteria

- [ ] CI enforces backend unit/integration coverage for V2 critical paths
- [ ] CI enforces frontend integration checks for core user journey
- [ ] Core failures are reproducible via tests, not only manual debugging
- [ ] Two consecutive green CI runs after merge activity on `dev`

## Phase C (Then): Release Readiness and Portfolio Evidence

Goal: package technical progress into a clean release candidate suitable for external review.

Target window: 1 week after Phase B

### Checklist

- [ ] Produce a release checklist for auth, generation, playback, and key management
- [ ] Capture demo artifacts: smoke outputs, CI passes, and short walkthrough script
- [ ] Publish concise architecture summary for V2 provider abstraction and BYOK
- [ ] Verify docs align: README, TESTING_GUIDE, PROGRESS, ROADMAP
- [ ] Tag a release candidate commit and note known limitations

### Exit Criteria

- [ ] One reproducible demo path works from clean checkout to successful generation
- [ ] Documentation is current and does not rely on archived 2025 session files
- [ ] Release candidate can be reviewed without tribal context
- [ ] Portfolio-ready evidence package is complete

## Execution Order

1. Phase A first (user-visible value)  
2. Phase B second (reliability and confidence)  
3. Phase C third (presentation and release discipline)

## Operating Rules for 2026 Execution

- Keep dry-run and strict-BYOK smoke validation as mandatory guardrails.
- Treat archived docs in `docs/archive/` as historical only.
- Update `README.md`, `PROGRESS.md`, and `TESTING_GUIDE.md` after each phase exit.
- Prefer small merges with passing CI over large feature drops.
