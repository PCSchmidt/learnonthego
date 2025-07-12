"""
LearnOnTheGo FastAPI Backend
A mobile-first app that converts text topics or PDF documents into personalized audio lectures.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import uvicorn
import os

# Initialize FastAPI app
app = FastAPI(
    title="LearnOnTheGo API",
    description="Convert text topics or PDF documents into personalized audio lectures",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:19006",  # Expo default
        "https://learnonthego-bice.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
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

# Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return HealthResponse(
        status="success",
        message="LearnOnTheGo API is running!",
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        version="1.0.0"
    )

@app.get("/api/health", response_model=HealthResponse)
async def api_health():
    """API health check"""
    return HealthResponse(
        status="healthy",
        message="API is ready to generate lectures",
        version="1.0.0"
    )

@app.post("/api/lectures/generate", response_model=LectureResponse)
async def generate_lecture(request: LectureRequest):
    """
    Generate audio lecture from text topic (Phase 0 - Proof of Concept)
    
    - **topic**: The subject matter for the lecture
    - **duration**: Length in minutes (5-60)
    - **difficulty**: beginner, intermediate, or advanced
    - **voice**: TTS voice selection
    
    Returns the generated lecture with download URL.
    """
    # Phase 0: Return mock response for proof of concept
    if not request.topic or len(request.topic.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Topic must be at least 3 characters long"
        )
    
    if request.duration < 5 or request.duration > 60:
        raise HTTPException(
            status_code=400,
            detail="Duration must be between 5 and 60 minutes"
        )
    
    if request.difficulty not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(
            status_code=400,
            detail="Difficulty must be: beginner, intermediate, or advanced"
        )
    
    # Mock response for Phase 0
    return LectureResponse(
        id="lecture_mock_001",
        title=f"Introduction to {request.topic}",
        duration=request.duration,
        audio_url="https://example.com/mock-lecture.mp3",
        status="completed"
    )

@app.get("/api/lectures")
async def list_lectures():
    """List user's lectures (requires authentication in Phase 1)"""
    # Phase 0: Return mock data
    return {
        "lectures": [],
        "total": 0,
        "message": "Authentication required - coming in Phase 1"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"detail": "Endpoint not found"}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"detail": "Internal server error"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True
    )
