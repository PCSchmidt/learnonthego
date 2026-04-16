# LearnOnTheGo Demo Guide

This guide is optimized for portfolio demos, recruiter walkthroughs, and interview presentations.

## Demo Objective

Demonstrate that the application provides:

- End-to-end AI content generation from multiple source types (text, PDF, URL) to audio lectures
- Production-grade authentication and BYOK (Bring Your Own Key) architecture
- Multi-provider LLM and TTS integration with structured error handling
- Deployed, CI-validated full-stack system with evidence-linked documentation

## Live Endpoints

- Frontend: [learnonthego-bice.vercel.app](https://learnonthego-bice.vercel.app)
- Backend API: [learnonthego-production.up.railway.app](https://learnonthego-production.up.railway.app)
- API Docs: [learnonthego-production.up.railway.app/docs](https://learnonthogo-production.up.railway.app/docs)

## Recommended Demo Duration

- Short version: 2-3 minutes (health check, auth flow, dry-run preview)
- Full version: 5-7 minutes (includes BYOK walkthrough, URL ingestion, playback)

## Pre-Demo Checklist

1. Confirm backend health:

```bash
curl -s https://learnonthego-production.up.railway.app/health
```

Expected: `{"status":"healthy"}`

2. Confirm frontend loads:

Open https://learnonthego-bice.vercel.app and verify the login screen renders.

3. Confirm auth endpoint is reachable:

```bash
curl -s -o /dev/null -w "%{http_code}" -X POST https://learnonthego-production.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}'
```

Expected: `401` (confirms the endpoint is live and validating credentials)

## Demo Script (5-7 Minutes)

### Step 1: Open the Product Surface

1. Open the live frontend at https://learnonthego-bice.vercel.app.
2. Briefly explain: this is a deployed React Native (web) + FastAPI system with multi-provider AI routing, BYOK key management, and CI/CD on GitHub Actions.

### Step 2: Show the Authentication Flow

1. Register a new account or log in with an existing one.
2. Point out: JWT-based auth with bcrypt password hashing, protected API routes, and token lifecycle management.

### Step 3: Show Lecture Creation (Dry-Run)

1. Navigate to the Create screen.
2. Enter a short topic (e.g., "Introduction to transformer architectures").
3. Select a model and voice.
4. Run a dry-run preview (no paid API usage).
5. Explain: the preview validates the full pipeline contract without incurring cost. This is how the system supports zero-cost testing and BYOK cost transparency.

### Step 4: Show BYOK Key Management

1. Navigate to Settings.
2. Show the API key management interface: add, validate, and delete keys per provider.
3. Explain: keys are encrypted with AES-256 before storage. The system supports OpenRouter, OpenAI, and ElevenLabs. Users control their own provider costs.

### Step 5: Show URL Ingestion (If Time Permits)

1. Return to Create and switch to URL input mode.
2. Paste a YouTube or web URL.
3. Show the diagnostics step: the system checks URL reachability, transcript availability, and content type before proceeding.
4. Explain: citation metadata (source URI, retrieval method, excerpt) is preserved through generation and stored with the lecture.

### Step 6: Close with Engineering Decisions

Summarize key tradeoffs:

- BYOK-first architecture over platform-managed keys for cost transparency
- Dry-run preview to validate contracts without paid generation
- Evidence-first documentation tied to live production artifacts
- Feature flags for safe incremental rollout (V2 pipeline, URL ingestion)

## Interviewer Q&A Prompts

### What architecture decisions did you make and why?

The system uses a BYOK model where users provide their own LLM and TTS API keys. This eliminates platform billing complexity and gives users full cost control. Keys are AES-256 encrypted at rest. The V2 pipeline uses feature flags so new capabilities (URL ingestion, provider routing) can be enabled incrementally without affecting stable paths.

### How do you validate production behavior?

Every release is backed by production walkthrough evidence artifacts (JSON files with step-by-step pass/fail results). CI runs backend contract tests and frontend type-check/build/test suites on every push. A local smoke script validates endpoint contracts without paid API calls.

### How do you handle multi-provider AI integration?

The backend abstracts LLM and TTS providers behind a routing layer. OpenRouter provides access to Claude 3.5, GPT-4o, and Llama 3.1. TTS routes through ElevenLabs with OpenAI as fallback. Provider failures return structured error contracts with actionable guidance rather than generic 500s.

### What would you build next?

Demo mode with pre-seeded sample lectures for zero-friction review, mobile-responsive layout polish, playback speed controls, and offline caching. The URL ingestion pipeline is ready for expanded source types (podcast RSS feeds, additional transcript providers).

## Optional Local Demo Setup

```bash
# Clone and start backend
git clone https://github.com/PCSchmidt/learnonthego.git
cd learnonthego/backend
pip install -r requirements.txt
JWT_SECRET_KEY=local-dev-secret ENABLE_V2_PIPELINE=true uvicorn main:app --reload

# In a separate terminal, start frontend
cd learnonthego
npm install
npm start
```

## Source of Truth

For current implementation status and architecture details, see:

- [README.md](README.md)
- [PROGRESS.md](PROGRESS.md)
- [ROADMAP.md](ROADMAP.md)
- [TESTING_GUIDE.md](TESTING_GUIDE.md)
