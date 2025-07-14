"""
SQLAlchemy User model for LearnOnTheGo database
Handles user accounts, authentication, and profile management
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from models.database import Base


class SubscriptionTier(enum.Enum):
    """User subscription tiers"""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class User(Base):
    """
    SQLAlchemy User model for database operations
    
    Stores user account information, authentication data, and preferences
    """
    __tablename__ = "users"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Subscription and limits
    subscription_tier = Column(
        SQLEnum(SubscriptionTier), 
        default=SubscriptionTier.FREE, 
        nullable=False
    )
    
    # Profile information
    full_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Preferences
    preferred_difficulty = Column(String(50), default="intermediate")  # beginner, intermediate, advanced
    preferred_duration = Column(Integer, default=15)  # Default 15 minutes
    preferred_voice = Column(String(100), nullable=True)  # ElevenLabs voice ID
    
    # Usage tracking
    lectures_generated_count = Column(Integer, default=0)
    total_audio_minutes = Column(Integer, default=0)  # Total minutes of audio generated
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Email verification
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    lectures = relationship("Lecture", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("UserAPIKey", back_populates="user", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    ai_preferences = relationship("UserAIPreferences", back_populates="user", cascade="all, delete-orphan", uselist=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', tier='{self.subscription_tier.value}')>"

    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription"""
        return self.subscription_tier in [SubscriptionTier.PREMIUM, SubscriptionTier.ENTERPRISE]

    @property
    def monthly_lecture_limit(self) -> int:
        """Get monthly lecture generation limit based on subscription tier"""
        limits = {
            SubscriptionTier.FREE: 10,
            SubscriptionTier.PREMIUM: 100,
            SubscriptionTier.ENTERPRISE: 1000
        }
        return limits.get(self.subscription_tier, 10)

    @property
    def monthly_pdf_limit(self) -> int:
        """Get monthly PDF upload limit based on subscription tier"""
        limits = {
            SubscriptionTier.FREE: 5,
            SubscriptionTier.PREMIUM: 50,
            SubscriptionTier.ENTERPRISE: 500
        }
        return limits.get(self.subscription_tier, 5)

    def to_dict(self) -> dict:
        """Convert user to dictionary for API responses"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "bio": self.bio,
            "subscription_tier": self.subscription_tier.value,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "preferred_difficulty": self.preferred_difficulty,
            "preferred_duration": self.preferred_duration,
            "preferred_voice": self.preferred_voice,
            "lectures_generated_count": self.lectures_generated_count,
            "total_audio_minutes": self.total_audio_minutes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "monthly_lecture_limit": self.monthly_lecture_limit,
            "monthly_pdf_limit": self.monthly_pdf_limit,
            "is_premium": self.is_premium
        }

    @classmethod
    def create_from_registration(
        cls, 
        email: str, 
        password_hash: str, 
        full_name: Optional[str] = None
    ) -> "User":
        """
        Factory method to create user from registration data
        """
        return cls(
            email=email.lower().strip(),
            password_hash=password_hash,
            full_name=full_name,
            is_verified=False,  # Require email verification
            is_active=True,
            subscription_tier=SubscriptionTier.FREE
        )
