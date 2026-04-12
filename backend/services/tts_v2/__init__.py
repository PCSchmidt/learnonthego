"""V2 TTS provider abstractions and adapters."""

from services.tts_v2.base import SynthesisInput, SynthesisResult
from services.tts_v2.elevenlabs_adapter import ElevenLabsTTSAdapter
from services.tts_v2.openai_adapter import OpenAITTSAdapter
from services.tts_v2.router import TTSRouter

__all__ = [
    "SynthesisInput",
    "SynthesisResult",
    "ElevenLabsTTSAdapter",
    "OpenAITTSAdapter",
    "TTSRouter",
]
