"""Provider router for LLM adapters."""

from services.ai_v2.base import ScriptGenerationInput, ScriptGenerationResult
from services.ai_v2.openai_adapter import OpenAILLMAdapter
from services.ai_v2.openrouter_adapter import OpenRouterLLMAdapter


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
        adapter = adapter_cls(api_key=api_key, model=model)
        return await adapter.generate_script(request)
