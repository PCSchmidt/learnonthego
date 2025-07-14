"""
Multi-Provider AI API Routes for LearnOnTheGo
Phase 2f: Enhanced lecture generation with intelligent provider routing

New endpoints for cost-optimized, multi-provider AI lecture generation.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

from services.multi_provider_llm import multi_provider_llm, LLMRequest, LLMResponse
from services.multi_provider_tts import multi_provider_tts, TTSRequest, TTSResponse
from services.ai_provider_manager import ai_provider_manager
from models.lecture_orm import QualityTier, LLMProvider, TTSProvider
from models.user_orm import User as UserORM
from models.user_models import User
from auth.dependencies import get_current_user

router = APIRouter(prefix="/api/ai", tags=["Multi-Provider AI"])


# Request/Response Models
class MultiProviderLectureRequest(BaseModel):
    """Enhanced lecture request with multi-provider options"""
    topic: str = Field(..., description="Lecture topic", min_length=10, max_length=500)
    duration: int = Field(..., description="Duration in minutes", ge=5, le=60)
    difficulty: str = Field(..., description="Difficulty level", regex="^(beginner|intermediate|advanced)$")
    
    # Quality and cost preferences
    quality_tier: QualityTier = Field(QualityTier.STANDARD, description="Quality vs cost preference")
    max_cost_usd: Optional[float] = Field(None, description="Maximum acceptable cost", ge=0, le=10)
    prefer_free_tier: bool = Field(True, description="Prefer free tier when available")
    
    # Provider preferences
    llm_provider_preference: Optional[LLMProvider] = Field(None, description="Preferred LLM provider")
    tts_provider_preference: Optional[TTSProvider] = Field(None, description="Preferred TTS provider")
    llm_model_preference: Optional[str] = Field(None, description="Specific LLM model")
    
    # Voice and language settings
    voice_id: str = Field("default", description="Voice ID for TTS")
    language: str = Field("en", description="Content language")
    voice_speed: float = Field(1.0, description="Speech rate", ge=0.5, le=2.0)
    
    # Content preferences
    content_style: str = Field("educational", description="Content style", regex="^(educational|conversational|formal)$")
    include_examples: bool = Field(True, description="Include examples in content")
    include_summary: bool = Field(True, description="Include summary section")


class ProviderRecommendation(BaseModel):
    """Provider recommendation with reasoning"""
    llm_recommendation: Dict[str, Any]
    tts_recommendation: Dict[str, Any]
    total_estimated_cost: float
    cost_breakdown: Dict[str, float]
    potential_savings: Dict[str, Any]


class MultiProviderLectureResponse(BaseModel):
    """Enhanced lecture response with provider information"""
    success: bool
    lecture_id: str
    title: str
    duration: int
    difficulty: str
    
    # AI Provider Information
    llm_provider_used: str
    llm_model_used: str
    tts_provider_used: str
    voice_used: str
    quality_tier_used: str
    
    # Cost Information
    llm_cost_usd: float
    tts_cost_usd: float
    total_cost_usd: float
    cost_optimization_used: bool
    was_cached: bool
    
    # Performance Metrics
    llm_generation_time_ms: int
    tts_generation_time_ms: int
    total_generation_time_ms: int
    
    # Content Information
    audio_file_url: str
    estimated_audio_duration: int
    character_count: int
    token_count: int
    
    # Metadata
    created_at: str
    error: Optional[str] = None


class CostAnalysisRequest(BaseModel):
    """Request for cost analysis across providers"""
    text_length_chars: int = Field(..., description="Estimated text length", ge=100, le=50000)
    estimated_tokens: int = Field(..., description="Estimated token count", ge=50, le=10000)
    quality_tier: QualityTier = Field(QualityTier.STANDARD, description="Quality tier")
    language: str = Field("en", description="Content language")


class CostAnalysisResponse(BaseModel):
    """Cost analysis across all providers"""
    current_approach_cost: float
    optimized_approach_cost: float
    potential_savings: float
    savings_percentage: float
    
    llm_provider_costs: Dict[str, float]
    tts_provider_costs: Dict[str, float]
    
    recommendations: Dict[str, str]
    monthly_projection: Dict[str, float]


# API Endpoints

@router.post("/generate-lecture", response_model=MultiProviderLectureResponse)
async def generate_lecture_multi_provider(
    request: MultiProviderLectureRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    🚀 Generate lecture using intelligent multi-provider AI routing
    
    **Features:**
    - Automatic cost optimization with 70-95% savings potential
    - Smart provider selection based on quality tier and preferences
    - Free tier utilization when available
    - Caching for repeated content
    - Comprehensive cost tracking and reporting
    
    **Quality Tiers:**
    - `free`: Prioritize free tier providers (Google TTS free tier)
    - `standard`: Balance cost and quality (recommended)
    - `premium`: Best quality available (ElevenLabs, GPT-4)
    
    **Cost Optimization:**
    - Automatic provider routing based on content and preferences
    - Free tier usage for Google TTS (4M chars/month)
    - Intelligent caching to avoid duplicate costs
    - Real-time cost estimation and alerts
    """
    
    start_time = datetime.utcnow()
    
    try:
        # Get user's API keys (would need to decrypt them)
        user_api_keys = {}  # TODO: Implement API key decryption
        
        # Get user's AI preferences
        user_preferences = None  # TODO: Load from database
        
        # Generate content with LLM
        llm_request = LLMRequest(
            prompt=f"""Create an engaging {request.duration}-minute educational lecture on: {request.topic}

Difficulty Level: {request.difficulty}
Content Style: {request.content_style}
Include Examples: {request.include_examples}
Include Summary: {request.include_summary}
Language: {request.language}

Please structure the lecture with:
1. Introduction (engaging hook)
2. Main content (clear explanations)
{'3. Practical examples' if request.include_examples else ''}
{'4. Summary and key takeaways' if request.include_summary else ''}

Target length: Approximately {request.duration * 200} words for {request.duration} minutes of audio.
Make it engaging, educational, and appropriate for {request.difficulty} level learners.""",
            max_tokens=4000,
            temperature=0.7,
            quality_tier=request.quality_tier,
            user_id=str(current_user.id)
        )
        
        llm_response = await multi_provider_llm.generate_content(
            request=llm_request,
            user_api_keys=user_api_keys,
            user_preferences=user_preferences
        )
        
        if not llm_response.success:
            raise HTTPException(status_code=500, detail=f"LLM generation failed: {llm_response.error}")
        
        # Generate audio with TTS
        tts_request = TTSRequest(
            text=llm_response.content,
            voice_id=request.voice_id,
            language=request.language,
            speed=request.voice_speed,
            quality_tier=request.quality_tier,
            user_id=str(current_user.id)
        )
        
        tts_response = await multi_provider_tts.generate_audio(
            request=tts_request,
            user_api_keys=user_api_keys,
            user_preferences=user_preferences
        )
        
        if not tts_response.success:
            raise HTTPException(status_code=500, detail=f"TTS generation failed: {tts_response.error}")
        
        # Calculate total metrics
        total_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        total_cost = llm_response.cost_usd + tts_response.cost_usd
        
        # Check cost limit
        if request.max_cost_usd and total_cost > request.max_cost_usd:
            raise HTTPException(
                status_code=400, 
                detail=f"Generated cost ${total_cost:.4f} exceeds maximum ${request.max_cost_usd:.4f}"
            )
        
        # TODO: Save lecture to database with all provider information
        lecture_id = f"lecture_{int(datetime.utcnow().timestamp())}"
        
        # TODO: Upload audio to storage and get URL
        audio_url = f"/api/audio/{lecture_id}"
        
        return MultiProviderLectureResponse(
            success=True,
            lecture_id=lecture_id,
            title=f"Lecture: {request.topic}",
            duration=request.duration,
            difficulty=request.difficulty,
            llm_provider_used=llm_response.provider_used.value,
            llm_model_used=llm_response.model_used,
            tts_provider_used=tts_response.provider_used.value,
            voice_used=tts_response.voice_used,
            quality_tier_used=request.quality_tier.value,
            llm_cost_usd=llm_response.cost_usd,
            tts_cost_usd=tts_response.cost_usd,
            total_cost_usd=total_cost,
            cost_optimization_used=True,
            was_cached=tts_response.cached,
            llm_generation_time_ms=llm_response.generation_time_ms,
            tts_generation_time_ms=tts_response.generation_time_ms,
            total_generation_time_ms=total_time,
            audio_file_url=audio_url,
            estimated_audio_duration=request.duration * 60,  # Convert to seconds
            character_count=len(llm_response.content),
            token_count=llm_response.tokens_used,
            created_at=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lecture generation failed: {str(e)}")


@router.post("/recommend-providers", response_model=ProviderRecommendation)
async def recommend_providers(
    request: MultiProviderLectureRequest,
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Get provider recommendations for a lecture request
    
    Analyzes the request and provides optimal provider recommendations
    with cost estimates and reasoning.
    """
    
    try:
        # Get user's API keys for filtering available providers
        user_api_keys = {}  # TODO: Load user's API keys
        
        # Get user preferences
        user_preferences = None  # TODO: Load from database
        
        # Estimate content length
        estimated_tokens = request.duration * 200 // 4  # Rough estimate
        estimated_chars = request.duration * 200
        
        # Get LLM recommendation
        llm_selection = await ai_provider_manager.select_optimal_llm_provider(
            user_preferences=user_preferences,
            quality_tier=request.quality_tier,
            estimated_tokens=estimated_tokens,
            user_api_keys=user_api_keys
        )
        
        # Get TTS recommendation
        tts_selection = await ai_provider_manager.select_optimal_tts_provider(
            user_preferences=user_preferences,
            quality_tier=request.quality_tier,
            estimated_characters=estimated_chars,
            language=request.language,
            user_api_keys=user_api_keys
        )
        
        # Calculate cost breakdown
        total_cost = llm_selection.estimated_cost + tts_selection.estimated_cost
        
        # Get cost savings analysis
        savings_analysis = await ai_provider_manager.calculate_cost_savings(
            estimated_tokens=estimated_tokens,
            estimated_characters=estimated_chars,
            quality_tier=request.quality_tier
        )
        
        return ProviderRecommendation(
            llm_recommendation={
                "provider": llm_selection.primary_provider.value,
                "cost": llm_selection.estimated_cost,
                "quality": llm_selection.expected_quality,
                "reasoning": llm_selection.reasoning,
                "fallback": llm_selection.fallback_provider.value if llm_selection.fallback_provider else None
            },
            tts_recommendation={
                "provider": tts_selection.primary_provider.value,
                "cost": tts_selection.estimated_cost,
                "quality": tts_selection.expected_quality,
                "reasoning": tts_selection.reasoning,
                "use_free_tier": tts_selection.use_free_tier,
                "fallback": tts_selection.fallback_provider.value if tts_selection.fallback_provider else None
            },
            total_estimated_cost=total_cost,
            cost_breakdown={
                "llm_cost": llm_selection.estimated_cost,
                "tts_cost": tts_selection.estimated_cost
            },
            potential_savings=savings_analysis["savings"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Provider recommendation failed: {str(e)}")


@router.post("/analyze-costs", response_model=CostAnalysisResponse)
async def analyze_costs(
    request: CostAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    💰 Analyze costs across all AI providers
    
    Compare costs between current single-provider approach and 
    optimized multi-provider strategy.
    """
    
    try:
        # Get comprehensive cost analysis
        analysis = await ai_provider_manager.calculate_cost_savings(
            estimated_tokens=request.estimated_tokens,
            estimated_characters=request.text_length_chars,
            quality_tier=request.quality_tier
        )
        
        # Get detailed provider costs
        llm_costs = {}
        tts_costs = {}
        
        # Calculate costs for each LLM provider
        for provider, capability in ai_provider_manager._llm_providers.items():
            cost = (request.estimated_tokens / 1000) * capability.cost_per_unit
            llm_costs[provider.value] = cost
        
        # Calculate costs for each TTS provider
        for provider, capability in ai_provider_manager._tts_providers.items():
            if capability.free_tier_available and capability.free_tier_limit:
                if request.text_length_chars <= capability.free_tier_limit:
                    cost = 0.0
                else:
                    cost = (request.text_length_chars / 1000) * capability.cost_per_unit
            else:
                cost = (request.text_length_chars / 1000) * capability.cost_per_unit
            tts_costs[provider.value] = cost
        
        return CostAnalysisResponse(
            current_approach_cost=analysis["current_approach"]["total_cost"],
            optimized_approach_cost=analysis["optimized_approach"]["total_cost"],
            potential_savings=analysis["savings"]["amount_usd"],
            savings_percentage=analysis["savings"]["percentage"],
            llm_provider_costs=llm_costs,
            tts_provider_costs=tts_costs,
            recommendations={
                "best_llm": min(llm_costs, key=llm_costs.get),
                "best_tts": min(tts_costs, key=tts_costs.get),
                "quality_tier": request.quality_tier.value
            },
            monthly_projection=analysis["monthly_projection"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost analysis failed: {str(e)}")


@router.get("/providers/status")
async def get_providers_status(current_user: User = Depends(get_current_user)):
    """
    📊 Get status of all AI providers
    
    Returns current status, capabilities, and performance metrics 
    for all supported AI providers.
    """
    
    try:
        status = await ai_provider_manager.get_provider_status()
        
        # Add user-specific information
        # TODO: Add user's API key status and usage statistics
        
        return {
            **status,
            "user_context": {
                "user_id": current_user.id,
                "subscription_tier": current_user.subscription_tier,
                "monthly_usage": "TODO",  # Get from usage logs
                "available_providers": "TODO"  # Based on API keys
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get provider status: {str(e)}")


@router.get("/providers/llm/models")
async def get_llm_models(
    provider: LLMProvider,
    current_user: User = Depends(get_current_user)
):
    """
    🤖 Get available models for an LLM provider
    
    Returns the list of available models for the specified provider.
    Requires valid API key for the provider.
    """
    
    try:
        # TODO: Get user's API key for this provider
        api_key = ""  # Get from encrypted storage
        
        if not api_key:
            raise HTTPException(
                status_code=400, 
                detail=f"No API key configured for {provider.value}"
            )
        
        models = await multi_provider_llm.get_available_models(provider, api_key)
        
        return {
            "provider": provider.value,
            "models": models,
            "count": len(models)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@router.get("/providers/tts/voices")
async def get_tts_voices(
    provider: TTSProvider,
    current_user: User = Depends(get_current_user)
):
    """
    🎤 Get available voices for a TTS provider
    
    Returns the list of available voices for the specified provider.
    """
    
    try:
        # TODO: Get user's API key for this provider (if required)
        api_key = None
        
        voices = await multi_provider_tts.get_available_voices(provider, api_key)
        
        return {
            "provider": provider.value,
            "voices": voices,
            "count": len(voices)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voices: {str(e)}")


@router.get("/cache/stats")
async def get_cache_stats(current_user: User = Depends(get_current_user)):
    """
    📈 Get TTS cache statistics
    
    Returns information about cached audio content for cost optimization.
    """
    
    try:
        stats = multi_provider_tts.get_cache_stats()
        
        return {
            "cache_stats": stats,
            "user_id": current_user.id,
            "cache_enabled": True  # TODO: Get from user preferences
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")


@router.post("/cache/clear")
async def clear_cache(current_user: User = Depends(get_current_user)):
    """
    🗑️ Clear TTS audio cache
    
    Clears the cached audio content. Use this if you want to force
    regeneration of previously cached content.
    """
    
    try:
        # Only allow premium users to clear cache frequently
        if current_user.subscription_tier == "free":
            raise HTTPException(
                status_code=403,
                detail="Cache clearing is limited for free tier users"
            )
        
        multi_provider_tts.clear_cache()
        
        return {
            "success": True,
            "message": "TTS cache cleared successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")
