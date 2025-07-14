"""
SQLAlchemy Lecture models for LearnOnTheGo database
Handles lecture storage, user relationships, and API key management
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from models.database import Base


class LectureSourceType(enum.Enum):
    """Source type for lecture generation"""
    TEXT = "text"
    PDF = "pdf"


class LectureStatus(enum.Enum):
    """Lecture processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class APIProvider(enum.Enum):
    """Supported API providers"""
    OPENROUTER = "openrouter"
    ELEVENLABS = "elevenlabs"


class Lecture(Base):
    """
    SQLAlchemy Lecture model for database operations
    
    Stores generated lectures, metadata, and user relationships
    """
    __tablename__ = "lectures"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Lecture metadata
    title = Column(String(500), nullable=False)
    topic = Column(Text, nullable=False)  # Original topic or extracted content
    difficulty = Column(String(50), nullable=False)  # beginner, intermediate, advanced
    duration_requested = Column(Integer, nullable=False)  # Requested minutes
    duration_actual = Column(Integer, nullable=True)  # Actual audio duration
    
    # Source information
    source_type = Column(SQLEnum(LectureSourceType), nullable=False)
    source_file_name = Column(String(255), nullable=True)  # Original PDF filename
    source_file_size = Column(Integer, nullable=True)  # File size in bytes
    custom_context = Column(Text, nullable=True)  # User-provided context
    
    # Processing status
    status = Column(SQLEnum(LectureStatus), default=LectureStatus.PENDING, nullable=False)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Generated content
    lecture_script = Column(Text, nullable=True)  # Generated lecture text
    audio_file_url = Column(String(1000), nullable=True)  # Cloudinary URL
    audio_file_size = Column(Integer, nullable=True)  # Audio file size in bytes
    
    # Voice settings used
    voice_provider = Column(String(50), nullable=True)  # elevenlabs
    voice_id = Column(String(100), nullable=True)
    voice_model = Column(String(100), nullable=True)
    voice_settings = Column(JSON, nullable=True)  # Complete voice configuration
    
    # User engagement
    is_favorited = Column(Boolean, default=False, nullable=False)
    play_count = Column(Integer, default=0, nullable=False)
    last_played_at = Column(DateTime(timezone=True), nullable=True)
    
    # Cost tracking
    llm_tokens_used = Column(Integer, nullable=True)
    tts_characters_used = Column(Integer, nullable=True)
    estimated_cost_usd = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    auto_delete_at = Column(DateTime(timezone=True), nullable=True)  # 30 days unless favorited
    
    # Relationships
    user = relationship("User", back_populates="lectures")

    def __repr__(self):
        return f"<Lecture(id={self.id}, title='{self.title[:50]}...', status='{self.status.value}')>"

    @property
    def is_completed(self) -> bool:
        """Check if lecture generation is completed"""
        return self.status == LectureStatus.COMPLETED

    @property
    def is_processing(self) -> bool:
        """Check if lecture is currently being processed"""
        return self.status in [LectureStatus.PENDING, LectureStatus.PROCESSING]

    @property
    def processing_duration_seconds(self) -> Optional[int]:
        """Get processing duration in seconds"""
        if self.processing_started_at and self.processing_completed_at:
            delta = self.processing_completed_at - self.processing_started_at
            return int(delta.total_seconds())
        return None

    def to_dict(self) -> dict:
        """Convert lecture to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "duration_requested": self.duration_requested,
            "duration_actual": self.duration_actual,
            "source_type": self.source_type.value,
            "source_file_name": self.source_file_name,
            "source_file_size": self.source_file_size,
            "custom_context": self.custom_context,
            "status": self.status.value,
            "processing_started_at": self.processing_started_at.isoformat() if self.processing_started_at else None,
            "processing_completed_at": self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            "error_message": self.error_message,
            "lecture_script": self.lecture_script,
            "audio_file_url": self.audio_file_url,
            "audio_file_size": self.audio_file_size,
            "voice_provider": self.voice_provider,
            "voice_id": self.voice_id,
            "voice_model": self.voice_model,
            "voice_settings": self.voice_settings,
            "is_favorited": self.is_favorited,
            "play_count": self.play_count,
            "last_played_at": self.last_played_at.isoformat() if self.last_played_at else None,
            "llm_tokens_used": self.llm_tokens_used,
            "tts_characters_used": self.tts_characters_used,
            "estimated_cost_usd": self.estimated_cost_usd,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "auto_delete_at": self.auto_delete_at.isoformat() if self.auto_delete_at else None,
            "is_completed": self.is_completed,
            "is_processing": self.is_processing,
            "processing_duration_seconds": self.processing_duration_seconds
        }


class UserAPIKey(Base):
    """
    Encrypted storage for user's API keys
    
    Securely stores user-provided API keys for external services
    """
    __tablename__ = "user_api_keys"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(SQLEnum(APIProvider), nullable=False)
    
    # Encrypted storage
    encrypted_key = Column(Text, nullable=False)  # AES-256 encrypted API key
    key_hash = Column(String(255), nullable=False)  # Hash for verification
    is_valid = Column(Boolean, default=True, nullable=False)  # Track if key works
    
    # Metadata
    key_name = Column(String(100), nullable=True)  # User-friendly name
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    last_validation_at = Column(DateTime(timezone=True), nullable=True)
    validation_error = Column(Text, nullable=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0, nullable=False)
    total_cost_usd = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<UserAPIKey(id={self.id}, user_id={self.user_id}, provider='{self.provider.value}')>"

    def to_dict(self) -> dict:
        """Convert API key to dictionary for API responses (without sensitive data)"""
        return {
            "id": self.id,
            "provider": self.provider.value,
            "key_name": self.key_name,
            "is_valid": self.is_valid,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "last_validation_at": self.last_validation_at.isoformat() if self.last_validation_at else None,
            "validation_error": self.validation_error,
            "usage_count": self.usage_count,
            "total_cost_usd": self.total_cost_usd,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class UsageLog(Base):
    """
    Track API usage for cost monitoring and rate limiting
    """
    __tablename__ = "usage_logs"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=True, index=True)
    api_key_id = Column(Integer, ForeignKey("user_api_keys.id"), nullable=True, index=True)
    
    # Usage details
    provider = Column(SQLEnum(APIProvider), nullable=False)
    operation_type = Column(String(50), nullable=False)  # llm_generation, tts_conversion
    tokens_used = Column(Integer, nullable=True)
    characters_used = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)
    
    # Request metadata
    request_duration_ms = Column(Integer, nullable=True)
    response_status = Column(String(50), nullable=False)  # success, error, timeout
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")
    lecture = relationship("Lecture")
    api_key = relationship("UserAPIKey")

    def __repr__(self):
        return f"<UsageLog(id={self.id}, provider='{self.provider.value}', operation='{self.operation_type}')>"

    def to_dict(self) -> dict:
        """Convert usage log to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "lecture_id": self.lecture_id,
            "api_key_id": self.api_key_id,
            "provider": self.provider.value,
            "operation_type": self.operation_type,
            "tokens_used": self.tokens_used,
            "characters_used": self.characters_used,
            "cost_usd": self.cost_usd,
            "request_duration_ms": self.request_duration_ms,
            "response_status": self.response_status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
