"""
Models package for LearnOnTheGo backend
Contains both Pydantic models (API) and SQLAlchemy models (Database)
"""

# Database configuration and base
from models.database import (
    Base,
    engine,
    async_engine,
    SessionLocal,
    AsyncSessionLocal,
    get_async_db,
    get_sync_db,
    create_tables,
    create_tables_async,
    drop_tables_async,
    check_database_health,
    get_database_info
)

# SQLAlchemy ORM models (database entities)
from models.user_orm import User as UserORM, SubscriptionTier
from models.lecture_orm import (
    Lecture,
    UserAPIKey,
    UsageLog,
    UserAIPreferences,
    AIProviderConfig,
    LectureSourceType,
    LectureStatus,
    APIProvider,
    LLMProvider,
    TTSProvider,
    QualityTier
)

# Pydantic models (API requests/responses)
from models.lecture_models import (
    VoiceSettings,
    LectureRequest,
    PDFLectureRequest,
    LectureResponse,
    APIKeyValidationRequest,
    APIKeyValidationResponse,
    LectureListItem,
    LectureLibraryResponse,
    LectureAnalytics,
    ContentSection,
    DetailedLectureResponse
)

from models.user_models import (
    User,
    UserRegistration,
    UserLogin,
    UserResponse,
    UserDetails,
    APIKeyUpdate,
    UserPreferencesUpdate,
    UserStatsResponse
)

__all__ = [
    # Database configuration and utilities
    "Base",
    "engine", 
    "async_engine",
    "SessionLocal",
    "AsyncSessionLocal", 
    "get_async_db",
    "get_sync_db",
    "create_tables",
    "create_tables_async",
    "drop_tables_async",
    "check_database_health",
    "get_database_info",
    
    # SQLAlchemy ORM models
    "UserORM",
    "SubscriptionTier",
    "Lecture",
    "UserAPIKey", 
    "UsageLog",
    "UserAIPreferences",
    "AIProviderConfig",
    "LectureSourceType",
    "LectureStatus", 
    "APIProvider",
    "LLMProvider",
    "TTSProvider",
    "QualityTier",
    
    # Pydantic API models - Lecture
    "VoiceSettings",
    "LectureRequest",
    "PDFLectureRequest", 
    "LectureResponse",
    "APIKeyValidationRequest",
    "APIKeyValidationResponse",
    "LectureListItem",
    "LectureLibraryResponse",
    "LectureAnalytics",
    "ContentSection",
    "DetailedLectureResponse",
    
    # Pydantic API models - User  
    "User",
    "UserRegistration",
    "UserLogin", 
    "UserResponse",
    "UserDetails",
    "APIKeyUpdate",
    "UserPreferencesUpdate",
    "UserStatsResponse"
]
