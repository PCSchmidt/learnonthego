"""
Multi-Provider TTS Service for LearnOnTheGo
Phase 2f: Intelligent TTS routing with cost optimization

Supports multiple TTS providers with automatic fallback and smart routing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json
import aiohttp
import base64
import tempfile
import os

from models.lecture_orm import TTSProvider, QualityTier
from services.encryption_service import EncryptionService
from services.ai_provider_manager import ai_provider_manager, ProviderSelection


@dataclass
class TTSResponse:
    """Response from TTS generation"""
    success: bool
    audio_data: Optional[bytes]
    audio_url: Optional[str]
    provider_used: TTSProvider
    characters_used: int
    cost_usd: float
    generation_time_ms: int
    voice_used: str
    cached: bool = False
    error: Optional[str] = None


@dataclass
class TTSRequest:
    """Request for TTS audio generation"""
    text: str
    voice_id: str = "default"
    language: str = "en"
    speed: float = 1.0
    quality_tier: QualityTier = QualityTier.STANDARD
    output_format: str = "mp3"
    user_id: str = ""


class MultiProviderTTSService:
    """
    Multi-provider TTS service with intelligent routing
    
    Features:
    - Automatic provider selection based on cost/quality
    - Free tier utilization
    - Audio caching for cost optimization
    - Fallback handling for reliability
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.encryption_service = EncryptionService()
        
        # Provider-specific configurations
        self._provider_configs = {
            TTSProvider.GOOGLE_STANDARD: {
                "base_url": "https://texttospeech.googleapis.com/v1",
                "voices": {
                    "en": ["en-US-Standard-A", "en-US-Standard-B", "en-US-Standard-C"],
                    "es": ["es-ES-Standard-A", "es-ES-Standard-B"],
                    "fr": ["fr-FR-Standard-A", "fr-FR-Standard-B"]
                }
            },
            TTSProvider.GOOGLE_NEURAL: {
                "base_url": "https://texttospeech.googleapis.com/v1",
                "voices": {
                    "en": ["en-US-Neural2-A", "en-US-Neural2-B", "en-US-Neural2-C"],
                    "es": ["es-ES-Neural2-A", "es-ES-Neural2-B"],
                    "fr": ["fr-FR-Neural2-A", "fr-FR-Neural2-B"]
                }
            },
            TTSProvider.OPENAI_TTS: {
                "base_url": "https://api.openai.com/v1",
                "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            },
            TTSProvider.ELEVENLABS: {
                "base_url": "https://api.elevenlabs.io/v1",
                "voices": {}  # Dynamic, fetched from API
            },
            TTSProvider.UNREAL_SPEECH: {
                "base_url": "https://api.v7.unrealspeech.com",
                "voices": ["Scarlett", "Dan", "Liv", "Will"]
            }
        }
        
        # Audio cache for cost optimization
        self._audio_cache = {}
        
        # Performance tracking
        self._performance_stats = {}
    
    async def generate_audio(
        self,
        request: TTSRequest,
        user_api_keys: Dict[str, str] = None,
        user_preferences: Optional[Any] = None
    ) -> TTSResponse:
        """
        Generate audio using optimal TTS provider
        
        Args:
            request: TTS generation request
            user_api_keys: User's decrypted API keys
            user_preferences: User's AI preferences
            
        Returns:
            TTSResponse with generated audio
        """
        
        start_time = datetime.utcnow()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self._audio_cache:
                cached_response = self._audio_cache[cache_key]
                cached_response.cached = True
                self.logger.info(f"Cache hit for TTS request: {len(request.text)} characters")
                return cached_response
            
            # Select optimal provider
            estimated_chars = len(request.text)
            provider_selection = await ai_provider_manager.select_optimal_tts_provider(
                user_preferences=user_preferences,
                quality_tier=request.quality_tier,
                estimated_characters=estimated_chars,
                language=request.language,
                user_api_keys=user_api_keys or {}
            )
            
            self.logger.info(f"Selected TTS provider: {provider_selection.reasoning}")
            
            # Attempt primary provider
            response = await self._call_provider(
                provider=provider_selection.primary_provider,
                request=request,
                api_key=user_api_keys.get(f"{provider_selection.primary_provider.value}_api_key") if user_api_keys else None,
                start_time=start_time,
                use_free_tier=provider_selection.use_free_tier
            )
            
            if response.success:
                # Cache successful response
                self._audio_cache[cache_key] = response
                return response
            
            # Fallback to secondary provider if available
            if provider_selection.fallback_provider:
                self.logger.warning(f"Primary provider failed, trying fallback: {provider_selection.fallback_provider}")
                
                fallback_response = await self._call_provider(
                    provider=provider_selection.fallback_provider,
                    request=request,
                    api_key=user_api_keys.get(f"{provider_selection.fallback_provider.value}_api_key") if user_api_keys else None,
                    start_time=start_time,
                    use_free_tier=False  # Primary provider might have used free tier
                )
                
                if fallback_response.success:
                    self._audio_cache[cache_key] = fallback_response
                    return fallback_response
            
            # All providers failed
            return TTSResponse(
                success=False,
                audio_data=None,
                audio_url=None,
                provider_used=provider_selection.primary_provider,
                characters_used=estimated_chars,
                cost_usd=0.0,
                generation_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                voice_used=request.voice_id,
                error="All TTS providers failed"
            )
            
        except Exception as e:
            self.logger.error(f"TTS generation failed: {str(e)}")
            return TTSResponse(
                success=False,
                audio_data=None,
                audio_url=None,
                provider_used=TTSProvider.GOOGLE_STANDARD,  # Default
                characters_used=len(request.text),
                cost_usd=0.0,
                generation_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                voice_used=request.voice_id,
                error=str(e)
            )
    
    def _generate_cache_key(self, request: TTSRequest) -> str:
        """Generate cache key for TTS request"""
        key_data = {
            "text": request.text,
            "voice_id": request.voice_id,
            "language": request.language,
            "speed": request.speed,
            "output_format": request.output_format
        }
        return base64.b64encode(json.dumps(key_data, sort_keys=True).encode()).decode()
    
    async def _call_provider(
        self,
        provider: TTSProvider,
        request: TTSRequest,
        api_key: Optional[str],
        start_time: datetime,
        use_free_tier: bool = False
    ) -> TTSResponse:
        """
        Call specific TTS provider
        
        Args:
            provider: TTS provider to use
            request: Generation request
            api_key: Decrypted API key (if required)
            start_time: Request start time
            use_free_tier: Whether to use free tier
            
        Returns:
            TTSResponse from the provider
        """
        
        config = self._provider_configs.get(provider)
        if not config:
            return TTSResponse(
                success=False,
                audio_data=None,
                audio_url=None,
                provider_used=provider,
                characters_used=len(request.text),
                cost_usd=0.0,
                generation_time_ms=0,
                voice_used=request.voice_id,
                error=f"Provider {provider.value} not configured"
            )
        
        # Check API key requirement
        requires_key = provider in [TTSProvider.ELEVENLABS, TTSProvider.OPENAI_TTS, TTSProvider.UNREAL_SPEECH]
        if requires_key and not api_key:
            return TTSResponse(
                success=False,
                audio_data=None,
                audio_url=None,
                provider_used=provider,
                characters_used=len(request.text),
                cost_usd=0.0,
                generation_time_ms=0,
                voice_used=request.voice_id,
                error=f"No API key configured for {provider.value}"
            )
        
        try:
            if provider == TTSProvider.GOOGLE_STANDARD:
                return await self._call_google_tts(request, api_key, config, start_time, use_free_tier, "standard")
            elif provider == TTSProvider.GOOGLE_NEURAL:
                return await self._call_google_tts(request, api_key, config, start_time, use_free_tier, "neural")
            elif provider == TTSProvider.OPENAI_TTS:
                return await self._call_openai_tts(request, api_key, config, start_time)
            elif provider == TTSProvider.ELEVENLABS:
                return await self._call_elevenlabs(request, api_key, config, start_time)
            elif provider == TTSProvider.UNREAL_SPEECH:
                return await self._call_unreal_speech(request, api_key, config, start_time)
            else:
                return TTSResponse(
                    success=False,
                    audio_data=None,
                    audio_url=None,
                    provider_used=provider,
                    characters_used=len(request.text),
                    cost_usd=0.0,
                    generation_time_ms=0,
                    voice_used=request.voice_id,
                    error=f"Provider {provider.value} not implemented yet"
                )
                
        except Exception as e:
            generation_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            return TTSResponse(
                success=False,
                audio_data=None,
                audio_url=None,
                provider_used=provider,
                characters_used=len(request.text),
                cost_usd=0.0,
                generation_time_ms=generation_time,
                voice_used=request.voice_id,
                error=f"Provider call failed: {str(e)}"
            )
    
    async def _call_google_tts(
        self,
        request: TTSRequest,
        api_key: Optional[str],
        config: Dict[str, Any],
        start_time: datetime,
        use_free_tier: bool,
        voice_type: str
    ) -> TTSResponse:
        """Call Google Cloud Text-to-Speech API"""
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Select voice based on language and type
        voices = config.get("voices", {})
        available_voices = voices.get(request.language, voices.get("en", ["en-US-Standard-A"]))
        voice_name = available_voices[0] if available_voices else "en-US-Standard-A"
        
        # Override with neural voice if specified
        if voice_type == "neural":
            voice_name = voice_name.replace("Standard", "Neural2")
        
        payload = {
            "input": {"text": request.text},
            "voice": {
                "languageCode": request.language if len(request.language) > 2 else f"{request.language}-US",
                "name": voice_name
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": request.speed
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/text:synthesize",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                generation_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Decode base64 audio
                    audio_data = base64.b64decode(data["audioContent"])
                    
                    # Calculate cost
                    characters_used = len(request.text)
                    if use_free_tier:
                        cost_usd = 0.0
                    else:
                        cost_per_1k = 0.016 if voice_type == "neural" else 0.004
                        cost_usd = (characters_used / 1000) * cost_per_1k
                    
                    return TTSResponse(
                        success=True,
                        audio_data=audio_data,
                        audio_url=None,
                        provider_used=TTSProvider.GOOGLE_NEURAL if voice_type == "neural" else TTSProvider.GOOGLE_STANDARD,
                        characters_used=characters_used,
                        cost_usd=cost_usd,
                        generation_time_ms=generation_time,
                        voice_used=voice_name
                    )
                else:
                    error_text = await response.text()
                    return TTSResponse(
                        success=False,
                        audio_data=None,
                        audio_url=None,
                        provider_used=TTSProvider.GOOGLE_NEURAL if voice_type == "neural" else TTSProvider.GOOGLE_STANDARD,
                        characters_used=len(request.text),
                        cost_usd=0.0,
                        generation_time_ms=generation_time,
                        voice_used=voice_name,
                        error=f"Google TTS API error {response.status}: {error_text}"
                    )
    
    async def _call_openai_tts(
        self,
        request: TTSRequest,
        api_key: str,
        config: Dict[str, Any],
        start_time: datetime
    ) -> TTSResponse:
        """Call OpenAI TTS API"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Select voice
        voices = config["voices"]
        voice = request.voice_id if request.voice_id in voices else voices[0]
        
        payload = {
            "model": "tts-1",
            "input": request.text,
            "voice": voice,
            "response_format": request.output_format,
            "speed": request.speed
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/audio/speech",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                generation_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                if response.status == 200:
                    audio_data = await response.read()
                    
                    # Calculate cost
                    characters_used = len(request.text)
                    cost_per_1k = 0.015  # OpenAI TTS pricing
                    cost_usd = (characters_used / 1000) * cost_per_1k
                    
                    return TTSResponse(
                        success=True,
                        audio_data=audio_data,
                        audio_url=None,
                        provider_used=TTSProvider.OPENAI_TTS,
                        characters_used=characters_used,
                        cost_usd=cost_usd,
                        generation_time_ms=generation_time,
                        voice_used=voice
                    )
                else:
                    error_text = await response.text()
                    return TTSResponse(
                        success=False,
                        audio_data=None,
                        audio_url=None,
                        provider_used=TTSProvider.OPENAI_TTS,
                        characters_used=len(request.text),
                        cost_usd=0.0,
                        generation_time_ms=generation_time,
                        voice_used=voice,
                        error=f"OpenAI TTS API error {response.status}: {error_text}"
                    )
    
    async def _call_elevenlabs(
        self,
        request: TTSRequest,
        api_key: str,
        config: Dict[str, Any],
        start_time: datetime
    ) -> TTSResponse:
        """Call ElevenLabs TTS API"""
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Use provided voice ID or default
        voice_id = request.voice_id if request.voice_id != "default" else "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
        
        payload = {
            "text": request.text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/text-to-speech/{voice_id}",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                generation_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                if response.status == 200:
                    audio_data = await response.read()
                    
                    # Calculate cost
                    characters_used = len(request.text)
                    cost_per_1k = 0.165  # ElevenLabs pricing
                    cost_usd = (characters_used / 1000) * cost_per_1k
                    
                    return TTSResponse(
                        success=True,
                        audio_data=audio_data,
                        audio_url=None,
                        provider_used=TTSProvider.ELEVENLABS,
                        characters_used=characters_used,
                        cost_usd=cost_usd,
                        generation_time_ms=generation_time,
                        voice_used=voice_id
                    )
                else:
                    error_text = await response.text()
                    return TTSResponse(
                        success=False,
                        audio_data=None,
                        audio_url=None,
                        provider_used=TTSProvider.ELEVENLABS,
                        characters_used=len(request.text),
                        cost_usd=0.0,
                        generation_time_ms=generation_time,
                        voice_used=voice_id,
                        error=f"ElevenLabs API error {response.status}: {error_text}"
                    )
    
    async def _call_unreal_speech(
        self,
        request: TTSRequest,
        api_key: str,
        config: Dict[str, Any],
        start_time: datetime
    ) -> TTSResponse:
        """Call Unreal Speech TTS API"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Select voice
        voices = config["voices"]
        voice = request.voice_id if request.voice_id in voices else voices[0]
        
        payload = {
            "Text": request.text,
            "VoiceId": voice,
            "Bitrate": "192k",
            "Speed": str(request.speed),
            "Pitch": "1.0",
            "TimestampType": "sentence"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config['base_url']}/stream",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                generation_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                if response.status == 200:
                    audio_data = await response.read()
                    
                    # Calculate cost
                    characters_used = len(request.text)
                    cost_per_1k = 0.002  # Unreal Speech pricing
                    cost_usd = (characters_used / 1000) * cost_per_1k
                    
                    return TTSResponse(
                        success=True,
                        audio_data=audio_data,
                        audio_url=None,
                        provider_used=TTSProvider.UNREAL_SPEECH,
                        characters_used=characters_used,
                        cost_usd=cost_usd,
                        generation_time_ms=generation_time,
                        voice_used=voice
                    )
                else:
                    error_text = await response.text()
                    return TTSResponse(
                        success=False,
                        audio_data=None,
                        audio_url=None,
                        provider_used=TTSProvider.UNREAL_SPEECH,
                        characters_used=len(request.text),
                        cost_usd=0.0,
                        generation_time_ms=generation_time,
                        voice_used=voice,
                        error=f"Unreal Speech API error {response.status}: {error_text}"
                    )
    
    async def get_available_voices(self, provider: TTSProvider, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available voices for a provider"""
        
        try:
            if provider == TTSProvider.ELEVENLABS and api_key:
                return await self._get_elevenlabs_voices(api_key)
            elif provider in [TTSProvider.GOOGLE_STANDARD, TTSProvider.GOOGLE_NEURAL]:
                return await self._get_google_voices(provider)
            elif provider == TTSProvider.OPENAI_TTS:
                return self._get_openai_voices()
            elif provider == TTSProvider.UNREAL_SPEECH:
                return self._get_unreal_speech_voices()
            else:
                return []
        except Exception as e:
            self.logger.error(f"Failed to get voices for {provider.value}: {str(e)}")
            return []
    
    async def _get_elevenlabs_voices(self, api_key: str) -> List[Dict[str, Any]]:
        """Get ElevenLabs available voices"""
        
        headers = {"xi-api-key": api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.elevenlabs.io/v1/voices",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return data.get("voices", [])
                else:
                    return []
    
    async def _get_google_voices(self, provider: TTSProvider) -> List[Dict[str, Any]]:
        """Get Google TTS available voices"""
        
        voice_type = "Neural2" if provider == TTSProvider.GOOGLE_NEURAL else "Standard"
        
        # Static list of common Google voices
        voices = []
        languages = ["en-US", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-BR"]
        
        for lang in languages:
            for variant in ["A", "B", "C"]:
                voices.append({
                    "name": f"{lang}-{voice_type}-{variant}",
                    "language": lang,
                    "gender": "FEMALE" if variant in ["A", "C"] else "MALE"
                })
        
        return voices
    
    def _get_openai_voices(self) -> List[Dict[str, Any]]:
        """Get OpenAI TTS available voices"""
        
        return [
            {"name": "alloy", "description": "Balanced and versatile"},
            {"name": "echo", "description": "Clear and expressive"},
            {"name": "fable", "description": "Warm and engaging"},
            {"name": "onyx", "description": "Deep and authoritative"},
            {"name": "nova", "description": "Bright and energetic"},
            {"name": "shimmer", "description": "Smooth and pleasant"}
        ]
    
    def _get_unreal_speech_voices(self) -> List[Dict[str, Any]]:
        """Get Unreal Speech available voices"""
        
        return [
            {"name": "Scarlett", "description": "Female, American English"},
            {"name": "Dan", "description": "Male, American English"},
            {"name": "Liv", "description": "Female, American English"},
            {"name": "Will", "description": "Male, American English"}
        ]
    
    def clear_cache(self):
        """Clear the audio cache"""
        self._audio_cache.clear()
        self.logger.info("TTS audio cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cached_items": len(self._audio_cache),
            "cache_size_mb": sum(len(r.audio_data) for r in self._audio_cache.values() if r.audio_data) / (1024 * 1024)
        }


# Global instance
multi_provider_tts = MultiProviderTTSService()
