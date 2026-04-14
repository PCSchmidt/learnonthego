"""Feature-flagged document -> script -> audio orchestration service (V2)."""

import os
from typing import Optional

from services.ai_v2.base import ScriptGenerationInput
from services.ai_v2.router import LLMRouter
from services.pdf_service import create_pdf_service
from services.tts_v2.base import SynthesisInput
from services.tts_v2.router import TTSRouter


class DocumentToAudioPipelineV2:
    def __init__(self):
        self.llm_router = LLMRouter()
        self.tts_router = TTSRouter()
        self.pdf_service = create_pdf_service()

    async def run(
        self,
        *,
        document_text: str,
        duration_minutes: int,
        difficulty: str,
        llm_provider: str,
        llm_model: Optional[str] = None,
        tts_provider: str,
        context: Optional[str] = None,
        voice_id: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        tts_api_key: Optional[str] = None,
    ) -> dict:
        script_request = ScriptGenerationInput(
            document_text=document_text,
            duration_minutes=duration_minutes,
            difficulty=difficulty,
            context=context,
        )
        script_result = await self.llm_router.generate_script(
            llm_provider,
            script_request,
            api_key=llm_api_key,
            model=llm_model,
        )

        tts_request = SynthesisInput(text=script_result.script, voice_id=voice_id)
        audio_result = await self.tts_router.synthesize(
            tts_provider,
            tts_request,
            api_key=tts_api_key,
        )

        return {
            "title": script_result.title,
            "script": script_result.script,
            "llm": {
                "provider": script_result.provider,
                "model": script_result.model,
                "usage": script_result.usage,
            },
            "audio": {
                "provider": audio_result.provider,
                "model": audio_result.model,
                "file_path": audio_result.file_path,
                "bytes_written": audio_result.bytes_written,
                "metadata": audio_result.metadata,
            },
        }


def v2_pipeline_enabled() -> bool:
    return os.getenv("ENABLE_V2_PIPELINE", "false").lower() == "true"


def create_document_pipeline_v2() -> DocumentToAudioPipelineV2:
    return DocumentToAudioPipelineV2()
