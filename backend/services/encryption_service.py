"""
Encryption Service for LearnOnTheGo
Handles secure encryption/decryption of user API keys using AES-256
"""

import os
import base64
import hashlib
from typing import Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionService:
    """Service for encrypting and decrypting sensitive user data"""
    
    def __init__(self, master_key: str = None):
        """
        Initialize encryption service
        
        Args:
            master_key: Master encryption key (uses env var if not provided)
        """
        self.master_key = master_key or os.getenv("ENCRYPTION_MASTER_KEY")
        if not self.master_key:
            # For development, create a default key with warning
            self.master_key = "dev-encryption-key-not-for-production-123456789012"
            print("WARNING: Using default encryption key for development. Set ENCRYPTION_MASTER_KEY for production.")
    
    def encrypt_api_key(self, api_key: str, user_id: str) -> str:
        """
        Encrypt user's API key with user-specific salt
        
        Args:
            api_key: The API key to encrypt
            user_id: User identifier for unique salt generation
            
        Returns:
            Base64 encoded encrypted API key
        """
        try:
            # Generate user-specific salt
            salt = self._generate_user_salt(user_id)
            
            # Derive encryption key from master key + salt
            encryption_key = self._derive_key(salt)
            
            # Create Fernet cipher
            cipher = Fernet(encryption_key)
            
            # Encrypt the API key
            encrypted_data = cipher.encrypt(api_key.encode('utf-8'))
            
            # Return base64 encoded result
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Failed to encrypt API key: {str(e)}")
    
    def decrypt_api_key(self, encrypted_api_key: str, user_id: str) -> str:
        """
        Decrypt user's API key with user-specific salt
        
        Args:
            encrypted_api_key: Base64 encoded encrypted API key
            user_id: User identifier for salt generation
            
        Returns:
            Decrypted API key
        """
        try:
            # Generate same user-specific salt
            salt = self._generate_user_salt(user_id)
            
            # Derive same encryption key
            encryption_key = self._derive_key(salt)
            
            # Create Fernet cipher
            cipher = Fernet(encryption_key)
            
            # Decode from base64 and decrypt
            encrypted_data = base64.b64decode(encrypted_api_key.encode('utf-8'))
            decrypted_data = cipher.decrypt(encrypted_data)
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Failed to decrypt API key: {str(e)}")
    
    def _generate_user_salt(self, user_id: str) -> bytes:
        """Generate consistent salt for a user"""
        # Use user_id + master_key to generate consistent salt
        salt_source = f"{user_id}:{self.master_key}".encode('utf-8')
        return hashlib.sha256(salt_source).digest()[:16]  # 16 bytes for salt
    
    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key from master key and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 32 bytes = 256 bits
            salt=salt,
            iterations=100000,  # Strong iteration count
        )
        key = kdf.derive(self.master_key.encode('utf-8'))
        return base64.urlsafe_b64encode(key)
    
    def validate_encryption_setup(self) -> bool:
        """Test encryption/decryption to ensure setup is working"""
        try:
            test_data = "test_api_key_12345"
            test_user = "test_user_id"
            
            # Encrypt test data
            encrypted = self.encrypt_api_key(test_data, test_user)
            
            # Decrypt and verify
            decrypted = self.decrypt_api_key(encrypted, test_user)
            
            return decrypted == test_data
            
        except Exception:
            return False
    
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """
        Hash password with salt for user authentication
        
        Args:
            password: Plain text password
            salt: Optional salt (generates new one if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = base64.b64encode(os.urandom(32)).decode('utf-8')
        
        # Use PBKDF2 for password hashing
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode('utf-8'),
            iterations=100000,
        )
        
        hashed = kdf.derive(password.encode('utf-8'))
        hashed_b64 = base64.b64encode(hashed).decode('utf-8')
        
        return hashed_b64, salt
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password to verify
            hashed_password: Stored hash
            salt: Salt used for hashing
            
        Returns:
            True if password matches
        """
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return computed_hash == hashed_password
        except Exception:
            return False


# Service instance factory
def create_encryption_service(master_key: str = None) -> EncryptionService:
    """Create encryption service instance"""
    return EncryptionService(master_key)
