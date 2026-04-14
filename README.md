# LearnOnTheGo 🎧📚

> Transform any topic or PDF into personalized audio lectures using AI

[![Railway Deploy](https://img.shields.io/badge/Deploy%20on-Railway-0B0D0E?logo=railway&logoColor=white)](https://railway.app)
[![Vercel Deploy](https://img.shields.io/badge/Deploy%20on-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![React Native](https://img.shields.io/badge/React%20Native-TypeScript-61DAFB?logo=react&logoColor=white)](https://reactnative.dev)

LearnOnTheGo converts text topics or PDF documents into personalized audio lectures tailored to your preferred duration, difficulty level, and voice. Perfect for learning during walks, commutes, or workouts.

## 🎯 Current Status (Source of Truth)

LearnOnTheGo is currently in a hardened MVP state with core backend capabilities in place and frontend integration partially complete.

### Latest Verified Updates (April 2026)
- ✅ V2 endpoints stabilized for typed form handling (`duration`, `dry_run`, provider params)
- ✅ BYOK user-key path validated end-to-end in dry-run mode
- ✅ API key storage path fixed for async DB usage and encryption compatibility
- ✅ Backend CI now runs a regression test for V2 form coercion on every push/PR
- ✅ Cost-aware TTS default strategy in create flow: environment mode defaults to OpenAI TTS, BYOK mode keeps ElevenLabs optional premium
- ✅ URL generation now supports ready web URLs behind feature flags (`ENABLE_URL_INGESTION_V1`, `EXPO_PUBLIC_ENABLE_URL_INGESTION_V1`)
- ✅ Backend CI contract gates added and validated green for:
    - `tests/test_v2_source_intake_v1a.py`
    - `tests/test_url_diagnostics_scaffold.py`
    - `tests/test_api_key_lifecycle_contract.py`

### Completed
- ✅ Backend API deployed on Railway: https://learnonthego-production.up.railway.app
- ✅ Frontend deployed on Vercel
- ✅ AI pipeline foundations: topic/PDF processing, LLM generation, TTS integration
- ✅ Database foundation (SQLAlchemy + PostgreSQL support)
- ✅ JWT authentication backend and protected route dependencies
- ✅ API key encryption and BYOK architecture

### In Progress
- 🔄 End-to-end lecture generation UX from authenticated frontend flows
- 🔄 Lecture library/dashboard polish for production-ready user journeys
- 🔄 CI/CD hardening to ensure test and build signals stay reliable

### Next Execution Priorities
1. Stabilize and validate authenticated lecture generation flows (text + PDF)
2. Finalize frontend UX and state handling for create/playback/library
3. Expand backend and frontend automated coverage beyond current V2 regression baseline
4. Publish one evidence-oriented release package for portfolio review

Historical progress notes remain in phase/session documents, but this section is the canonical project status.

## ✨ Features

- **Text-to-Lecture**: Convert any topic into structured audio content
- **PDF Processing**: Extract and summarize PDF documents into lectures
- **Customizable Parameters**: Duration (5-60 min), difficulty, voice selection
- **Offline Playback**: Download lectures for offline listening
- **Multi-Provider Support**: OpenRouter, OpenAI, Anthropic for LLM; ElevenLabs, Google TTS for audio
- **Cost-Aware Routing**: Environment mode uses lower-cost default TTS, with BYOK premium provider path available
- **Secure API Key Management**: AES-256 encrypted storage of your API keys
- **Progressive Web App**: Works on mobile and desktop

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

### Phase 1: MVP (Current - Phase 2b Authentication)
- [x] Basic text-to-lecture generation
- [x] PDF processing capabilities  
- [x] PostgreSQL database with user management
- [x] JWT authentication infrastructure
- [ ] Complete authentication testing and integration
- [ ] Social login implementation (Google, Apple, GitHub)
- [ ] Mobile app authentication with biometrics

### Phase 2: Enhancement (Phase 2c-2d)
- [ ] Biometric authentication (Touch ID, Face ID)
- [ ] Multiple language support
- [ ] Quiz mode for comprehension
- [ ] Cloud synchronization with user accounts
- [ ] Advanced voice options
- [ ] Lecture sharing between users

### Phase 3: Scale
- [ ] Team collaboration features
- [ ] Analytics dashboard
- [ ] API for third-party integrations
- [ ] Enterprise features

---

**Built with ❤️ for lifelong learners everywhere**

*Transform your commute into classroom time.*
