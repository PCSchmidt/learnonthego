"""
Models package for LearnOnTheGo backend
Contains all Pydantic models for API requests and responses
"""

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
    APIKeyUpdate,
    UserPreferencesUpdate,
    UserStatsResponse
)

__all__ = [
    # Lecture models
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
    
    # User models
    "User",
    "UserRegistration",
    "UserLogin",
    "UserResponse",
    "APIKeyUpdate",
    "UserPreferencesUpdate",
    "UserStatsResponse"
]
