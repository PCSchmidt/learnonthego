# LearnOnTheGo Execution Roadmap

Last Updated: April 16, 2026
Release: v1.0.0 GA

## Design Quality Mandate (Non-Negotiable)

The product UI must be sophisticated and portfolio-grade, reflecting strong engineering judgment and professional standards.

Required bar for all user-facing screens:

- Intentional visual system (typography, spacing, color, component hierarchy)
- High-end, professional tone (not playful or "clownish")
- Consistent interaction patterns and polished loading/error/empty states
- Mobile and desktop layouts that feel designed, not default

This mandate is enforced in Phase A deliverables and exit criteria.

## Current Baseline

Backend and validation baseline already achieved:

- V2 document endpoints are in place and stable (`/api/lectures/generate-document-v2`, `/api/lectures/generate-document-v2-byok`)
- Dry-run smoke script validates env-key and BYOK response contracts
- BYOK user key storage path is fixed and tested
- Backend CI runs the V2 form coercion regression test
- Guarded production BYOK paid walkthrough now passes for a validated user key set (`phase4_single_paid_byok_closure_2026-04-15.json`)

Primary gap now is productized frontend user journey and broader reliability coverage.

## Phase A (Now): Frontend End-to-End V2 Integration

Goal: deliver one complete authenticated user flow from sign-in to generated audio playback using the V2 backend path.

Target window: 1-2 weeks

### UI Excellence Workstream (Runs In Parallel With Integration)

- [x] Define a professional visual direction and token set (type scale, spacing scale, color roles)
- [x] Standardize core components for app-wide consistency (buttons, inputs, cards, status banners)
- [x] Upgrade key screens to premium layout quality (auth, create, player, library)
- [x] Improve perceived quality with purposeful motion and transition consistency
- [x] Add accessibility and readability checks for contrast, spacing, and touch targets
- [x] Perform a final UI critique pass against portfolio quality bar before Phase A sign-off

### Checklist

- [x] Wire frontend generate flow to `/api/lectures/generate-document-v2` as default
- [x] Add BYOK key-status UI and key setup guidance using `/api/api-keys` endpoints
- [x] Add strict handling for missing-key responses from BYOK endpoint
- [x] Add generation state UX: idle, submitting, processing, success, failure
- [x] Add playback handoff from successful generation to player screen
- [x] Add PDF upload path parity with text input path
- [x] Validate auth session continuity through generation and playback
- [x] Run smoke script in strict mode before each frontend milestone merge

### Exit Criteria

- [x] A user can sign in, submit text, and play generated output end-to-end
- [x] A user with configured BYOK keys can pass strict BYOK smoke validation
- [x] Frontend error states are explicit for auth failure, key-missing, and validation errors
- [x] Core user-facing screens meet the professional UI mandate (auth/create/player/library)
- [x] No manual backend hotfixes are needed to demo the core flow

## Phase A.5 (Immediate): BYOK Productization + Multi-Source Ingestion Foundation

Goal: convert current backend/auth foundations into a user-complete content-to-podcast workflow.

Target window: 1 week

### Checklist

- [x] Add explicit BYOK setup status panel in create flow (connected/missing/invalid)
- [x] Add model selection UX with provider + model mapping
- [x] Add source type switcher (Text, PDF, URL)
- [x] Implement URL intake validator and source diagnostics surface
- [x] Add script preview before audio generation
- [x] Add generation mode explanation (Environment vs BYOK) with fallback policy
- [x] Add production telemetry for source type, model choice, duration target, and generation outcome

### Exit Criteria

- [x] User can produce audio from pasted text and PDF in production UI
- [x] User can choose model, voice, and duration with clear defaults
- [x] BYOK status and failure reasons are understandable without log inspection
- [x] URL ingestion foundation is in place with explicit unsupported-source messaging

## Phase A.6 (Next): External Source Ingestion (YouTube + Podcast URL)

Goal: support URL-driven generation workflows with legal/compliance-safe implementation.

Target window: 1-2 weeks after Phase A.5

### Checklist

- [x] Implement YouTube transcript-first ingestion path
- [x] Implement podcast URL ingestion using RSS/public transcript-first approach
- [x] Add source-availability fallbacks when transcript/content cannot be retrieved
- [x] Add citation/source metadata in generated script when available
- [x] Add dedicated tests for URL parsing, retrieval failures, and timeout handling

### Exit Criteria

- [x] YouTube URL generation works reliably for supported transcript scenarios
- [x] Podcast URL generation works for supported RSS/transcript scenarios
- [x] Unsupported or inaccessible sources fail with actionable user messaging

## Phase B (Next): Reliability and Test Coverage Expansion

Goal: convert current backend stability into repeatable, CI-enforced reliability across core flows.

Target window: 1-2 weeks after Phase A

### Checklist

- [x] Add backend tests for API key storage/retrieval with async DB session path
- [x] Add backend tests for BYOK missing-key, unsupported provider, and success responses
- [x] Add backend tests for non-dry-run guardrails (input validation and failure contracts)
- [x] Add frontend integration tests for create/generate/playback states
- [x] Add a CI step for smoke test contract checks in non-paid mode
- [x] Track and fix flaky tests until two consecutive clean CI runs on `dev` (validated locally with two consecutive backend+frontend CI-equivalent cycles)

### Exit Criteria

- [x] CI enforces backend unit/integration coverage for V2 critical paths
- [x] CI enforces frontend integration checks for core user journey
- [x] Core failures are reproducible via tests, not only manual debugging
- [x] Two consecutive green CI-equivalent validation cycles completed locally on `dev` (backend source-intake contracts + frontend create/url integration suites)

## Phase C (Complete): Audio Player + Premium UI

Goal: deliver a functional audio player and apply the design system across all core screens to reach portfolio quality.

Target window: 1 week after Phase B

### Checklist

- [x] Build functional audio player with expo-av (play/pause, seek bar, progress, buffering)
- [x] Wire navigation params from CreateLectureScreen to LecturePlayerScreen (audioUrl, citations, sourceContext)
- [x] Define design token set in `tokens.ts` (colors, spacing, typography, surfaces, radii)
- [x] Build shared Premium components (PremiumButton, PremiumField, PremiumPanel)
- [x] Apply design system across all 6 core screens (Login, Register, Home, Create, Player, Settings)
- [x] Remove dead screen files (EnhancedCreateLectureScreen, EnhancedLectureScreen, MultiProviderDemoScreen)
- [x] 43/43 frontend tests passing, TypeScript clean

### Exit Criteria

- [x] Audio player supports play/pause, seek, and progress display
- [x] All core screens use tokens.ts + Premium components (no hardcoded hex values in token-mapped positions)
- [x] No dead/unused screen files remain
- [x] All existing tests pass with zero regressions

## Phase C.5 (Complete): Owner-Target + Release Packaging

Goal: bring docs current, capture passing full-flow evidence, tag RC and GA.

Completed April 16, 2026.

- Production walkthrough 6/6 pass (`phase4_production_walkthrough_6of6.json`)
- CI green on `dev` and `main`
- Tagged v1.0.0-rc.1, then v1.0.0 GA
- Vercel and Railway auto-deploying from `main`
- Portfolio demo links updated on pcschmidt.github.io
- Password visibility toggle and header navigation added (on `dev`)

## Future Work

Prioritized improvements for post-v1.0.0 development:

1. **Demo mode** — Pre-seeded sample lectures for zero-friction portfolio review
2. **Mobile-responsive polish** — Layout verification for small viewports (390px), touch-friendly controls
3. **Login rate limiting** — 5 attempts per 15 minutes (documented in SECURITY.md, not yet implemented)
4. **Offline download and caching** — Save lectures for offline playback
5. **Playback speed control** — 1x / 1.5x / 2x speed options
6. **Library persistence** — Listening history and favorites
7. **Multiple language support** — Internationalized UI and multi-language generation
8. **Social authentication** — Google, Apple, GitHub OAuth

## Operating Rules

- Keep dry-run and strict-BYOK smoke validation as mandatory guardrails.
- Treat archived docs in `docs/archive/` as historical only.
- Update `README.md`, `PROGRESS.md`, and `TESTING_GUIDE.md` after each milestone.
- Prefer small merges with passing CI over large feature drops.
- Merge `dev` to `main` and tag before starting new feature work.
