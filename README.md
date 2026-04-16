# LearnOnTheGo 🎧📚

> Transform any topic or PDF into personalized audio lectures using AI

[![Railway Deploy](https://img.shields.io/badge/Deploy%20on-Railway-0B0D0E?logo=railway&logoColor=white)](https://railway.app)
[![Vercel Deploy](https://img.shields.io/badge/Deploy%20on-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![React Native](https://img.shields.io/badge/React%20Native-TypeScript-61DAFB?logo=react&logoColor=white)](https://reactnative.dev)

LearnOnTheGo converts text topics or PDF documents into personalized audio lectures tailored to your preferred duration, difficulty level, and voice. Perfect for learning during walks, commutes, or workouts.

## 🎯 Current Status (Source of Truth)

LearnOnTheGo is in a **portfolio-ready MVP** state with functional audio playback, a premium design system, and BYOK key management across all core screens.

### Latest Verified Updates (April 2026)
- ✅ Functional audio player with play/pause, seek, and progress display (expo-av)
- ✅ Premium design system applied across all 6 core screens (tokens.ts + PremiumButton/PremiumField/PremiumPanel)
- ✅ Dead code cleanup: removed EnhancedCreateLectureScreen, EnhancedLectureScreen, MultiProviderDemoScreen
- ✅ V2 endpoints stabilized for typed form handling (`duration`, `dry_run`, provider params)
- ✅ BYOK user-key path validated end-to-end with self-service Settings UI
- ✅ URL ingestion supports web, YouTube transcript, and podcast feed sources with citation metadata
- ✅ Cost-aware TTS: environment mode defaults to OpenAI TTS, BYOK mode keeps ElevenLabs as optional premium
- ✅ 43/43 frontend tests passing, tsc clean
- ✅ Backend + frontend CI workflows green on `dev`

### Completed
- ✅ Backend API deployed on Railway: https://learnonthego-production.up.railway.app
- ✅ Frontend deployed on Vercel with premium editorial UI
- ✅ Audio player: play/pause, seek bar, progress, buffering states
- ✅ AI pipeline: topic/PDF/URL processing, LLM generation, TTS integration
- ✅ JWT authentication backend and protected route dependencies
- ✅ API key encryption and BYOK architecture with Settings self-service
- ✅ CI gates: V2 contract tests, source intake, URL diagnostics, API key lifecycle

### Next
- Production provider key configuration for non-dry-run generation
- Full production walkthrough evidence (auth → create → preview → confirm → playback)
- RC tag and deploy verification

## ✨ Features

- **Text-to-Lecture**: Convert any topic into structured audio content
- **PDF Processing**: Extract and summarize PDF documents into lectures
- **URL Ingestion**: Generate from web pages, YouTube transcripts, and podcast feeds
- **Audio Player**: Play/pause, seek bar, progress display with buffering states
- **Premium Design System**: Tokenized editorial UI with brass/dark theme across all screens
- **Customizable Parameters**: Duration (5-60 min), difficulty, voice selection
- **Multi-Provider Support**: OpenRouter, OpenAI for LLM; ElevenLabs, OpenAI TTS for audio
- **BYOK (Bring Your Own Key)**: Self-service key management with AES-256 encrypted storage
- **Cost-Aware Routing**: Environment mode uses lower-cost default TTS, BYOK enables premium providers
- **Progressive Web App**: Works on mobile and desktop via Vercel

## 🏗️ Architecture

```
React Native Frontend (Vercel)
           ↓
FastAPI Backend (Railway) ← JWT Authentication
           ↓
PostgreSQL Database (Railway) ← User Management & Sessions
           ↓
External APIs (OpenRouter, ElevenLabs) ← Encrypted API Keys
```

### Phase 2 Database & Authentication Architecture

```
📱 Mobile App
    ↓ (JWT Tokens)
🔐 Authentication Layer
    ├── Email/Password Registration
    ├── Social Login (Google, Apple, GitHub)
    ├── JWT Token Management (30min access + 7day refresh)
    └── Biometric Authentication (Touch ID, Face ID)
    ↓
🗄️ PostgreSQL Database
    ├── Users (email, password_hash, subscription_tier)
    ├── User Sessions (refresh_tokens, device_info)
    ├── API Keys (encrypted with AES-256)
    └── Lectures (user_library, metadata, file_paths)
    ↓
🤖 AI Services (User's API Keys)
    ├── OpenRouter (LLM processing)
    └── ElevenLabs (TTS synthesis)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/PCSchmidt/learnonthego.git
cd learnonthego
git checkout dev
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
uvicorn main:app --reload
```

### 3. Frontend Setup
```bash
# Install dependencies (package.json now in root)
npm install

# Build React Native Web app
npm run build

# For development
npm run web
```

### 4. Environment Variables
Create `backend/.env`:
```bash
DATABASE_URL=sqlite:///./learnonthego.db
JWT_SECRET_KEY=your-secret-key
ENABLE_V2_PIPELINE=true
ENABLE_URL_INGESTION_V1=true
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

For frontend URL-ready generation in Create flow, set:

```bash
# frontend/.env (or CI frontend env config)
EXPO_PUBLIC_ENABLE_URL_INGESTION_V1=true
```

### 5. Deterministic Local V2 Runbook (Recommended)

Use the one-click scripts to avoid local startup drift.

Start backend with required V2 flags:

```bash
# Git Bash
./scripts/start_backend_v2_local.sh
```

```powershell
# PowerShell
.\scripts\start_backend_v2_local.ps1
```

Run token-based smoke (fast-fail timeout defaults to 3s):

```bash
# Git Bash
export LOTG_TOKEN="<jwt-token>"
./scripts/run_v2_smoke_token.sh
```

```powershell
# PowerShell
$env:LOTG_TOKEN = "<jwt-token>"
.\scripts\run_v2_smoke_token.ps1
```

Strict BYOK validation (requires user keys already stored in backend):

```bash
export LOTG_TOKEN="<jwt-token>"
export LOTG_STRICT_BYOK=true
./scripts/run_v2_smoke_token.sh
```

```powershell
$env:LOTG_TOKEN = "<jwt-token>"
.\scripts\run_v2_smoke_token.ps1 -StrictByok
```

For detailed setup instructions, see [GETTING_STARTED.md](GETTING_STARTED.md).

## 📖 Documentation

- **[Getting Started Guide](GETTING_STARTED.md)** - Step-by-step setup instructions
- **[Testing Guide](TESTING_GUIDE.md)** - Current local and CI validation flows
- **[Archive Index](docs/archive/README.md)** - Historical session and dated status documents
- **[Archived Product Docs](docs/archive/root-legacy-2026/)** - Legacy PRD/concept/strategy references
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running locally)

## 🛠️ Development

### Project Structure
```
├── backend/           # FastAPI backend
│   ├── api/          # API route handlers
│   │   ├── auth.py   # Authentication endpoints (register, login)
│   │   ├── users.py  # User management (protected routes)
│   │   └── lectures.py # Lecture generation endpoints
│   ├── services/     # Business logic (LLM, TTS, PDF)
│   ├── models/       # Database models & Pydantic schemas
│   │   ├── database.py    # Async database config
│   │   ├── user_orm.py    # SQLAlchemy User model
│   │   └── user_models.py # Pydantic validation models
│   ├── auth/         # Authentication & JWT
│   │   ├── jwt_handler.py     # JWT token management
│   │   └── password_utils.py  # bcrypt password handling
│   └── tests/        # Backend tests
│       ├── test_database.py          # Database validation suite
│       └── test_v2_form_coercion.py  # V2 typed form regression
├── frontend/         # React Native app
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── screens/     # App screens (Auth, Create, Library)
│   │   ├── services/    # API calls with authentication
│   │   └── auth/        # Frontend authentication logic
│   └── tests/        # Frontend tests
└── docs/             # Additional documentation
    └── archive/      # Historical session and dated status docs
```

### Tech Stack
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Pytest
- **Frontend**: React Native, TypeScript, Jest
- **AI/ML**: OpenRouter, ElevenLabs, PDFPlumber
- **Hosting**: Railway (backend), Vercel (frontend)
- **Storage**: Cloudinary (temporary files)

### Development Commands
```bash
# Backend Development
cd backend
uvicorn main:app --reload          # Start development server
python test_database.py           # Test database operations
pytest --cov=.                    # Run tests with coverage
black . && flake8 . && bandit -r . # Code quality checks

# Docker Development (Recommended)
docker-compose up                  # Start all services (backend, db, frontend, redis)
docker-compose up backend db      # Start only backend services
docker-compose logs -f backend    # Follow backend logs

# Frontend
cd frontend
npm start                          # Start React Native
npm run web                        # Start web version
npm test                          # Run tests
npm run lint                      # Lint code

# Database Operations
cd backend
python -c "from models.database import create_tables_async; import asyncio; asyncio.run(create_tables_async())"

# Deployment
railway up                        # Deploy backend
vercel --prod                     # Deploy frontend
```

## 🔒 Security Features

- **API Key Encryption**: AES-256 encryption for stored API keys
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Prevents API abuse (10 lectures/hour, 5 PDF uploads/hour)
- **Input Sanitization**: Protection against injection attacks
- **PDF Validation**: Rejects malicious or scanned PDFs
- **Temporary File Cleanup**: Auto-deletion of processed files

## 💰 Cost Structure

### Free Tier (Development)
- Railway: 500 hours/month free
- Vercel: Generous free tier for frontend
- Cloudinary: 10GB storage, 25k transformations/month
- **Total**: $0/month

### Production (Small Scale)
- Railway Pro: $5/month (backend + database)
- Vercel: Free (for most use cases)
- Cloudinary: Free tier sufficient
- **Total**: ~$5-10/month

*API costs (OpenRouter, ElevenLabs) are borne by users via their own API keys.*

## 📱 Usage

### Basic Lecture Generation
1. Enter a topic or question
2. Select duration, difficulty, and voice
3. Add your API keys (OpenRouter, ElevenLabs)
4. Generate and download your lecture

### PDF Processing
1. Upload a text-based PDF (max 50MB)
2. Optionally specify focus topic
3. Configure lecture parameters
4. Generate structured audio content

### Lecture Management
- Save up to 10 lectures (free tier)
- Offline playback with speed controls
- Track listening progress
- Auto-cleanup after 30 days (unless favorited)

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest --cov=. --cov-report=html
```

### V2 Endpoint Smoke Test (Dry Run)
```bash
# Uses dry_run=true to validate response contracts without paid generation
LOTG_BASE_URL=http://localhost:8000 \
LOTG_EMAIL=your-email@example.com \
LOTG_PASSWORD=your-password \
python scripts/v2_endpoint_smoke.py
```

### Strict BYOK Contract Validation
```bash
# Requires user-level OpenRouter + ElevenLabs keys stored via /api/api-keys
LOTG_BASE_URL=http://localhost:8000 \
LOTG_EMAIL=your-email@example.com \
LOTG_PASSWORD=your-password \
LOTG_STRICT_BYOK=true \
python scripts/v2_endpoint_smoke.py
```

### Backend V2 Regression Test
```bash
cd backend
python -m pytest tests/test_v2_form_coercion.py -q
```

### Frontend Testing
```bash
cd frontend
npm test -- --coverage
```

### Security Testing
```bash
bandit -r backend/
npm audit
```

## 🚀 Deployment

### Railway (Backend)
```bash
cd backend
railway login
railway init
railway up
```

### Vercel (Frontend)
```bash
cd frontend
vercel --prod
```

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed deployment instructions.

## 📊 Performance Targets

- **Lecture Generation**: <30s (text), <45s (PDF)
- **PDF Processing**: <10s for 50MB files
- **Uptime**: 99.9% target
- **Crash Rate**: <1% sessions
- **Audio Quality**: 128 kbps MP3

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the development guidelines in [GETTING_STARTED.md](GETTING_STARTED.md)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines
- Follow the coding standards defined in `.github/copilot-instructions.md`
- Maintain >80% test coverage for critical paths
- Use conventional commit messages
- Ensure all linting checks pass

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/PCSchmidt/learnonthego/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/PCSchmidt/learnonthego/discussions)
- **Security Issues**: Email maintainer privately

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenRouter** for democratizing LLM access
- **ElevenLabs** for high-quality text-to-speech
- **Railway** and **Vercel** for excellent free tiers
- **FastAPI** and **React Native** communities

## 🗺️ Roadmap

### Phase A-B: V2 Integration + Reliability (Complete)
- [x] V2 document generation endpoints (text, PDF, URL)
- [x] BYOK key management with encrypted storage
- [x] JWT authentication end-to-end
- [x] URL ingestion (web, YouTube transcript, podcast feed)
- [x] CI contract gates for V2 critical paths
- [x] Frontend integration tests for core user journey

### Phase C: Release Readiness (Complete)
- [x] Premium design system (tokens.ts + PremiumButton/PremiumField/PremiumPanel)
- [x] Functional audio player (expo-av: play/pause, seek, progress)
- [x] UI premium pass across all 6 core screens
- [x] Dead code cleanup
- [x] 43/43 frontend tests passing, tsc clean
- [x] Backend + frontend CI green on dev

### Phase C.5: Owner-Target + Release (In Progress)
- [x] Owner-target deployment on PCSchmidt.github.io
- [ ] Production provider keys configured for non-dry-run generation
- [ ] Full production walkthrough evidence (6/6 steps)
- [ ] RC tag (v1.0.0-rc.1) on main

### Future
- [ ] Offline download and caching
- [ ] Playback speed control (1x/1.5x/2x)
- [ ] Library/history persistence
- [ ] Multiple language support
- [ ] Social login (Google, Apple, GitHub)
- [ ] Team collaboration and sharing

---

**Built with ❤️ for lifelong learners everywhere**

*Transform your commute into classroom time.*
