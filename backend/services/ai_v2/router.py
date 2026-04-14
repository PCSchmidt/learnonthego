"""Provider router for LLM adapters."""

import httpx

from services.ai_v2.base import ScriptGenerationInput, ScriptGenerationResult
from services.ai_v2.openai_adapter import OpenAILLMAdapter
from services.ai_v2.openrouter_adapter import OpenRouterLLMAdapter
from services.pipeline_errors import PipelineExecutionError


class LLMRouter:
    def __init__(self):
        self._providers = {
            "openrouter": OpenRouterLLMAdapter,
            "openai": OpenAILLMAdapter,
        }

    async def generate_script(
        self,
        provider: str,
        request: ScriptGenerationInput,
        api_key: str | None = None,
        model: str | None = None,
    ) -> ScriptGenerationResult:
        key = (provider or "openrouter").lower().strip()
        adapter_cls = self._providers.get(key)
        if not adapter_cls:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        try:
            adapter = adapter_cls(api_key=api_key, model=model)
        except ValueError:
            raise
        except Exception as exc:
            raise PipelineExecutionError(
                stage="llm_init",
                provider=key,
                message="Failed to initialize LLM adapter",
                cause_type=type(exc).__name__,
            ) from exc

        try:
            return await adapter.generate_script(request)
        except ValueError:
            raise
        except Exception as exc:
            status_code = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None
            retryable = status_code in {408, 429, 500, 502, 503, 504}
            message = (
                f"LLM provider request failed with HTTP {status_code}"
                if status_code is not None
                else "LLM generation request failed"
            )
            raise PipelineExecutionError(
                stage="llm_generate",
                provider=key,
                message=message,
                status_code=status_code,
                retryable=retryable,
                cause_type=type(exc).__name__,
            ) from exc
