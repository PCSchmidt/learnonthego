"""
API Key Management Service
Handles CRUD operations for user API keys with encryption
"""

from typing import Any, Dict, List, Optional
import inspect
import hashlib
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.lecture_orm import UserAPIKey, APIProvider
from models.user_orm import User
from services.encryption_service import create_encryption_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class APIKeyService:
    """Service for managing user API keys"""
    
    def __init__(self):
        self.encryption_service = create_encryption_service()

    async def _execute(self, db: Any, stmt):
        result = db.execute(stmt)
        if inspect.isawaitable(result):
            return await result
        return result

    async def _commit(self, db: Any) -> None:
        result = db.commit()
        if inspect.isawaitable(result):
            await result

    async def _rollback(self, db: Any) -> None:
        result = db.rollback()
        if inspect.isawaitable(result):
            await result

    async def _refresh(self, db: Any, obj: Any) -> None:
        result = db.refresh(obj)
        if inspect.isawaitable(result):
            await result
    
    async def store_api_key(
        self,
        db: Session,
        user_id: int,
        provider: APIProvider,
        api_key: str,
        key_name: Optional[str] = None
    ) -> UserAPIKey:
        """
        Store encrypted API key for user
        
        Args:
            db: Database session
            user_id: User ID
            provider: API provider (openrouter, elevenlabs)
            api_key: Plain text API key
            key_name: Optional friendly name
            
        Returns:
            Created UserAPIKey instance
        """
        try:
            # Encrypt the API key
            encrypted_key = self.encryption_service.encrypt_api_key(api_key, str(user_id))
            key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
            
            # Check if user already has a key for this provider
            existing_key_result = await self._execute(
                db,
                select(UserAPIKey).where(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider,
                ),
            )
            existing_key = existing_key_result.scalar_one_or_none()
            
            if existing_key:
                # Update existing key
                existing_key.encrypted_key = encrypted_key
                existing_key.key_hash = key_hash
                existing_key.key_name = key_name or existing_key.key_name
                existing_key.is_valid = True
                existing_key.validation_error = None
                existing_key.updated_at = datetime.utcnow()
                await self._commit(db)
                await self._refresh(db, existing_key)
                logger.info(f"Updated API key for user {user_id}, provider {provider.value}")
                return existing_key
            else:
                # Create new key
                db_api_key = UserAPIKey(
                    user_id=user_id,
                    provider=provider,
                    encrypted_key=encrypted_key,
                    key_hash=key_hash,
                    key_name=key_name or f"{provider.value.title()} API Key",
                    is_valid=True
                )
                db.add(db_api_key)
                await self._commit(db)
                await self._refresh(db, db_api_key)
                logger.info(f"Stored new API key for user {user_id}, provider {provider.value}")
                return db_api_key
                
        except Exception as e:
            await self._rollback(db)
            logger.error(f"Failed to store API key for user {user_id}: {str(e)}")
            raise
    
    async def get_api_key(
        self,
        db: Session,
        user_id: int,
        provider: APIProvider
    ) -> Optional[str]:
        """
        Retrieve and decrypt API key for user
        
        Args:
            db: Database session
            user_id: User ID
            provider: API provider
            
        Returns:
            Decrypted API key or None if not found
        """
        try:
            db_api_key_result = await self._execute(
                db,
                select(UserAPIKey).where(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider,
                    UserAPIKey.is_valid == True,
                ),
            )
            db_api_key = db_api_key_result.scalar_one_or_none()
            
            if not db_api_key:
                return None
            
            # Decrypt the API key
            decrypted_key = self.encryption_service.decrypt_api_key(
                db_api_key.encrypted_key,
                user_id
            )
            
            # Update last used timestamp
            db_api_key.last_used_at = datetime.utcnow()
            db_api_key.usage_count += 1
            await self._commit(db)
            
            return decrypted_key
            
        except Exception as e:
            logger.error(f"Failed to retrieve API key for user {user_id}, provider {provider.value}: {str(e)}")
            return None
    
    async def list_user_api_keys(
        self,
        db: Session,
        user_id: int
    ) -> List[UserAPIKey]:
        """
        List all API keys for user (without decrypting)
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of UserAPIKey instances
        """
        result = await self._execute(
            db,
            select(UserAPIKey)
            .where(UserAPIKey.user_id == user_id)
            .order_by(UserAPIKey.created_at.desc()),
        )
        return list(result.scalars().all())
    
    async def delete_api_key(
        self,
        db: Session,
        user_id: int,
        provider: APIProvider
    ) -> bool:
        """
        Delete API key for user
        
        Args:
            db: Database session
            user_id: User ID
            provider: API provider
            
        Returns:
            True if deleted, False if not found
        """
        try:
            db_api_key_result = await self._execute(
                db,
                select(UserAPIKey).where(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider,
                ),
            )
            db_api_key = db_api_key_result.scalar_one_or_none()
            
            if db_api_key:
                db.delete(db_api_key)
                await self._commit(db)
                logger.info(f"Deleted API key for user {user_id}, provider {provider.value}")
                return True
            
            return False
            
        except Exception as e:
            await self._rollback(db)
            logger.error(f"Failed to delete API key for user {user_id}: {str(e)}")
            raise
    
    async def validate_api_key(
        self,
        db: Session,
        user_id: int,
        provider: APIProvider,
        test_function = None
    ) -> bool:
        """
        Validate API key by testing it
        
        Args:
            db: Database session
            user_id: User ID
            provider: API provider
            test_function: Function to test the API key
            
        Returns:
            True if valid, False otherwise
        """
        try:
            api_key = await self.get_api_key(db, user_id, provider)
            if not api_key:
                return False
            
            # If no test function provided, just check if key exists
            if not test_function:
                return True
            
            # Test the API key
            is_valid = await test_function(api_key)
            
            # Update validation status in database
            db_api_key_result = await self._execute(
                db,
                select(UserAPIKey).where(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider,
                ),
            )
            db_api_key = db_api_key_result.scalar_one_or_none()
            
            if db_api_key:
                db_api_key.is_valid = is_valid
                db_api_key.last_validation_at = datetime.utcnow()
                if not is_valid:
                    db_api_key.validation_error = "API key validation failed"
                else:
                    db_api_key.validation_error = None
                await self._commit(db)
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Failed to validate API key for user {user_id}: {str(e)}")
            return False
    
    async def get_user_api_keys_status(
        self,
        db: Session,
        user_id: int
    ) -> Dict[str, Dict]:
        """
        Get status of all API keys for user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary mapping provider to key status
        """
        api_keys = await self.list_user_api_keys(db, user_id)
        
        status = {}
        for api_key in api_keys:
            status[api_key.provider.value] = {
                "has_key": True,
                "is_valid": api_key.is_valid,
                "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
                "last_validation_at": api_key.last_validation_at.isoformat() if api_key.last_validation_at else None,
                "validation_error": api_key.validation_error,
                "usage_count": api_key.usage_count,
                "key_name": api_key.key_name
            }
        
        # Add missing providers
        for provider in APIProvider:
            if provider.value not in status:
                status[provider.value] = {
                    "has_key": False,
                    "is_valid": False,
                    "last_used_at": None,
                    "last_validation_at": None,
                    "validation_error": None,
                    "usage_count": 0,
                    "key_name": None
                }
        
        return status


# Global service instance
_api_key_service = None

def get_api_key_service() -> APIKeyService:
    """Get global API key service instance"""
    global _api_key_service
    if _api_key_service is None:
        _api_key_service = APIKeyService()
    return _api_key_service
