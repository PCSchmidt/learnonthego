"""Provider-agnostic interfaces for text-to-speech synthesis."""

from dataclasses import dataclass
from typing import Protocol, Dict, Any, Optional


@dataclass
class SynthesisInput:
    text: str
    voice_id: Optional[str] = None


@dataclass
class SynthesisResult:
    file_path: str
    provider: str
    model: str
    bytes_written: int
    metadata: Dict[str, Any]


class TTSProvider(Protocol):
    provider_name: str

    async def synthesize(self, request: SynthesisInput) -> SynthesisResult:
        ...
