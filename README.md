# LearnOnTheGo 🎧📚

> Transform any topic or PDF into personalized audio lectures using AI

## ⚠️ CRITICAL: Deployment Directory Warning

**ALWAYS run deployment commands from the ROOT directory only!**

```bash
# ✅ CORRECT - From root directory
cd LearnOnTheGo
./deploy.sh           # Linux/Mac
deploy.bat            # Windows

# ❌ WRONG - From subdirectories
cd frontend && vercel deploy  # This will break everything!
cd backend && railway up      # This will miss dependencies!
```

This is a **monorepo** with specific build paths configured. Running deployments from wrong directories will:
- Deploy wrong files
- Break build dependencies  
- Cause authentication/permission issues
- Create inconsistent environments

**Use the provided deployment scripts ONLY from the root directory.**

[![Railway Deploy](https://img.shields.io/badge/Deploy%20on-Railway-0B0D0E?logo=railway&logoColor=white)](https://railway.app)
[![Vercel Deploy](https://img.shields.io/badge/Deploy%20on-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![React Native](https://img.shields.io/badge/React%20Native-TypeScript-61DAFB?logo=react&logoColor=white)](https://reactnative.dev)

LearnOnTheGo converts text topics or PDF documents into personalized audio lectures tailored to your preferred duration, difficulty level, and voice. Perfect for learning during walks, commutes, or workouts.

## 🎯 Current Status

**Phase 0 (Proof of Concept): ✅ COMPLETED**
- ✅ Backend API deployed on Railway: https://learnonthego-production.up.railway.app
- ✅ Frontend deployed on Vercel: https://learnonthego-bica.vercel.app
- ✅ Complete React Native app structure with navigation
- ✅ Mock lecture generation endpoint working
- ✅ Automatic CI/CD pipeline (dev branch → production)
- ✅ Development environment fully configured

**Phase 1 (AI Integration): ✅ COMPLETED**
- ✅ OpenRouter LLM integration with direct HTTP API (Claude 3.5, GPT-4o, Llama 3.1)
- ✅ ElevenLabs TTS integration with Google TTS fallback
- ✅ PDF processing with pdfplumber for text extraction
- ✅ AES-256 API key encryption for user security
- ✅ Complete lecture generation pipeline (Text/PDF → LLM → TTS → Audio)
- ✅ BYOK (Bring Your Own Key) architecture for cost control
- ✅ Mock mode for zero-cost development and testing
- ✅ Production deployment with health monitoring

**Phase 2a (Database Foundation): ✅ COMPLETED**
- ✅ PostgreSQL database integration with SQLAlchemy 2.0.23 async
- ✅ Complete User ORM with subscription tiers and preferences
- ✅ Full CRUD API endpoints with validation and error handling
- ✅ Async database session management and health monitoring
- ✅ Comprehensive database test suite with validation
- ✅ Docker development environment (Backend, DB, Frontend, Redis)

**Phase 2b (Authentication): ✅ COMPLETED**
- ✅ JWT token system with python-jose (create, verify, decode, refresh)
- ✅ Password security with bcrypt hashing and 12 salt rounds
- ✅ Complete authentication API endpoints (register, login, profile, refresh, logout)
- ✅ Protected route middleware with dependency injection
- ✅ Token refresh mechanism and password reset flow
- ✅ Comprehensive authentication test suite (10/10 tests passing)
- ✅ Production deployment with enterprise-grade security validation

**Phase 2e (Authentication Integration): ✅ COMPLETED - Track B**
- ✅ React Native authentication UI with login/register screens
- ✅ FastAPI backend integration with JWT token management
- ✅ Secure API communication with Bearer token headers
- ✅ User session management with localStorage (web)
- ✅ Professional UI with loading states and error handling
- ✅ React Native Web compatibility fixes and build optimization
- ✅ Root-level project structure with clean deployment pipeline
- ✅ Production deployment and API compatibility verification
- ✅ Complete end-to-end authentication flow working

**Phase 2f (Lecture Generation Integration): 🚧 PLANNED - Track C**
- 🔲 Connect authentication with AI lecture generation
- 🔲 Personal lecture library and user dashboard
- 🔲 Secure per-user API key management
- 🔲 Mobile-optimized lecture creation and playback
- 🔲 Complete user experience from signup to audio generation

**Phase 2d (Frontend Integration): ✅ COMPLETED - Track A**
- ✅ React Native Web deployment to Vercel via custom webpack build system
- ✅ Professional landing page with early access signup functionality
- ✅ Simplified Vercel configuration for reliable React Native Web deployment
- ✅ Complete frontend build pipeline (React Native → Webpack → Static Bundle → Vercel)
- ✅ Live deployment: https://learnonthego-bice.vercel.app

**Phase 2e (Authentication Integration): 🚧 IN PROGRESS - Track B**
- 🔄 Integrate React Native authentication with FastAPI backend
- 📋 Connect signup/login forms to JWT authentication system
- 📋 Implement secure token storage (AsyncStorage with encryption)
- 📋 Add protected route navigation and user session management
- ✅ Complete authentication services (API client, JWT management)
- ✅ Authentication UI screens (Login, Register) with validation
- ✅ Authentication context and state management
- ✅ Protected routing and navigation system
- 🔲 **CURRENT**: Professional landing page design
- 🔲 **NEXT**: Restore full authentication flow
- 🔲 **PRIORITY**: CreateLectureScreen implementation

## 🎯 Next Phase Roadmap (A, B, C Options)

### **Option A: Professional Landing Page (IMMEDIATE - 30 min)**
**Goal**: Convert visitors with compelling value proposition
- 🔲 Hero section with clear value prop and demo
- 🔲 Feature highlights with icons and benefits
- 🔲 Social proof and testimonials section
- 🔲 Clear call-to-action for early access
- 🔲 Responsive design for mobile/desktop

### **Option B: Restore Authentication System (NEXT - 1 hour)**
**Goal**: Enable user registration and secure access
- 🔲 Restore full authentication App.tsx (code ready)
- 🔲 Test end-to-end login/register flow
- 🔲 Validate JWT token storage and management
- 🔲 Verify protected route navigation
- 🔲 Error handling and loading states

### **Option C: Core Lecture Creation (PRIORITY - 2-3 hours)**
**Goal**: MVP functionality - users can create lectures
- 🔲 CreateLectureScreen with topic input
- 🔲 API integration for lecture generation
- 🔲 Progress tracking and loading states
- 🔲 Audio playback and download
- 🔲 Lecture library and history

**Phase 2c (Social Authentication): 📋 PLANNED**
- 🔲 Google OAuth integration for one-click registration
- 🔲 Apple Sign-In (required for iOS App Store)
- 🔲 GitHub OAuth integration for developer users
- 🔲 Account linking and social profile merging

**Phase 2d (Mobile Enhancement): 📋 PLANNED**
- 🔲 iOS biometric authentication (Touch ID, Face ID)
- 🔲 Android biometric authentication (Fingerprint, Face Unlock)
- 🔲 Secure token storage (iOS Keychain, Android Keystore)
- 🔲 Frontend AI service integration with authentication

## ✨ Features

- **Text-to-Lecture**: Convert any topic into structured audio content
- **PDF Processing**: Extract and summarize PDF documents into lectures
- **Customizable Parameters**: Duration (5-60 min), difficulty, voice selection
- **Offline Playback**: Download lectures for offline listening
- **Multi-Provider Support**: OpenRouter, OpenAI, Anthropic for LLM; ElevenLabs, Google TTS for audio
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
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

For detailed setup instructions, see [GETTING_STARTED.md](GETTING_STARTED.md).

## 📖 Documentation

- **[Product Requirements Document](PRD.md)** - Complete feature specifications and technical requirements
- **[Concept Document](CONCEPT.md)** - Development strategy and cost optimization
- **[Getting Started Guide](GETTING_STARTED.md)** - Step-by-step setup instructions
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
│       └── test_database.py  # Database validation suite
├── frontend/         # React Native app
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── screens/     # App screens (Auth, Create, Library)
│   │   ├── services/    # API calls with authentication
│   │   └── auth/        # Frontend authentication logic
│   └── tests/        # Frontend tests
└── docs/             # Additional documentation
    ├── PHASE2A_COMPLETE.md      # Database completion summary
    ├── AUTHENTICATION_SYSTEM_OVERVIEW.md  # Auth system details
    └── SESSION_SUMMARY_2025-07-13.md     # Development progress
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
