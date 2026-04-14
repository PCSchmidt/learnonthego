"""Provider router for TTS adapters."""

import httpx

from services.tts_v2.base import SynthesisInput, SynthesisResult
from services.tts_v2.elevenlabs_adapter import ElevenLabsTTSAdapter
from services.tts_v2.openai_adapter import OpenAITTSAdapter
from services.pipeline_errors import PipelineExecutionError


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
        try:
            adapter = adapter_cls(api_key=api_key)
        except ValueError:
            raise
        except Exception as exc:
            raise PipelineExecutionError(
                stage="tts_init",
                provider=key,
                message="Failed to initialize TTS adapter",
                cause_type=type(exc).__name__,
            ) from exc

        try:
            return await adapter.synthesize(request)
        except ValueError:
            raise
        except Exception as exc:
            status_code = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None
            retryable = status_code in {408, 429, 500, 502, 503, 504}
            message = (
                f"TTS provider request failed with HTTP {status_code}"
                if status_code is not None
                else "TTS synthesis request failed"
            )
            raise PipelineExecutionError(
                stage="tts_synthesize",
                provider=key,
                message=message,
                status_code=status_code,
                retryable=retryable,
                cause_type=type(exc).__name__,
            ) from exc
