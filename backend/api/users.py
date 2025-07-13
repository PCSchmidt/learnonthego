"""
User management API endpoints - Phase 2b: Protected User Management
CRUD operations for users with authentication
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models import (
    get_async_db,
    UserORM,
    SubscriptionTier,
    UserDetails,
    User as UserPydantic
)

from auth import get_current_active_user

router = APIRouter(prefix="/api/users", tags=["users"])


# Note: User registration is now handled by /api/auth/register
# This module focuses on user management and admin operations


@router.get("/{user_id}", response_model=UserDetails)
async def get_user(
    user_id: int,
    current_user: UserORM = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get user by ID (Protected endpoint)
    
    Phase 2b: Requires authentication - users can only access their own profile
    """
    # Users can only access their own profile (non-admin)
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Can only access your own profile"
        )
    
    try:
        # Query user by ID
        result = await db.execute(select(UserORM).where(UserORM.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Convert to response model
        return UserDetails(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            subscription_tier=user.subscription_tier.value,
            is_verified=user.is_verified,
            is_active=user.is_active,
            created_at=user.created_at,
            lectures_generated_count=user.lectures_generated_count,
            total_audio_minutes=user.total_audio_minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )


# Note: List users endpoint disabled in Phase 2b - requires admin authentication
# @router.get("/", response_model=List[UserDetails])
# Will be re-enabled in Phase 2c with proper admin role checks


@router.get("/email/{email}", response_model=UserDetails)
async def get_user_by_email(
    email: str,
    current_user: UserORM = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get user by email address (Protected endpoint)
    
    Phase 2b: Users can only access their own profile by email
    """
    # Users can only access their own profile by email
    if current_user.email.lower() != email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Can only access your own profile"
        )
    try:
        # Query user by email
        result = await db.execute(
            select(UserORM).where(UserORM.email == email.lower().strip())
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Convert to response model
        return UserDetails(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            subscription_tier=user.subscription_tier.value,
            is_verified=user.is_verified,
            is_active=user.is_active,
            created_at=user.created_at,
            lectures_generated_count=user.lectures_generated_count,
            total_audio_minutes=user.total_audio_minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Delete user account
    
    Phase 2a: Basic user deletion for testing
    Phase 2b will add proper authorization
    """
    try:
        # Find user
        result = await db.execute(select(UserORM).where(UserORM.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Delete user
        await db.delete(user)
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


# Database health check endpoint
@router.get("/system/health")
async def database_health():
    """
    Check database connection health
    """
    from models import check_database_health, get_database_info
    
    is_healthy = await check_database_health()
    db_info = get_database_info()
    
    return {
        "database_healthy": is_healthy,
        "database_info": db_info,
        "status": "healthy" if is_healthy else "unhealthy"
    }
