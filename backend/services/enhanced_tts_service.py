"""
Enhanced TTS Service - Multi-Provider Strategy
Phase 2f: Cost-Optimized TTS with Quality Tiers
"""

import os
import asyncio
from typing import Dict, Optional, Union, List, Literal
import httpx
import aiofiles
from datetime import datetime
import hashlib
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession


TTS_PROVIDER = Literal["google_standard", "google_neural", "openai", "elevenlabs", "unreal_speech"]
QUALITY_TIER = Literal["free", "standard", "premium"]


class EnhancedTTSService:
    """
    Multi-provider TTS service with cost optimization
    
    Tier Strategy:
    - Free: Google Standard (4M chars free) or Silero open-source
    - Standard: Google Neural2 or OpenAI TTS (cost-effective)  
    - Premium: ElevenLabs (highest quality)
    """
    
    def __init__(self):
        self.providers = {
            "google_standard": {
                "cost_per_million": 4.0,
                "free_tier": 4_000_000,
                "quality_score": 3.5,
                "languages": 40
            },
            "google_neural": {
                "cost_per_million": 16.0,
                "free_tier": 1_000_000,
                "quality_score": 4.2,
                "languages": 40
            },
            "openai": {
                "cost_per_million": 15.0,
                "free_tier": 0,
                "quality_score": 4.0,
                "languages": 20
            },
            "elevenlabs": {
                "cost_per_million": 165.0,  # Based on Creator plan analysis
                "free_tier": 10_000,
                "quality_score": 4.7,
                "languages": 32
            },
            "unreal_speech": {
                "cost_per_million": 2.0,
                "free_tier": 0,
                "quality_score": 4.0,
                "languages": 1  # English only
            }
        }
        
        self.output_dir = "temp_audio"
        self.cache_dir = "audio_cache"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_content_hash(self, text: str, voice_id: str, provider: str) -> str:
        """Generate unique hash for caching"""
        content = f"{text}_{voice_id}_{provider}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def check_cache(self, content_hash: str) -> Optional[str]:
        """Check if audio already exists in cache"""
        cache_path = os.path.join(self.cache_dir, f"{content_hash}.mp3")
        if os.path.exists(cache_path):
            return cache_path
        return None
    
    def select_optimal_provider(
        self, 
        user_tier: QUALITY_TIER,
        text_length: int,
        language: str = "en",
        monthly_usage: int = 0
    ) -> TTS_PROVIDER:
        """
        Select best provider based on user tier, usage, and cost optimization
        """
        if user_tier == "free":
            # Use Google Standard free tier (4M chars) first
            if monthly_usage < 4_000_000:
                return "google_standard"
            else:
                # Fall back to open-source (would need implementation)
                return "google_standard"  # For now
        
        elif user_tier == "standard":
            # Cost-effective quality balance
            if language == "en" and text_length < 50_000:
                return "unreal_speech"  # Most cost-effective for English
            else:
                return "openai"  # Good quality/cost ratio
        
        elif user_tier == "premium":
            return "elevenlabs"  # Highest quality
        
        return "google_neural"  # Default fallback
    
    async def optimize_text_input(self, text: str) -> str:
        """
        Optimize text to reduce character count while preserving meaning
        Implementation of Grok3 suggestion
        """
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Remove common file artifacts
        text = text.replace("\\n", " ").replace("\\t", " ")
        
        # Remove URLs and email addresses (they don't speak well)
        import re
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[-]{2,}', '-', text)
        
        return text.strip()
    
    async def generate_audio_smart(
        self,
        content: str,
        user_id: int,
        user_tier: QUALITY_TIER,
        voice_settings: Dict,
        provider_override: Optional[TTS_PROVIDER] = None,
        language: str = "en"
    ) -> Dict[str, Union[str, bool, float]]:
        """
        Smart TTS generation with caching, optimization, and provider selection
        """
        # Step 1: Optimize text content
        optimized_content = await self.optimize_text_input(content)
        text_length = len(optimized_content)
        
        # Step 2: Check cache first
        provider = provider_override or self.select_optimal_provider(
            user_tier, text_length, language
        )
        
        content_hash = self.get_content_hash(optimized_content, voice_settings.get("voice_id", "default"), provider)
        cached_audio = await self.check_cache(content_hash)
        
        if cached_audio:
            return {
                "success": True,
                "file_path": cached_audio,
                "provider": provider,
                "cached": True,
                "cost_saved": self.providers[provider]["cost_per_million"] * (text_length / 1_000_000),
                "character_count": text_length
            }
        
        # Step 3: Generate new audio
        try:
            if provider == "google_standard":
                result = await self._generate_google_tts(optimized_content, voice_settings, neural=False)
            elif provider == "google_neural":
                result = await self._generate_google_tts(optimized_content, voice_settings, neural=True)
            elif provider == "openai":
                result = await self._generate_openai_tts(optimized_content, voice_settings)
            elif provider == "elevenlabs":
                result = await self._generate_elevenlabs_tts(optimized_content, voice_settings)
            elif provider == "unreal_speech":
                result = await self._generate_unreal_tts(optimized_content, voice_settings)
            else:
                raise ValueError(f"Unknown provider: {provider}")
            
            # Step 4: Cache the result
            if result["success"]:
                cache_path = os.path.join(self.cache_dir, f"{content_hash}.mp3")
                # Copy to cache
                import shutil
                shutil.copy2(result["file_path"], cache_path)
                result["cached"] = False
                result["character_count"] = text_length
                result["estimated_cost"] = self.providers[provider]["cost_per_million"] * (text_length / 1_000_000)
            
            return result
            
        except Exception as e:
            # Fallback strategy
            if provider != "google_standard":
                return await self.generate_audio_smart(
                    content, user_id, "free", voice_settings, "google_standard", language
                )
            else:
                return {"success": False, "error": str(e), "provider": provider}
    
    async def _generate_google_tts(self, content: str, voice_settings: Dict, neural: bool = True) -> Dict:
        """Google TTS implementation"""
        # This would implement Google Cloud TTS API
        # For now, return mock response
        return {
            "success": True,
            "file_path": f"{self.output_dir}/google_{'neural' if neural else 'standard'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
            "provider": "google_neural" if neural else "google_standard"
        }
    
    async def _generate_openai_tts(self, content: str, voice_settings: Dict) -> Dict:
        """OpenAI TTS implementation"""
        # Implementation for OpenAI TTS API
        return {
            "success": True,
            "file_path": f"{self.output_dir}/openai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
            "provider": "openai"
        }
    
    async def _generate_unreal_tts(self, content: str, voice_settings: Dict) -> Dict:
        """Unreal Speech implementation"""
        # Implementation for Unreal Speech API  
        return {
            "success": True,
            "file_path": f"{self.output_dir}/unreal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
            "provider": "unreal_speech"
        }
    
    async def _generate_elevenlabs_tts(self, content: str, voice_settings: Dict) -> Dict:
        """ElevenLabs implementation (existing code can be reused)"""
        # Use existing ElevenLabs implementation
        return {
            "success": True,
            "file_path": f"{self.output_dir}/elevenlabs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
            "provider": "elevenlabs"
        }
    
    async def get_usage_stats(self, user_id: int, month: int, year: int) -> Dict:
        """Get user's monthly TTS usage for cost optimization"""
        # This would query the database for user's monthly character usage
        return {
            "characters_used": 0,
            "cost_incurred": 0.0,
            "free_tier_remaining": 4_000_000,
            "provider_breakdown": {}
        }
    
    def estimate_cost(self, text_length: int, provider: TTS_PROVIDER) -> float:
        """Estimate cost for given text length and provider"""
        return self.providers[provider]["cost_per_million"] * (text_length / 1_000_000)
    
    def recommend_tier_upgrade(self, monthly_usage: int, current_tier: QUALITY_TIER) -> Dict:
        """Recommend tier upgrade based on usage patterns"""
        if current_tier == "free" and monthly_usage > 4_000_000:
            return {
                "should_upgrade": True,
                "recommended_tier": "standard",
                "reason": "Exceeded free tier limit",
                "cost_savings": "Switch to OpenAI TTS for cost-effective scaling"
            }
        elif current_tier == "standard" and monthly_usage > 10_000_000:
            return {
                "should_upgrade": True,
                "recommended_tier": "premium",
                "reason": "High usage - premium quality justified",
                "cost_savings": "Better user experience with ElevenLabs"
            }
        return {"should_upgrade": False}


# Cost comparison utility
class TTSCostAnalyzer:
    """Analyze and compare TTS costs across providers"""
    
    @staticmethod
    def compare_monthly_costs(character_count: int) -> Dict:
        """Compare costs across all providers for given monthly usage"""
        providers = EnhancedTTSService().providers
        
        results = {}
        for provider, config in providers.items():
            free_chars = min(character_count, config["free_tier"])
            paid_chars = max(0, character_count - config["free_tier"])
            
            cost = (paid_chars / 1_000_000) * config["cost_per_million"]
            
            results[provider] = {
                "total_cost": cost,
                "free_characters": free_chars,
                "paid_characters": paid_chars,
                "quality_score": config["quality_score"],
                "cost_per_quality": cost / config["quality_score"] if cost > 0 else 0
            }
        
        return results
    
    @staticmethod
    def get_best_value_provider(character_count: int, min_quality: float = 4.0) -> str:
        """Get the best value provider for given usage and quality requirements"""
        comparison = TTSCostAnalyzer.compare_monthly_costs(character_count)
        
        eligible = {
            name: data for name, data in comparison.items() 
            if data["quality_score"] >= min_quality
        }
        
        if not eligible:
            return "google_standard"  # Fallback
        
        # Find provider with lowest cost per quality point
        best = min(eligible.items(), key=lambda x: x[1]["cost_per_quality"] if x[1]["cost_per_quality"] > 0 else float('inf'))
        return best[0]
