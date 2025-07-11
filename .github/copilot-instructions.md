# AI Coding Agent Instructions for LearnOnTheGo

## Project Overview
LearnOnTheGo is a mobile-first app that converts text topics or PDF documents into personalized audio lectures using LLMs and TTS services. This project prioritizes **cost-conscious development** with free-tier services and user-provided API keys.

## Architecture & Tech Stack

### Core Architecture Pattern
```
React Native Frontend (Vercel) → FastAPI Backend (Railway) → PostgreSQL (Railway) → External APIs (OpenRouter, ElevenLabs)
```

- **Frontend**: React Native with TypeScript (Airbnb ESLint config) deployed to Vercel
- **Backend**: Python FastAPI on Railway with Pytest testing 
- **Database**: PostgreSQL on Railway with SQLAlchemy ORM
- **Storage**: Cloudinary free tier for temporary files (auto-delete post-processing)
- **Auth**: Custom JWT tokens with bcrypt password hashing
- **APIs**: OpenRouter (LLM), ElevenLabs (TTS), PDFPlumber (PDF extraction)

### Development Phases
The project follows a **progressive implementation** strategy:
- **Phase 0**: Proof of concept (text-to-lecture only, no PDF)
- **Phase 1**: Mobile MVP with PDF processing and auth
- **Phase 2**: Polish, optimization, app store deployment

## Critical Development Conventions

### Cost-First Development
- **Always use free tiers first**: Railway for hosting, Cloudinary for file storage, Vercel for frontend
- **User-provided API keys**: Never embed company API keys in code
- **Progressive scaling**: Start with Railway free tier, upgrade to $5/month only when needed
- **Temporary file strategy**: Upload → Process → Delete within 24 hours max

### Security Requirements (Non-Negotiable)
- **API key encryption**: AES-256 for all stored API keys
- **JWT secure storage**: iOS Keychain / Android Keystore only
- **PDF validation**: Reject scanned PDFs, 50MB limit, text-based only
- **Rate limiting**: 10 lectures/hour/user, 5 PDF uploads/hour/user
- **Input sanitization**: All user inputs must be sanitized before DB/API calls

### Audio Processing Pipeline
```python
# Standard lecture generation flow
def generate_lecture(input_type, content, duration, difficulty, voice):
    # 1. Content processing (PDF extraction or direct text)
    # 2. LLM prompt engineering (structured format: 10% intro, 60% concepts, 20% examples, 10% conclusion)
    # 3. TTS conversion with fallback (ElevenLabs → Google TTS)
    # 4. Audio optimization (±5% duration tolerance)
    # 5. MP3 output (128 kbps standard)
```

### File Structure Expectations
```
/backend/
  /api/          # FastAPI routes
  /services/     # LLM, TTS, PDF processing
  /models/       # SQLAlchemy models
  /auth/         # JWT authentication
  /tests/        # Pytest tests (>80% coverage required)
/frontend/
  /src/
    /components/ # Reusable UI components
    /screens/    # App screens (Create, Library, Settings)
    /services/   # API calls, offline storage
    /auth/       # Authentication logic
  /tests/        # Jest + React Testing Library
```

## Key Implementation Patterns

### Error Handling Strategy
- **User-facing errors**: Clear, actionable messages (e.g., "Invalid PDF: Scanned documents not supported")
- **Retry logic**: 1 automatic retry for failed LLM/TTS calls with fallback providers
- **Graceful degradation**: If PDF processing fails, prompt manual topic input

### Testing Requirements
- **Unit tests**: Jest (frontend), Pytest (backend) with >80% coverage on critical paths
- **Integration tests**: End-to-end lecture generation flows
- **Performance tests**: Must validate <30s text generation, <45s PDF generation
- **Security tests**: API key storage, JWT validation, input sanitization

### Database Schema Principles
- **User table**: email, hashed_password, created_at, subscription_tier
- **Lecture table**: user_id, title, duration, source_type (text/pdf), file_path, created_at
- **API_keys table**: user_id, provider, encrypted_key, is_valid
- **Auto-cleanup**: Lectures deleted after 30 days unless favorited

## Development Workflow Commands

### Backend Setup
```bash
# Virtual environment with specific requirements
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your actual values

# Run with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Docker development (alternative)
docker-compose up backend

# Railway deployment
npm install -g @railway/cli
railway login
railway init
railway up

# Testing and quality checks
pytest --cov=. --cov-report=html
black . && flake8 . && bandit -r .
isort . && mypy .
```

### Frontend Setup
```bash
# React Native with TypeScript
npx react-native init LearnOnTheGo --template react-native-template-typescript
npm install @react-native-async-storage/async-storage react-native-document-picker
npm install @react-navigation/native @react-navigation/stack

# Copy environment file and configure
cp .env.example .env
# Edit .env with your backend URL

# For web deployment to Vercel
npm install @expo/webpack-config react-native-web
npx expo install expo

# Docker development (alternative)
docker-compose up frontend

# Linting and testing
npx eslint . --ext .js,.jsx,.ts,.tsx --fix
npm run prettier --write .
npm test -- --coverage --watchAll=false

# Vercel deployment
npm install -g vercel
vercel --prod
```

## Docker Development (Optional but Recommended)

### Full Stack Development
```bash
# Start entire development environment
docker-compose up

# Start specific services
docker-compose up backend db
docker-compose up frontend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Clean rebuild
docker-compose down -v
docker-compose up --build
```

### Benefits of Docker Approach
- **Consistent Environment**: Same setup across all developers
- **Database Included**: PostgreSQL + Redis automatically configured
- **No Local Dependencies**: Python, Node.js versions managed in containers
- **Easy Cleanup**: `docker-compose down -v` removes everything

## API Documentation

### FastAPI Auto-Generated Docs
- **Swagger UI**: `http://localhost:8000/docs` (interactive API testing)
- **ReDoc**: `http://localhost:8000/redoc` (clean documentation)
- **OpenAPI JSON**: `http://localhost:8000/openapi.json` (machine-readable spec)

### Documentation Best Practices
```python
# Always include comprehensive docstrings and response models
@app.post("/api/lectures/generate", response_model=LectureResponse)
async def generate_lecture(
    request: LectureRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate audio lecture from text topic.
    
    - **topic**: The subject matter for the lecture
    - **duration**: Length in minutes (5-60)
    - **difficulty**: beginner, intermediate, or advanced
    - **voice**: TTS voice selection
    
    Returns the generated lecture with download URL.
    """
```

## Performance & Monitoring

### Required Metrics
- **Lecture generation time**: <30s (text), <45s (PDF)
- **PDF processing time**: <10s for 50MB files
- **Crash-free rate**: >99% (Firebase Crashlytics required)
- **API call success rate**: >95% with fallback handling

### Monitoring Setup
- **AWS CloudWatch**: For backend performance and errors
- **Firebase Analytics**: For user behavior and crashes
- **Sentry.io**: Error tracking (free tier: 5,000 events/month)

## Accessibility Requirements
- **WCAG 2.1 Level AA compliance** required
- **Screen reader support**: VoiceOver (iOS), TalkBack (Android)
- **Minimum font size**: 16pt scalable text
- **Audio controls**: Must have proper ARIA labels

## When Contributing Code
1. **Check PRD.md and CONCEPT.md first** for feature specifications and cost constraints
2. **Use free-tier services** unless explicitly approved for paid alternatives
3. **Include comprehensive error handling** with user-friendly messages
4. **Write tests for critical paths** (auth, lecture generation, PDF processing)
5. **Follow security-first approach** for API keys and user data
6. **Validate against performance requirements** before submitting PRs

## Common Gotchas
- **PDF processing**: Always validate text-based PDFs before expensive LLM calls
- **API costs**: Implement usage tracking to prevent runaway costs
- **Mobile storage**: Respect 10 lecture limit for free tier users
- **JWT expiry**: Implement refresh token logic for seamless UX
- **Cross-platform**: Test audio playback on both iOS and Android
