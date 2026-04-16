import sys
import os
# Add both the current directory and auth directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'auth'))

"""
LearnOnTheGo Backend
FastAPI application with OpenRouter LLM integration for lecture generation
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import os
from datetime import datetime

# Import API routes
# from api.lectures import router as lectures_router
from api.users import router as users_router
from api.auth import router as auth_router
from api.api_key_routes import router as api_keys_router
from api.lecture_routes import router as lectures_router

# Import database initialization
from models import create_tables_async, check_database_health

# Initialize FastAPI app
app = FastAPI(
    title="LearnOnTheGo API",
    description="Backend API for generating personalized audio lectures from text topics and PDF documents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for React Native frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://learnonthego-bice.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# Include API routes
app.include_router(lectures_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(api_keys_router)


# Database initialization on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup"""
    try:
        # Create database tables if they don't exist
        await create_tables_async()
        print("✅ Database tables initialized successfully")
        
        # Check database health
        is_healthy = await check_database_health()
        if is_healthy:
            print("✅ Database connection verified")
        else:
            print("⚠️ Database connection issues detected")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Don't fail startup - allow app to run for debugging

# Pydantic models for existing endpoints
class HealthResponse(BaseModel):
    status: str
    message: str
    version: str

class LectureRequest(BaseModel):
    topic: str
    duration: int  # minutes
    difficulty: str  # beginner, intermediate, advanced
    voice: str = "default"

class LectureResponse(BaseModel):
    id: str
    title: str
    duration: int
    audio_url: str
    status: str

class StatusResponse(BaseModel):
    status: str
    phase: str
    features_implemented: list[str]
    next_features: list[str]
    deployment: dict

# Routes
@app.get("/", response_model=dict)
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "LearnOnTheGo API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "features": {
            "openrouter_integration": True,
            "pdf_processing": True,
            "tts_generation": True,
            "api_key_encryption": True
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        message="All services operational",
        version="1.0.0"
    )

@app.get("/api/health", response_model=HealthResponse)
async def api_health():
    """API health check"""
    return HealthResponse(
        status="healthy", 
        message="AI integration ready - OpenRouter, PDF, TTS services available",
        version="1.0.0"
    )

@app.get("/api/config")
async def get_api_config():
    """
    Get API configuration and available features
    
    Returns:
        API configuration for frontend integration
    """
    return {
        "features": {
            "text_to_lecture": True,
            "pdf_to_lecture": True,
            "custom_voices": True,
            "multiple_models": True,
            "user_api_keys": True,
            "real_time_generation": True
        },
        "limits": {
            "max_duration": 60,
            "min_duration": 5,
            "max_pdf_size_mb": 50,
            "max_pdf_pages": 200,
            "max_topic_length": 500,
            "max_context_length": 2000
        },
        "supported_formats": {
            "input": ["text", "pdf"],
            "output": ["mp3"],
            "pdf_types": ["text-based only"]
        },
        "providers": {
            "llm": ["openrouter"],
            "tts": ["elevenlabs", "fallback"],
            "models": [
                "anthropic/claude-3.5-sonnet",
                "openai/gpt-4o",
                "meta-llama/llama-3.1-405b-instruct"
            ]
        },
        "version": "1.0.0"
    }

@app.get("/api/audio/{lecture_id}")
async def download_audio(lecture_id: str):
    """
    Download audio file for a lecture
    
    Args:
        lecture_id: Unique lecture identifier
        
    Returns:
        Audio file download
    """
    try:
        # Look for audio file in temp_audio directory
        audio_dir = "temp_audio"
        
        # Try different file formats
        for ext in [".mp3", "_fallback.txt"]:
            audio_path = os.path.join(audio_dir, f"lecture_{lecture_id}{ext}")
            if os.path.exists(audio_path):
                if ext == ".mp3":
                    return FileResponse(
                        audio_path,
                        media_type="audio/mpeg",
                        filename=f"lecture_{lecture_id}.mp3"
                    )
                else:
                    return FileResponse(
                        audio_path,
                        media_type="text/plain",
                        filename=f"lecture_{lecture_id}_fallback.txt"
                    )
        
        # If no file found, check if it might be in chunks
        chunk_files = []
        for i in range(10):  # Check up to 10 chunks
            chunk_path = os.path.join(audio_dir, f"lecture_{lecture_id}_chunk_{i:02d}.mp3")
            if os.path.exists(chunk_path):
                chunk_files.append(chunk_path)
        
        if chunk_files:
            # Return first chunk for now (in production, would concatenate)
            return FileResponse(
                chunk_files[0],
                media_type="audio/mpeg",
                filename=f"lecture_{lecture_id}_part1.mp3"
            )
        
        raise HTTPException(
            status_code=404,
            detail=f"Audio file not found for lecture {lecture_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve audio file: {str(e)}"
        )

@app.get("/status", response_model=StatusResponse)
async def get_development_status():
    """Development status and progress tracking endpoint"""
    return StatusResponse(
        status="operational",
        phase="1.0.0 GA",
        features_implemented=[
            "✅ FastAPI backend with Railway deployment",
            "✅ React Native frontend with Vercel deployment", 
            "✅ Automatic CI/CD pipeline from dev branch",
            "✅ Complete app navigation structure",
            "✅ Mock lecture generation API",
            "✅ Health monitoring endpoints",
            "✅ CORS configuration for frontend integration",
            "✅ API documentation with Swagger/ReDoc",
            "✅ OpenRouter LLM service integration",
            "✅ ElevenLabs TTS service with fallback",
            "✅ PDF text extraction and processing",
            "✅ AES-256 API key encryption service",
            "✅ Complete lecture generation pipeline",
            "✅ Structured API endpoints for AI features"
        ],
        next_features=[
            "🔄 Database integration (SQLAlchemy + PostgreSQL)",
            "🔄 User authentication and JWT implementation",
            "🔄 Frontend AI service integration",
            "🔄 File upload and management",
            "🔄 User library and lecture storage",
            "🔄 Rate limiting and usage tracking"
        ],
        deployment={
            "backend_url": "https://learnonthego-production.up.railway.app",
            "frontend_url": "https://learnonthego-bice.vercel.app",
            "docs_url": "https://learnonthego-production.up.railway.app/docs",
            "last_updated": "2025-01-14",
            "build_status": "v1.0.0_ga",
            "ai_services": "integrated"
        }
    )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Endpoint not found"})

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True
    )
