"""
Authentication package for LearnOnTheGo
Provides JWT token management and password hashing
"""

# Use both relative and absolute imports as fallback
try:
    # Try relative imports first
    from .jwt_handler import (
        create_access_token,
        verify_token,
        get_current_user,
        get_current_active_user
    )
    
    from .password_utils import (
        hash_password,
        verify_password
    )
except ImportError:
    # Fallback to absolute imports
    from auth.jwt_handler import (
        create_access_token,
        verify_token,
        get_current_user,
        get_current_active_user
    )
    
    from auth.password_utils import (
        hash_password,
        verify_password
    )

__all__ = [
    "create_access_token",
    "verify_token", 
    "get_current_user",
    "get_current_active_user",
    "hash_password",
    "verify_password"
]
