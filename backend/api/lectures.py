"""
Lecture Generation API Routes for LearnOnTheGo
Handles lecture creation from text topics and PDF documents
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, Dict, Any
import os
from datetime import datetime

from services import create_lecture_service, LectureGenerationService
from models.lecture_models import (
    LectureRequest,
    LectureResponse,
    PDFLectureRequest,
    VoiceSettings,
    APIKeyValidationRequest,
    APIKeyValidationResponse
)
from auth.dependencies import get_current_user
from models.user_models import User

router = APIRouter(prefix="/api/lectures", tags=["lectures"])

# Initialize lecture service
lecture_service = create_lecture_service()


@router.post("/generate", response_model=LectureResponse)
async def generate_lecture_from_text(
    request: LectureRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate audio lecture from text topic
    
    ⚠️ COST WARNING: This endpoint uses external APIs with costs:
    - AI Content Generation: ~$0.001-0.003 per lecture
    - Text-to-Speech: ~$0.50-2.00 per lecture (depending on length)
    - Total estimated cost: $0.50-2.00 per lecture
    
    Users must provide their own API keys and accept cost responsibility.
    
    🎭 DEVELOPMENT: Set MOCK_MODE=true environment variable for cost-free testing
    
    Args:
        request: Lecture generation parameters including topic, duration, difficulty
        current_user: Authenticated user (from JWT token)
        
    Returns:
        LectureResponse with generated audio file and metadata
        
    Raises:
        HTTPException: If API keys invalid, rate limit exceeded, or generation fails
    """
    
    try:
        # Initialize AI service with user's API key
        init_success = await lecture_service.initialize_ai_service(
            encrypted_api_key=current_user.openrouter_api_key,
            user_id=str(current_user.id)
        )
        
        if not init_success:
            raise HTTPException(
                status_code=400,
                detail="Invalid or missing OpenRouter API key. Please configure your API key in settings."
            )
        
        # Validate input parameters
        if not request.topic or len(request.topic.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Topic must be at least 10 characters long"
            )
        
        if not 5 <= request.duration <= 60:
            raise HTTPException(
                status_code=400,
                detail="Duration must be between 5 and 60 minutes"
            )
        
        if request.difficulty not in ["beginner", "intermediate", "advanced"]:
            raise HTTPException(
                status_code=400,
                detail="Difficulty must be beginner, intermediate, or advanced"
            )
        
        # Generate lecture
        result = await lecture_service.generate_lecture_from_text(
            topic=request.topic,
            duration=request.duration,
            difficulty=request.difficulty,
            voice_settings=request.voice_settings.dict(),
            user_context=request.user_context
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Lecture generation failed")
            )
        
        # Return successful response
        return LectureResponse(
            success=True,
            lecture_id=result["lecture_id"],
            title=result["title"],
            duration=result["duration"],
            difficulty=result["difficulty"],
            source_type=result["source_type"],
            audio_file_url=f"/api/audio/{result['lecture_id']}",
            file_size=result["file_size"],
            estimated_duration=result["estimated_duration"],
            created_at=result["created_at"],
            content_sections=result["content_sections"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/generate-from-pdf", response_model=LectureResponse)
async def generate_lecture_from_pdf(
    file: UploadFile = File(...),
    duration: int = Form(...),
    difficulty: str = Form(...),
    voice_settings: str = Form(...),  # JSON string
    custom_topic: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Generate audio lecture from PDF document
    
    - **file**: PDF file to process (max 50MB, text-based only)
    - **duration**: Length in minutes (5-60)
    - **difficulty**: beginner, intermediate, or advanced
    - **voice_settings**: TTS voice configuration (JSON string)
    - **custom_topic**: Optional custom topic override
    
    Returns the generated lecture with download URL.
    """
    
    temp_file_path = None
    
    try:
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Validate form parameters
        if not 5 <= duration <= 60:
            raise HTTPException(
                status_code=400,
                detail="Duration must be between 5 and 60 minutes"
            )
        
        if difficulty not in ["beginner", "intermediate", "advanced"]:
            raise HTTPException(
                status_code=400,
                detail="Difficulty must be beginner, intermediate, or advanced"
            )
        
        # Parse voice settings JSON
        import json
        try:
            voice_settings_dict = json.loads(voice_settings)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid voice_settings JSON format"
            )
        
        # Initialize AI service with user's API key
        init_success = await lecture_service.initialize_ai_service(
            encrypted_api_key=current_user.openrouter_api_key,
            user_id=str(current_user.id)
        )
        
        if not init_success:
            raise HTTPException(
                status_code=400,
                detail="Invalid or missing OpenRouter API key. Please configure your API key in settings."
            )
        
        # Save uploaded file temporarily
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"upload_{timestamp}_{file.filename}"
        temp_file_path = os.path.join(temp_dir, temp_filename)
        
        # Write file content
        content = await file.read()
        with open(temp_file_path, "wb") as f:
            f.write(content)
        
        # Generate lecture from PDF
        result = await lecture_service.generate_lecture_from_pdf(
            pdf_path=temp_file_path,
            duration=duration,
            difficulty=difficulty,
            voice_settings=voice_settings_dict,
            custom_topic=custom_topic
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "PDF lecture generation failed")
            )
        
        # Return successful response
        return LectureResponse(
            success=True,
            lecture_id=result["lecture_id"],
            title=result["title"],
            duration=result["duration"],
            difficulty=result["difficulty"],
            source_type=result["source_type"],
            source_file=result.get("source_file"),
            audio_file_url=f"/api/audio/{result['lecture_id']}",
            file_size=result["file_size"],
            estimated_duration=result["estimated_duration"],
            created_at=result["created_at"],
            content_sections=result["content_sections"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass  # Ignore cleanup errors


@router.post("/validate-api-key", response_model=APIKeyValidationResponse)
async def validate_openrouter_api_key(
    request: APIKeyValidationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Validate user's OpenRouter API key and return available models
    
    - **encrypted_api_key**: User's encrypted OpenRouter API key
    
    Returns validation result with available models if successful.
    """
    
    try:
        # Validate API key
        result = await lecture_service.validate_user_api_key(
            encrypted_api_key=request.encrypted_api_key,
            user_id=str(current_user.id)
        )
        
        if not result["success"]:
            return APIKeyValidationResponse(
                success=False,
                valid=False,
                error=result.get("error", "API key validation failed")
            )
        
        return APIKeyValidationResponse(
            success=True,
            valid=result["valid"],
            available_models=result.get("available_models", []),
            model_count=result.get("model_count", 0)
        )
        
    except Exception as e:
        return APIKeyValidationResponse(
            success=False,
            valid=False,
            error=f"Validation error: {str(e)}"
        )


@router.get("/service-status")
async def get_service_status(current_user: User = Depends(get_current_user)):
    """
    Get status of all lecture generation services
    
    Returns current status of OpenRouter, PDF, TTS, and encryption services.
    """
    
    try:
        status = await lecture_service.get_service_status()
        
        return {
            "success": True,
            "services": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service status: {str(e)}"
        )


@router.get("/models")
async def get_available_models(current_user: User = Depends(get_current_user)):
    """
    Get available OpenRouter models for lecture generation
    
    Returns list of available LLM models with their capabilities.
    """
    
    try:
        # Initialize AI service if possible
        if current_user.openrouter_api_key:
            await lecture_service.initialize_ai_service(
                encrypted_api_key=current_user.openrouter_api_key,
                user_id=str(current_user.id)
            )
            
            if lecture_service.openrouter_service:
                models = await lecture_service.openrouter_service.get_available_models()
                return {
                    "success": True,
                    "models": models
                }
        
        # Return default models if no API key configured
        return {
            "success": True,
            "models": [
                {
                    "id": "anthropic/claude-3.5-sonnet",
                    "name": "Claude 3.5 Sonnet",
                    "description": "Excellent for content generation",
                    "context_length": 200000
                },
                {
                    "id": "openai/gpt-4o",
                    "name": "GPT-4o", 
                    "description": "High-quality content generation",
                    "context_length": 128000
                }
            ],
            "note": "Configure OpenRouter API key to see all available models"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get models: {str(e)}"
        )
