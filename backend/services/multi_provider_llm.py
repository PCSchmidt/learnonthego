"""
Multi-Provider LLM Service for LearnOnTheGo
Phase 2f: Intelligent LLM routing with cost optimization

Supports multiple LLM providers with automatic fallback and smart routing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json
import aiohttp

from models.lecture_orm import LLMProvider, QualityTier
from services.encryption_service import EncryptionService
from services.ai_provider_manager import ai_provider_manager, ProviderSelection


@dataclass
class LLMResponse:
    """Response from LLM generation"""
    success: bool
    content: str
    provider_used: LLMProvider
    tokens_used: int
    cost_usd: float
    generation_time_ms: int
    model_used: str
    error: Optional[str] = None


@dataclass
class LLMRequest:
    """Request for LLM content generation"""
    prompt: str
    max_tokens: int = 4000
    temperature: float = 0.7
    model_preference: Optional[str] = None
    quality_tier: QualityTier = QualityTier.STANDARD
    user_id: str = ""


class MultiProviderLLMService:
    """
    Multi-provider LLM service with intelligent routing
    
    Features:
    - Automatic provider selection based on cost/quality
    - Fallback handling for reliability
    - Cost tracking and optimization
    - Performance monitoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.encryption_service = EncryptionService()
        
        # Provider-specific configurations
        self._provider_configs = {
            LLMProvider.OPENROUTER: {
                "base_url": "https://openrouter.ai/api/v1",
                "default_model": "anthropic/claude-3.5-sonnet",
                "headers": {"HTTP-Referer": "https://learnonthego.app"}
            },
            LLMProvider.OPENAI_DIRECT: {
                "base_url": "https://api.openai.com/v1",
                "default_model": "gpt-4o",
                "headers": {}
            },
            LLMProvider.ANTHROPIC_DIRECT: {
                "base_url": "https://api.anthropic.com/v1",
                "default_model": "claude-3-5-sonnet-20241022",
                "headers": {"anthropic-version": "2023-06-01"}
            }
        }
        
        # Performance tracking
        self._performance_stats = {}
    
    async def generate_content(
        self,
        request: LLMRequest,
        user_api_keys: Dict[str, str],
        user_preferences: Optional[Any] = None
    ) -> LLMResponse:
        """
        Generate content using optimal LLM provider
        
        Args:
            request: LLM generation request
            user_api_keys: User's decrypted API keys
            user_preferences: User's AI preferences
            
        Returns:
            LLMResponse with generated content
        """
        
        start_time = datetime.utcnow()
        
        try:
            # Select optimal provider
            provider_selection = await ai_provider_manager.select_optimal_llm_provider(
                user_preferences=user_preferences,
                quality_tier=request.quality_tier,
                estimated_tokens=request.max_tokens,
                user_api_keys=user_api_keys
            )
            
            self.logger.info(f"Selected LLM provider: {provider_selection.reasoning}")
            
            # Attempt primary provider
            response = await self._call_provider(
                provider=provider_selection.primary_provider,
                request=request,
                api_key=user_api_keys.get(f"{provider_selection.primary_provider.value}_api_key"),
                start_time=start_time
            )
            
            if response.success:
                return response
            
            # Fallback to secondary provider if available
            if provider_selection.fallback_provider:
                self.logger.warning(f"Primary provider failed, trying fallback: {provider_selection.fallback_provider}")
                
                fallback_response = await self._call_provider(
                    provider=provider_selection.fallback_provider,
                    request=request,
                    api_key=user_api_keys.get(f"{provider_selection.fallback_provider.value}_api_key"),
                    start_time=start_time
                )
                
                if fallback_response.success:
                    return fallback_response
            
            # All providers failed
            return LLMResponse(
                success=False,
                content="",
                provider_used=provider_selection.primary_provider,
                tokens_used=0,
                cost_usd=0.0,
                generation_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                model_used="",
                error="All LLM providers failed"
            )
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {str(e)}")
            return LLMResponse(
                success=False,
                content="",
                provider_used=LLMProvider.OPENROUTER,  # Default
                tokens_used=0,
                cost_usd=0.0,
                generation_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                model_used="",
                error=str(e)
            )
    
    async def _call_provider(
        self,
        provider: LLMProvider,
        request: LLMRequest,
        api_key: str,
        start_time: datetime
    ) -> LLMResponse:
        """
        Call specific LLM provider
        
        Args:
            provider: LLM provider to use
            request: Generation request
            api_key: Decrypted API key
            start_time: Request start time
            
        Returns:
            LLMResponse from the provider
        """
        
        if not api_key:
            return LLMResponse(
                success=False,
                content="",
                provider_used=provider,
                tokens_used=0,
                cost_usd=0.0,
                generation_time_ms=0,
                model_used="",
                error=f"No API key configured for {provider.value}"
            )
        
        config = self._provider_configs.get(provider)
        if not config:
            return LLMResponse(
                success=False,
                content="",
                provider_used=provider,
                tokens_used=0,
                cost_usd=0.0,
                generation_time_ms=0,
                model_used="",
                error=f"Provider {provider.value} not configured"
            )
        
        try:
            if provider == LLMProvider.OPENROUTER:
                return await self._call_openrouter(request, api_key, config, start_time)
            elif provider == LLMProvider.OPENAI_DIRECT:
                return await self._call_openai(request, api_key, config, start_time)
            elif provider == LLMProvider.ANTHROPIC_DIRECT:
                return await self._call_anthropic(request, api_key, config, start_time)
            else:
                return LLMResponse(
                    success=False,
                    content="",
                    provider_used=provider,
                    tokens_used=0,
                    cost_usd=0.0,
                    generation_time_ms=0,
                    model_used="",
                    error=f"Provider {provider.value} not implemented yet"
                )
                
        except Exception as e:
            generation_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            return LLMResponse(
                success=False,
                content="",
                provider_used=provider,
                tokens_used=0,
                cost_usd=0.0,
                generation_time_ms=generation_time,
                model_used="",
                error=f"Provider call failed: {str(e)}"
            )
    
    async def _call_openrouter(
        self,
        request: LLMRequest,
        api_key: str,
        config: Dict[str, Any],
        start_time: datetime
    ) -> LLMResponse:
        """Call OpenRouter API"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            **config["headers"]
        }
        
        # Select model based on quality tier
        model = request.model_preference or config["default_model"]
        if request.quality_tier == QualityTier.FREE:
            model = "microsoft/wizardlm-2-8x22b"  # Cheaper option
        elif request.quality_tier == QualityTier.PREMIUM:
            model = "anthropic/claude-3.5-sonnet"  # Best quality
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": request.prompt}
            ],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                
                generation_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    content = data["choices"][0]["message"]["content"]
                    tokens_used = data["usage"]["total_tokens"]
                    
                    # Estimate cost (OpenRouter varies by model)
                    cost_per_1k = 0.02  # Average estimate
                    cost_usd = (tokens_used / 1000) * cost_per_1k
                    
                    return LLMResponse(
                        success=True,
                        content=content,
                        provider_used=LLMProvider.OPENROUTER,
                        tokens_used=tokens_used,
                        cost_usd=cost_usd,
                        generation_time_ms=generation_time,
                        model_used=model
                    )
                else:
                    error_text = await response.text()
                    return LLMResponse(
                        success=False,
                        content="",
                        provider_used=LLMProvider.OPENROUTER,
                        tokens_used=0,
                        cost_usd=0.0,
                        generation_time_ms=generation_time,
                        model_used=model,
                        error=f"OpenRouter API error {response.status}: {error_text}"
                    )
    
    async def _call_openai(
        self,
        request: LLMRequest,
        api_key: str,
        config: Dict[str, Any],
        start_time: datetime
    ) -> LLMResponse:
        """Call OpenAI API directly"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Select model based on quality tier
        model = request.model_preference or config["default_model"]
        if request.quality_tier == QualityTier.FREE:
            model = "gpt-3.5-turbo"  # Cheaper option
        elif request.quality_tier == QualityTier.PREMIUM:
            model = "gpt-4o"  # Best quality
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": request.prompt}
            ],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                
                generation_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    content = data["choices"][0]["message"]["content"]
                    tokens_used = data["usage"]["total_tokens"]
                    
                    # OpenAI pricing
                    cost_per_1k = 0.03 if "gpt-4" in model else 0.002
                    cost_usd = (tokens_used / 1000) * cost_per_1k
                    
                    return LLMResponse(
                        success=True,
                        content=content,
                        provider_used=LLMProvider.OPENAI_DIRECT,
                        tokens_used=tokens_used,
                        cost_usd=cost_usd,
                        generation_time_ms=generation_time,
                        model_used=model
                    )
                else:
                    error_text = await response.text()
                    return LLMResponse(
                        success=False,
                        content="",
                        provider_used=LLMProvider.OPENAI_DIRECT,
                        tokens_used=0,
                        cost_usd=0.0,
                        generation_time_ms=generation_time,
                        model_used=model,
                        error=f"OpenAI API error {response.status}: {error_text}"
                    )
    
    async def _call_anthropic(
        self,
        request: LLMRequest,
        api_key: str,
        config: Dict[str, Any],
        start_time: datetime
    ) -> LLMResponse:
        """Call Anthropic API directly"""
        
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            **config["headers"]
        }
        
        # Select model based on quality tier
        model = request.model_preference or config["default_model"]
        if request.quality_tier == QualityTier.FREE:
            model = "claude-3-haiku-20240307"  # Cheaper option
        elif request.quality_tier == QualityTier.PREMIUM:
            model = "claude-3-5-sonnet-20241022"  # Best quality
        
        payload = {
            "model": model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": [
                {"role": "user", "content": request.prompt}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/messages",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                
                generation_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    content = data["content"][0]["text"]
                    
                    # Estimate tokens (Anthropic doesn't always return usage)
                    tokens_used = data.get("usage", {}).get("output_tokens", len(content) // 4)
                    
                    # Anthropic pricing
                    cost_per_1k = 0.025  # Average estimate
                    cost_usd = (tokens_used / 1000) * cost_per_1k
                    
                    return LLMResponse(
                        success=True,
                        content=content,
                        provider_used=LLMProvider.ANTHROPIC_DIRECT,
                        tokens_used=tokens_used,
                        cost_usd=cost_usd,
                        generation_time_ms=generation_time,
                        model_used=model
                    )
                else:
                    error_text = await response.text()
                    return LLMResponse(
                        success=False,
                        content="",
                        provider_used=LLMProvider.ANTHROPIC_DIRECT,
                        tokens_used=0,
                        cost_usd=0.0,
                        generation_time_ms=generation_time,
                        model_used=model,
                        error=f"Anthropic API error {response.status}: {error_text}"
                    )
    
    async def get_available_models(self, provider: LLMProvider, api_key: str) -> List[Dict[str, Any]]:
        """Get available models for a provider"""
        
        try:
            if provider == LLMProvider.OPENROUTER:
                return await self._get_openrouter_models(api_key)
            elif provider == LLMProvider.OPENAI_DIRECT:
                return await self._get_openai_models(api_key)
            elif provider == LLMProvider.ANTHROPIC_DIRECT:
                return await self._get_anthropic_models(api_key)
            else:
                return []
        except Exception as e:
            self.logger.error(f"Failed to get models for {provider.value}: {str(e)}")
            return []
    
    async def _get_openrouter_models(self, api_key: str) -> List[Dict[str, Any]]:
        """Get OpenRouter available models"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://learnonthego.app"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    return []
    
    async def _get_openai_models(self, api_key: str) -> List[Dict[str, Any]]:
        """Get OpenAI available models"""
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.openai.com/v1/models",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    # Filter to chat models only
                    models = [m for m in data.get("data", []) if "gpt" in m.get("id", "")]
                    return models
                else:
                    return []
    
    async def _get_anthropic_models(self, api_key: str) -> List[Dict[str, Any]]:
        """Get Anthropic available models (static list since they don't have a models endpoint)"""
        
        return [
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "type": "premium"},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "type": "standard"},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "type": "premium"}
        ]


# Global instance
multi_provider_llm = MultiProviderLLMService()
