# LearnOnTheGo - Getting Started Guide

## Development Stack Setup (Railway + Vercel + Cloudinary)

This guide follows the **Path 2: Python-First** approach with cost-optimized hosting.

---

## Phase 0: Development Environment Setup

### Prerequisites
- Python 3.9+ installed
- Node.js 18+ installed  
- Git configured
- VS Code with GitHub Copilot

### Step 1: Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/PCSchmidt/learnonthego.git
cd learnonthego

# Switch to dev branch for development
git checkout dev

# Create local development structure
mkdir -p backend frontend docs
```

### Step 2: Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install core dependencies
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install sqlalchemy==2.0.23
pip install psycopg2-binary==2.9.9
pip install alembic==1.12.1

# Install processing dependencies
pip install pdfplumber==4.0.2
pip install PyPDF2==3.0.1
pip install requests==2.31.0

# Install security dependencies
pip install cryptography==41.0.8
pip install bcrypt==4.1.2
pip install pyjwt==2.8.0

# Install file storage
pip install cloudinary==1.36.0

# Install development dependencies
pip install pytest==7.4.3
pip install pytest-cov==4.1.0
pip install black==23.11.0
pip install flake8==6.1.0
pip install bandit==1.7.5

# Create requirements.txt
pip freeze > requirements.txt
```

### Step 3: Create Basic Backend Structure

```bash
# Create backend directory structure
mkdir -p api services models auth tests config

# Create main application file
touch main.py

# Create configuration files
touch config/__init__.py
touch config/settings.py
touch config/database.py

# Create API routes
touch api/__init__.py
touch api/auth.py
touch api/lectures.py
touch api/users.py

# Create services
touch services/__init__.py
touch services/llm_service.py
touch services/tts_service.py
touch services/pdf_service.py

# Create models
touch models/__init__.py
touch models/user.py
touch models/lecture.py
touch models/api_key.py

# Create auth
touch auth/__init__.py
touch auth/jwt_handler.py
touch auth/password.py

# Create tests
touch tests/__init__.py
touch tests/test_auth.py
touch tests/test_lectures.py
```

### Step 4: Frontend Setup (React Native)

```bash
# Navigate back to root
cd ..

# Create React Native app in frontend directory
npx react-native init frontend --template react-native-template-typescript

# Navigate to frontend
cd frontend

# Install navigation dependencies
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context

# Install storage and utilities
npm install @react-native-async-storage/async-storage
npm install react-native-document-picker
npm install react-native-sound

# Install development dependencies
npm install --save-dev @types/react-native
npm install --save-dev eslint-config-airbnb-typescript
npm install --save-dev @testing-library/react-native
npm install --save-dev jest

# For web deployment (Vercel)
npm install @expo/webpack-config react-native-web
npx expo install expo
```

---

## Phase 1: Service Account Setup

### Step 1: Railway Setup

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project (run from backend directory)
cd backend
railway init

# Create railway.json configuration
echo '{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health"
  }
}' > railway.json
```

### Step 2: Vercel Setup

```bash
# Install Vercel CLI
npm install -g vercel

# From frontend directory
cd ../frontend

# Initialize Vercel project
vercel init

# Create vercel.json for React Native web
echo '{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "web-build" }
    }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}' > vercel.json
```

### Step 3: Cloudinary Setup

1. Create free account at [cloudinary.com](https://cloudinary.com)
2. Get your Cloud Name, API Key, and API Secret
3. Add to Railway environment variables:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

---

## Phase 2: Basic Implementation

### Step 1: Create Basic FastAPI App

Create `backend/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, lectures, users
from config.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LearnOnTheGo API",
    description="Audio lecture generation API",
    version="0.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(lectures.router, prefix="/api/lectures", tags=["lectures"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/")
async def root():
    return {"message": "LearnOnTheGo API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### Step 2: Database Configuration

Create `backend/config/database.py`:
```python
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./learnonthego.db"  # Fallback for local development
)

# Handle Railway PostgreSQL URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Step 3: Environment Variables Setup

Create `backend/.env` (for local development):
```bash
DATABASE_URL=sqlite:///./learnonthego.db
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Step 4: Deploy Initial Version

```bash
# Deploy backend to Railway
cd backend
railway up

# Deploy frontend to Vercel
cd ../frontend
vercel --prod
```

---

## Phase 3: Development Workflow

### Local Development Commands

```bash
# Start backend (from backend directory)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (from frontend directory)
npx react-native start
# For web development:
npm run web

# Run tests
# Backend:
pytest --cov=. --cov-report=html
# Frontend:
npm test

# Code quality checks
black . && flake8 . && bandit -r .
```

### Git Workflow

```bash
# Feature development workflow
git checkout dev
git pull origin dev
git checkout -b feature/lecture-generation
# ... make changes ...
git add .
git commit -m "feat: implement basic lecture generation"
git push origin feature/lecture-generation
# ... create PR to dev branch ...
```

### Environment Setup for Railway

Set these environment variables in Railway dashboard:
```bash
DATABASE_URL=postgresql://... # Automatically provided by Railway
JWT_SECRET_KEY=your-production-jwt-secret
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
OPENROUTER_FALLBACK_KEY=optional-fallback-key
```

---

## Phase 4: Next Steps

### Immediate Tasks (Week 1)
1. ✅ Set up development environment
2. ✅ Deploy basic "Hello World" to Railway + Vercel
3. ⏳ Implement user authentication (JWT)
4. ⏳ Create basic UI components
5. ⏳ Set up API key management

### Week 2-3 Tasks
1. Implement text-to-lecture generation
2. Add OpenRouter integration
3. Add basic TTS with fallback
4. Create audio playback component
5. Add basic error handling

### Week 4-6 Tasks
1. Add PDF processing capabilities
2. Implement lecture library
3. Add offline storage
4. Performance optimization
5. Security audit

---

## Useful Commands Reference

### Railway Commands
```bash
railway login
railway status
railway logs
railway shell
railway run python manage.py migrate
railway environment
```

### Vercel Commands
```bash
vercel dev          # Local development
vercel --prod       # Production deployment
vercel logs         # View logs
vercel env ls       # List environment variables
```

### Development Commands
```bash
# Backend
source venv/bin/activate  # Activate virtual environment
uvicorn main:app --reload # Start development server
pytest                   # Run tests
black .                  # Format code
flake8 .                 # Lint code

# Frontend
npm start               # Start React Native packager
npm run web            # Start web development
npm test               # Run tests
npm run lint           # Lint code
```

---

## Troubleshooting

### Common Issues
1. **Railway deployment fails**: Check `requirements.txt` and `railway.json`
2. **Database connection issues**: Verify `DATABASE_URL` format
3. **CORS errors**: Update allowed origins in FastAPI middleware
4. **React Native build fails**: Clear metro cache with `npx react-native start --reset-cache`

### Getting Help
- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs
- FastAPI docs: https://fastapi.tiangolo.com
- React Native docs: https://reactnative.dev

This setup gives you a solid foundation for building LearnOnTheGo with minimal upfront costs while maintaining the flexibility to scale as needed.
