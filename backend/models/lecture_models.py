"""
Pydantic models for lecture-related API requests and responses
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List, Any
from datetime import datetime


class VoiceSettings(BaseModel):
    """Voice configuration for TTS generation"""
    model_config = {"protected_namespaces": ()}
    
    provider: str = Field(..., description="TTS provider (elevenlabs)")
    api_key: str = Field(..., description="TTS API key")
    voice_id: str = Field(default="21m00Tcm4TlvDq8ikWAM", description="Voice ID")
    model_id: str = Field(default="eleven_multilingual_v2", description="TTS model ID")
    stability: float = Field(default=0.5, ge=0.0, le=1.0, description="Voice stability")
    similarity_boost: float = Field(default=0.75, ge=0.0, le=1.0, description="Similarity boost")
    style: float = Field(default=0.0, ge=0.0, le=1.0, description="Voice style")
    use_speaker_boost: bool = Field(default=True, description="Use speaker boost")


class LectureRequest(BaseModel):
    """Request model for generating lecture from text topic"""
    topic: str = Field(..., min_length=10, max_length=500, description="Lecture topic")
    duration: int = Field(..., ge=5, le=60, description="Duration in minutes")
    difficulty: str = Field(..., description="Difficulty level")
    voice_settings: VoiceSettings = Field(..., description="TTS voice configuration")
    user_context: Optional[str] = Field(None, max_length=2000, description="Additional context")
    
    @field_validator('difficulty')
    def validate_difficulty(cls, v):
        if v not in ['beginner', 'intermediate', 'advanced']:
            raise ValueError('Difficulty must be beginner, intermediate, or advanced')
        return v


class PDFLectureRequest(BaseModel):
    """Request model for generating lecture from PDF (used in multipart form)"""
    duration: int = Field(..., ge=5, le=60, description="Duration in minutes")
    difficulty: str = Field(..., description="Difficulty level")
    voice_settings: Dict[str, Any] = Field(..., description="TTS voice configuration")
    custom_topic: Optional[str] = Field(None, max_length=200, description="Custom topic override")
    
    @field_validator('difficulty')
    def validate_difficulty(cls, v):
        if v not in ['beginner', 'intermediate', 'advanced']:
            raise ValueError('Difficulty must be beginner, intermediate, or advanced')
        return v


class LectureResponse(BaseModel):
    """Response model for lecture generation"""
    success: bool = Field(..., description="Whether generation was successful")
    lecture_id: Optional[str] = Field(None, description="Unique lecture identifier")
    title: Optional[str] = Field(None, description="Lecture title")
    duration: Optional[int] = Field(None, description="Requested duration in minutes")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    source_type: Optional[str] = Field(None, description="Source type (text or pdf)")
    source_file: Optional[str] = Field(None, description="Original source filename for PDF")
    audio_file_url: Optional[str] = Field(None, description="URL to download audio file")
    file_size: Optional[int] = Field(None, description="Audio file size in bytes")
    estimated_duration: Optional[int] = Field(None, description="Estimated audio duration in seconds")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    content_sections: Optional[Dict[str, str]] = Field(None, description="Generated content sections")
    error: Optional[str] = Field(None, description="Error message if generation failed")


class APIKeyValidationRequest(BaseModel):
    """Request model for API key validation"""
    encrypted_api_key: str = Field(..., description="Encrypted OpenRouter API key")


class APIKeyValidationResponse(BaseModel):
    """Response model for API key validation"""
    model_config = {"protected_namespaces": ()}
    
    success: bool = Field(..., description="Whether validation was successful")
    valid: bool = Field(..., description="Whether the API key is valid")
    available_models: Optional[List[Dict[str, Any]]] = Field(None, description="Available models")
    model_count: Optional[int] = Field(None, description="Number of available models")
    error: Optional[str] = Field(None, description="Error message if validation failed")


class LectureListItem(BaseModel):
    """Model for lecture in user's library list"""
    lecture_id: str = Field(..., description="Unique lecture identifier")
    title: str = Field(..., description="Lecture title")
    duration: int = Field(..., description="Duration in minutes")
    difficulty: str = Field(..., description="Difficulty level")
    source_type: str = Field(..., description="Source type (text or pdf)")
    source_file: Optional[str] = Field(None, description="Original filename for PDF")
    file_size: int = Field(..., description="Audio file size in bytes")
    estimated_duration: int = Field(..., description="Estimated audio duration in seconds")
    created_at: str = Field(..., description="Creation timestamp")
    is_favorited: bool = Field(default=False, description="Whether lecture is favorited")


class LectureLibraryResponse(BaseModel):
    """Response model for user's lecture library"""
    success: bool = Field(..., description="Whether request was successful")
    lectures: List[LectureListItem] = Field(..., description="List of user's lectures")
    total_count: int = Field(..., description="Total number of lectures")
    total_size: int = Field(..., description="Total size of all audio files in bytes")
    error: Optional[str] = Field(None, description="Error message if request failed")


class LectureAnalytics(BaseModel):
    """Model for lecture analytics data"""
    total_lectures: int = Field(..., description="Total lectures generated")
    total_duration: int = Field(..., description="Total duration in minutes")
    avg_duration: float = Field(..., description="Average duration in minutes")
    difficulty_breakdown: Dict[str, int] = Field(..., description="Count by difficulty level")
    source_type_breakdown: Dict[str, int] = Field(..., description="Count by source type")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Recent lecture activity")


class ContentSection(BaseModel):
    """Model for individual content section"""
    section_type: str = Field(..., description="Section type (intro, main, examples, conclusion)")
    content: str = Field(..., description="Section content")
    word_count: int = Field(..., description="Word count for section")
    estimated_duration: int = Field(..., description="Estimated duration in seconds")


class DetailedLectureResponse(BaseModel):
    """Detailed response model with full lecture information"""
    success: bool = Field(..., description="Whether request was successful")
    lecture_id: str = Field(..., description="Unique lecture identifier")
    title: str = Field(..., description="Lecture title")
    duration: int = Field(..., description="Requested duration in minutes")
    difficulty: str = Field(..., description="Difficulty level")
    source_type: str = Field(..., description="Source type (text or pdf)")
    source_file: Optional[str] = Field(None, description="Original filename for PDF")
    audio_file_url: str = Field(..., description="URL to download audio file")
    file_size: int = Field(..., description="Audio file size in bytes")
    estimated_duration: int = Field(..., description="Estimated audio duration in seconds")
    created_at: str = Field(..., description="Creation timestamp")
    is_favorited: bool = Field(default=False, description="Whether lecture is favorited")
    content_sections: List[ContentSection] = Field(..., description="Detailed content sections")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error: Optional[str] = Field(None, description="Error message if request failed")
