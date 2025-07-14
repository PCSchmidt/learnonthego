"""
SQLAlchemy Lecture models for LearnOnTheGo database
Handles lecture storage, user relationships, and API key management
Enhanced for Phase 2f: Multi-Provider AI Architecture
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Float, Enum as SQLEnum, Numeric
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
    # Multi-provider extensions
    GOOGLE_TTS = "google_tts"
    OPENAI_TTS = "openai_tts"
    UNREAL_SPEECH = "unreal_speech"
    OPENAI_DIRECT = "openai_direct"
    ANTHROPIC_DIRECT = "anthropic_direct"


class LLMProvider(enum.Enum):
    """Supported LLM providers for content generation"""
    OPENROUTER = "openrouter"  # Multi-model hub
    OPENAI_DIRECT = "openai_direct"  # Direct OpenAI API
    ANTHROPIC_DIRECT = "anthropic_direct"  # Direct Anthropic API
    GOOGLE_VERTEX = "google_vertex"  # Google Vertex AI
    LOCAL_OLLAMA = "local_ollama"  # Local Ollama models


class TTSProvider(enum.Enum):
    """Supported TTS providers with quality tiers"""
    ELEVENLABS = "elevenlabs"  # Premium quality
    GOOGLE_STANDARD = "google_standard"  # Free tier available
    GOOGLE_NEURAL = "google_neural"  # Enhanced quality
    OPENAI_TTS = "openai_tts"  # High quality
    UNREAL_SPEECH = "unreal_speech"  # Cost-effective
    AZURE_TTS = "azure_tts"  # Enterprise grade


class QualityTier(enum.Enum):
    """AI service quality tiers for cost optimization"""
    FREE = "free"  # Use free tier providers when possible
    STANDARD = "standard"  # Balance of cost and quality
    PREMIUM = "premium"  # Best quality available
    ENTERPRISE = "enterprise"  # Custom enterprise solutions


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
    
    # Multi-Provider AI Tracking (Phase 2f)
    llm_provider_used = Column(SQLEnum(LLMProvider), nullable=True)
    llm_model_name = Column(String(100), nullable=True)  # e.g., "gpt-4o", "claude-3.5-sonnet"
    tts_provider_used = Column(SQLEnum(TTSProvider), nullable=True)
    quality_tier_used = Column(SQLEnum(QualityTier), nullable=True)
    
    # Legacy voice settings (maintain compatibility)
    voice_provider = Column(String(50), nullable=True)  # elevenlabs
    voice_id = Column(String(100), nullable=True)
    voice_model = Column(String(100), nullable=True)
    voice_settings = Column(JSON, nullable=True)  # Complete voice configuration
    
    # Enhanced AI Cost Tracking
    llm_tokens_used = Column(Integer, nullable=True)
    llm_cost_usd = Column(Numeric(8, 4), nullable=True)  # Separate LLM cost
    tts_characters_used = Column(Integer, nullable=True)
    tts_cost_usd = Column(Numeric(8, 4), nullable=True)  # Separate TTS cost
    total_ai_cost_usd = Column(Numeric(8, 4), nullable=True)  # Combined AI cost
    cost_optimization_used = Column(Boolean, default=False)  # Was smart routing used?
    
    # Provider Performance Metrics
    llm_generation_time_ms = Column(Integer, nullable=True)
    tts_generation_time_ms = Column(Integer, nullable=True)
    total_generation_time_ms = Column(Integer, nullable=True)
    cache_hit = Column(Boolean, default=False)  # Was cached content used?
    
    # User engagement
    is_favorited = Column(Boolean, default=False, nullable=False)
    play_count = Column(Integer, default=0, nullable=False)
    last_played_at = Column(DateTime(timezone=True), nullable=True)
    
    # Cost tracking (legacy - for backwards compatibility)
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
    Encrypted storage for user's API keys - Enhanced for Multi-Provider AI
    
    Securely stores user-provided API keys for external services
    """
    __tablename__ = "user_api_keys"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(SQLEnum(APIProvider), nullable=False)
    
    # Multi-Provider Support (Phase 2f)
    provider_type = Column(String(20), nullable=False, default="llm")  # "llm", "tts", "both"
    provider_tier = Column(SQLEnum(QualityTier), nullable=True)  # User's preferred tier for this provider
    
    # Encrypted storage
    encrypted_key = Column(Text, nullable=False)  # AES-256 encrypted API key
    key_hash = Column(String(255), nullable=False)  # Hash for verification
    is_valid = Column(Boolean, default=True, nullable=False)  # Track if key works
    is_active = Column(Boolean, default=True, nullable=False)  # User can disable keys
    
    # Free Tier Management
    free_tier_remaining = Column(Integer, nullable=True)  # Characters/tokens remaining in free tier
    free_tier_reset_date = Column(DateTime(timezone=True), nullable=True)  # When free tier resets
    monthly_usage_limit = Column(Integer, nullable=True)  # User-set monthly limit
    
    # Metadata
    key_name = Column(String(100), nullable=True)  # User-friendly name
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    last_validation_at = Column(DateTime(timezone=True), nullable=True)
    validation_error = Column(Text, nullable=True)
    
    # Enhanced Usage tracking
    usage_count = Column(Integer, default=0, nullable=False)
    total_cost_usd = Column(Numeric(10, 4), default=0.0, nullable=False)
    monthly_cost_usd = Column(Numeric(8, 4), default=0.0, nullable=False)  # This month's cost
    cost_alert_threshold = Column(Numeric(8, 4), nullable=True)  # Alert when exceeded
    
    # Performance Metrics
    avg_response_time_ms = Column(Integer, nullable=True)
    success_rate_percent = Column(Float, nullable=True)
    total_requests = Column(Integer, default=0, nullable=False)
    failed_requests = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<UserAPIKey(id={self.id}, user_id={self.user_id}, provider='{self.provider.value}')>"

    @property
    def is_approaching_limit(self) -> bool:
        """Check if user is approaching their monthly limit"""
        if self.monthly_usage_limit and self.monthly_cost_usd:
            return self.monthly_cost_usd >= (self.monthly_usage_limit * 0.8)
        return False

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 100.0
        return ((self.total_requests - self.failed_requests) / self.total_requests) * 100

    def to_dict(self) -> dict:
        """Convert API key to dictionary for API responses (without sensitive data)"""
        return {
            "id": self.id,
            "provider": self.provider.value,
            "provider_type": self.provider_type,
            "provider_tier": self.provider_tier.value if self.provider_tier else None,
            "key_name": self.key_name,
            "is_valid": self.is_valid,
            "is_active": self.is_active,
            "free_tier_remaining": self.free_tier_remaining,
            "free_tier_reset_date": self.free_tier_reset_date.isoformat() if self.free_tier_reset_date else None,
            "monthly_usage_limit": self.monthly_usage_limit,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "last_validation_at": self.last_validation_at.isoformat() if self.last_validation_at else None,
            "validation_error": self.validation_error,
            "usage_count": self.usage_count,
            "total_cost_usd": float(self.total_cost_usd) if self.total_cost_usd else 0.0,
            "monthly_cost_usd": float(self.monthly_cost_usd) if self.monthly_cost_usd else 0.0,
            "cost_alert_threshold": float(self.cost_alert_threshold) if self.cost_alert_threshold else None,
            "avg_response_time_ms": self.avg_response_time_ms,
            "success_rate_percent": self.success_rate,
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "is_approaching_limit": self.is_approaching_limit,
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


class UserAIPreferences(Base):
    """
    User preferences for AI provider selection and cost optimization
    """
    __tablename__ = "user_ai_preferences"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # General AI Preferences
    default_quality_tier = Column(SQLEnum(QualityTier), default=QualityTier.STANDARD, nullable=False)
    enable_cost_optimization = Column(Boolean, default=True, nullable=False)
    enable_smart_routing = Column(Boolean, default=True, nullable=False)  # Auto-select best provider
    enable_caching = Column(Boolean, default=True, nullable=False)  # Use cached results when available
    
    # LLM Preferences
    preferred_llm_provider = Column(SQLEnum(LLMProvider), nullable=True)
    preferred_llm_model = Column(String(100), nullable=True)  # e.g., "gpt-4o", "claude-3.5-sonnet"
    llm_creativity_level = Column(Float, default=0.7, nullable=False)  # 0.0-1.0 for temperature
    llm_max_tokens = Column(Integer, default=4000, nullable=False)
    
    # TTS Preferences
    preferred_tts_provider = Column(SQLEnum(TTSProvider), nullable=True)
    preferred_voice_id = Column(String(100), nullable=True)
    preferred_language = Column(String(10), default="en", nullable=False)
    voice_speed = Column(Float, default=1.0, nullable=False)  # Speech rate multiplier
    voice_stability = Column(Float, default=0.75, nullable=False)  # ElevenLabs specific
    voice_clarity = Column(Float, default=0.75, nullable=False)  # ElevenLabs specific
    
    # Cost Management
    monthly_budget_usd = Column(Numeric(8, 2), nullable=True)  # User's monthly AI budget
    cost_alert_percentage = Column(Integer, default=80, nullable=False)  # Alert at 80% of budget
    auto_downgrade_quality = Column(Boolean, default=False, nullable=False)  # Downgrade when approaching limit
    prefer_free_tier = Column(Boolean, default=True, nullable=False)  # Prefer free tier when possible
    
    # Performance Preferences
    max_generation_time_seconds = Column(Integer, default=120, nullable=False)  # Timeout preference
    require_high_success_rate = Column(Boolean, default=True, nullable=False)  # Only use reliable providers
    
    # Content Preferences
    content_style = Column(String(50), default="educational", nullable=False)  # educational, conversational, formal
    include_examples = Column(Boolean, default=True, nullable=False)
    include_summary = Column(Boolean, default=True, nullable=False)
    preferred_content_length = Column(String(20), default="standard", nullable=False)  # concise, standard, detailed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ai_preferences", uselist=False)

    def __repr__(self):
        return f"<UserAIPreferences(user_id={self.user_id}, quality_tier='{self.default_quality_tier.value}')>"

    def to_dict(self) -> dict:
        """Convert AI preferences to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "default_quality_tier": self.default_quality_tier.value,
            "enable_cost_optimization": self.enable_cost_optimization,
            "enable_smart_routing": self.enable_smart_routing,
            "enable_caching": self.enable_caching,
            "preferred_llm_provider": self.preferred_llm_provider.value if self.preferred_llm_provider else None,
            "preferred_llm_model": self.preferred_llm_model,
            "llm_creativity_level": float(self.llm_creativity_level),
            "llm_max_tokens": self.llm_max_tokens,
            "preferred_tts_provider": self.preferred_tts_provider.value if self.preferred_tts_provider else None,
            "preferred_voice_id": self.preferred_voice_id,
            "preferred_language": self.preferred_language,
            "voice_speed": float(self.voice_speed),
            "voice_stability": float(self.voice_stability),
            "voice_clarity": float(self.voice_clarity),
            "monthly_budget_usd": float(self.monthly_budget_usd) if self.monthly_budget_usd else None,
            "cost_alert_percentage": self.cost_alert_percentage,
            "auto_downgrade_quality": self.auto_downgrade_quality,
            "prefer_free_tier": self.prefer_free_tier,
            "max_generation_time_seconds": self.max_generation_time_seconds,
            "require_high_success_rate": self.require_high_success_rate,
            "content_style": self.content_style,
            "include_examples": self.include_examples,
            "include_summary": self.include_summary,
            "preferred_content_length": self.preferred_content_length,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class AIProviderConfig(Base):
    """
    System-wide AI provider configuration and capabilities
    """
    __tablename__ = "ai_provider_configs"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(50), nullable=False, unique=True)
    provider_type = Column(String(20), nullable=False)  # "llm", "tts"
    
    # Provider Details
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    documentation_url = Column(String(500), nullable=True)
    pricing_url = Column(String(500), nullable=True)
    
    # Capabilities
    supported_languages = Column(JSON, nullable=True)  # List of language codes
    supported_models = Column(JSON, nullable=True)  # Available models/voices
    max_characters = Column(Integer, nullable=True)  # For TTS providers
    max_tokens = Column(Integer, nullable=True)  # For LLM providers
    
    # Cost Information
    cost_per_1k_tokens = Column(Numeric(10, 6), nullable=True)  # LLM pricing
    cost_per_1k_chars = Column(Numeric(10, 6), nullable=True)  # TTS pricing
    free_tier_limit = Column(Integer, nullable=True)  # Free tier tokens/characters
    free_tier_reset_period = Column(String(20), nullable=True)  # "monthly", "daily"
    
    # Quality Metrics
    quality_score = Column(Float, nullable=False, default=5.0)  # 1-10 scale
    reliability_score = Column(Float, nullable=False, default=5.0)  # 1-10 scale
    speed_score = Column(Float, nullable=False, default=5.0)  # 1-10 scale
    
    # Availability
    is_enabled = Column(Boolean, default=True, nullable=False)
    is_free_tier_available = Column(Boolean, default=False, nullable=False)
    requires_api_key = Column(Boolean, default=True, nullable=False)
    
    # Rate Limiting
    requests_per_minute = Column(Integer, nullable=True)
    requests_per_day = Column(Integer, nullable=True)
    concurrent_requests = Column(Integer, default=1, nullable=False)
    
    # Performance Metrics
    avg_response_time_ms = Column(Integer, nullable=True)
    success_rate_24h = Column(Float, nullable=True)
    last_status_check = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AIProviderConfig(provider='{self.provider_name}', type='{self.provider_type}')>"

    def to_dict(self) -> dict:
        """Convert provider config to dictionary for API responses"""
        return {
            "id": self.id,
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "display_name": self.display_name,
            "description": self.description,
            "documentation_url": self.documentation_url,
            "pricing_url": self.pricing_url,
            "supported_languages": self.supported_languages,
            "supported_models": self.supported_models,
            "max_characters": self.max_characters,
            "max_tokens": self.max_tokens,
            "cost_per_1k_tokens": float(self.cost_per_1k_tokens) if self.cost_per_1k_tokens else None,
            "cost_per_1k_chars": float(self.cost_per_1k_chars) if self.cost_per_1k_chars else None,
            "free_tier_limit": self.free_tier_limit,
            "free_tier_reset_period": self.free_tier_reset_period,
            "quality_score": float(self.quality_score),
            "reliability_score": float(self.reliability_score),
            "speed_score": float(self.speed_score),
            "is_enabled": self.is_enabled,
            "is_free_tier_available": self.is_free_tier_available,
            "requires_api_key": self.requires_api_key,
            "requests_per_minute": self.requests_per_minute,
            "requests_per_day": self.requests_per_day,
            "concurrent_requests": self.concurrent_requests,
            "avg_response_time_ms": self.avg_response_time_ms,
            "success_rate_24h": float(self.success_rate_24h) if self.success_rate_24h else None,
            "last_status_check": self.last_status_check.isoformat() if self.last_status_check else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
