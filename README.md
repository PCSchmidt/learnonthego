# LearnOnTheGo 🎧📚

> Transform any topic or PDF into personalized audio lectures using AI

[![Railway Deploy](https://img.shields.io/badge/Deploy%20on-Railway-0B0D0E?logo=railway&logoColor=white)](https://railway.app)
[![Vercel Deploy](https://img.shields.io/badge/Deploy%20on-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![React Native](https://img.shields.io/badge/React%20Native-TypeScript-61DAFB?logo=react&logoColor=white)](https://reactnative.dev)

LearnOnTheGo converts text topics or PDF documents into personalized audio lectures tailored to your preferred duration, difficulty level, and voice. Perfect for learning during walks, commutes, or workouts.

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
FastAPI Backend (Railway)
           ↓
PostgreSQL Database (Railway)
           ↓
External APIs (OpenRouter, ElevenLabs)
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
cd frontend
npm install
npm start
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
│   ├── services/     # Business logic (LLM, TTS, PDF)
│   ├── models/       # Database models
│   ├── auth/         # Authentication & JWT
│   └── tests/        # Backend tests
├── frontend/         # React Native app
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── screens/     # App screens
│   │   ├── services/    # API calls
│   │   └── auth/        # Frontend authentication
│   └── tests/        # Frontend tests
└── docs/             # Additional documentation
```

### Tech Stack
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Pytest
- **Frontend**: React Native, TypeScript, Jest
- **AI/ML**: OpenRouter, ElevenLabs, PDFPlumber
- **Hosting**: Railway (backend), Vercel (frontend)
- **Storage**: Cloudinary (temporary files)

### Development Commands
```bash
# Backend
cd backend
uvicorn main:app --reload          # Start development server
pytest --cov=.                    # Run tests with coverage
black . && flake8 . && bandit -r . # Code quality checks

# Frontend
cd frontend
npm start                          # Start React Native
npm run web                        # Start web version
npm test                          # Run tests
npm run lint                      # Lint code

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

### Phase 1: MVP (Current)
- [x] Basic text-to-lecture generation
- [x] PDF processing capabilities
- [x] User authentication
- [x] Audio playback and library
- [ ] Mobile app deployment

### Phase 2: Enhancement
- [ ] Multiple language support
- [ ] Quiz mode for comprehension
- [ ] Cloud synchronization
- [ ] Advanced voice options
- [ ] Lecture sharing

### Phase 3: Scale
- [ ] Team collaboration features
- [ ] Analytics dashboard
- [ ] API for third-party integrations
- [ ] Enterprise features

---

**Built with ❤️ for lifelong learners everywhere**

*Transform your commute into classroom time.*
