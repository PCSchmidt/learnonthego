"""Provider-agnostic interfaces for LLM script generation."""

from dataclasses import dataclass
from typing import Protocol, Optional, Dict, Any


@dataclass
class ScriptGenerationInput:
    document_text: str
    duration_minutes: int
    difficulty: str
    context: Optional[str] = None


@dataclass
class ScriptGenerationResult:
    title: str
    script: str
    provider: str
    model: str
    usage: Dict[str, Any]


class LLMProvider(Protocol):
    provider_name: str

    async def generate_script(self, request: ScriptGenerationInput) -> ScriptGenerationResult:
        ...
