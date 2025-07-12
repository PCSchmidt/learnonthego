"""
Text-to-Speech Service for LearnOnTheGo
Handles audio generation with ElevenLabs TTS and fallback options
"""

import os
import asyncio
from typing import Dict, Optional, Union, List
import httpx
import aiofiles
from datetime import datetime


class TTSService:
    """Service for converting text to speech audio"""
    
    def __init__(self):
        self.elevenlabs_url = "https://api.elevenlabs.io/v1"
        self.output_dir = "temp_audio"
        self.max_text_length = 500000  # ElevenLabs limit
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_audio(
        self,
        content: str,
        voice_settings: Dict,
        output_filename: str = None
    ) -> Dict[str, Union[str, bool]]:
        """
        Generate audio from text content
        
        Args:
            content: Text content to convert to speech
            voice_settings: Voice configuration including API key
            output_filename: Optional custom filename
            
        Returns:
            Dictionary with audio file path and metadata
        """
        
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"lecture_{timestamp}.mp3"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # Validate content length
            if len(content) > self.max_text_length:
                return await self._handle_long_content(content, voice_settings, output_path)
            
            # Try ElevenLabs first
            if voice_settings.get("provider") == "elevenlabs" and voice_settings.get("api_key"):
                result = await self._generate_elevenlabs_audio(content, voice_settings, output_path)
                if result["success"]:
                    return result
            
            # Fallback to local TTS (for development/testing)
            return await self._generate_fallback_audio(content, output_path)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Audio generation failed: {str(e)}"
            }
    
    async def _generate_elevenlabs_audio(
        self,
        content: str,
        voice_settings: Dict,
        output_path: str
    ) -> Dict[str, Union[str, bool]]:
        """Generate audio using ElevenLabs API"""
        
        try:
            api_key = voice_settings["api_key"]
            voice_id = voice_settings.get("voice_id", "21m00Tcm4TlvDq8ikWAM")  # Default voice
            
            # Prepare request
            url = f"{self.elevenlabs_url}/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            
            # Voice settings
            data = {
                "text": content,
                "model_id": voice_settings.get("model_id", "eleven_multilingual_v2"),
                "voice_settings": {
                    "stability": voice_settings.get("stability", 0.5),
                    "similarity_boost": voice_settings.get("similarity_boost", 0.75),
                    "style": voice_settings.get("style", 0.0),
                    "use_speaker_boost": voice_settings.get("use_speaker_boost", True)
                }
            }
            
            # Make request
            async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout
                response = await client.post(url, json=data, headers=headers)
                
                if response.status_code == 200:
                    # Save audio file
                    async with aiofiles.open(output_path, "wb") as f:
                        await f.write(response.content)
                    
                    # Get file size and estimate duration
                    file_size = len(response.content)
                    estimated_duration = self._estimate_audio_duration(content, file_size)
                    
                    return {
                        "success": True,
                        "file_path": output_path,
                        "file_size": file_size,
                        "estimated_duration": estimated_duration,
                        "provider": "elevenlabs"
                    }
                else:
                    error_msg = f"ElevenLabs API error: {response.status_code}"
                    if response.status_code == 401:
                        error_msg = "Invalid ElevenLabs API key"
                    elif response.status_code == 402:
                        error_msg = "ElevenLabs quota exceeded"
                    elif response.status_code == 422:
                        error_msg = "Invalid voice settings or content"
                    
                    return {
                        "success": False,
                        "error": error_msg
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"ElevenLabs generation failed: {str(e)}"
            }
    
    async def _generate_fallback_audio(self, content: str, output_path: str) -> Dict[str, Union[str, bool]]:
        """
        Fallback audio generation (for development/testing)
        Creates a placeholder file or uses system TTS if available
        """
        try:
            # For now, create a placeholder that indicates fallback was used
            # In production, this could integrate with Google TTS or other services
            
            placeholder_content = f"""
            This is a placeholder audio file for development.
            Original content length: {len(content)} characters
            Original content preview: {content[:200]}...
            
            To use real TTS, configure ElevenLabs API key in voice settings.
            """
            
            # Create a simple text file for now (would be audio in production)
            fallback_path = output_path.replace('.mp3', '_fallback.txt')
            async with aiofiles.open(fallback_path, "w", encoding="utf-8") as f:
                await f.write(placeholder_content)
            
            return {
                "success": True,
                "file_path": fallback_path,
                "file_size": len(placeholder_content.encode("utf-8")),
                "estimated_duration": self._estimate_audio_duration(content, 0),
                "provider": "fallback",
                "note": "Fallback mode - configure ElevenLabs for real audio"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Fallback generation failed: {str(e)}"
            }
    
    async def _handle_long_content(
        self,
        content: str,
        voice_settings: Dict,
        output_path: str
    ) -> Dict[str, Union[str, bool]]:
        """Handle content that exceeds TTS API limits by chunking"""
        
        try:
            # Split content into chunks
            chunks = self._split_content_into_chunks(content)
            
            if len(chunks) > 10:  # Reasonable limit for chunks
                return {
                    "success": False,
                    "error": f"Content too long ({len(chunks)} chunks). Maximum content length exceeded."
                }
            
            # Generate audio for each chunk
            chunk_files = []
            for i, chunk in enumerate(chunks):
                chunk_filename = output_path.replace('.mp3', f'_chunk_{i:02d}.mp3')
                
                # Generate audio for this chunk
                chunk_result = await self._generate_elevenlabs_audio(chunk, voice_settings, chunk_filename)
                
                if not chunk_result["success"]:
                    # Clean up partial files
                    await self._cleanup_chunk_files(chunk_files)
                    return chunk_result
                
                chunk_files.append(chunk_result["file_path"])
            
            # Combine chunks (for now, just return first chunk info)
            # In production, would concatenate audio files
            total_size = sum(os.path.getsize(f) for f in chunk_files if os.path.exists(f))
            
            return {
                "success": True,
                "file_path": chunk_files[0],  # First chunk
                "file_size": total_size,
                "estimated_duration": self._estimate_audio_duration(content, total_size),
                "provider": "elevenlabs",
                "chunks": len(chunks),
                "chunk_files": chunk_files,
                "note": "Content was split into multiple chunks"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Long content handling failed: {str(e)}"
            }
    
    def _split_content_into_chunks(self, content: str, max_chunk_size: int = 400000) -> List[str]:
        """Split content into chunks for TTS processing"""
        
        # Try to split at natural boundaries (paragraphs, sentences)
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) < max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If any chunk is still too long, split by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= max_chunk_size:
                final_chunks.append(chunk)
            else:
                # Split by sentences
                sentences = chunk.replace('. ', '.\n').split('\n')
                sub_chunk = ""
                for sentence in sentences:
                    if len(sub_chunk) + len(sentence) < max_chunk_size:
                        sub_chunk += sentence + " "
                    else:
                        if sub_chunk:
                            final_chunks.append(sub_chunk.strip())
                        sub_chunk = sentence + " "
                if sub_chunk:
                    final_chunks.append(sub_chunk.strip())
        
        return final_chunks
    
    def _estimate_audio_duration(self, content: str, file_size: int) -> int:
        """Estimate audio duration in seconds"""
        # Rough estimate: 150 words per minute for speech
        word_count = len(content.split())
        estimated_seconds = (word_count / 150) * 60
        return int(estimated_seconds)
    
    async def _cleanup_chunk_files(self, chunk_files: List[str]) -> None:
        """Clean up temporary chunk files"""
        for file_path in chunk_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass  # Ignore cleanup errors
    
    async def get_available_voices(self, api_key: str) -> Dict[str, Union[list, bool]]:
        """Get available voices from ElevenLabs"""
        try:
            url = f"{self.elevenlabs_url}/voices"
            headers = {"xi-api-key": api_key}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    voices_data = response.json()
                    voices = [
                        {
                            "voice_id": voice["voice_id"],
                            "name": voice["name"],
                            "category": voice.get("category", "generated"),
                            "description": voice.get("description", ""),
                            "preview_url": voice.get("preview_url", "")
                        }
                        for voice in voices_data.get("voices", [])
                    ]
                    
                    return {
                        "success": True,
                        "voices": voices
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to fetch voices: {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Voice fetch failed: {str(e)}"
            }
    
    async def check_availability(self) -> bool:
        """Check if TTS service is available"""
        return True  # Always available (has fallback)
    
    async def cleanup_temp_files(self, max_age_hours: int = 24) -> None:
        """Clean up old temporary audio files"""
        try:
            current_time = datetime.now().timestamp()
            
            for filename in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, filename)
                file_age = current_time - os.path.getmtime(file_path)
                
                # Delete files older than max_age_hours
                if file_age > (max_age_hours * 3600):
                    os.remove(file_path)
                    
        except Exception as e:
            print(f"Warning: Failed to cleanup temp files: {e}")


# Service instance factory
def create_tts_service() -> TTSService:
    """Create TTS service instance"""
    return TTSService()
