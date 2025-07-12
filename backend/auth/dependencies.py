"""
Authentication dependencies for FastAPI routes
Handles JWT token validation and user authentication
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import os
from datetime import datetime
from typing import Optional

from models.user_models import User

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

# Security scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        User object if token is valid
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    
    try:
        # Extract token
        token = credentials.credentials
        
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract user info
        user_id = payload.get("user_id")
        email = payload.get("email")
        
        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create user object (in production, this would fetch from database)
        user = User(
            id=user_id,
            email=email,
            created_at=datetime.utcnow(),
            subscription_tier=payload.get("subscription_tier", "free"),
            openrouter_api_key=payload.get("openrouter_api_key"),
            elevenlabs_api_key=payload.get("elevenlabs_api_key"),
            preferences=payload.get("preferences", {})
        )
        
        return user
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_access_token(user_data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Create JWT access token for user
    
    Args:
        user_data: User data to encode in token
        expires_delta: Token expiration time in seconds
        
    Returns:
        Encoded JWT token string
    """
    
    try:
        # Set expiration time
        if expires_delta:
            expire = datetime.utcnow().timestamp() + expires_delta
        else:
            expire = datetime.utcnow().timestamp() + (24 * 60 * 60)  # 24 hours
        
        # Create payload
        payload = {
            **user_data,
            "exp": expire,
            "iat": datetime.utcnow().timestamp()
        }
        
        # Encode token
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
        
    except Exception as e:
        raise Exception(f"Failed to create access token: {str(e)}")


def verify_token(token: str) -> dict:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        Exception: If token is invalid
    """
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        raise Exception(f"Invalid token: {str(e)}")


class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass


# Optional dependency for routes that can work with or without auth
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise
    Used for routes that can work with or without authentication
    """
    
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
