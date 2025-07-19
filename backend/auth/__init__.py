"""
Authentication package for LearnOnTheGo
Provides JWT token management and password hashing
"""

# Import JWT functions with fallback
try:
    from .jwt_handler import (
        create_access_token,
        verify_token,
        get_current_user,
        get_current_active_user
    )
except ImportError:
    from auth.jwt_handler import (
        create_access_token,
        verify_token,
        get_current_user,
        get_current_active_user
    )

# Import password functions with fallback
try:
    from .password_utils import (
        hash_password,
        verify_password
    )
except ImportError:
    try:
        from auth.password_utils import (
            hash_password,
            verify_password
        )
    except ImportError:
        # If password_utils still doesn't exist, create stub functions
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        def hash_password(password: str) -> str:
            """Hash a password using bcrypt"""
            return pwd_context.hash(password)
        
        def verify_password(plain_password: str, hashed_password: str) -> bool:
            """Verify a password against its hash"""
            return pwd_context.verify(plain_password, hashed_password)

__all__ = [
    "create_access_token",
    "verify_token", 
    "get_current_user",
    "get_current_active_user",
    "hash_password",
    "verify_password"
]
