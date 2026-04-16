# LearnOnTheGo

**Transform any topic or PDF into personalized audio lectures using AI.**

[![CI Status](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/PCSchmidt/learnonthego/actions)
[![Release](https://img.shields.io/badge/release-v1.0.0-blue)](https://github.com/PCSchmidt/learnonthego/releases/tag/v1.0.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776AB)](https://python.org)
[![TypeScript](https://img.shields.io/badge/typescript-strict-3178C6)](https://typescriptlang.org)

LearnOnTheGo converts text topics, PDF documents, and web URLs into structured audio lectures tailored to your preferred duration, difficulty level, and voice. Built as a full-stack portfolio project demonstrating AI pipeline engineering, BYOK architecture, and modern web deployment.

**Live Demo:** [learnonthego-bice.vercel.app](https://learnonthego-bice.vercel.app)

---

## Status

**v1.0.0 GA** — Released April 16, 2026

All core features are production-verified with a 6/6 end-to-end walkthrough (auth, create, preview, confirm, generate, playback) using BYOK provider keys.

- 43/43 frontend tests passing, TypeScript strict clean
- Backend and frontend CI green on `dev` and `main`
- Frontend deployed on Vercel; backend deployed on Railway
- Password visibility toggle and header navigation on all screens

---

## Features

- **Text-to-Lecture** — Convert any topic into structured audio content
- **PDF Processing** — Extract and summarize documents into lectures
- **URL Ingestion** — Generate from web pages, YouTube transcripts, and podcast feeds
- **Audio Player** — Play/pause, seek bar, progress display with buffering states
- **BYOK (Bring Your Own Key)** — Self-service key management with AES-256 encrypted storage
- **Multi-Provider Support** — OpenRouter and OpenAI for LLM; ElevenLabs and OpenAI for TTS
- **Customizable Parameters** — Duration (5-60 min), difficulty level, voice selection
- **Cost-Aware Routing** — Environment mode uses lower-cost defaults; BYOK enables premium providers
- **Premium Design System** — Tokenized editorial UI (dark/brass theme) across all screens
- **Progressive Web App** — Works on mobile and desktop browsers

---

## Architecture

```
Frontend (React Native Web)          Backend (FastAPI)
    Vercel                               Railway
       |                                    |
       +--- JWT Auth ---+--- PostgreSQL ----+
                         |
                    External APIs
                  (OpenRouter, ElevenLabs)
                         |
                  Encrypted API Keys
                  (AES-256, per-user salt)
```

| Layer       | Technology                         | Hosting   |
|-------------|------------------------------------|-----------|
| Frontend    | React Native 0.72 + TypeScript     | Vercel    |
| Backend     | FastAPI + SQLAlchemy (async)        | Railway   |
| Database    | PostgreSQL                         | Railway   |
| AI/LLM      | OpenRouter, OpenAI                 | User BYOK |
| TTS         | ElevenLabs, OpenAI TTS             | User BYOK |
| Storage     | Cloudinary (temporary audio files) | Cloudinary|
| CI/CD       | GitHub Actions                     | GitHub    |

---

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git

### 1. Clone and Configure

```bash
git clone https://github.com/PCSchmidt/learnonthego.git
cd learnonthego
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=sqlite:///./learnonthego.db
JWT_SECRET_KEY=your-secret-key
ENABLE_V2_PIPELINE=true
ENABLE_URL_INGESTION_V1=true
```

Start the server:

```bash
uvicorn main:app --reload
```

### 3. Frontend Setup

```bash
cd ..
npm install
npm run build    # Production build
npm run web      # Development server
```

### 4. Local Smoke Test

One-click scripts validate the V2 pipeline without paid API calls:

```bash
# Start backend with V2 flags
./scripts/start_backend_v2_local.sh

# Run smoke test (dry-run mode)
export LOTG_TOKEN="<jwt-token>"
./scripts/run_v2_smoke_token.sh
```

See [GETTING_STARTED.md](GETTING_STARTED.md) for full setup details including Docker and Windows-specific instructions.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](GETTING_STARTED.md) | Development environment setup and deployment |
| [Testing Guide](TESTING_GUIDE.md) | Local and CI validation workflows |
| [Security](SECURITY.md) | Security policy, encryption, and vulnerability reporting |
| [Contributing](CONTRIBUTING.md) | Development guidelines and PR process |
| [Roadmap](ROADMAP.md) | Execution phases and future plans |
| [Progress](PROGRESS.md) | Detailed development log |
| [Cost Optimization](COST_OPTIMIZATION.md) | BYOK cost model and provider pricing |

---

## Project Structure

```
learnonthego/
  backend/
    api/              # Route handlers (auth, lectures, users, api-keys)
    services/         # Business logic (LLM, TTS, PDF processing)
    models/           # SQLAlchemy ORM + Pydantic schemas
    auth/             # JWT and password utilities
    tests/            # Backend test suites
  frontend/
    src/
      components/     # Reusable UI (PremiumButton, PremiumField, PremiumPanel)
      screens/        # App screens (Login, Register, Home, Create, Player, Settings)
      services/       # API client with auth headers
      auth/           # AuthContext and token management
      theme/          # Design tokens (colors, spacing, typography)
    __mocks__/        # Jest mocks
  scripts/            # Local dev and smoke test scripts
  docs/               # Specifications, checklists, and archive
  .github/workflows/  # CI pipelines (backend-tests, frontend-tests)
```

---

## Tech Stack

| Category   | Technologies |
|------------|-------------|
| Backend    | Python, FastAPI, SQLAlchemy 2.x, PostgreSQL, Pytest |
| Frontend   | React Native, TypeScript, Webpack 5, Jest, Expo 49 |
| AI/ML      | OpenRouter (Claude, GPT-4o, Llama), ElevenLabs, OpenAI TTS |
| Hosting    | Railway (backend + DB), Vercel (frontend) |
| Security   | AES-256 encryption (Fernet), bcrypt, JWT HS256 |
| CI/CD      | GitHub Actions (lint, type-check, test, build) |

---

## Security

- **API Key Encryption** — Fernet (AES-128-CBC) with PBKDF2 key derivation, per-user salt
- **Password Hashing** — bcrypt with automatic salt
- **JWT Authentication** — HS256 tokens with 30-minute expiry
- **CORS** — Locked to production Vercel domain
- **Input Validation** — Pydantic models on all endpoints
- **PDF Validation** — File type and size limits, rejection of scanned/malicious files

See [SECURITY.md](SECURITY.md) for the full security policy and vulnerability reporting process.

---

## Testing

```bash
# Backend
cd backend
pytest --cov=. --cov-report=html

# Frontend
cd frontend
npm test -- --coverage

# V2 smoke test (dry-run, no API cost)
LOTG_BASE_URL=http://localhost:8000 \
LOTG_EMAIL=you@example.com \
LOTG_PASSWORD=yourpassword \
python scripts/v2_endpoint_smoke.py
```

CI enforces contract gates for V2 endpoints, source intake, URL diagnostics, and API key lifecycle on every push.

---

## Deployment

| Service  | Platform | URL |
|----------|----------|-----|
| Frontend | Vercel   | [learnonthego-bice.vercel.app](https://learnonthego-bice.vercel.app) |
| Backend  | Railway  | [learnonthego-production.up.railway.app](https://learnonthego-production.up.railway.app) |
| API Docs | Railway  | [/docs](https://learnonthego-production.up.railway.app/docs) |
| Health   | Railway  | [/health](https://learnonthego-production.up.railway.app/health) |

Both platforms auto-deploy from the `main` branch.

---

## Cost Model

Infrastructure costs are minimal. API costs are borne entirely by users through BYOK.

| Component | Cost |
|-----------|------|
| Railway (backend + DB) | ~$5/month |
| Vercel (frontend) | Free tier |
| OpenRouter (LLM, per lecture) | ~$0.001-0.003 |
| ElevenLabs (TTS, per lecture) | ~$0.50-2.00 |

---

## Roadmap

### Completed (v1.0.0)

- V2 document generation pipeline (text, PDF, URL)
- BYOK key management with encrypted storage and self-service UI
- JWT authentication with protected routes
- URL ingestion (web, YouTube transcript, podcast feed)
- Premium design system across all screens
- Audio player with expo-av (play/pause, seek, progress)
- Full CI pipeline with contract gates
- Production walkthrough 6/6 verified
- Password visibility toggle and header navigation

### Future

- Demo mode for zero-friction portfolio review
- Mobile-responsive polish for small viewports
- Offline download and caching
- Playback speed control (1x / 1.5x / 2x)
- Library and listening history persistence
- Login rate limiting (5 attempts / 15 min)
- Multiple language support

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines, branch naming, and PR process.

---

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [OpenRouter](https://openrouter.ai) — LLM access
- [ElevenLabs](https://elevenlabs.io) — Text-to-speech
- [Railway](https://railway.app) and [Vercel](https://vercel.com) — Hosting
- [FastAPI](https://fastapi.tiangolo.com) and [React Native](https://reactnative.dev) — Frameworks
