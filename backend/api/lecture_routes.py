"""
Authenticated Lecture API Routes
Protected endpoints for lecture generation and management
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
 # Removed Session and AsyncSession imports to avoid FastAPI type inference issues
from sqlalchemy import select
from typing import List, Optional, Dict, Any
import json
import logging

from models.database import get_async_db
from models.user_orm import User
from models.lecture_orm import Lecture, LectureStatus, LectureSourceType, APIProvider
from models.lecture_models import LectureRequest, VoiceSettings
from auth.jwt_auth import get_current_user
from services.api_key_service import get_api_key_service
from services.lecture_service import create_lecture_service
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/lectures", tags=["lectures"])


@router.post("/generate", response_model=None)
async def generate_lecture_from_text(
    request: LectureRequest,
    background_tasks,
    current_user = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Generate audio lecture from text topic
    
    Requires user to have valid OpenRouter and ElevenLabs API keys
    """
    try:
        # Check if user has required API keys
        api_key_service = get_api_key_service()
        
        # Validate OpenRouter key
        openrouter_key = await api_key_service.get_api_key(
            db, current_user.id, APIProvider.OPENROUTER
        )
        if not openrouter_key:
            raise HTTPException(
                status_code=400,
                detail="OpenRouter API key required. Please add your API key in settings."
            )
        
        # Validate ElevenLabs key
        elevenlabs_key = await api_key_service.get_api_key(
            db, current_user.id, APIProvider.ELEVENLABS
        )
        if not elevenlabs_key:
            raise HTTPException(
                status_code=400,
                detail="ElevenLabs API key required. Please add your API key in settings."
            )
        
        # Check rate limits
        if not await _check_rate_limits(db, current_user):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Create lecture record
        lecture = Lecture(
            user_id=current_user.id,
            title=f"Lecture: {request.topic[:100]}...",
            topic=request.topic,
            difficulty=request.difficulty,
            duration_requested=request.duration,
            source_type=LectureSourceType.TEXT,
            custom_context=request.user_context,
            status=LectureStatus.PENDING,
            voice_provider=request.voice_settings.provider,
            voice_id=request.voice_settings.voice_id,
            voice_model=request.voice_settings.model_id,
            voice_settings=request.voice_settings.dict(),
            auto_delete_at=datetime.utcnow() + timedelta(days=30)
        )
        
        db.add(lecture)
        await db.commit()
        await db.refresh(lecture)
        
        # Start background lecture generation
        lecture_service = create_lecture_service()
        background_tasks.add_task(
            lecture_service.generate_lecture_background,
            lecture.id,
            openrouter_key,
            elevenlabs_key,
            db
        )
        
        logger.info(f"Started lecture generation for user {current_user.id}, lecture {lecture.id}")
        
        return {
            "lecture_id": lecture.id,
            "status": lecture.status.value,
            "message": "Lecture generation started. Check status for updates.",
            "estimated_completion": "2-5 minutes"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start lecture generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start lecture generation")


@router.post("/generate-pdf", response_model=None)
async def generate_lecture_from_pdf(
    background_tasks,
    file = File(...),
    duration = Form(...),
    difficulty = Form(...),
    voice_settings = Form(...),
    custom_topic = Form(None),
    current_user = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Generate audio lecture from PDF document
    
    Requires user to have valid OpenRouter and ElevenLabs API keys
    """
    try:
        # Validate form data
        if difficulty not in ['beginner', 'intermediate', 'advanced']:
            raise HTTPException(status_code=400, detail="Invalid difficulty level")
        
        if duration < 5 or duration > 60:
            raise HTTPException(status_code=400, detail="Duration must be between 5 and 60 minutes")
        
        # Parse voice settings
        try:
            voice_settings_dict = json.loads(voice_settings)
            voice_config = VoiceSettings(**voice_settings_dict)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid voice settings: {str(e)}")
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        if file.size and file.size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File size must be under 50MB")
        
        # Check if user has required API keys
        api_key_service = get_api_key_service()
        
        openrouter_key = await api_key_service.get_api_key(
            db, current_user.id, APIProvider.OPENROUTER
        )
        if not openrouter_key:
            raise HTTPException(
                status_code=400,
                detail="OpenRouter API key required. Please add your API key in settings."
            )
        
        elevenlabs_key = await api_key_service.get_api_key(
            db, current_user.id, APIProvider.ELEVENLABS
        )
        if not elevenlabs_key:
            raise HTTPException(
                status_code=400,
                detail="ElevenLabs API key required. Please add your API key in settings."
            )
        
        # Check rate limits
        if not await _check_rate_limits(db, current_user, is_pdf=True):
            raise HTTPException(
                status_code=429,
                detail="PDF upload rate limit exceeded. Please try again later."
            )
        
        # Create lecture record
        title = custom_topic or f"PDF Lecture: {file.filename}"
        lecture = Lecture(
            user_id=current_user.id,
            title=title,
            topic="", # Will be filled after PDF processing
            difficulty=difficulty,
            duration_requested=duration,
            source_type=LectureSourceType.PDF,
            source_file_name=file.filename,
            source_file_size=file.size,
            custom_context=custom_topic,
            status=LectureStatus.PENDING,
            voice_provider=voice_config.provider,
            voice_id=voice_config.voice_id,
            voice_model=voice_config.model_id,
            voice_settings=voice_config.dict(),
            auto_delete_at=datetime.utcnow() + timedelta(days=30)
        )
        
        db.add(lecture)
        await db.commit()
        await db.refresh(lecture)
        
        # Start background PDF processing and lecture generation
        lecture_service = create_lecture_service()
        background_tasks.add_task(
            lecture_service.generate_lecture_from_pdf_background,
            lecture.id,
            file,
            openrouter_key,
            elevenlabs_key,
            db
        )
        
        logger.info(f"Started PDF lecture generation for user {current_user.id}, lecture {lecture.id}")
        
        return {
            "lecture_id": lecture.id,
            "status": lecture.status.value,
            "message": "PDF processing and lecture generation started. Check status for updates.",
            "estimated_completion": "3-8 minutes"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start PDF lecture generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start PDF lecture generation")


@router.get("/", response_model=None)
async def list_user_lectures(
    skip = 0,
    limit = 20,
    status = None,
    current_user = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    List user's lectures with optional filtering
    """
    try:
        stmt = (
            select(Lecture)
            .where(Lecture.user_id == current_user.id)
            .order_by(Lecture.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if status:
            try:
                status_enum = LectureStatus(status)
                stmt = stmt.where(Lecture.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid status filter")
        result = await db.execute(stmt)
        lectures = result.scalars().all()
        return [lecture.to_dict() for lecture in lectures]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list lectures for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve lectures")


@router.get("/{lecture_id}", response_model=None)
async def get_lecture(
    lecture_id,
    current_user = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Get specific lecture details
    """
    try:
        stmt = select(Lecture).where(
            Lecture.id == lecture_id,
            Lecture.user_id == current_user.id
        )
        result = await db.execute(stmt)
        lecture = result.scalars().first()
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        return lecture.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get lecture {lecture_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve lecture")


@router.put("/{lecture_id}/favorite", response_model=None)
async def toggle_lecture_favorite(
    lecture_id,
    current_user = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Toggle lecture favorite status
    """
    try:
        stmt = select(Lecture).where(
            Lecture.id == lecture_id,
            Lecture.user_id == current_user.id
        )
        result = await db.execute(stmt)
        lecture = result.scalars().first()
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        lecture.is_favorited = not lecture.is_favorited
        # If favorited, remove auto-delete
        if lecture.is_favorited:
            lecture.auto_delete_at = None
        else:
            # If unfavorited, set auto-delete to 30 days from now
            lecture.auto_delete_at = datetime.utcnow() + timedelta(days=30)
        await db.commit()
        await db.refresh(lecture)
        return {
            "lecture_id": lecture.id,
            "is_favorited": lecture.is_favorited,
            "auto_delete_at": lecture.auto_delete_at.isoformat() if lecture.auto_delete_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle favorite for lecture {lecture_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to toggle favorite")


@router.delete("/{lecture_id}", response_model=None)
async def delete_lecture(
    lecture_id,
    current_user = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Delete a lecture
    """
    try:
        stmt = select(Lecture).where(
            Lecture.id == lecture_id,
            Lecture.user_id == current_user.id
        )
        result = await db.execute(stmt)
        lecture = result.scalars().first()
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        # TODO: Delete audio file from Cloudinary
        # lecture_service = get_lecture_service()
        # await lecture_service.delete_audio_file(lecture.audio_file_url)
        await db.delete(lecture)
        await db.commit()
        logger.info(f"Deleted lecture {lecture_id} for user {current_user.id}")
        return {"message": "Lecture deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete lecture {lecture_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete lecture")


@router.post("/{lecture_id}/play", response_model=None)
async def record_lecture_play(
    lecture_id,
    current_user = Depends(get_current_user),
    db = Depends(get_async_db)
):
    """
    Record that user played a lecture
    """
    try:
        stmt = select(Lecture).where(
            Lecture.id == lecture_id,
            Lecture.user_id == current_user.id
        )
        result = await db.execute(stmt)
        lecture = result.scalars().first()
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        lecture.play_count += 1
        lecture.last_played_at = datetime.utcnow()
        await db.commit()
        return {
            "lecture_id": lecture.id,
            "play_count": lecture.play_count,
            "last_played_at": lecture.last_played_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record play for lecture {lecture_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to record play")


# Helper functions

async def _check_rate_limits(db, user, is_pdf = False):
    """
    Check if user is within rate limits
    
    Args:
        db: Database session
        user: Current user
        is_pdf: Whether this is a PDF upload
        
    Returns:
        True if within limits, False otherwise
    """
    try:
        # Check hourly limits
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        stmt = select(Lecture).where(
            Lecture.user_id == user.id,
            Lecture.created_at >= one_hour_ago
        )
        result = await db.execute(stmt)
        recent_lectures = len(result.scalars().all())
        # Rate limits
        hourly_limit = 10  # 10 lectures per hour
        pdf_hourly_limit = 5  # 5 PDF uploads per hour
        if is_pdf and recent_lectures >= pdf_hourly_limit:
            return False
        elif not is_pdf and recent_lectures >= hourly_limit:
            return False
        # Check monthly limits for free users
        if not user.is_premium:
            one_month_ago = datetime.utcnow() - timedelta(days=30)
            stmt_month = select(Lecture).where(
                Lecture.user_id == user.id,
                Lecture.created_at >= one_month_ago
            )
            result_month = await db.execute(stmt_month)
            monthly_lectures = len(result_month.scalars().all())
            if monthly_lectures >= user.monthly_lecture_limit:
                return False
        return True
    except Exception as e:
        logger.error(f"Error checking rate limits for user {user.id}: {str(e)}")
        return False
