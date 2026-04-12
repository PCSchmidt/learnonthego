"""OpenAI adapter for text-to-speech synthesis."""

import os
from datetime import datetime

import aiofiles
import httpx

from services.tts_v2.base import SynthesisInput, SynthesisResult


class OpenAITTSAdapter:
    provider_name = "openai"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI TTS adapter")
        self.model = model or os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
        self.voice = os.getenv("OPENAI_TTS_VOICE", "alloy")
        self.output_dir = "temp_audio"
        os.makedirs(self.output_dir, exist_ok=True)

    async def synthesize(self, request: SynthesisInput) -> SynthesisResult:
        payload = {
            "model": self.model,
            "voice": request.voice_id or self.voice,
            "input": request.text,
            "format": "mp3",
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post("https://api.openai.com/v1/audio/speech", headers=headers, json=payload)
            response.raise_for_status()

        filename = f"v2_{self.provider_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
        path = os.path.join(self.output_dir, filename)
        async with aiofiles.open(path, "wb") as f:
            await f.write(response.content)

        return SynthesisResult(
            file_path=path,
            provider=self.provider_name,
            model=self.model,
            bytes_written=len(response.content),
            metadata={"voice": payload["voice"]},
        )
