"""
Pydantic models for user-related API requests and responses
"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Dict, Any
from datetime import datetime


class User(BaseModel):
    """User model for authentication and API responses"""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    created_at: datetime = Field(..., description="Account creation timestamp")
    is_active: bool = Field(default=True, description="Whether user account is active")
    subscription_tier: str = Field(default="free", description="User subscription tier")
    openrouter_api_key: Optional[str] = Field(None, description="Encrypted OpenRouter API key")
    elevenlabs_api_key: Optional[str] = Field(None, description="Encrypted ElevenLabs API key")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")


class UserRegistration(BaseModel):
    """Request model for user registration"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    confirm_password: str = Field(..., description="Password confirmation")
    full_name: Optional[str] = Field(None, description="User's full name")
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values.data and v != values.data['password']:
            raise ValueError('Passwords do not match')
        return v


class UserLogin(BaseModel):
    """Request model for user login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Response model for user data"""
    success: bool = Field(..., description="Whether request was successful")
    user: Optional[User] = Field(None, description="User data")
    access_token: Optional[str] = Field(None, description="JWT access token")
    token_type: Optional[str] = Field(None, description="Token type (bearer)")
    error: Optional[str] = Field(None, description="Error message if request failed")


class UserDetails(BaseModel):
    """Detailed user information for listing"""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User's full name")
    subscription_tier: str = Field(..., description="User subscription tier")
    is_verified: bool = Field(..., description="Whether email is verified")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    lectures_generated_count: int = Field(default=0, description="Number of lectures generated")
    total_audio_minutes: int = Field(default=0, description="Total audio minutes listened")


class APIKeyUpdate(BaseModel):
    """Request model for updating API keys"""
    provider: str = Field(..., description="API provider (openrouter, elevenlabs)")
    api_key: str = Field(..., description="API key to encrypt and store")
    
    @field_validator('provider')
    def validate_provider(cls, v):
        if v not in ['openrouter', 'elevenlabs']:
            raise ValueError('Provider must be openrouter or elevenlabs')
        return v


class UserPreferencesUpdate(BaseModel):
    """Request model for updating user preferences"""
    default_voice_id: Optional[str] = Field(None, description="Default voice ID for TTS")
    default_difficulty: Optional[str] = Field(None, description="Default difficulty level")
    default_duration: Optional[int] = Field(None, ge=5, le=60, description="Default duration")
    auto_cleanup_days: Optional[int] = Field(None, ge=1, le=365, description="Auto cleanup period")
    notifications_enabled: Optional[bool] = Field(None, description="Enable notifications")
    
    @field_validator('default_difficulty')
    def validate_difficulty(cls, v):
        if v is not None and v not in ['beginner', 'intermediate', 'advanced']:
            raise ValueError('Difficulty must be beginner, intermediate, or advanced')
        return v


class UserStatsResponse(BaseModel):
    """Response model for user statistics"""
    success: bool = Field(..., description="Whether request was successful")
    total_lectures: int = Field(..., description="Total lectures generated")
    total_duration: int = Field(..., description="Total duration in minutes")
    storage_used: int = Field(..., description="Storage used in bytes")
    storage_limit: int = Field(..., description="Storage limit in bytes")
    lectures_this_month: int = Field(..., description="Lectures generated this month")
    subscription_tier: str = Field(..., description="Current subscription tier")
    api_keys_configured: Dict[str, bool] = Field(..., description="Which API keys are configured")
    error: Optional[str] = Field(None, description="Error message if request failed")
