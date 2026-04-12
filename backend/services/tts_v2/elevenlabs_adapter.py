"""ElevenLabs adapter for text-to-speech synthesis."""

import os
from datetime import datetime

import aiofiles
import httpx

from services.tts_v2.base import SynthesisInput, SynthesisResult


class ElevenLabsTTSAdapter:
    provider_name = "elevenlabs"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is required for ElevenLabs adapter")
        self.model = model or os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        self.output_dir = "temp_audio"
        os.makedirs(self.output_dir, exist_ok=True)

    async def synthesize(self, request: SynthesisInput) -> SynthesisResult:
        voice_id = request.voice_id or self.voice_id
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }
        payload = {
            "text": request.text,
            "model_id": self.model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=payload)
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
            metadata={"voice_id": voice_id},
        )
