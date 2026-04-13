# Product Requirements Document (PRD) for LearnOnTheGo

**Document Version**: 2.0  
**Date**: July 13, 2025  
**Author**: AI Development Team  
**App Name**: LearnOnTheGo

---

## 1. Overview

### 1.1 Purpose
LearnOnTheGo is a mobile-first app that generates personalized, fact-filled audio lectures based on user-specified topics, questions, or uploaded PDF content, tailored to desired durations, difficulty levels, and voice preferences. It leverages large language models (LLMs) via OpenRouter and text-to-speech (TTS) services to create downloadable audio files for offline learning during activities like walking, commuting, or exercising.

### 1.2 Vision
To empower users to learn complex topics in an engaging, accessible audio format, integrated into daily routines, with the flexibility to generate lectures from both freeform inputs and specific documents like PDFs.

### 1.3 Target Audience
- **Primary**: Lifelong learners, students, professionals, and researchers (18-45)
- **Secondary**: Content creators, educators, and knowledge workers
- **Technical Profile**: Users comfortable with API key management or willing to learn
- **Use Cases**: Commuting, exercising, multitasking, accessibility needs

### 1.4 Success Metrics
- **User Acquisition**: 1,000 early access users within 3 months of launch
- **User Engagement**: 50% of users generate 3+ lectures/month 
- **Retention**: 70% monthly active users after 3 months
- **Audio Completion**: 80% of lectures listened to completion
- **PDF Adoption**: 30% of lectures from PDFs within 6 months
- **User Satisfaction**: 4.5/5 average rating within 6 months
- **Security**: Zero critical vulnerabilities; 99.9% uptime
- **Performance**: <30s text-to-lecture, <45s PDF-to-lecture generation

### 1.5 Current Implementation Status (July 13, 2025)

#### ✅ COMPLETED PHASES

**Phase 0 - Proof of Concept: COMPLETED**
- Backend Infrastructure: FastAPI server deployed on Railway with PostgreSQL
- Frontend Infrastructure: React Native app deployed on Vercel with TypeScript
- CI/CD Pipeline: Automatic deployments from dev branch to production
- Core Architecture: Full-stack foundation with proper separation of concerns
- Development Environment: Complete local development setup with Docker support

**Phase 1 - AI Integration: COMPLETED**
- OpenRouter LLM integration with direct HTTP API (Claude 3.5, GPT-4o, Llama 3.1)
- ElevenLabs TTS integration with Google TTS fallback
- PDF processing with pdfplumber for text extraction
- AES-256 API key encryption for user security
- Complete lecture generation pipeline (Text/PDF → LLM → TTS → Audio)
- BYOK (Bring Your Own Key) architecture for cost control
- Mock mode for zero-cost development and testing
- Production deployment with health monitoring

**Phase 2a - Database Foundation: COMPLETED**
- PostgreSQL database integration with SQLAlchemy 2.0.23 async
- Complete User ORM with subscription tiers and preferences
- Full CRUD API endpoints with validation and error handling
- Async database session management and health monitoring
- Comprehensive database test suite with validation
- Docker development environment (Backend, DB, Frontend, Redis)

**Phase 2b - Authentication: COMPLETED**
- JWT token system with python-jose (create, verify, decode, refresh)
- Password security with bcrypt hashing and 12 salt rounds
- Complete authentication API endpoints (register, login, profile, refresh, logout)
- Protected route middleware with dependency injection
- Token refresh mechanism and password reset flow
- Comprehensive authentication test suite (10/10 tests passing)
- Production deployment with enterprise-grade security validation

#### 🚧 CURRENT PHASE

**Phase 2d - Frontend Integration: IN PROGRESS**
- ✅ React Native Web deployment to Vercel (professional landing page)
- ✅ Complete authentication services (API client, JWT management)
- ✅ Authentication UI screens (Login, Register) with validation
- ✅ Authentication context and state management
- ✅ Protected routing and navigation system
- 🔲 **CURRENT TASK**: Professional landing page optimization
- 🔲 **NEXT TASK**: Authentication system integration testing
- 🔲 **PRIORITY TASK**: CreateLectureScreen implementation

#### 📋 NEXT PHASES

**Phase 2d Immediate Roadmap (Next 4-6 hours):**

**Track A: Professional Landing Page (30 minutes)**
- Hero section with compelling value proposition
- Feature highlights with benefit-focused messaging
- Social proof and early access signup
- Mobile-responsive design optimization

**Track B: Authentication Integration (1 hour)**
- Restore full authentication flow from backup code
- End-to-end testing of user registration and login
- JWT token management and secure storage validation
- Protected route navigation and error handling

**Track C: Core Lecture Creation (2-3 hours)**
- CreateLectureScreen with topic input and settings
- Integration with backend lecture generation API
- Progress tracking and audio playback interface
- Lecture history and library management

#### Phase 2a - Database Foundation: ✅ COMPLETED  
- ✅ PostgreSQL database integration with SQLAlchemy 2.0.23 async
- ✅ Complete User ORM with subscription tiers and preferences
- ✅ Full CRUD API endpoints with validation and error handling
- ✅ Async database session management and health monitoring
- ✅ Comprehensive database test suite with validation
- ✅ Docker development environment (Backend, DB, Frontend, Redis)

#### Phase 2b - Authentication: ✅ COMPLETED
- ✅ JWT authentication system (create, verify, refresh) with 30min access tokens
- ✅ bcrypt password security with 12 salt rounds for enterprise-grade protection
- ✅ Complete authentication API (registration, login, profile, refresh, logout)
- ✅ Protected route middleware with automatic user validation
- ✅ Security implementation (SQL injection protection, account enumeration protection)
- ✅ Comprehensive authentication testing (10/10 tests passing)
- ✅ Production deployment with Docker environment validation

#### Phase 2c - Social Authentication: 🔄 NEXT
- 🔄 Google OAuth integration for one-click registration
- 🔄 Apple Sign-In (required for iOS App Store)
- 🔄 GitHub OAuth integration for developer users
- 🔄 Account linking and social profile merging
- 🔄 PDF upload and text extraction pipeline
- 🔄 User authentication with JWT tokens
- 🔄 Encrypted API key storage (AES-256)
- 🔄 End-to-end lecture generation workflow

**Deployment URLs:**
- **Backend**: https://learnonthego-production.up.railway.app
- **Frontend**: https://learnonthego-bice.vercel.app
- **API Documentation**: https://learnonthego-production.up.railway.app/docs

---

## 2. Features and Requirements

### 2.0 Feasibility Statement (April 2026)

The requested workflow is feasible and aligns with the current architecture:

- Input sources: pasted text, file upload, and external URLs
- Analysis: user-selectable AI model/provider
- Output shaping: summarized script with configurable duration and style
- Audio generation: user-selectable voice and provider path (environment or BYOK)

Current system status:

- Authentication and deployment are operational
- BYOK storage and validation contracts exist
- Generation pipeline exists but must be productized for the full multi-source journey

### 2.0.1 New Product Capability: Multi-Source Podcast Generation

Users can create a generated audio lecture/podcast from one of four inputs:

- Pasted text
- Uploaded file (PDF first, additional formats phased)
- YouTube URL
- Podcast URL (Spotify support subject to legal/technical constraints)

The user then selects:

- AI model/provider for analysis and script generation
- Voice/provider for TTS
- Target duration and difficulty/tone

The system produces:

- Structured summary/script
- Audio output generated from that summary/script

### 2.0.2 Delivery Phases for This Capability

Phase 1 (MVP+):

- Pasted text + PDF upload
- Model selection from supported providers
- Voice and duration controls
- Script preview + audio generation

Phase 2:

- YouTube URL ingestion (transcript-first path)
- URL validation and source diagnostics

Phase 3:

- Podcast URL ingestion (RSS/public transcript-first)
- Provider-specific handling and fallback UX when transcript/content is unavailable

### 2.0.3 Required Product Decisions (Blocking Questions)

1. Source support policy:
- Which source types are in first release: text + PDF only, or include YouTube immediately?

2. Legal/compliance boundaries:
- Are we allowed to process full third-party audio/video content, or only transcripts/metadata supplied by user or publicly available?

3. Spotify ingestion policy:
- Do we support only RSS/public transcript flows first, with explicit "no transcript found" behavior?

4. Model selection UX:
- Show provider/model names directly, or provide curated presets (Cost Saver, Balanced, Best Quality)?

5. Duration control semantics:
- Hard duration target (strict +/- small tolerance) or best-effort duration?

6. Summary depth:
- Should output prefer concise briefings, full lesson narratives, or user-selectable depth presets?

7. BYOK behavior:
- If BYOK is missing/invalid, do we auto-fallback to environment keys or require user action?

8. Cost governance:
- Need per-run estimate and/or usage budget caps before generation?

9. File constraints:
- What file types and size limits are acceptable for initial release beyond PDF?

10. Trust and citation requirements:
- Must summaries include citations/source excerpts when available?

### 2.1 Core Features

#### 1. Lecture Generation
- **Description**: Users input a topic/question or upload a PDF (via file path, drag-and-drop, or URL) to generate a fact-filled audio lecture
- **Requirements**:
  - Input options:
    - Text: Topic/question (max 500 characters)
    - PDF: Upload via file path, drag-and-drop, or URL (text-based PDFs, max 50 MB)
    - Optional PDF topic focus (text input)
  - Parameters: Duration (5–60 minutes), difficulty (Beginner, Intermediate, Advanced), voice (5+ TTS options), LLM provider (OpenRouter primary)
  - Output: MP3 (128 kbps) or WAV, downloadable for offline playback
  - Lecture structure: Introduction (10%), key concepts (60%), examples/analogies (20%), conclusion (10%)
  - PDF processing: Extract text using PDFPlumber (primary) or PyPDF2; reject scanned PDFs
- **Predestined Decisions**:
  - Default settings: 20-minute duration, Intermediate difficulty, Neutral American voice, English language
  - PDF size limit: 50 MB
  - Audio format: MP3 (128 kbps)
  - Scanned PDFs: Rejected with error ("Please upload a text-based PDF")

#### 2. API Key Management
- **Description**: Users input and manage API keys for LLM providers
- **Requirements**:
  - Secure input form with validation
  - Encrypted storage (AES-256)
  - Support OpenRouter (primary); optional OpenAI, Anthropic
  - Tutorial for OpenRouter API key setup
- **Predestined Decisions**:
  - Users bear API costs
  - Validation on input and before lecture generation

#### 3. Audio Playback and Library
- **Description**: Users play, pause, and manage lectures
- **Requirements**:
  - Playback controls: Play, pause, skip ±15 seconds, speed (0.5x–2x)
  - Library: Store 50 lectures locally (10 for free tier); cloud sync for premium
  - Metadata: Topic, duration, date, completion status, source (text/PDF)
  - Offline mode: Download lectures for offline playback
- **Predestined Decisions**:
  - Auto-delete lectures after 30 days unless favorited
  - Playback speed default: 1x

#### 4. User Profiles and Settings
- **Description**: Users customize preferences and track progress
- **Requirements**:
  - Account creation: Email/password or OAuth (Google, Apple)
  - Settings: Default duration, difficulty, voice, language (English default; Spanish, French, Mandarin in Phase 2)
  - Progress tracking: Log topics, listening time, completed lectures, PDF sources
- **Predestined Decisions**:
  - Progress tracking opt-in
  - No social login for MVP

### 2.2 Non-Core Features (Phase 2)
- Quiz mode, sharing, depth customization, PDF annotation, analytics dashboard
- **Predestined**: Quiz and PDF annotation for premium users; sharing audio-only in MVP

---

## 3. User Flows

### 3.1 Generate Lecture
1. User opens "Create Lecture" screen
2. Selects input: Text (topic/question) or PDF (file path, drag-and-drop, URL)
3. Inputs duration, difficulty, voice, LLM
4. App validates API key and PDF (if applicable)
5. Submits request; app shows "Generating…" (10–30s for text, 15–45s for PDF)
6. Backend processes input, generates script, converts to audio
7. App delivers MP3; user saves or plays

### 3.2 Listen to Lecture
1. User navigates to "Library"
2. Selects lecture (e.g., "Attention Heads, 25 min, PDF: paper.pdf")
3. Playback screen with controls; offline listening supported

### 3.3 Manage API Keys
1. User navigates to "Settings" > "API Keys"
2. Inputs OpenRouter API key; app validates and encrypts

---

## 4. Technical Requirements

### 4.1 Frontend
- **Framework**: React Native for iOS/Android
- **UI Components**:
  - Input forms, PDF upload (file picker, drag-and-drop, URL input)
  - Audio player with waveform
  - Library grid/list view
  - Settings page
- **Offline Support**: Store 10 lectures (free tier), PDFs (max 50 MB each)
- **Accessibility**:
  - Support screen readers (e.g., VoiceOver, TalkBack)
  - High-contrast mode, scalable text (min 16pt font)
  - ARIA-compliant labels for PDF upload and playback controls
  - Test with WCAG 2.1 Level AA compliance

### 4.2 Backend
- **Framework**: Python with FastAPI
- **Database**: PostgreSQL (user profiles, lecture metadata, API keys, PDF metadata)
- **Processing Pipeline**:
  - PDF text extraction: PDFPlumber (primary), PyPDF2 (fallback)
  - Prompt engineering: Structured prompts for text/PDF inputs
  - LLM integration: OpenRouter (primary); optional OpenAI, Anthropic
  - TTS integration: ElevenLabs (primary); Google Cloud TTS fallback
  - Audio optimization: Adjust script length/speed (±5% duration tolerance)
- **Security**:
  - Encrypt API keys and PDF uploads (AES-256)
  - Delete PDFs/extracted text post-processing
  - Validate URL inputs (HTTPS only, blocklisted domains)
  - Implement JWT for user authentication
  - Rate limiting: 10 lectures/hour/user; 5 PDF uploads/hour/user
  - Input sanitization: Prevent SQL injection, XSS, and malicious PDF uploads
  - Penetration testing: Conduct pre-launch security audit
- **Logging and Monitoring**:
  - Log all API calls, errors, and lecture generation events (e.g., in AWS CloudWatch)
  - Monitor performance (e.g., lecture generation time, PDF processing latency)
  - Alert on critical errors (e.g., API key failure, server downtime)
- **Error Handling**:
  - User-facing errors: Clear messages (e.g., "Invalid PDF: Scanned documents not supported")
  - Retry logic: 1 retry for failed LLM/TTS calls; fallback to secondary provider (e.g., Google TTS)
  - Graceful degradation: If PDF processing fails, prompt user to input topic manually

### 4.3 APIs
- **OpenRouter**: LLM access (Llama, Claude, Mistral)
- **ElevenLabs**: TTS for audio generation
- **PDFPlumber/PyPDF2**: Server-side text extraction
- **Optional**: Serper API for web search to supplement PDF content

### 4.4 Hosting
- **Backend**: Railway (FastAPI + PostgreSQL)
- **Frontend**: Vercel (React Native web builds)
- **Storage**: Cloudinary free tier for temporary PDFs/audio (deleted post-processing)
- **Cost Estimate**: $5–$25/month (after free tiers)

### 4.5 Performance Requirements
- Lecture generation: <30s (text), <45s (PDF)
- PDF processing: <10s for text extraction (50 MB)
- Audio file size: ~15 MB for 20-minute MP3
- Uptime: 99.9%
- **Crash-free rate**: >99% sessions (tested via Firebase Crashlytics)

### 4.6 Testing
- **Unit Testing**:
  - Frontend: Test UI components (e.g., input forms, playback controls) using Jest/React Testing Library
  - Backend: Test PDF extraction, prompt generation, and API integrations using Pytest
  - Coverage: >80% for critical paths (lecture generation, authentication)
- **Integration Testing**:
  - Test end-to-end flows: Text/PDF input to audio output
  - Validate API integrations (OpenRouter, ElevenLabs, PDFPlumber)
- **UI/UX Testing**:
  - Usability testing with 20–50 beta users (include PDF upload)
  - Test accessibility with screen readers and WCAG tools
- **Performance Testing**:
  - Load test for 1,000 concurrent users; 100 simultaneous PDF uploads
  - Stress test PDF processing for 50 MB files
- **Security Testing**:
  - Penetration testing for authentication, API key storage, and PDF uploads
  - Static code analysis with tools like Bandit (Python) and ESLint (React Native)
- **Beta Testing**:
  - Conduct with 50 users; collect feedback on text/PDF inputs, playback, and errors
  - Use Firebase Analytics to track feature usage and crashes

### 4.7 Linting and Code Quality
- **Frontend**:
  - Use ESLint with Airbnb style guide for React Native
  - Enforce TypeScript for type safety
  - Run linting in CI/CD pipeline (e.g., GitHub Actions)
- **Backend**:
  - Use Flake8 and Black for Python code formatting
  - Enforce PEP 8 standards
  - Static analysis with Bandit for security vulnerabilities
- **Code Review**:
  - Require pull request reviews with >1 approver
  - Automated linting checks before merging

### 4.8 Authentication and Registration
- **Registration**:
  - Email/password sign-up with verification email
  - OAuth support (Google, Apple) for simplified login
  - Password requirements: Min 8 characters, 1 uppercase, 1 number, 1 special character
  - Store user data in PostgreSQL with hashed passwords (bcrypt)
- **Login**:
  - Email/password or OAuth login
  - JWT-based session management (tokens expire after 24 hours)
  - Support refresh tokens for seamless re-authentication
  - Two-factor authentication (2FA) optional for premium users (Phase 2)
- **Error Handling**:
  - Clear error messages (e.g., "Invalid email/password" or "Email already registered")
  - Rate limit login attempts (5 attempts/15 minutes)
- **Predestined Decisions**:
  - No social login beyond Google/Apple in MVP
  - JWT stored securely in device keychain (iOS) or Keystore (Android)
  - 2FA deferred to Phase 2

---

## 5. Predestined Decisions

1. **Primary LLM Provider**: OpenRouter
2. **Primary TTS Provider**: ElevenLabs; Google TTS fallback
3. **MVP Scope**: Lecture generation (text/PDF), playback, API key management, registration/login
4. **Monetization**: Freemium (10 lectures/month free, 5 PDF-based; premium for higher quotas)
5. **Audio Format**: MP3 (128 kbps)
6. **Duration Limits**: 5–60 minutes
7. **Default Settings**: 20-minute duration, Intermediate difficulty, Neutral American voice, English
8. **PDF Input**: Text-based PDFs (50 MB max); PDFPlumber primary; scanned PDFs rejected
9. **Security**:
   - JWT for authentication; bcrypt for passwords
   - Encrypt API keys/PDFs; delete post-processing
   - Penetration testing pre-launch
10. **Testing**:
    - Unit/integration testing with >80% coverage
    - Beta testing with 50 users
    - Automated linting in CI/CD
11. **Platform**: Mobile-first (React Native); web deferred to Phase 2

---

## 6. Non-Functional Requirements

- **Usability**: <3 taps to generate lecture; intuitive PDF upload
- **Performance**: Lecture generation <30s (text), <45s (PDF); PDF processing <10s
- **Scalability**: Support 1,000 concurrent users; 100 simultaneous PDF uploads
- **Privacy**: GDPR/CCPA compliance; delete PDFs/extracted text post-processing
- **Accessibility**: WCAG 2.1 Level AA compliance
- **Security**:
  - No critical vulnerabilities (CVSS >7.0) post-launch
  - Regular security audits (quarterly post-launch)
- **Reliability**:
  - Crash-free rate >99% (monitored via Firebase Crashlytics)
  - Backend uptime 99.9% (monitored via AWS CloudWatch)
- **Maintainability**:
  - Codebase linted and documented (API endpoints, functions)
  - Modular architecture for easy updates (e.g., new LLMs)

---

## 7. Development Timeline and Milestones

### Phase 1: MVP (5 months)
- **Month 1**:
  - Finalize UI/UX designs (include PDF upload, registration/login)
  - Set up backend (FastAPI, PostgreSQL, AWS)
  - Integrate OpenRouter, ElevenLabs, PDFPlumber
- **Month 2**:
  - Develop lecture generation (text/PDF), PDF extraction, authentication
  - Implement frontend (input forms, PDF upload, playback, login)
  - Set up linting (ESLint, Flake8) and CI/CD (GitHub Actions)
- **Month 3**:
  - Build library, offline mode, and user settings
  - Write unit/integration tests (Jest, Pytest)
  - Conduct initial security audit (API key storage, PDF uploads)
- **Month 4**:
  - Beta testing with 50 users (text/PDF inputs, authentication)
  - Test accessibility (WCAG compliance)
  - Optimize performance (PDF processing, generation latency)
- **Month 5**:
  - Penetration testing and final security fixes
  - Fix bugs, finalize crash reporting (Firebase Crashlytics)
  - Launch on iOS/Android

### Phase 2: Enhancements (3 months)
- Add quiz mode, sharing, PDF annotation, analytics
- Support additional LLMs/languages
- Implement 2FA for premium users

### Phase 3: Scale (3 months)
- Optimize for low-bandwidth (e.g., PDF compression)
- Add cloud sync and advanced analytics
- Explore web version

### Budget Estimate
- Development: $25,000–$35,000 (increased for testing/security)
- Hosting: $75–$150/month
- API Costs: User-paid via API keys
- **Security audit**: $5,000 (pre-launch penetration testing)

---

## 8. Risks and Mitigations

- **Risk**: High API costs for PDF processing
  - **Mitigation**: Limit PDF size (50 MB); summarize content before LLM processing
- **Risk**: Inaccurate lecture content
  - **Mitigation**: Use PDF as primary source; supplement with LLM/web search
- **Risk**: Scanned PDFs
  - **Mitigation**: Reject with clear error; suggest OCR tools for Phase 2
- **Risk**: Security vulnerabilities
  - **Mitigation**: Conduct penetration testing; use static analysis (Bandit, ESLint); encrypt sensitive data
- **Risk**: Poor code quality
  - **Mitigation**: Enforce linting (ESLint, Flake8); require code reviews; maintain >80% test coverage
- **Risk**: Authentication failures
  - **Mitigation**: Implement JWT refresh tokens; rate limit login attempts; test edge cases (e.g., expired tokens)
- **Risk**: Accessibility non-compliance
  - **Mitigation**: Test with WCAG tools and screen readers; involve users with disabilities in beta testing

---

## 9. Sample Prompts for LLM

### Text Input
> You are an expert educator with deep knowledge in [topic]. Create a [duration]-minute lecture script for a [difficulty] audience on "[topic/question]." Structure: Introduction (10%), key concepts (60%), examples/analogies (20%), conclusion (10%). Target [150 words/minute × duration] words. Prioritize factual accuracy.

### PDF Input
> You are an expert educator. Create a [duration]-minute lecture script for a [difficulty] audience based on the following PDF content: [extracted text/summary]. Focus on [user-specified topic or auto-summarized topic]. Structure: Introduction (10%), key concepts (60%), examples/analogies (20%), conclusion (10%). Target [150 words/minute × duration] words. Use PDF as primary source; supplement if needed.

---

## 10. Why a PRD is a Good Idea

### Benefits
1. **Clarity and Alignment**: Explicit testing, security, and authentication requirements ensure team alignment
2. **Predestined Decisions**: Defining linting tools, testing coverage, and security measures reduces ambiguity
3. **Efficiency**: Comprehensive specs for registration/login and error handling minimize rework
4. **User Trust**: Robust security and accessibility build confidence, especially for PDF uploads and API keys
5. **Risk Management**: Testing and monitoring plans mitigate crashes, vulnerabilities, and usability issues

### Considerations
- **Over-Specification**: Balanced by deferring complex features (e.g., 2FA, OCR) to Phase 2
- **Maintenance**: Assign product manager to update PRD post-beta feedback
- **Validation**: Beta testing critical to confirm authentication and PDF upload usability

---

## 11. Next Steps

1. **Validate PRD**: Share with developers/stakeholders, focusing on testing, security, and authentication
2. **Prototype**: Build web-based prototype for text/PDF-to-lecture pipeline, including login flow
3. **User Testing**: Beta test with 50 users (10 using PDF inputs, 10 testing accessibility)
4. **Hire Team**: Engage 2–3 developers, 1 UI/UX designer, 1 security consultant
5. **API Setup**: Test OpenRouter, ElevenLabs, PDFPlumber; validate authentication (JWT, OAuth)
6. **Security Audit**: Schedule penetration testing 1 month before launch
7. **CI/CD Setup**: Configure GitHub Actions with linting (ESLint, Flake8) and testing (Jest, Pytest)

---

## 12. Verification of Key Aspects

- **Testing**: Comprehensive unit, integration, UI/UX, performance, and security testing; >80% coverage; beta testing with 50 users
- **Linting**: ESLint (Airbnb) for frontend, Flake8/Black for backend; enforced in CI/CD
- **Authentication**: JWT-based with refresh tokens; OAuth (Google, Apple); rate-limited login attempts
- **Security**: AES-256 encryption, input sanitization, penetration testing, temporary PDF storage
- **Registration/Login**: Email/password with verification, OAuth support, secure password storage (bcrypt)
- **Other**: Accessibility (WCAG 2.1), logging (CloudWatch), error handling, crash monitoring (Firebase Crashlytics)
