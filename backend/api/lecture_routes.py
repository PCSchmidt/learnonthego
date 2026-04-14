"""
Authenticated Lecture API Routes
Protected endpoints for lecture generation and management
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
 # Removed Session and AsyncSession imports to avoid FastAPI type inference issues
from sqlalchemy import select
from typing import List, Optional, Dict, Any, NoReturn
import json
import logging
import os
import tempfile
import asyncio
import socket
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path

from models.database import get_async_db
from models.user_orm import User
from models.lecture_orm import Lecture, LectureStatus, LectureSourceType, APIProvider, UserAPIKey
from models.lecture_models import LectureRequest, VoiceSettings
from auth import get_current_user
from services.api_key_service import get_api_key_service
from services.lecture_service import create_lecture_service
from services.pipeline_v2 import create_document_pipeline_v2, v2_pipeline_enabled
from services.encryption_service import create_encryption_service
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/lectures", tags=["lectures"])

SOURCE_INTAKE_CONTRACT_VERSION = "v1a"
SUPPORTED_SOURCE_TYPES_V1A = {"text", "txt", "md", "pdf"}
SUPPORTED_UPLOAD_EXTENSIONS_V1A = {".txt", ".md", ".pdf"}
MAX_TEXT_FILE_BYTES = 2 * 1024 * 1024
MAX_PDF_FILE_BYTES = 50 * 1024 * 1024
MAX_URL_TEXT_CHARS = 60_000
SOURCE_INTAKE_ERROR_SCHEMA = "source-intake-error-v1"
URL_DIAGNOSTICS_SCHEMA = "url-diagnostics-v1"


def _url_ingestion_v1_enabled() -> bool:
    return os.getenv("ENABLE_URL_INGESTION_V1", "false").lower() == "true"


def _supported_source_types_v1a() -> List[str]:
    supported = set(SUPPORTED_SOURCE_TYPES_V1A)
    if _url_ingestion_v1_enabled():
        supported.add("url")
    return sorted(supported)


def _validation_hint_v1a() -> str:
    if _url_ingestion_v1_enabled():
        return (
            "Supported source_type values for v1a are: text, txt, md, pdf, url. "
            "URL source intake currently supports web pages that pass URL diagnostics as ready."
        )
    return (
        "Supported source_type values for v1a are: text, txt, md, pdf. "
        "YouTube/podcast/url ingestion is intentionally deferred to the next slice."
    )


def _raise_source_intake_error(
    *,
    code: str,
    message: str,
    status_code: int = 400,
    field: Optional[str] = None,
    hint: Optional[str] = None,
    max_bytes: Optional[int] = None,
) -> NoReturn:
    detail: Dict[str, Any] = {
        "schema": SOURCE_INTAKE_ERROR_SCHEMA,
        "code": code,
        "message": message,
        "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
        "supported_source_types": _supported_source_types_v1a(),
    }
    if field:
        detail["field"] = field
    if hint:
        detail["hint"] = hint
    if max_bytes is not None:
        detail["max_bytes"] = max_bytes

    raise HTTPException(status_code=status_code, detail=detail)


def _normalize_source_type_v1a(source_type: Optional[str]) -> Optional[str]:
    if source_type is None:
        return None
    normalized = source_type.strip().lower()
    if not normalized:
        return None
    if normalized not in _supported_source_types_v1a():
        _raise_source_intake_error(
            code="unsupported_source_type",
            field="source_type",
            message=f"source_type '{normalized}' is not supported in v1a.",
            hint=_validation_hint_v1a(),
        )
    return normalized


def _extract_text_from_html(content: str) -> str:
    without_scripts = re.sub(r"<script[^>]*>.*?</script>", " ", content, flags=re.IGNORECASE | re.DOTALL)
    without_styles = re.sub(r"<style[^>]*>.*?</style>", " ", without_scripts, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", without_styles)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _fetch_url_source_text(source_uri: str, max_chars: int = MAX_URL_TEXT_CHARS) -> str:
    request = Request(source_uri, method="GET", headers={"User-Agent": "LearnOnTheGo/url-intake"})
    with urlopen(request, timeout=8) as response:
        raw_bytes = response.read()
        content_type = (response.headers.get("Content-Type") or "").lower()

    if "text" not in content_type and "html" not in content_type and "json" not in content_type:
        raise ValueError("URL content type is not text-based and cannot be ingested.")

    decoded = raw_bytes.decode("utf-8", errors="ignore")
    extracted = _extract_text_from_html(decoded)
    if not extracted:
        raise ValueError("URL content extraction returned empty text.")

    return extracted[:max_chars]


async def _diagnose_url_readiness_v1(source_uri: str) -> Dict[str, Any]:
    parsed = urlparse(source_uri)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {
            "success": False,
            "schema": URL_DIAGNOSTICS_SCHEMA,
            "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
            "source_uri": source_uri,
            "source_class": "unknown",
            "outcome": "unsupported",
            "diagnostics": {
                "code": "unsupported",
                "message": "Invalid URL format. Use a full http(s) URL.",
                "retryable": False,
            },
        }

    availability = await asyncio.to_thread(_probe_url_availability, source_uri)
    if not availability.get("reachable"):
        return {
            "success": False,
            "schema": URL_DIAGNOSTICS_SCHEMA,
            "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
            "source_uri": source_uri,
            "source_class": _classify_url_source(source_uri),
            "outcome": "unreachable",
            "diagnostics": {
                "code": "unreachable",
                "message": "URL could not be reached from the service. Check URL and try again.",
                "retryable": True,
                "status_code": availability.get("status_code"),
            },
        }

    source_class = _classify_url_source(source_uri)
    if source_class == "video":
        return {
            "success": False,
            "schema": URL_DIAGNOSTICS_SCHEMA,
            "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
            "source_uri": source_uri,
            "source_class": source_class,
            "outcome": "no_transcript",
            "diagnostics": {
                "code": "no_transcript",
                "message": "Video transcript ingestion is not enabled in this slice yet.",
                "retryable": False,
                "status_code": availability.get("status_code"),
            },
        }

    if source_class in {"podcast", "audio"}:
        return {
            "success": False,
            "schema": URL_DIAGNOSTICS_SCHEMA,
            "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
            "source_uri": source_uri,
            "source_class": source_class,
            "outcome": "unsupported",
            "diagnostics": {
                "code": "unsupported",
                "message": "Podcast/audio URL ingestion is deferred to the next slice.",
                "retryable": False,
                "status_code": availability.get("status_code"),
            },
        }

    return {
        "success": True,
        "schema": URL_DIAGNOSTICS_SCHEMA,
        "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
        "source_uri": source_uri,
        "source_class": source_class,
        "outcome": "ready",
        "diagnostics": {
            "code": "ready",
            "message": "URL is reachable and ready for upcoming web-source ingestion flow.",
            "retryable": False,
            "status_code": availability.get("status_code"),
        },
    }


async def _resolve_source_text_v1a(
    *,
    document_text: Optional[str],
    file: Optional[UploadFile],
    source_uri: Optional[str],
    source_type: Optional[str],
) -> Dict[str, str]:
    normalized_source_type = _normalize_source_type_v1a(source_type)

    has_text = bool(document_text and document_text.strip())
    has_file = file is not None
    has_url = bool(source_uri and source_uri.strip())
    if int(has_text) + int(has_file) + int(has_url) != 1:
        _raise_source_intake_error(
            code="invalid_source_input_combination",
            field="document_text|file|source_uri",
            message="Provide exactly one input source: document_text, file, or source_uri.",
        )

    if has_text:
        text_value = (document_text or "").strip()
        if normalized_source_type and normalized_source_type != "text":
            _raise_source_intake_error(
                code="source_type_input_mismatch",
                field="source_type",
                message=f"source_type '{normalized_source_type}' does not match document_text input.",
            )

        return {
            "source_text": text_value,
            "source_name": "pasted_text",
            "source_type": "text",
        }

    upload_file = file
    if has_url:
        cleaned_uri = (source_uri or "").strip()
        if normalized_source_type and normalized_source_type != "url":
            _raise_source_intake_error(
                code="source_type_input_mismatch",
                field="source_type",
                message=f"source_type '{normalized_source_type}' does not match source_uri input.",
            )
        if not _url_ingestion_v1_enabled():
            _raise_source_intake_error(
                code="url_ingestion_disabled",
                field="source_uri",
                message="URL ingestion is disabled. Set ENABLE_URL_INGESTION_V1=true to enable ready URL generation.",
                hint="Run URL diagnostics and enable the URL ingestion feature flag for ready URLs.",
            )

        diagnostics = await _diagnose_url_readiness_v1(cleaned_uri)
        if diagnostics.get("outcome") != "ready":
            _raise_source_intake_error(
                code="url_not_ready",
                field="source_uri",
                message=diagnostics.get("diagnostics", {}).get("message", "URL is not ready for ingestion."),
                hint="Run URL diagnostics and only submit URLs with outcome 'ready'.",
            )

        try:
            fetched_text = await asyncio.to_thread(_fetch_url_source_text, cleaned_uri)
        except Exception as exc:
            _raise_source_intake_error(
                code="url_fetch_failed",
                field="source_uri",
                message=f"Failed to fetch URL content: {str(exc)}",
                hint="Ensure the URL is publicly reachable and returns text-based content.",
            )

        if not fetched_text.strip():
            _raise_source_intake_error(
                code="empty_url_content",
                field="source_uri",
                message="URL content extraction returned empty text.",
                hint="Use a content-rich article URL and re-run diagnostics.",
            )

        return {
            "source_text": fetched_text,
            "source_name": cleaned_uri,
            "source_type": "url",
        }

    if upload_file is None:
        _raise_source_intake_error(
            code="invalid_source_input_combination",
            field="document_text|file|source_uri",
            message="Provide exactly one input source: document_text, file, or source_uri.",
        )

    file_name = (upload_file.filename or "upload").strip()
    extension = Path(file_name).suffix.lower()
    if extension not in SUPPORTED_UPLOAD_EXTENSIONS_V1A:
        _raise_source_intake_error(
            code="unsupported_file_extension",
            field="file",
            message=(
                "Unsupported file type. v1a supports uploads: .txt, .md, .pdf. "
                "YouTube/podcast/url ingestion is deferred to the next slice."
            ),
        )

    inferred_type = extension.lstrip(".")
    if normalized_source_type and normalized_source_type != inferred_type:
        _raise_source_intake_error(
            code="source_type_input_mismatch",
            field="source_type",
            message=f"source_type '{normalized_source_type}' does not match uploaded file type '{inferred_type}'.",
        )

    raw_bytes = await upload_file.read()
    if extension in {".txt", ".md"}:
        if len(raw_bytes) > MAX_TEXT_FILE_BYTES:
            _raise_source_intake_error(
                code="file_too_large",
                field="file",
                message=f"Text file size must be under {MAX_TEXT_FILE_BYTES // (1024 * 1024)}MB.",
                max_bytes=MAX_TEXT_FILE_BYTES,
            )

        try:
            decoded = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            _raise_source_intake_error(
                code="invalid_text_encoding",
                field="file",
                message="Text and markdown uploads must be UTF-8 encoded.",
            )

        if not decoded.strip():
            _raise_source_intake_error(
                code="empty_text_content",
                field="file",
                message="Uploaded text content is empty.",
            )

        return {
            "source_text": decoded.strip(),
            "source_name": file_name,
            "source_type": inferred_type,
        }

    if len(raw_bytes) > MAX_PDF_FILE_BYTES:
        _raise_source_intake_error(
            code="file_too_large",
            field="file",
            message=f"PDF file size must be under {MAX_PDF_FILE_BYTES // (1024 * 1024)}MB.",
            max_bytes=MAX_PDF_FILE_BYTES,
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(raw_bytes)
        tmp_path = tmp.name

    try:
        pdf_result = await create_document_pipeline_v2().pdf_service.extract_and_process(tmp_path)
        if not pdf_result.get("success"):
            _raise_source_intake_error(
                code="pdf_parse_failed",
                field="file",
                message=str(pdf_result.get("error", "PDF parsing failed")),
            )

        processed_content = str(pdf_result.get("processed_content", "")).strip()
        if not processed_content:
            _raise_source_intake_error(
                code="pdf_parse_failed",
                field="file",
                message="PDF parsing produced empty content.",
            )

        return {
            "source_text": processed_content,
            "source_name": file_name,
            "source_type": inferred_type,
        }
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def _build_v2_dry_run_response(
    *,
    source: str,
    source_type: str,
    duration: int,
    difficulty: str,
    llm_provider: str,
    llm_model: Optional[str],
    tts_provider: str,
    key_source: str,
) -> Dict[str, Any]:
    """Return a stable response contract without invoking paid generation."""
    return {
        "success": True,
        "dry_run": True,
        "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
        "source": source,
        "source_type": source_type,
        "duration": duration,
        "difficulty": difficulty,
        "key_source": key_source,
        "title": "Dry Run Lecture Contract",
        "script": "Dry run mode validates contract only. No LLM/TTS generation executed.",
        "llm": {
            "provider": llm_provider,
            "model": llm_model or "dry-run",
            "usage": {},
        },
        "audio": {
            "provider": tts_provider,
            "model": "dry-run",
            "file_path": "",
            "bytes_written": 0,
            "metadata": {"skipped": True},
        },
    }


def _classify_url_source(source_uri: str) -> str:
    parsed = urlparse(source_uri)
    host = (parsed.netloc or "").lower()
    path = (parsed.path or "").lower()

    if any(domain in host for domain in ["youtube.com", "youtu.be", "vimeo.com"]):
        return "video"
    if any(domain in host for domain in ["spotify.com", "soundcloud.com", "podcasts.apple.com"]):
        return "podcast"
    if any(path.endswith(ext) for ext in [".mp3", ".wav", ".m4a", ".aac"]):
        return "audio"
    return "web"


def _probe_url_availability(source_uri: str) -> Dict[str, Any]:
    request = Request(source_uri, method="GET", headers={"User-Agent": "LearnOnTheGo/diagnostics"})
    try:
        with urlopen(request, timeout=5) as response:
            return {"reachable": True, "status_code": getattr(response, "status", 200)}
    except HTTPError as err:
        # Auth-gated and method-restricted URLs are still reachable from a diagnostics perspective.
        if err.code in {401, 403, 405}:
            return {"reachable": True, "status_code": err.code}
        return {"reachable": False, "status_code": err.code, "error": str(err)}
    except (URLError, TimeoutError, socket.timeout) as err:
        return {"reachable": False, "status_code": None, "error": str(err)}


@router.post("/url-diagnostics-v1", response_model=None)
async def diagnose_source_url_v1(
    source_uri: str = Form(...),
    current_user = Depends(get_current_user),
):
    """Diagnose URL ingestion readiness with stable, actionable outcomes for frontend UX."""
    return await _diagnose_url_readiness_v1((source_uri or "").strip())


@router.post("/generate-document-v2", response_model=None)
async def generate_document_audio_v2(
    background_tasks: BackgroundTasks,
    source_type: Optional[str] = Form(None),
    document_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    source_uri: Optional[str] = Form(None),
    duration: int = Form(10),
    difficulty: str = Form("intermediate"),
    llm_provider: str = Form("openrouter"),
    llm_model: Optional[str] = Form(None),
    tts_provider: str = Form("openai"),
    context: Optional[str] = Form(None),
    voice_id: Optional[str] = Form(None),
    dry_run: bool = Form(False),
    current_user = Depends(get_current_user),
):
    """Feature-flagged V2 path: document -> script -> audio via pluggable providers."""
    if not v2_pipeline_enabled():
        raise HTTPException(
            status_code=404,
            detail="V2 pipeline is disabled. Set ENABLE_V2_PIPELINE=true to enable.",
        )

    if difficulty not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty level")

    if duration < 5 or duration > 60:
        raise HTTPException(status_code=400, detail="Duration must be between 5 and 60 minutes")

    source_input = await _resolve_source_text_v1a(
        document_text=document_text,
        file=file,
        source_uri=source_uri,
        source_type=source_type,
    )

    source_text = source_input["source_text"]
    source_name = source_input["source_name"]
    normalized_source_type = source_input["source_type"]

    if dry_run:
        return _build_v2_dry_run_response(
            source=source_name,
            source_type=normalized_source_type,
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            key_source="environment",
        )

    try:
        pipeline = create_document_pipeline_v2()
        result = await pipeline.run(
            document_text=source_text,
            duration_minutes=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            context=context,
            voice_id=voice_id,
        )

        logger.info(
            "V2 generation completed for user %s with llm=%s tts=%s source=%s",
            current_user.id,
            llm_provider,
            tts_provider,
            source_name,
        )
        return {
            "success": True,
            "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
            "source": source_name,
            "source_type": normalized_source_type,
            "duration": duration,
            "difficulty": difficulty,
            **result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("V2 generation failed for user %s: %s", current_user.id, str(e))
        raise HTTPException(status_code=500, detail="V2 generation failed")


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


async def _get_user_api_key(db, user_id: int, provider: APIProvider) -> Optional[str]:
    """Fetch and decrypt a user's provider key from encrypted storage."""
    result = await db.execute(
        select(UserAPIKey).where(
            UserAPIKey.user_id == user_id,
            UserAPIKey.provider == provider,
            UserAPIKey.is_valid == True,
        )
    )
    key_row = result.scalar_one_or_none()
    if not key_row:
        return None

    decryptor = create_encryption_service()
    return decryptor.decrypt_api_key(key_row.encrypted_key, str(user_id))


@router.post("/generate-document-v2-byok", response_model=None)
async def generate_document_audio_v2_byok(
    background_tasks: BackgroundTasks,
    source_type: Optional[str] = Form(None),
    document_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    source_uri: Optional[str] = Form(None),
    duration: int = Form(10),
    difficulty: str = Form("intermediate"),
    llm_provider: str = Form("openrouter"),
    llm_model: Optional[str] = Form(None),
    tts_provider: str = Form("elevenlabs"),
    context: Optional[str] = Form(None),
    voice_id: Optional[str] = Form(None),
    dry_run: bool = Form(False),
    current_user = Depends(get_current_user),
    db = Depends(get_async_db),
):
    """V2 BYOK path: uses the authenticated user's stored encrypted provider keys."""
    if not v2_pipeline_enabled():
        raise HTTPException(
            status_code=404,
            detail="V2 pipeline is disabled. Set ENABLE_V2_PIPELINE=true to enable.",
        )

    provider_map = {
        "openrouter": APIProvider.OPENROUTER,
        "elevenlabs": APIProvider.ELEVENLABS,
    }
    llm_enum = provider_map.get((llm_provider or "").lower())
    tts_enum = provider_map.get((tts_provider or "").lower())

    if not llm_enum:
        raise HTTPException(
            status_code=400,
            detail="BYOK endpoint currently supports LLM provider: openrouter",
        )
    if not tts_enum:
        raise HTTPException(
            status_code=400,
            detail="BYOK endpoint currently supports TTS provider: elevenlabs",
        )

    llm_key = await _get_user_api_key(db, current_user.id, llm_enum)
    tts_key = await _get_user_api_key(db, current_user.id, tts_enum)

    missing = []
    if not llm_key:
        missing.append(llm_provider)
    if not tts_key:
        missing.append(tts_provider)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing valid API keys for: {', '.join(missing)}. Add keys in settings first.",
        )

    if difficulty not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty level")

    if duration < 5 or duration > 60:
        raise HTTPException(status_code=400, detail="Duration must be between 5 and 60 minutes")

    source_input = await _resolve_source_text_v1a(
        document_text=document_text,
        file=file,
        source_uri=source_uri,
        source_type=source_type,
    )

    source_text = source_input["source_text"]
    source_name = source_input["source_name"]
    normalized_source_type = source_input["source_type"]

    if dry_run:
        return _build_v2_dry_run_response(
            source=source_name,
            source_type=normalized_source_type,
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            key_source="user-encrypted-storage",
        )

    try:
        pipeline = create_document_pipeline_v2()
        result = await pipeline.run(
            document_text=source_text,
            duration_minutes=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            context=context,
            voice_id=voice_id,
            llm_api_key=llm_key,
            tts_api_key=tts_key,
        )

        logger.info(
            "V2 BYOK generation completed for user %s with llm=%s tts=%s source=%s",
            current_user.id,
            llm_provider,
            tts_provider,
            source_name,
        )
        return {
            "success": True,
            "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
            "source": source_name,
            "source_type": normalized_source_type,
            "duration": duration,
            "difficulty": difficulty,
            "key_source": "user-encrypted-storage",
            **result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("V2 BYOK generation failed for user %s: %s", current_user.id, str(e))
        raise HTTPException(status_code=500, detail="V2 BYOK generation failed")
