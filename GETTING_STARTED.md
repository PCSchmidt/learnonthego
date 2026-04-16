# LearnOnTheGo - Getting Started Guide

## Live Deployments

**Release: v1.0.0 GA (April 16, 2026)**

### Production URLs
- **Frontend**: https://learnonthego-bice.vercel.app
- **Backend API**: https://learnonthego-production.up.railway.app
- **API Documentation**: https://learnonthego-production.up.railway.app/docs
- **Health Check**: https://learnonthego-production.up.railway.app/health
- **Auth Endpoints**: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`

### Local Development
- **Backend**: http://localhost:8000 (FastAPI with auto-reload)
- **Frontend**: http://localhost:3000 (React Native web)
- **Database**: PostgreSQL on localhost:5432
- **Redis Cache**: localhost:6379

---

## System Capabilities

### Operational Features
- **AI-Powered Lecture Generation** — Text, PDF, and URL input to structured audio lectures
- **Audio Player** — Play/pause, seek bar, progress display via expo-av
- **Design System** — Tokenized UI with PremiumButton/PremiumField/PremiumPanel
- **Multi-Provider LLM** — OpenRouter (Claude 3.5, GPT-4o, Llama 3.1), OpenAI
- **Text-to-Speech** — ElevenLabs with OpenAI TTS fallback
- **BYOK** — Self-service key management in Settings with AES-256 encrypted storage
- **URL Ingestion** — Web page, YouTube transcript, and podcast feed with citation metadata
- **Authentication** — JWT tokens with bcrypt password hashing
- **Protected Routes** — Full authentication middleware
- **Database** — PostgreSQL with async SQLAlchemy
- **CI/CD** — Backend + frontend GitHub Actions workflows, Railway + Vercel deploy pipeline

### Planned Enhancements
- Offline download and caching
- Playback speed control (1x/1.5x/2x)
- Library/history persistence and browsing
- Social authentication (Google, Apple, GitHub OAuth)

---

## Development Environment Setup

### Prerequisites
- Docker Desktop installed and running
- Python 3.9+ installed (for local development)
- Node.js 18+ installed
- Git configured
- VS Code with recommended extensions

### Step 1: Clone Repository and Setup

```bash
# Clone the repository
git clone https://github.com/PCSchmidt/learnonthego.git
cd learnonthego

# Switch to dev branch (current development)
git checkout dev
```

### Step 2: Docker Development Setup (Recommended)

```bash
# Start all services (backend, database, frontend, redis)
docker-compose up

# Or start specific services
docker-compose up backend db
docker-compose up frontend

# View logs
docker-compose logs -f backend
docker-compose logs -f db

# Run authentication tests
docker exec -it learnonthego-backend-1 python test_authentication.py
```

**Docker Services:**
- **Backend**: FastAPI on port 8000 with auto-reload
- **Database**: PostgreSQL on port 5432 with persistent data
- **Frontend**: React Native development server on port 3000
- **Redis**: Cache service on port 6379

### Step 3: Local Backend Development (Alternative)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with required settings

# Run database migrations
python database.py

# Start development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Local Frontend Development

```bash
# Navigate to frontend directory  
cd ../frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
# Edit .env:
# EXPO_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm start
# or for web-only development:
npm run web
```

---

## Environment Configuration

### Backend .env (Required Variables)
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/learnonthego

# JWT Security
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys (User-Provided)
OPENROUTER_API_KEY=your-openrouter-key
ELEVENLABS_API_KEY=your-elevenlabs-key

# Encryption for stored API keys
ENCRYPTION_KEY=32-byte-base64-encoded-key

# Environment
ENVIRONMENT=development
```

### Frontend .env
```env
# Backend API URL
EXPO_PUBLIC_API_URL=http://localhost:8000

# For production
EXPO_PUBLIC_API_URL=https://learnonthego-production.up.railway.app
```

---

## Testing the Authentication System

### Authentication Endpoints Available

```bash
# Register new user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'

# Login user
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'

# Get user profile (protected route)
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Running the Test Suite

```bash
# Run comprehensive authentication tests
cd backend
python test_authentication.py

# Expected output: 10/10 tests passing
# Tests cover: registration, login, protected routes, JWT validation, password security
```

---

## Current Features

### v1.0.0 GA (April 2026)
- **User Registration and Login** — Email/password with bcrypt hashing, JWT tokens
- **BYOK Key Management** — Self-service encrypted key storage via Settings screen
- **Lecture Generation** — Text, PDF, and URL to structured audio content
- **Audio Player** — Play/pause, seek, progress with expo-av
- **Design System** — Premium tokenized UI across all screens
- **URL Ingestion** — Web page, YouTube transcript, podcast feed with citations
- **CI/CD** — Automated backend and frontend pipelines

---

## Development Commands

### Backend Testing & Quality
```bash
# Run authentication test suite
python test_authentication.py

# Check code quality
black . && flake8 . && bandit -r .
isort . && mypy .

# Database operations
python database.py  # Create tables
```

### Frontend Development
```bash
# Install dependencies
npm install

# Development server
npm start
npm run web  # Web-only mode

# Testing
npm test -- --coverage --watchAll=false

# Linting
npx eslint . --ext .js,.jsx,.ts,.tsx --fix
npm run prettier --write .
```

### Docker Operations
```bash
# Full development environment
docker-compose up

# Specific services
docker-compose up backend db
docker-compose up frontend

# Rebuild containers
docker-compose down -v
docker-compose up --build

# Run tests in container
docker exec -it learnonthego-backend-1 python test_authentication.py
```

---

## Production Deployment Status

### Backend (Railway) - Deployed
- **URL**: https://learnonthego-production.up.railway.app
- **Health Check**: https://learnonthego-production.up.railway.app/health
- **API Docs**: https://learnonthego-production.up.railway.app/docs
- **Database**: PostgreSQL on Railway

### Frontend (Vercel) - Deployed
- **URL**: https://learnonthego-bice.vercel.app

---

## Next Development Phases

## Next Development Priorities

1. Demo mode for zero-friction portfolio review
2. Mobile-responsive polish for small viewports
3. Login rate limiting
4. Offline download and caching
5. Playback speed control

---

## Troubleshooting Guide

### Common Development Issues

1. **Docker container issues**: Run `docker-compose down -v` then `docker-compose up --build`
2. **Database connection errors**: Ensure PostgreSQL container is running
3. **Authentication test failures**: Check JWT secret key configuration
4. **Missing environment variables**: Copy from `.env.example` and configure

### Performance
- **Database**: Async operations with connection pooling
- **API Response**: <200ms for most endpoints
- **Security**: AES-256 encryption, bcrypt hashing, JWT validation

### Getting Help
1. Check interactive API docs at `/docs`
2. Review authentication test output for debugging
3. Verify Docker container logs: `docker-compose logs -f backend`
4. Test endpoints individually using Swagger UI

---

## Project Status

**v1.0.0 GA** — Released April 16, 2026.

All core features are production-verified. See [PROGRESS.md](PROGRESS.md) for detailed development history and [ROADMAP.md](ROADMAP.md) for planned enhancements.
