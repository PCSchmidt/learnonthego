"""
AI Provider Manager for LearnOnTheGo
Phase 2f: Multi-Provider Architecture with Smart Routing

This service manages multiple AI providers for both LLM and TTS services,
providing intelligent routing based on cost, quality, and user preferences.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from models.lecture_orm import (
    LLMProvider, TTSProvider, QualityTier, 
    UserAIPreferences, AIProviderConfig
)
from models.user_orm import User as UserORM
from services.encryption_service import EncryptionService


@dataclass
class ProviderCapability:
    """Provider capability information"""
    provider: Union[LLMProvider, TTSProvider]
    quality_score: float
    cost_per_unit: float  # Per 1k tokens or 1k characters
    reliability_score: float
    speed_score: float
    free_tier_available: bool
    free_tier_limit: Optional[int]
    supported_languages: List[str]
    max_concurrent: int


@dataclass
class ProviderSelection:
    """Result of provider selection algorithm"""
    primary_provider: Union[LLMProvider, TTSProvider]
    fallback_provider: Optional[Union[LLMProvider, TTSProvider]]
    estimated_cost: float
    expected_quality: float
    reasoning: str
    use_free_tier: bool


class AIProviderManager:
    """
    Centralized manager for all AI providers with intelligent routing
    
    Features:
    - Cost-optimized provider selection
    - Quality tier management
    - Free tier utilization
    - Automatic fallback handling
    - Performance monitoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.encryption_service = EncryptionService()
        
        # Provider capabilities cache
        self._llm_providers: Dict[LLMProvider, ProviderCapability] = {}
        self._tts_providers: Dict[TTSProvider, ProviderCapability] = {}
        
        # Performance tracking
        self._provider_performance: Dict[str, Dict[str, Any]] = {}
        
        # Initialize provider capabilities
        self._initialize_provider_capabilities()
    
    def _initialize_provider_capabilities(self):
        """Initialize provider capability information"""
        
        # LLM Provider Capabilities
        self._llm_providers = {
            LLMProvider.OPENROUTER: ProviderCapability(
                provider=LLMProvider.OPENROUTER,
                quality_score=8.5,
                cost_per_unit=0.02,  # Average across models
                reliability_score=9.0,
                speed_score=8.0,
                free_tier_available=False,
                free_tier_limit=None,
                supported_languages=["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                max_concurrent=5
            ),
            LLMProvider.OPENAI_DIRECT: ProviderCapability(
                provider=LLMProvider.OPENAI_DIRECT,
                quality_score=9.5,
                cost_per_unit=0.03,  # GPT-4 pricing
                reliability_score=9.5,
                speed_score=8.5,
                free_tier_available=False,
                free_tier_limit=None,
                supported_languages=["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                max_concurrent=3
            ),
            LLMProvider.ANTHROPIC_DIRECT: ProviderCapability(
                provider=LLMProvider.ANTHROPIC_DIRECT,
                quality_score=9.0,
                cost_per_unit=0.025,  # Claude pricing
                reliability_score=9.0,
                speed_score=7.5,
                free_tier_available=False,
                free_tier_limit=None,
                supported_languages=["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                max_concurrent=3
            )
        }
        
        # TTS Provider Capabilities
        self._tts_providers = {
            TTSProvider.GOOGLE_STANDARD: ProviderCapability(
                provider=TTSProvider.GOOGLE_STANDARD,
                quality_score=6.5,
                cost_per_unit=0.004,  # $4 per 1M chars
                reliability_score=9.5,
                speed_score=8.5,
                free_tier_available=True,
                free_tier_limit=4000000,  # 4M chars per month
                supported_languages=["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "hi", "ar"],
                max_concurrent=10
            ),
            TTSProvider.GOOGLE_NEURAL: ProviderCapability(
                provider=TTSProvider.GOOGLE_NEURAL,
                quality_score=8.0,
                cost_per_unit=0.016,  # $16 per 1M chars
                reliability_score=9.5,
                speed_score=8.0,
                free_tier_available=True,
                free_tier_limit=1000000,  # 1M chars per month
                supported_languages=["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                max_concurrent=8
            ),
            TTSProvider.OPENAI_TTS: ProviderCapability(
                provider=TTSProvider.OPENAI_TTS,
                quality_score=8.5,
                cost_per_unit=0.015,  # $15 per 1M chars
                reliability_score=9.0,
                speed_score=7.5,
                free_tier_available=False,
                free_tier_limit=None,
                supported_languages=["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                max_concurrent=5
            ),
            TTSProvider.ELEVENLABS: ProviderCapability(
                provider=TTSProvider.ELEVENLABS,
                quality_score=9.5,
                cost_per_unit=0.165,  # $165 per 1M chars
                reliability_score=8.5,
                speed_score=6.5,
                free_tier_available=True,
                free_tier_limit=10000,  # 10k chars per month
                supported_languages=["en", "es", "fr", "de", "it", "pt", "hi"],
                max_concurrent=3
            ),
            TTSProvider.UNREAL_SPEECH: ProviderCapability(
                provider=TTSProvider.UNREAL_SPEECH,
                quality_score=7.0,
                cost_per_unit=0.002,  # $2 per 1M chars
                reliability_score=8.0,
                speed_score=9.0,
                free_tier_available=False,
                free_tier_limit=None,
                supported_languages=["en"],  # English only
                max_concurrent=5
            )
        }
    
    async def select_optimal_llm_provider(
        self,
        user_preferences: Optional[UserAIPreferences],
        quality_tier: QualityTier,
        estimated_tokens: int,
        user_api_keys: Dict[str, str]
    ) -> ProviderSelection:
        """
        Select the optimal LLM provider based on cost, quality, and preferences
        
        Args:
            user_preferences: User's AI preferences
            quality_tier: Desired quality tier
            estimated_tokens: Estimated token usage
            user_api_keys: Available API keys for the user
            
        Returns:
            ProviderSelection with optimal provider choice
        """
        
        available_providers = []
        
        # Filter providers based on available API keys
        for provider, capability in self._llm_providers.items():
            provider_key = f"{provider.value}_api_key"
            if provider_key in user_api_keys:
                available_providers.append((provider, capability))
        
        if not available_providers:
            raise ValueError("No LLM providers available - please configure API keys")
        
        # Apply quality tier filtering
        if quality_tier == QualityTier.FREE:
            # Prefer providers with free tiers or lowest cost
            available_providers.sort(key=lambda x: (
                not x[1].free_tier_available,
                x[1].cost_per_unit
            ))
        elif quality_tier == QualityTier.PREMIUM:
            # Prefer highest quality providers
            available_providers.sort(key=lambda x: -x[1].quality_score)
        else:  # STANDARD
            # Balance cost and quality
            available_providers.sort(key=lambda x: (
                x[1].cost_per_unit / x[1].quality_score
            ))
        
        # Select primary provider
        primary_provider, primary_capability = available_providers[0]
        
        # Select fallback provider
        fallback_provider = None
        if len(available_providers) > 1:
            fallback_provider = available_providers[1][0]
        
        # Calculate estimated cost
        estimated_cost = (estimated_tokens / 1000) * primary_capability.cost_per_unit
        
        # Generate reasoning
        reasoning = f"Selected {primary_provider.value} for quality tier {quality_tier.value}. "
        reasoning += f"Quality score: {primary_capability.quality_score}/10, "
        reasoning += f"Estimated cost: ${estimated_cost:.4f}"
        
        if primary_capability.free_tier_available:
            reasoning += " (free tier available)"
        
        return ProviderSelection(
            primary_provider=primary_provider,
            fallback_provider=fallback_provider,
            estimated_cost=estimated_cost,
            expected_quality=primary_capability.quality_score,
            reasoning=reasoning,
            use_free_tier=primary_capability.free_tier_available
        )
    
    async def select_optimal_tts_provider(
        self,
        user_preferences: Optional[UserAIPreferences],
        quality_tier: QualityTier,
        estimated_characters: int,
        language: str = "en",
        user_api_keys: Dict[str, str] = None
    ) -> ProviderSelection:
        """
        Select the optimal TTS provider based on cost, quality, and preferences
        
        Args:
            user_preferences: User's AI preferences
            quality_tier: Desired quality tier
            estimated_characters: Estimated character count
            language: Target language
            user_api_keys: Available API keys for the user
            
        Returns:
            ProviderSelection with optimal provider choice
        """
        
        available_providers = []
        
        # Filter providers based on language support
        for provider, capability in self._tts_providers.items():
            if language in capability.supported_languages:
                # Check if API key is available (if required)
                if capability.provider in [TTSProvider.ELEVENLABS, TTSProvider.OPENAI_TTS]:
                    provider_key = f"{provider.value}_api_key"
                    if user_api_keys and provider_key not in user_api_keys:
                        continue
                
                available_providers.append((provider, capability))
        
        if not available_providers:
            # Fallback to English-only providers if language not supported
            for provider, capability in self._tts_providers.items():
                if "en" in capability.supported_languages:
                    available_providers.append((provider, capability))
        
        if not available_providers:
            raise ValueError("No TTS providers available")
        
        # Apply quality tier filtering and cost optimization
        if quality_tier == QualityTier.FREE:
            # Prioritize free tier providers
            free_tier_providers = [p for p in available_providers if p[1].free_tier_available]
            if free_tier_providers:
                # Sort by free tier limit (descending) then quality
                free_tier_providers.sort(key=lambda x: (
                    -(x[1].free_tier_limit or 0),
                    -x[1].quality_score
                ))
                available_providers = free_tier_providers
            else:
                # No free tier available, use cheapest
                available_providers.sort(key=lambda x: x[1].cost_per_unit)
        
        elif quality_tier == QualityTier.PREMIUM:
            # Prefer highest quality
            available_providers.sort(key=lambda x: -x[1].quality_score)
        
        else:  # STANDARD
            # Cost-effectiveness optimization
            def cost_effectiveness_score(provider_tuple):
                provider, capability = provider_tuple
                
                # If free tier available and usage fits, prioritize it
                if (capability.free_tier_available and 
                    capability.free_tier_limit and 
                    estimated_characters <= capability.free_tier_limit):
                    return -1000  # Highest priority for free tier usage
                
                # Otherwise, calculate cost per quality point
                return capability.cost_per_unit / capability.quality_score
            
            available_providers.sort(key=cost_effectiveness_score)
        
        # Select primary provider
        primary_provider, primary_capability = available_providers[0]
        
        # Select fallback provider
        fallback_provider = None
        if len(available_providers) > 1:
            fallback_provider = available_providers[1][0]
        
        # Calculate estimated cost
        use_free_tier = (
            primary_capability.free_tier_available and 
            primary_capability.free_tier_limit and
            estimated_characters <= primary_capability.free_tier_limit
        )
        
        if use_free_tier:
            estimated_cost = 0.0
        else:
            estimated_cost = (estimated_characters / 1000) * primary_capability.cost_per_unit
        
        # Generate reasoning
        reasoning = f"Selected {primary_provider.value} for {language} language. "
        reasoning += f"Quality: {primary_capability.quality_score}/10, "
        
        if use_free_tier:
            reasoning += f"Using free tier ({estimated_characters:,} chars)"
        else:
            reasoning += f"Cost: ${estimated_cost:.4f} ({estimated_characters:,} chars)"
        
        return ProviderSelection(
            primary_provider=primary_provider,
            fallback_provider=fallback_provider,
            estimated_cost=estimated_cost,
            expected_quality=primary_capability.quality_score,
            reasoning=reasoning,
            use_free_tier=use_free_tier
        )
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        
        status = {
            "llm_providers": {},
            "tts_providers": {},
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # LLM provider status
        for provider, capability in self._llm_providers.items():
            status["llm_providers"][provider.value] = {
                "quality_score": capability.quality_score,
                "cost_per_1k_tokens": capability.cost_per_unit,
                "reliability_score": capability.reliability_score,
                "supported_languages": capability.supported_languages,
                "max_concurrent": capability.max_concurrent
            }
        
        # TTS provider status
        for provider, capability in self._tts_providers.items():
            status["tts_providers"][provider.value] = {
                "quality_score": capability.quality_score,
                "cost_per_1k_chars": capability.cost_per_unit,
                "reliability_score": capability.reliability_score,
                "free_tier_available": capability.free_tier_available,
                "free_tier_limit": capability.free_tier_limit,
                "supported_languages": capability.supported_languages,
                "max_concurrent": capability.max_concurrent
            }
        
        return status
    
    async def calculate_cost_savings(
        self,
        estimated_tokens: int,
        estimated_characters: int,
        quality_tier: QualityTier = QualityTier.STANDARD
    ) -> Dict[str, Any]:
        """
        Calculate potential cost savings with multi-provider approach
        
        Args:
            estimated_tokens: Estimated LLM token usage
            estimated_characters: Estimated TTS character usage
            quality_tier: Quality tier for comparison
            
        Returns:
            Cost comparison and savings analysis
        """
        
        # Current single-provider approach (ElevenLabs + OpenRouter)
        current_llm_cost = (estimated_tokens / 1000) * 0.02  # OpenRouter average
        current_tts_cost = (estimated_characters / 1000) * 0.165  # ElevenLabs
        current_total = current_llm_cost + current_tts_cost
        
        # Optimized multi-provider approach
        optimized_llm_cost = 0
        optimized_tts_cost = 0
        
        # Find optimal LLM provider
        llm_providers = list(self._llm_providers.items())
        if quality_tier == QualityTier.FREE:
            llm_providers.sort(key=lambda x: x[1].cost_per_unit)
        else:
            llm_providers.sort(key=lambda x: x[1].cost_per_unit / x[1].quality_score)
        
        if llm_providers:
            optimized_llm_cost = (estimated_tokens / 1000) * llm_providers[0][1].cost_per_unit
        
        # Find optimal TTS provider
        tts_providers = list(self._tts_providers.items())
        best_tts_cost = float('inf')
        
        for provider, capability in tts_providers:
            if (capability.free_tier_available and 
                capability.free_tier_limit and 
                estimated_characters <= capability.free_tier_limit):
                cost = 0.0
            else:
                cost = (estimated_characters / 1000) * capability.cost_per_unit
            
            if cost < best_tts_cost:
                best_tts_cost = cost
        
        optimized_tts_cost = best_tts_cost if best_tts_cost != float('inf') else 0
        optimized_total = optimized_llm_cost + optimized_tts_cost
        
        # Calculate savings
        savings_amount = current_total - optimized_total
        savings_percentage = (savings_amount / current_total * 100) if current_total > 0 else 0
        
        return {
            "current_approach": {
                "llm_cost": current_llm_cost,
                "tts_cost": current_tts_cost,
                "total_cost": current_total
            },
            "optimized_approach": {
                "llm_cost": optimized_llm_cost,
                "tts_cost": optimized_tts_cost,
                "total_cost": optimized_total
            },
            "savings": {
                "amount_usd": savings_amount,
                "percentage": savings_percentage
            },
            "monthly_projection": {
                "current_monthly": current_total * 30,
                "optimized_monthly": optimized_total * 30,
                "monthly_savings": savings_amount * 30
            }
        }


# Global instance
ai_provider_manager = AIProviderManager()
