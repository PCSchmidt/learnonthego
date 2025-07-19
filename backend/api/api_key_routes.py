"""
API Key Management Routes
Protected endpoints for managing user API keys
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from typing import Dict, Any, List
from pydantic import BaseModel, Field
import logging

from models.database import get_async_db
from models.user_orm import User
from models.lecture_orm import APIProvider
from auth import get_current_user
from services.api_key_service import get_api_key_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/api-keys", tags=["api-keys"])


class APIKeyRequest(BaseModel):
    """Request model for storing API key"""
    provider: str = Field(..., description="API provider (openrouter, elevenlabs)")
    api_key: str = Field(..., min_length=10, description="API key")
    key_name: str = Field(None, description="Friendly name for the key")
    
    class Config:
        schema_extra = {
            "example": {
                "provider": "openrouter",
                "api_key": "sk-or-v1-abc123...",
                "key_name": "My OpenRouter Key"
            }
        }


@router.post("/", response_model=Dict[str, Any])
async def store_api_key(
    request: APIKeyRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Store encrypted API key for user
    
    Securely stores user's API key with AES-256 encryption
    """
    try:
        # Validate provider
        try:
            provider = APIProvider(request.provider)
        except ValueError:
            valid_providers = [p.value for p in APIProvider]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Must be one of: {valid_providers}"
            )
        
        # Store the API key
        api_key_service = get_api_key_service()
        stored_key = await api_key_service.store_api_key(
            db=db,
            user_id=current_user.id,
            provider=provider,
            api_key=request.api_key,
            key_name=request.key_name
        )
        
        logger.info(f"Stored API key for user {current_user.id}, provider {provider.value}")
        
        return {
            "message": "API key stored successfully",
            "provider": provider.value,
            "key_name": stored_key.key_name,
            "created_at": stored_key.created_at.isoformat(),
            "is_valid": stored_key.is_valid
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to store API key for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to store API key")


@router.get("/", response_model=Dict[str, Any])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    List user's API keys (without exposing the actual keys)
    
    Returns status and metadata for all API keys
    """
    try:
        api_key_service = get_api_key_service()
        api_keys_status = await api_key_service.get_user_api_keys_status(
            db=db,
            user_id=current_user.id
        )
        
        return {
            "api_keys": api_keys_status,
            "total_keys": sum(1 for status in api_keys_status.values() if status["has_key"]),
            "valid_keys": sum(1 for status in api_keys_status.values() if status["is_valid"])
        }
        
    except Exception as e:
        logger.error(f"Failed to list API keys for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve API keys")


@router.get("/status", response_model=Dict[str, Any])
async def get_api_keys_status(
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Get status of required API keys for lecture generation
    
    Returns whether user has all required keys configured
    """
    try:
        api_key_service = get_api_key_service()
        
        # Check for required providers
        openrouter_key = await api_key_service.get_api_key(
            db, current_user.id, APIProvider.OPENROUTER
        )
        elevenlabs_key = await api_key_service.get_api_key(
            db, current_user.id, APIProvider.ELEVENLABS
        )
        
        can_generate_lectures = bool(openrouter_key and elevenlabs_key)
        
        return {
            "can_generate_lectures": can_generate_lectures,
            "missing_keys": [
                provider for provider, has_key in [
                    ("openrouter", bool(openrouter_key)),
                    ("elevenlabs", bool(elevenlabs_key))
                ] if not has_key
            ],
            "setup_complete": can_generate_lectures
        }
        
    except Exception as e:
        logger.error(f"Failed to get API keys status for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get API keys status")


@router.delete("/{provider}", response_model=Dict[str, Any])
async def delete_api_key(
    provider: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Delete API key for specific provider
    """
    try:
        # Validate provider
        try:
            provider_enum = APIProvider(provider)
        except ValueError:
            valid_providers = [p.value for p in APIProvider]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Must be one of: {valid_providers}"
            )
        
        # Delete the API key
        api_key_service = get_api_key_service()
        deleted = await api_key_service.delete_api_key(
            db=db,
            user_id=current_user.id,
            provider=provider_enum
        )
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"No API key found for provider {provider}"
            )
        
        logger.info(f"Deleted API key for user {current_user.id}, provider {provider}")
        
        return {
            "message": f"API key for {provider} deleted successfully",
            "provider": provider
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete API key for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete API key")


@router.post("/{provider}/validate", response_model=Dict[str, Any])
async def validate_api_key(
    provider: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Validate API key by testing it with the provider
    """
    try:
        # Validate provider
        try:
            provider_enum = APIProvider(provider)
        except ValueError:
            valid_providers = [p.value for p in APIProvider]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Must be one of: {valid_providers}"
            )
        
        # TODO: Implement actual API key validation
        # For now, just check if key exists
        api_key_service = get_api_key_service()
        is_valid = await api_key_service.validate_api_key(
            db=db,
            user_id=current_user.id,
            provider=provider_enum
        )
        
        if not is_valid:
            return {
                "is_valid": False,
                "provider": provider,
                "message": "API key not found or invalid"
            }
        
        return {
            "is_valid": True,
            "provider": provider,
            "message": "API key is valid"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate API key for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to validate API key")


@router.get("/setup-guide", response_model=Dict[str, Any])
async def get_setup_guide(
    current_user: User = Depends(get_current_user)
):
    """
    Get setup guide for configuring API keys
    
    Returns instructions for obtaining and configuring API keys
    """
    return {
        "providers": {
            "openrouter": {
                "name": "OpenRouter",
                "description": "Required for AI-powered lecture generation",
                "signup_url": "https://openrouter.ai/",
                "instructions": [
                    "1. Sign up at openrouter.ai",
                    "2. Go to the API Keys section",
                    "3. Create a new API key",
                    "4. Copy the key (starts with 'sk-or-v1-')",
                    "5. Add credits to your account ($5 minimum)",
                    "6. Paste the key in the form above"
                ],
                "cost_estimate": "$0.01-0.05 per lecture",
                "key_format": "sk-or-v1-..."
            },
            "elevenlabs": {
                "name": "ElevenLabs",
                "description": "Required for high-quality text-to-speech",
                "signup_url": "https://elevenlabs.io/",
                "instructions": [
                    "1. Sign up at elevenlabs.io",
                    "2. Go to Profile → API Keys",
                    "3. Copy your API key",
                    "4. Paste the key in the form above"
                ],
                "cost_estimate": "$0.30 per 1000 characters (~$3-5 per lecture)",
                "free_tier": "10,000 characters per month",
                "key_format": "sk-..."
            }
        },
        "cost_estimates": {
            "text_lecture": "$3.05-5.05 per lecture",
            "pdf_lecture": "$3.10-5.10 per lecture",
            "monthly_free_tier": "Up to $30-50 for 10 lectures"
        },
        "setup_steps": [
            "1. Get OpenRouter API key (for AI generation)",
            "2. Get ElevenLabs API key (for voice synthesis)",
            "3. Add both keys using the form above",
            "4. Start generating lectures!"
        ]
    }
