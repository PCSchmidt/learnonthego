"""
Authentication package for LearnOnTheGo
Provides JWT token management and password hashing
"""

# Use relative imports to avoid circular dependencies and path issues
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

__all__ = [
    "create_access_token",
    "verify_token", 
    "get_current_user",
    "get_current_active_user",
    "hash_password",
    "verify_password"
]
