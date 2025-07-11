"""
FastAPI app configuration with automatic API documentation generation.

This module sets up the FastAPI application with:
- Automatic OpenAPI/Swagger documentation
- ReDoc documentation  
- CORS configuration
- Health checks
- Error handling
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
import os

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="LearnOnTheGo API",
        description="""
        ## LearnOnTheGo Audio Lecture Generation API

        Transform text topics or PDF documents into personalized audio lectures using AI.

        ### Features
        - **Text-to-Lecture**: Convert any topic into structured audio content
        - **PDF Processing**: Extract and summarize PDF documents into lectures  
        - **Customizable Parameters**: Duration, difficulty, voice selection
        - **Secure API Key Management**: Encrypted storage of user API keys
        - **Multi-Provider Support**: OpenRouter, OpenAI, Anthropic for LLM; ElevenLabs, Google TTS for audio

        ### Authentication
        Most endpoints require JWT authentication. Use the `/auth/login` endpoint to obtain a token.

        ### Rate Limits
        - Lecture generation: 10 per hour per user
        - PDF uploads: 5 per hour per user
        - Login attempts: 5 per 15 minutes

        ### File Limits
        - PDF files: Maximum 50MB, text-based only
        - Audio output: MP3 format, 128 kbps
        """,
        version="0.1.0",
        contact={
            "name": "LearnOnTheGo Support",
            "url": "https://github.com/PCSchmidt/learnonthego",
            "email": "support@learnonthego.app",
        },
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
        docs_url="/docs" if os.getenv("DEBUG", "False").lower() == "true" else None,
        redoc_url="/redoc" if os.getenv("DEBUG", "False").lower() == "true" else None,
    )

    # CORS configuration
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )

    return app

def custom_openapi(app: FastAPI):
    """
    Generate custom OpenAPI schema with additional metadata.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        dict: Custom OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="LearnOnTheGo API",
        version="0.1.0",
        description="Audio lecture generation API with AI",
        routes=app.routes,
    )
    
    # Add custom metadata
    openapi_schema["info"]["x-logo"] = {
        "url": "https://your-domain.com/logo.png"
    }
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://your-app.railway.app",
            "description": "Production server"
        }
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Example of how to document endpoints with proper schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class DifficultyLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class LectureRequest(BaseModel):
    '''Request model for lecture generation'''
    topic: str = Field(..., description="Topic or question for the lecture", max_length=500)
    duration: int = Field(..., description="Lecture duration in minutes", ge=5, le=60)
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    voice: str = Field(..., description="TTS voice selection")
    language: str = Field("en", description="Language code", regex="^[a-z]{2}$")
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "Quantum computing fundamentals",
                "duration": 20,
                "difficulty": "intermediate",
                "voice": "nova",
                "language": "en"
            }
        }

class LectureResponse(BaseModel):
    '''Response model for generated lecture'''
    id: str = Field(..., description="Unique lecture identifier")
    title: str = Field(..., description="Generated lecture title")
    duration: int = Field(..., description="Actual lecture duration in minutes")
    audio_url: str = Field(..., description="URL to download the audio file")
    created_at: str = Field(..., description="Creation timestamp in ISO format")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "lec_abc123",
                "title": "Quantum Computing Fundamentals",
                "duration": 20,
                "audio_url": "https://cdn.example.com/lectures/lec_abc123.mp3",
                "created_at": "2025-07-11T12:00:00Z"
            }
        }

# Example endpoint with full documentation
@app.post(
    "/api/lectures/generate",
    response_model=LectureResponse,
    summary="Generate audio lecture",
    description="Generate a personalized audio lecture from a text topic",
    responses={
        200: {"description": "Lecture generated successfully"},
        400: {"description": "Invalid request parameters"},
        401: {"description": "Authentication required"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    },
    tags=["Lectures"]
)
async def generate_lecture(
    request: LectureRequest,
    current_user: User = Depends(get_current_user)
):
    '''
    Generate an audio lecture from a text topic.
    
    This endpoint creates a personalized audio lecture based on the provided topic,
    duration, difficulty level, and voice preferences. The lecture is structured
    with an introduction, key concepts, examples, and conclusion.
    
    **Rate Limits:** 10 lectures per hour per user
    
    **Processing Time:** Typically 10-30 seconds
    '''
    pass
"""
