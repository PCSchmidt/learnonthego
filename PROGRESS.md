# LearnOnTheGo Development Progress

**Last Updated:** April 16, 2026
**Release:** v1.0.0 GA
**Branch:** `dev` (ahead of `main` with UX improvements)

---

## Current State

v1.0.0 released on April 16, 2026. Production walkthrough passed 6/6 steps (health, register, login, auth/me, dry-run preview, paid BYOK generation) using OpenRouter LLM and ElevenLabs TTS.

Frontend deployed on Vercel. Backend deployed on Railway. Portfolio demo links updated on pcschmidt.github.io.

### Post-GA Work (on `dev`, not yet merged to `main`)

- Password visibility toggle on all auth password fields (PremiumField `secureToggle` prop with Ionicons)
- Header navigation buttons on all authenticated screens (settings + logout on Home; home + logout on all others)
- Webpack `.ttf` file-loader rule for `@expo/vector-icons` font files
- Jest mock for `@expo/vector-icons`
- Portfolio demo links fixed (projects.astro and learnonthego.astro redirect to Vercel app)

---

## April 2026 Completed Work

### v1.0.0 Release (April 16)

- Tagged v1.0.0 on `main` (commit 4994992)
- RC tag v1.0.0-rc.1 (commit fad9cee) preceded GA after walkthrough verification
- Production walkthrough evidence: `phase4_production_walkthrough_6of6.json`
- Both CI workflows green on `dev` and `main`
- Vercel serving login page at learnonthego-bice.vercel.app
- Railway backend healthy at learnonthego-production.up.railway.app
- Known issue: GH Actions deploy workflow has stale Railway token (non-blocking; Railway auto-deploys from GitHub)

### Phase C: Audio Player and Premium UI

- Functional audio player using expo-av (play/pause, seek bar, progress, buffering states)
- LecturePlayerScreen with full design system integration
- Navigation params wired from CreateLectureScreen (audioUrl, citations, sourceContext)
- 9 unit tests for player controls, null audio handling, and citation display

### Phase C: Design System

- Token system in `tokens.ts` (colors, spacing, typography, surfaces, radii)
- Shared components: PremiumButton (primary/secondary/danger + loading), PremiumField, PremiumPanel (dark/light)
- Applied across all 6 core screens: Login, Register, Home, Create, Player, Settings
- Dead code removed: EnhancedCreateLectureScreen, EnhancedLectureScreen, MultiProviderDemoScreen
- Verification gate: 43/43 frontend tests passing, TypeScript clean

### Phase B: Reliability and CI (April 2026)

- V2 document-to-audio endpoints stabilized
- BYOK route validated with encrypted user key retrieval
- Dry-run smoke script validates env-key and BYOK contracts
- Backend CI enforces V2 contract gates (`test_v2_form_coercion`, `test_v2_source_intake_v1a`, `test_url_diagnostics_scaffold`, `test_api_key_lifecycle_contract`)
- Frontend integration tests for create/generate/playback states
- Two consecutive green CI-equivalent cycles completed locally on `dev`
- Non-paid smoke contract CI gate added (launches local backend, runs dry-run mode)

### Phase A.6: URL Ingestion (April 2026)

- YouTube transcript-first ingestion path
- Podcast URL ingestion via RSS/public transcript
- Citation and source metadata in generated scripts (`source_uri`, `source_class`, `retrieval_method`, `excerpt`)
- URL diagnostics ready/non-ready deterministic contract behavior
- Feature-flagged behind `ENABLE_URL_INGESTION_V1`

### Phase A / A.5: Frontend Integration and BYOK (March-April 2026)

- Wired frontend generate flow to V2 backend endpoints
- BYOK key-status UI with Settings self-service
- Generation state UX (idle, submitting, processing, success, failure)
- PDF upload path parity with text input
- Cost-aware default TTS (environment mode defaults to OpenAI; BYOK enables ElevenLabs)
- Model selection UX with provider mapping
- Source type switcher (Text, PDF, URL)
- Script preview before audio generation

### Production Walkthrough History

| Date | Score | Notes |
|------|-------|-------|
| April 16, 2026 | 6/6 | Full pass with BYOK (OpenRouter + ElevenLabs). GA release. |
| April 15, 2026 | 5/5 | No-cost + BYOK paid closure verification |
| April 14, 2026 | 4/6 | Improved after deploy unblock; blocked on missing provider keys |
| April 14, 2026 | 3/6 | Initial run; auth passed, endpoints not found |

Evidence artifacts are stored in the repository root as `phase4_*.json` files.

### Known Issues

- `App.simple.test.tsx` empty test suite warning (no test cases; pre-existing, non-blocking)
- GH Actions "Deploy to Production" workflow has expired Railway token (non-blocking; Railway auto-deploys from GitHub)

---

## Legacy Reference

Historical records from 2025 phases are archived in `docs/archive/root-legacy-2025/`. Use this file and [ROADMAP.md](ROADMAP.md) for all current planning decisions.