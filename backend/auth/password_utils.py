"""
Password hashing and verification utilities.

Uses pbkdf2_sha256 for new hashes to avoid bcrypt backend incompatibilities
on newer Python environments while preserving verification of legacy bcrypt
hashes that may already exist in the database.
"""

from passlib.context import CryptContext

# Prefer pbkdf2 for new hashes; keep bcrypt for backward verification.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    default="pbkdf2_sha256",
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password to hash
    
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hashed password
    
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)
