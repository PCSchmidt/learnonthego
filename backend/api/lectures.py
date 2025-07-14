"""
Enhanced Lecture Generation API Routes for LearnOnTheGo
Phase 2f: Multi-Provider TTS with Cost Optimization
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, Dict, Any, Literal
import os
from datetime import datetime
from pydantic import BaseModel

from services import create_lecture_service, LectureGenerationService
from services.enhanced_tts_service import EnhancedTTSService, QUALITY_TIER, TTS_PROVIDER, TTSCostAnalyzer
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

# Initialize services
lecture_service = create_lecture_service()
enhanced_tts = EnhancedTTSService()


# Enhanced request models
class EnhancedLectureRequest(BaseModel):
    topic: str
    duration: int  # minutes (5-60)
    difficulty: str  # beginner, intermediate, advanced
    voice_id: str
    quality_tier: QUALITY_TIER = "standard"
    provider_preference: Optional[TTS_PROVIDER] = None
    language: str = "en"

class CostEstimateRequest(BaseModel):
    character_count: int
    provider: Optional[TTS_PROVIDER] = None
    
class CostEstimateResponse(BaseModel):
    provider: str
    estimated_cost: float
    free_tier_remaining: int
    quality_score: float


@router.post("/generate", response_model=LectureResponse)
async def generate_lecture_from_text(
    request: LectureRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate audio lecture from text topic
    
    🚀 ENHANCED: Now with smart TTS provider selection and cost optimization!
    
    ⚠️ COST WARNING: API costs vary by provider:
    - Google Standard: $4/million chars (4M free/month)
    - Google Neural2: $16/million chars (1M free/month)
    - OpenAI TTS: $15/million chars 
    - ElevenLabs: $165/million chars (premium quality)
    - Unreal Speech: $2/million chars (English only)
    
    💡 SMART SELECTION: Service automatically chooses optimal provider
    
    Args:
        request: Lecture generation parameters
        current_user: Authenticated user
        
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


# ===============================
# ENHANCED TTS ENDPOINTS (Phase 2f)
# ===============================

@router.post("/generate-enhanced", response_model=LectureResponse)
async def generate_lecture_enhanced(
    request: EnhancedLectureRequest,
    current_user: User = Depends(get_current_user)
):
    """
    🚀 Enhanced lecture generation with smart TTS provider selection
    
    Features:
    - Automatic provider selection based on cost/quality
    - Audio caching to prevent duplicate TTS costs
    - Text optimization to reduce character count
    - Transparent cost reporting
    
    Quality Tiers:
    - free: Google Standard (4M chars free/month)
    - standard: OpenAI TTS or Unreal Speech (cost-effective)
    - premium: ElevenLabs (highest quality)
    """
    try:
        # Initialize AI service
        init_success = await lecture_service.initialize_ai_service(
            encrypted_api_key=current_user.openrouter_api_key,
            user_id=str(current_user.id)
        )
        
        if not init_success:
            raise HTTPException(
                status_code=400,
                detail="Invalid or missing OpenRouter API key"
            )
        
        # Generate lecture content
        content_result = await lecture_service.generate_lecture_from_text(
            topic=request.topic,
            duration=request.duration,
            difficulty=request.difficulty,
            voice_settings={"voice_id": request.voice_id},
            user_context={}
        )
        
        if not content_result["success"]:
            raise HTTPException(status_code=500, detail="Content generation failed")
        
        # Extract script content for TTS
        script_content = content_result.get("content_sections", {}).get("script", "")
        if not script_content:
            raise HTTPException(status_code=500, detail="No script content generated")
        
        # Generate audio using enhanced TTS
        voice_settings = {"voice_id": request.voice_id}
        tts_result = await enhanced_tts.generate_audio_smart(
            content=script_content,
            user_id=current_user.id,
            user_tier=request.quality_tier,
            voice_settings=voice_settings,
            provider_override=request.provider_preference,
            language=request.language
        )
        
        if not tts_result["success"]:
            raise HTTPException(
                status_code=500, 
                detail=f"TTS generation failed: {tts_result.get('error', 'Unknown error')}"
            )
        
        # Return enhanced response with cost information
        return LectureResponse(
            success=True,
            lecture_id=content_result["lecture_id"],
            title=content_result["title"],
            duration=content_result["duration"],
            difficulty=content_result["difficulty"],
            source_type="text",
            audio_file_url=f"/api/audio/{content_result['lecture_id']}",
            file_size=tts_result.get("file_size", 0),
            estimated_duration=content_result["estimated_duration"],
            created_at=content_result["created_at"],
            content_sections=content_result["content_sections"],
            # Enhanced fields
            provider_used=tts_result["provider"],
            estimated_cost=tts_result.get("estimated_cost", 0.0),
            character_count=tts_result.get("character_count", 0),
            was_cached=tts_result.get("cached", False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced generation failed: {str(e)}")


@router.post("/estimate-cost", response_model=CostEstimateResponse)
async def estimate_tts_cost(
    request: CostEstimateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Estimate TTS cost for given character count
    
    Helps users make informed decisions about provider selection
    and understand potential costs before generation.
    """
    try:
        # Get user's current monthly usage (placeholder)
        monthly_usage = 0  # TODO: Implement actual usage tracking
        
        # Select optimal provider if not specified
        provider = request.provider or enhanced_tts.select_optimal_provider(
            user_tier="standard",  # Default tier
            text_length=request.character_count,
            monthly_usage=monthly_usage
        )
        
        estimated_cost = enhanced_tts.estimate_cost(request.character_count, provider)
        provider_config = enhanced_tts.providers[provider]
        
        return CostEstimateResponse(
            provider=provider,
            estimated_cost=estimated_cost,
            free_tier_remaining=max(0, provider_config["free_tier"] - monthly_usage),
            quality_score=provider_config["quality_score"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost estimation failed: {str(e)}")


@router.get("/cost-comparison/{character_count}")
async def get_cost_comparison(
    character_count: int,
    current_user: User = Depends(get_current_user)
):
    """
    Compare costs across all TTS providers for transparency
    
    Returns comprehensive cost analysis to help users choose
    the best provider for their needs and budget.
    """
    try:
        if character_count <= 0 or character_count > 10_000_000:
            raise HTTPException(
                status_code=400,
                detail="Character count must be between 1 and 10,000,000"
            )
        
        comparison = TTSCostAnalyzer.compare_monthly_costs(character_count)
        best_value = TTSCostAnalyzer.get_best_value_provider(character_count)
        
        # Calculate potential savings
        elevenlabs_cost = comparison["elevenlabs"]["total_cost"]
        google_neural_cost = comparison["google_neural"]["total_cost"]
        best_value_cost = comparison[best_value]["total_cost"]
        
        return {
            "character_count": character_count,
            "provider_comparison": comparison,
            "recommended_provider": best_value,
            "cost_analysis": {
                "cheapest_option": min(comparison.items(), key=lambda x: x[1]["total_cost"]),
                "highest_quality": max(comparison.items(), key=lambda x: x[1]["quality_score"]),
                "best_value": best_value
            },
            "potential_savings": {
                "vs_elevenlabs": round(elevenlabs_cost - best_value_cost, 4),
                "vs_google_neural": round(google_neural_cost - best_value_cost, 4),
                "savings_percentage": round(((elevenlabs_cost - best_value_cost) / elevenlabs_cost * 100), 1) if elevenlabs_cost > 0 else 0
            },
            "recommendations": {
                "for_free_tier": "Use Google Standard (4M chars free)",
                "for_cost_effective": "Use Unreal Speech for English content",
                "for_premium_quality": "Use ElevenLabs for best results",
                "for_multilingual": "Use Google Neural2 for non-English content"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost comparison failed: {str(e)}")


@router.get("/tts-providers")
async def get_tts_providers(current_user: User = Depends(get_current_user)):
    """
    Get available TTS providers with their capabilities and pricing
    
    Returns comprehensive information about all supported TTS providers
    to help users make informed decisions.
    """
    try:
        providers_info = {}
        
        for provider_id, config in enhanced_tts.providers.items():
            providers_info[provider_id] = {
                "name": provider_id.replace("_", " ").title(),
                "cost_per_million_chars": config["cost_per_million"],
                "free_tier_chars": config["free_tier"],
                "quality_score": config["quality_score"],
                "supported_languages": config["languages"],
                "best_for": {
                    "google_standard": "Free tier users, basic quality needs",
                    "google_neural": "Multilingual content, good quality",
                    "openai": "Balanced cost and quality",
                    "elevenlabs": "Premium quality, realistic voices",
                    "unreal_speech": "Cost-effective English content"
                }.get(provider_id, "General use"),
                "features": {
                    "google_standard": ["Free 4M chars/month", "40+ languages", "Basic quality"],
                    "google_neural": ["Free 1M chars/month", "Neural voices", "40+ languages"],
                    "openai": ["High quality", "6 voices", "20+ languages"],
                    "elevenlabs": ["Premium quality", "Voice cloning", "Emotion control"],
                    "unreal_speech": ["Very low cost", "English only", "Good quality"]
                }.get(provider_id, ["Standard features"])
            }
        
        return {
            "providers": providers_info,
            "usage_recommendations": {
                "free_users": "Start with Google Standard (4M free chars)",
                "standard_users": "Use Unreal Speech for English, OpenAI for others",
                "premium_users": "Use ElevenLabs for best quality",
                "multilingual": "Use Google Neural2 for non-English content"
            },
            "cost_optimization_tips": [
                "Use caching to avoid duplicate TTS costs",
                "Optimize text length before TTS generation",
                "Choose provider based on content language",
                "Monitor monthly usage to stay within free tiers"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TTS providers: {str(e)}")
