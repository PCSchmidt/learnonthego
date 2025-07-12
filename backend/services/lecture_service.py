"""
Lecture Generation Service - Core orchestration for LearnOnTheGo
Handles the complete flow from input to final audio lecture
"""

import os
import asyncio
from typing import Dict, Optional, Union
from datetime import datetime
import hashlib

from services.openrouter_service import OpenRouterService
from services.pdf_service import PDFService
from services.tts_service import TTSService
from services.encryption_service import EncryptionService
from services.mock_services import get_openrouter_service, get_tts_service, get_pdf_service


class LectureGenerationService:
    """Main service that orchestrates lecture generation from input to audio"""
    
    def __init__(self):
        # Use mock services if MOCK_MODE is enabled for cost-free testing
        self.openrouter_service = None
        self.pdf_service = get_pdf_service()
        self.tts_service = get_tts_service()
        self.encryption_service = EncryptionService()
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
    
    async def initialize_ai_service(self, encrypted_api_key: str, user_id: str) -> bool:
        """Initialize OpenRouter service with decrypted user API key"""
        try:
            if self.mock_mode:
                # Use mock service for cost-free testing
                self.openrouter_service = get_openrouter_service()
                print("🎭 MOCK MODE: Using mock AI service (no API costs)")
                return True
            
            # Decrypt user's API key for real service
            api_key = self.encryption_service.decrypt_api_key(encrypted_api_key, user_id)
            
            # Initialize OpenRouter service
            self.openrouter_service = OpenRouterService(api_key)
            
            return True
        except Exception as e:
            print(f"Failed to initialize AI service: {e}")
            return False
    
    async def generate_lecture_from_text(
        self,
        topic: str,
        duration: int,
        difficulty: str,
        voice_settings: Dict,
        user_context: Optional[str] = None
    ) -> Dict[str, Union[str, bool]]:
        """
        Generate complete audio lecture from text topic
        
        Args:
            topic: The lecture topic
            duration: Duration in minutes (5-60)
            difficulty: beginner, intermediate, advanced
            voice_settings: TTS voice configuration
            user_context: Optional additional context
            
        Returns:
            Dictionary with lecture metadata and file paths
        """
        
        if not self.openrouter_service:
            return {
                "success": False,
                "error": "AI service not initialized. Please provide valid API key."
            }
        
        try:
            # Generate lecture content using OpenRouter
            lecture_content = await self.openrouter_service.generate_lecture_content(
                topic=topic,
                duration=duration,
                difficulty=difficulty,
                user_context=user_context
            )
            
            # Create lecture metadata
            lecture_id = self._generate_lecture_id(topic, duration)
            
            # Convert to audio using TTS
            audio_result = await self.tts_service.generate_audio(
                content=lecture_content["full_content"],
                voice_settings=voice_settings,
                output_filename=f"lecture_{lecture_id}.mp3"
            )
            
            if not audio_result["success"]:
                return {
                    "success": False,
                    "error": f"Audio generation failed: {audio_result.get('error', 'Unknown error')}"
                }
            
            # Return complete lecture data
            return {
                "success": True,
                "lecture_id": lecture_id,
                "title": topic,
                "duration": duration,
                "difficulty": difficulty,
                "source_type": "text",
                "content_sections": lecture_content,
                "audio_file": audio_result["file_path"],
                "file_size": audio_result.get("file_size", 0),
                "created_at": datetime.utcnow().isoformat(),
                "estimated_duration": audio_result.get("estimated_duration", duration * 60)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Lecture generation failed: {str(e)}"
            }
    
    async def generate_lecture_from_pdf(
        self,
        pdf_path: str,
        duration: int,
        difficulty: str,
        voice_settings: Dict,
        custom_topic: Optional[str] = None
    ) -> Dict[str, Union[str, bool]]:
        """
        Generate complete audio lecture from PDF document
        
        Args:
            pdf_path: Path to uploaded PDF file
            duration: Duration in minutes (5-60)
            difficulty: beginner, intermediate, advanced
            voice_settings: TTS voice configuration
            custom_topic: Optional custom topic override
            
        Returns:
            Dictionary with lecture metadata and file paths
        """
        
        if not self.openrouter_service:
            return {
                "success": False,
                "error": "AI service not initialized. Please provide valid API key."
            }
        
        try:
            # Extract and process PDF content
            pdf_result = await self.pdf_service.extract_and_process(pdf_path)
            
            if not pdf_result["success"]:
                return {
                    "success": False,
                    "error": f"PDF processing failed: {pdf_result.get('error', 'Unknown error')}"
                }
            
            # Use custom topic or extracted title
            topic = custom_topic or pdf_result["extracted_title"]
            
            # Generate lecture content with PDF context
            lecture_content = await self.openrouter_service.generate_lecture_content(
                topic=topic,
                duration=duration,
                difficulty=difficulty,
                user_context=pdf_result["processed_content"]
            )
            
            # Create lecture metadata
            lecture_id = self._generate_lecture_id(topic, duration)
            
            # Convert to audio using TTS
            audio_result = await self.tts_service.generate_audio(
                content=lecture_content["full_content"],
                voice_settings=voice_settings,
                output_filename=f"lecture_{lecture_id}.mp3"
            )
            
            if not audio_result["success"]:
                return {
                    "success": False,
                    "error": f"Audio generation failed: {audio_result.get('error', 'Unknown error')}"
                }
            
            # Clean up temporary PDF file
            await self._cleanup_temp_file(pdf_path)
            
            # Return complete lecture data
            return {
                "success": True,
                "lecture_id": lecture_id,
                "title": topic,
                "duration": duration,
                "difficulty": difficulty,
                "source_type": "pdf",
                "source_file": pdf_result["filename"],
                "content_sections": lecture_content,
                "audio_file": audio_result["file_path"],
                "file_size": audio_result.get("file_size", 0),
                "created_at": datetime.utcnow().isoformat(),
                "estimated_duration": audio_result.get("estimated_duration", duration * 60)
            }
            
        except Exception as e:
            # Clean up PDF file on error
            await self._cleanup_temp_file(pdf_path)
            return {
                "success": False,
                "error": f"PDF lecture generation failed: {str(e)}"
            }
    
    async def validate_user_api_key(self, encrypted_api_key: str, user_id: str) -> Dict[str, Union[str, bool]]:
        """
        Validate user's OpenRouter API key
        
        Args:
            encrypted_api_key: User's encrypted API key
            user_id: User identifier for decryption
            
        Returns:
            Validation result with available models if successful
        """
        try:
            # Decrypt and test API key
            api_key = self.encryption_service.decrypt_api_key(encrypted_api_key, user_id)
            test_service = OpenRouterService(api_key)
            
            # Test API key by fetching available models
            models = await test_service.get_available_models()
            
            return {
                "success": True,
                "valid": True,
                "available_models": models,
                "model_count": len(models)
            }
            
        except Exception as e:
            return {
                "success": False,
                "valid": False,
                "error": f"API key validation failed: {str(e)}"
            }
    
    def _generate_lecture_id(self, topic: str, duration: int) -> str:
        """Generate unique lecture ID"""
        content = f"{topic}_{duration}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    async def _cleanup_temp_file(self, file_path: str) -> None:
        """Clean up temporary files"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Failed to cleanup temp file {file_path}: {e}")
    
    async def get_service_status(self) -> Dict[str, bool]:
        """Get status of all integrated services"""
        return {
            "openrouter_initialized": self.openrouter_service is not None,
            "pdf_service_ready": True,  # PDFService is always available
            "tts_service_ready": await self.tts_service.check_availability(),
            "encryption_service_ready": True  # EncryptionService is always available
        }


# Service instance factory
def create_lecture_service() -> LectureGenerationService:
    """Create lecture generation service instance"""
    return LectureGenerationService()
