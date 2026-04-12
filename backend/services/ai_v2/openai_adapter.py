"""OpenAI adapter for script generation using chat completions API."""

import json
import os
from typing import Any, Dict

import httpx

from services.ai_v2.base import ScriptGenerationInput, ScriptGenerationResult


class OpenAILLMAdapter:
    provider_name = "openai"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI adapter")
        self.model = model or os.getenv("OPENAI_LLM_MODEL", "gpt-4.1-mini")
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def generate_script(self, request: ScriptGenerationInput) -> ScriptGenerationResult:
        payload = {
            "model": self.model,
            "temperature": 0.4,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an instructional designer. Return strict JSON with keys "
                        "title, outline, and script."
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_prompt(request),
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = self._parse_structured_response(content)

        return ScriptGenerationResult(
            title=parsed.get("title", "Generated Lecture"),
            script=parsed.get("script", content),
            provider=self.provider_name,
            model=self.model,
            usage=data.get("usage", {}),
        )

    def _build_prompt(self, request: ScriptGenerationInput) -> str:
        return (
            f"Create an educational lecture script from this source document.\\n"
            f"Duration target: {request.duration_minutes} minutes.\\n"
            f"Difficulty: {request.difficulty}.\\n"
            f"Optional context: {request.context or 'None'}.\\n"
            "Return JSON only with: title, outline (array), script (string).\\n\\n"
            f"DOCUMENT:\\n{request.document_text[:18000]}"
        )

    def _parse_structured_response(self, content: str) -> Dict[str, Any]:
        cleaned = content.strip().replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"title": "Generated Lecture", "outline": [], "script": content}
