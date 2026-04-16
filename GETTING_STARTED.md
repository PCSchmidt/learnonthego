# LearnOnTheGo - Getting Started Guide

## 🚀 Quick Access to Live Deployments

**Current Status: Phase C.5 — Portfolio-Ready MVP with Audio Player, Design System, and BYOK**

### Live Applications
- **🌐 Frontend (React Native)**: https://learnonthego-bice.vercel.app
- **⚡ Backend API**: https://learnonthego-production.up.railway.app
- **📚 API Documentation**: https://learnonthego-production.up.railway.app/docs
- **🔍 Health Check**: https://learnonthego-production.up.railway.app/health
- **🔐 Authentication Endpoints**: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`

### Development Environment (Docker-based)
- **Backend**: http://localhost:8000 (FastAPI with auto-reload)
- **Frontend**: http://localhost:3000 (React Native web)
- **Database**: PostgreSQL on localhost:5432
- **Redis Cache**: localhost:6379

---

## Current System Capabilities

### ✅ Fully Operational Features
- **AI-Powered Lecture Generation**: Text, PDF, and URL input → Structured audio lectures
- **Functional Audio Player**: Play/pause, seek bar, progress display via expo-av
- **Premium Design System**: Tokenized UI (colors, typography, spacing) with PremiumButton/PremiumField/PremiumPanel components across all screens
- **Multi-Provider LLM Support**: OpenRouter (Claude 3.5, GPT-4o, Llama 3.1), OpenAI
- **High-Quality TTS**: ElevenLabs with OpenAI TTS fallback
- **BYOK (Bring Your Own Key)**: Self-service key management in Settings with encrypted AES-256 storage
- **URL Ingestion**: Web page, YouTube transcript, and podcast feed support with citation metadata
- **Secure User Authentication**: JWT tokens with bcrypt password hashing
- **Protected API Routes**: Full authentication middleware
- **Database Operations**: PostgreSQL with async SQLAlchemy
- **CI/CD**: Backend + frontend GitHub Actions workflows, Railway + Vercel deploy pipeline

### 🔄 Future Enhancements
- Offline download and caching
- Playback speed control (1x/1.5x/2x)
- Library/history persistence and browsing
- Social authentication (Google, Apple, GitHub OAuth)

---

## Phase 2b Development Environment Setup

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

## Current Features & Capabilities

### ✅ Phase 2b Complete - Authentication System
- **User Registration**: Email/password with bcrypt hashing
- **Secure Login**: JWT token generation with 30-minute expiry
- **Protected Routes**: Middleware for authenticated endpoints
- **Token Refresh**: Seamless token renewal
- **Password Security**: Bcrypt with salt rounds for protection
- **Session Management**: Proper logout and token invalidation

### ✅ Phase 2a Complete - Database Foundation
- **PostgreSQL Integration**: Async SQLAlchemy 2.0.23
- **User Model**: Email, hashed passwords, timestamps
- **Database Migrations**: Automated table creation
- **Connection Pooling**: Efficient database connections

### ✅ Phase 0-1 Complete - Core Features
- **AI Lecture Generation**: Text and PDF → structured audio
- **Multi-LLM Support**: Claude 3.5, GPT-4o, Llama 3.1
- **Professional TTS**: ElevenLabs with Google fallback
- **PDF Processing**: Text extraction with validation
- **API Documentation**: Interactive Swagger UI

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

### Backend (Railway) - ✅ Deployed
- **URL**: https://learnonthego-production.up.railway.app
- **Health Check**: https://learnonthego-production.up.railway.app/health
- **API Docs**: https://learnonthego-production.up.railway.app/docs
- **Database**: PostgreSQL on Railway with persistent storage
- **Features**: Full authentication system, lecture generation, PDF processing

### Frontend (Vercel) - ✅ Deployed
- **URL**: https://learnonthego-bice.vercel.app
- **Status**: React Native web build deployed
- **Ready for**: Mobile app deployment to stores

---

## Next Development Phases

### Phase 2c - Social Authentication (Next)
- Google OAuth integration
- Apple Sign-In for iOS
- GitHub authentication option
- Social profile synchronization

### Phase 2d - Mobile Enhancement
- Biometric authentication (Face ID, Touch ID)
- Offline lecture storage
- Background audio playback
- Push notifications

### Phase 3 - Production Polish
- App store submission
- Performance optimization
- Advanced analytics
- User feedback system

---

## Troubleshooting Guide

### Common Development Issues

1. **Docker container issues**: Run `docker-compose down -v` then `docker-compose up --build`
2. **Database connection errors**: Ensure PostgreSQL container is running
3. **Authentication test failures**: Check JWT secret key configuration
4. **Missing environment variables**: Copy from `.env.example` and configure

### Performance Verification
- **Authentication**: All 10 tests passing (100% success rate)
- **Database**: Async operations with connection pooling
- **API Response**: <200ms for most endpoints
- **Security**: AES-256 encryption, bcrypt hashing, JWT validation

### Getting Help
1. Check interactive API docs at `/docs`
2. Review authentication test output for debugging
3. Verify Docker container logs: `docker-compose logs -f backend`
4. Test endpoints individually using Swagger UI

---

## Project Status: 75% Complete

**Phase 0**: ✅ Core lecture generation system
**Phase 1**: ✅ PDF processing and basic infrastructure  
**Phase 2a**: ✅ Database foundation with PostgreSQL
**Phase 2b**: ✅ Authentication system with JWT security
**Phase 2c**: 🔄 Social authentication (next milestone)
**Phase 3**: 🔄 Mobile polish and app store deployment

The system is **production-ready** with enterprise-grade authentication and can generate high-quality audio lectures from text or PDF input.
