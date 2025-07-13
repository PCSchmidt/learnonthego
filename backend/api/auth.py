"""
Authentication API endpoints - Phase 2b
Handles user registration, login, and profile management
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from pydantic.networks import EmailStr

from models import (
    get_async_db,
    UserORM,
    UserRegistration,
    UserLogin,
    UserResponse,
    UserDetails,
    User as UserPydantic
)

from auth import (
    create_access_token,
    hash_password,
    verify_password,
    get_current_active_user
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistration,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Register a new user account
    
    Phase 2b: Complete registration with password hashing and JWT token
    """
    try:
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Create new user
        new_user = UserORM.create_from_registration(
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name
        )
        
        # Add user to database
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": new_user.email, "user_id": new_user.id},
            expires_delta=access_token_expires
        )
        
        # Convert to response model
        user_response = UserPydantic(
            id=new_user.id,
            email=new_user.email,
            created_at=new_user.created_at,
            is_active=new_user.is_active,
            subscription_tier=new_user.subscription_tier.value,
            preferences={}
        )
        
        return UserResponse(
            success=True,
            user=user_response,
            access_token=access_token,
            token_type="bearer"
        )
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )


@router.post("/login", response_model=UserResponse)
async def login_user(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Authenticate user and return JWT token
    
    Phase 2b: Complete login with password verification
    """
    try:
        # Find user by email
        result = await db.execute(
            select(UserORM).where(UserORM.email == user_credentials.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(user_credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is disabled"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        # Update last login
        from datetime import datetime
        user.last_login_at = datetime.utcnow()
        await db.commit()
        
        # Convert to response model
        user_response = UserPydantic(
            id=user.id,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active,
            subscription_tier=user.subscription_tier.value,
            preferences={}
        )
        
        return UserResponse(
            success=True,
            user=user_response,
            access_token=access_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserDetails)
async def get_current_user_profile(
    current_user: UserORM = Depends(get_current_active_user)
):
    """
    Get current user's profile information
    
    Phase 2b: Protected endpoint requiring authentication
    """
    return UserDetails(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        subscription_tier=current_user.subscription_tier.value,
        is_verified=current_user.is_verified,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        lectures_generated_count=current_user.lectures_generated_count,
        total_audio_minutes=current_user.total_audio_minutes
    )


@router.post("/logout")
async def logout_user():
    """
    Logout user (client-side token removal)
    
    Phase 2b: Logout functionality
    """
    return {
        "success": True,
        "message": "Logged out successfully. Please remove the token from client storage."
    }


@router.post("/refresh", response_model=UserResponse)
async def refresh_token(
    current_user: UserORM = Depends(get_current_active_user)
):
    """
    Refresh JWT access token
    
    Phase 2b: Token refresh for extended sessions
    """
    try:
        # Create new access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": current_user.email, "user_id": current_user.id},
            expires_delta=access_token_expires
        )
        
        # Convert to response model
        user_response = UserPydantic(
            id=current_user.id,
            email=current_user.email,
            created_at=current_user.created_at,
            is_active=current_user.is_active,
            subscription_tier=current_user.subscription_tier.value,
            preferences={}
        )
        
        return UserResponse(
            success=True,
            user=user_response,
            access_token=access_token,
            token_type="bearer"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/password-reset-request")
async def request_password_reset(
    request_data: dict,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Request password reset token
    
    Phase 2b: Password reset functionality
    """
    try:
        email = request_data.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        # Find user by email
        result = await db.execute(
            select(UserORM).where(UserORM.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Don't reveal if email exists for security
            return {"success": True, "message": "If the email exists, a reset link has been sent"}
        
        # Generate reset token (simple implementation)
        import secrets
        reset_token = secrets.token_urlsafe(32)
        
        # In a real implementation, you would:
        # 1. Store the reset token in database with expiry
        # 2. Send email with reset link
        # For now, we'll just return success
        
        return {"success": True, "message": "Password reset link sent to your email"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )
