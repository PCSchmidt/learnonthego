"""Provider router for TTS adapters."""

from services.tts_v2.base import SynthesisInput, SynthesisResult
from services.tts_v2.elevenlabs_adapter import ElevenLabsTTSAdapter
from services.tts_v2.openai_adapter import OpenAITTSAdapter


class TTSRouter:
    def __init__(self):
        self._providers = {
            "elevenlabs": ElevenLabsTTSAdapter,
            "openai": OpenAITTSAdapter,
        }

    async def synthesize(
        self,
        provider: str,
        request: SynthesisInput,
        api_key: str | None = None,
    ) -> SynthesisResult:
        key = (provider or "elevenlabs").lower().strip()
        adapter_cls = self._providers.get(key)
        if not adapter_cls:
            raise ValueError(f"Unsupported TTS provider: {provider}")
        adapter = adapter_cls(api_key=api_key)
        return await adapter.synthesize(request)
