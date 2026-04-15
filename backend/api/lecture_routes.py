"""
Authenticated Lecture API Routes
Protected endpoints for lecture generation and management
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import JSONResponse, FileResponse
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
from urllib.request import Request as UrlRequest, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path
from html import unescape
from xml.etree import ElementTree

from models.database import get_async_db
from models.user_orm import User
from models.lecture_orm import Lecture, LectureStatus, LectureSourceType, APIProvider, UserAPIKey
from models.lecture_models import LectureRequest, VoiceSettings
from auth import get_current_user
from services.api_key_service import get_api_key_service
from services.lecture_service import create_lecture_service
from services.pipeline_v2 import create_document_pipeline_v2, v2_pipeline_enabled
from services.pipeline_errors import PipelineExecutionError
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
MAX_URL_TRANSCRIPT_PREVIEW_CHARS = 8_000
SOURCE_INTAKE_ERROR_SCHEMA = "source-intake-error-v1"
URL_DIAGNOSTICS_SCHEMA = "url-diagnostics-v1"
DURATION_POLICY_SCHEMA = "duration-best-effort-v1"
V2_GENERATION_ERROR_SCHEMA = "v2-generation-error-v1"
BYOK_KEY_ERROR_SCHEMA = "byok-key-error-v1"
BYOK_PRIORITY_PAID_ENV_FLAG = "ENABLE_BYOK_PRIORITY_FOR_PAID"
DURATION_TOLERANCE_RATIO = 0.15
DURATION_MIN_TOLERANCE_MINUTES = 1.0
DURATION_WPM_BY_DIFFICULTY = {
    "beginner": 130.0,
    "intermediate": 145.0,
    "advanced": 160.0,
}


def _emit_generation_telemetry(
    *,
    user_id: int,
    route: str,
    execution_mode: str,
    source_type: str,
    source_class: Optional[str],
    duration: int,
    difficulty: str,
    llm_provider: str,
    llm_model: Optional[str],
    tts_provider: str,
    outcome: str,
    error_code: Optional[str] = None,
    error_stage: Optional[str] = None,
) -> None:
    payload: Dict[str, Any] = {
        "event": "generation_telemetry_v1",
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "user_id": user_id,
        "route": route,
        "execution_mode": execution_mode,
        "source_type": source_type,
        "source_class": source_class,
        "duration": duration,
        "difficulty": difficulty,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
        "tts_provider": tts_provider,
        "outcome": outcome,
    }
    if error_code:
        payload["error_code"] = error_code
    if error_stage:
        payload["error_stage"] = error_stage

    logger.info("TELEMETRY %s", json.dumps(payload, default=str, sort_keys=True))


def _url_ingestion_v1_enabled() -> bool:
    return os.getenv("ENABLE_URL_INGESTION_V1", "false").lower() == "true"


def _byok_priority_for_paid_enabled() -> bool:
    return os.getenv(BYOK_PRIORITY_PAID_ENV_FLAG, "false").lower() == "true"


def _supported_source_types_v1a() -> List[str]:
    supported = set(SUPPORTED_SOURCE_TYPES_V1A)
    if _url_ingestion_v1_enabled():
        supported.add("url")
    return sorted(supported)


def _validation_hint_v1a() -> str:
    if _url_ingestion_v1_enabled():
        return (
            "Supported source_type values for v1a are: text, txt, md, pdf, url. "
            "URL source intake supports ready web pages plus transcript-first YouTube/podcast sources."
        )
    return (
        "Supported source_type values for v1a are: text, txt, md, pdf. "
        "Enable ENABLE_URL_INGESTION_V1=true to use URL source intake."
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


def _request_url_text(source_uri: str, timeout: int, user_agent: str) -> Dict[str, str]:
    request = UrlRequest(source_uri, method="GET", headers={"User-Agent": user_agent})
    with urlopen(request, timeout=timeout) as response:
        raw_bytes = response.read()
        content_type = (response.headers.get("Content-Type") or "").lower()
    return {
        "content": raw_bytes.decode("utf-8", errors="ignore"),
        "content_type": content_type,
    }


def _looks_like_feed_url(source_uri: str) -> bool:
    parsed = urlparse(source_uri)
    path = (parsed.path or "").lower()
    query = (parsed.query or "").lower()
    return any(token in path for token in [".xml", ".rss", "/feed"]) or any(
        token in query for token in ["rss", "feed"]
    )


def _extract_youtube_video_id(source_uri: str) -> Optional[str]:
    parsed = urlparse(source_uri)
    host = (parsed.netloc or "").lower()
    path = (parsed.path or "").strip("/")

    if "youtu.be" in host and path:
        return path.split("/")[0]

    if "youtube.com" in host:
        if path == "watch":
            query = parsed.query or ""
            match = re.search(r"(?:^|&)v=([A-Za-z0-9_-]{6,})", query)
            if match:
                return match.group(1)
        for prefix in ["embed/", "shorts/"]:
            if path.startswith(prefix):
                candidate = path.split("/")[1] if len(path.split("/")) > 1 else ""
                if candidate:
                    return candidate
    return None


def _extract_text_from_caption_xml(content: str) -> str:
    try:
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError:
        return ""

    chunks: List[str] = []
    for node in root.findall(".//text"):
        text = "".join(node.itertext()).strip()
        if text:
            chunks.append(unescape(text))
    return " ".join(chunks).strip()


def _extract_podcast_transcript_link(feed_xml: str) -> Optional[str]:
    try:
        root = ElementTree.fromstring(feed_xml)
    except ElementTree.ParseError:
        return None

    # RFC-agnostic tag scan for transcript URL attributes in RSS/Podcast feeds.
    for node in root.iter():
        tag_name = (node.tag or "").lower()
        if tag_name.endswith("transcript"):
            url_value = node.attrib.get("url") or (node.text or "").strip()
            if url_value:
                return url_value
    return None


def _fetch_youtube_transcript_text(source_uri: str, max_chars: int = MAX_URL_TEXT_CHARS) -> str:
    video_id = _extract_youtube_video_id(source_uri)
    if not video_id:
        raise ValueError("Could not parse YouTube video ID from URL.")

    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    watch_page = _request_url_text(watch_url, timeout=8, user_agent="LearnOnTheGo/youtube-transcript")
    watch_html = watch_page["content"]

    caption_match = re.search(r'"captionTracks":\s*(\[.*?\])', watch_html, flags=re.DOTALL)
    if not caption_match:
        raise ValueError("No public captions/transcript found for this YouTube video.")

    tracks_blob = caption_match.group(1).replace("\\u0026", "&")
    try:
        tracks = json.loads(tracks_blob)
    except json.JSONDecodeError as exc:
        raise ValueError("Could not parse YouTube caption metadata.") from exc

    base_url = None
    for track in tracks:
        candidate = track.get("baseUrl")
        if candidate:
            base_url = candidate
            if track.get("kind") != "asr":
                break

    if not base_url:
        raise ValueError("No caption track URL found for this YouTube video.")

    transcript_payload = _request_url_text(base_url, timeout=8, user_agent="LearnOnTheGo/youtube-caption")
    transcript_text = _extract_text_from_caption_xml(transcript_payload["content"])
    if not transcript_text:
        raise ValueError("Caption track was available but transcript content was empty.")

    return transcript_text[:max_chars]


def _fetch_podcast_transcript_text(source_uri: str, max_chars: int = MAX_URL_TEXT_CHARS) -> str:
    if not _looks_like_feed_url(source_uri):
        raise ValueError("Podcast transcript-first ingestion currently requires an RSS/feed URL.")

    feed_payload = _request_url_text(source_uri, timeout=8, user_agent="LearnOnTheGo/podcast-feed")
    transcript_link = _extract_podcast_transcript_link(feed_payload["content"])
    if not transcript_link:
        raise ValueError("No public podcast transcript link found in RSS feed metadata.")

    transcript_payload = _request_url_text(transcript_link, timeout=8, user_agent="LearnOnTheGo/podcast-transcript")
    transcript_text = _extract_text_from_html(transcript_payload["content"])
    if not transcript_text:
        raise ValueError("Podcast transcript content was empty.")

    return transcript_text[:max_chars]


def _resolve_url_source_text_v1(source_uri: str, source_class: str, max_chars: int = MAX_URL_TEXT_CHARS) -> str:
    if source_class == "video":
        return _fetch_youtube_transcript_text(source_uri, max_chars=max_chars)
    if source_class in {"podcast", "audio"}:
        return _fetch_podcast_transcript_text(source_uri, max_chars=max_chars)
    return _fetch_url_source_text(source_uri, max_chars=max_chars)


def _source_retrieval_method(source_type: str, source_class: Optional[str] = None) -> str:
    if source_type == "url":
        if source_class == "video":
            return "youtube_transcript"
        if source_class in {"podcast", "audio"}:
            return "podcast_feed_transcript"
        return "web_fetch"
    if source_type == "text":
        return "pasted_text"
    return "file_upload"


def _build_source_metadata(
    *,
    source_name: str,
    source_type: str,
    source_text: str,
    source_uri: Optional[str] = None,
    source_class: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "source_uri": source_uri,
        "source_class": source_class or ("web" if source_type == "url" else source_type),
        "retrieval_method": _source_retrieval_method(source_type, source_class),
        "retrieval_timestamp": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "excerpt": (source_text or "").strip()[:280],
        "source_name": source_name,
    }


def _build_citations(source_metadata: Dict[str, Any]) -> list:
    source_uri = source_metadata.get("source_uri")
    source_class = source_metadata.get("source_class")
    retrieval_method = source_metadata.get("retrieval_method")
    excerpt = source_metadata.get("excerpt") or ""

    note_parts = [
        f"class={source_class}",
        f"retrieval={retrieval_method}",
    ]
    if excerpt:
        note_parts.append(f"excerpt={excerpt[:140]}")

    return [
        {
            "label": "Primary Source",
            "source_uri": source_uri,
            "note": "; ".join(note_parts),
        }
    ]


def _fetch_url_source_text(source_uri: str, max_chars: int = MAX_URL_TEXT_CHARS) -> str:
    payload = _request_url_text(source_uri, timeout=8, user_agent="LearnOnTheGo/url-intake")
    content_type = payload["content_type"]

    if "text" not in content_type and "html" not in content_type and "json" not in content_type:
        raise ValueError("URL content type is not text-based and cannot be ingested.")

    decoded = payload["content"]
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
        try:
            await asyncio.to_thread(_fetch_youtube_transcript_text, source_uri, MAX_URL_TRANSCRIPT_PREVIEW_CHARS)
        except Exception as exc:
            return {
                "success": False,
                "schema": URL_DIAGNOSTICS_SCHEMA,
                "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
                "source_uri": source_uri,
                "source_class": source_class,
                "outcome": "no_transcript",
                "diagnostics": {
                    "code": "no_transcript",
                    "message": f"YouTube transcript not available: {str(exc)}",
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
                "message": "YouTube transcript is available and ready for ingestion.",
                "retryable": False,
                "status_code": availability.get("status_code"),
            },
        }

    if source_class in {"podcast", "audio"}:
        if not _looks_like_feed_url(source_uri):
            return {
                "success": False,
                "schema": URL_DIAGNOSTICS_SCHEMA,
                "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
                "source_uri": source_uri,
                "source_class": source_class,
                "outcome": "unsupported",
                "diagnostics": {
                    "code": "unsupported",
                    "message": "Podcast ingestion requires an RSS/feed URL with public transcript metadata.",
                    "retryable": False,
                    "status_code": availability.get("status_code"),
                },
            }

        try:
            await asyncio.to_thread(_fetch_podcast_transcript_text, source_uri, MAX_URL_TRANSCRIPT_PREVIEW_CHARS)
        except Exception as exc:
            return {
                "success": False,
                "schema": URL_DIAGNOSTICS_SCHEMA,
                "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
                "source_uri": source_uri,
                "source_class": source_class,
                "outcome": "no_transcript",
                "diagnostics": {
                    "code": "no_transcript",
                    "message": f"Podcast transcript not available: {str(exc)}",
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
                "message": "Podcast transcript feed is available and ready for ingestion.",
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
) -> Dict[str, Any]:
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
            "source_metadata": _build_source_metadata(
                source_name="pasted_text",
                source_type="text",
                source_text=text_value,
                source_class="text",
            ),
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
            fetched_text = await asyncio.to_thread(
                _resolve_url_source_text_v1,
                cleaned_uri,
                diagnostics.get("source_class", "web"),
            )
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
            "source_metadata": _build_source_metadata(
                source_name=cleaned_uri,
                source_type="url",
                source_text=fetched_text,
                source_uri=cleaned_uri,
                source_class=diagnostics.get("source_class"),
            ),
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
                "For URLs, use source_type=url and run diagnostics first."
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
            "source_metadata": _build_source_metadata(
                source_name=file_name,
                source_type=inferred_type,
                source_text=decoded.strip(),
                source_class=inferred_type,
            ),
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
            "source_metadata": _build_source_metadata(
                source_name=file_name,
                source_type=inferred_type,
                source_text=processed_content,
                source_class=inferred_type,
            ),
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
    execution_mode: str,
    source_metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """Return a stable response contract without invoking paid generation."""
    preview_script = {
        "title": "Dry Run Lecture Contract",
        "content": "Dry run mode validates contract only. No LLM/TTS generation executed.",
        "duration_minutes": duration,
        "difficulty": difficulty,
    }
    metadata = _build_response_metadata(
        script=preview_script["content"],
        target_duration_minutes=duration,
        difficulty=difficulty,
        credential_source=execution_mode,
        source_metadata=source_metadata,
    )
    citations = _build_citations(source_metadata)
    return {
        "success": True,
        "dry_run": True,
        "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
        "source": source,
        "source_type": source_type,
        "duration": duration,
        "difficulty": difficulty,
        "key_source": key_source,
        "execution_mode": execution_mode,
        "title": "Dry Run Lecture Contract",
        "script": "Dry run mode validates contract only. No LLM/TTS generation executed.",
        "summary": "Dry run preview only. Confirm to run final generation.",
        "preview_script": preview_script,
        "llm": {
            "provider": llm_provider,
            "model": llm_model or "dry-run",
            "usage": {},
        },
        "script_sections": _build_script_sections(preview_script["content"], citations),
        "citations": citations,
        "source_metadata": source_metadata,
        "metadata": metadata,
        "audio": {
            "provider": tts_provider,
            "model": "dry-run",
            "file_path": "",
            "bytes_written": 0,
            "metadata": {"skipped": True},
        },
    }


def _build_script_sections(script: str, citations: Optional[list] = None) -> list:
    cleaned = (script or "").strip()
    if not cleaned:
        return []
    sections = [
        {
            "id": "main",
            "heading": "Main Script",
            "content": cleaned,
        }
    ]

    citation_items = citations or []
    if citation_items:
        lines = []
        for citation in citation_items:
            uri = citation.get("source_uri") or "source-uri-unavailable"
            note = citation.get("note") or ""
            lines.append(f"- {uri}{f' ({note})' if note else ''}")
        sections.append(
            {
                "id": "sources",
                "heading": "Sources",
                "content": "\n".join(lines),
            }
        )

    return sections


def _build_script_summary(script: str) -> str:
    cleaned = (script or "").strip()
    if not cleaned:
        return ""
    summary = cleaned.split("\n", 1)[0].strip()
    if len(summary) > 220:
        summary = summary[:217].rstrip() + "..."
    return summary


def _count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def _build_duration_policy(script: str, target_duration_minutes: int, difficulty: str) -> Dict[str, Any]:
    word_count = _count_words(script)
    speech_rate = DURATION_WPM_BY_DIFFICULTY.get((difficulty or "").lower(), 145.0)
    estimated_duration = round((word_count / speech_rate) if speech_rate > 0 else 0.0, 2)
    tolerance = round(max(DURATION_MIN_TOLERANCE_MINUTES, target_duration_minutes * DURATION_TOLERANCE_RATIO), 2)
    delta = round(estimated_duration - float(target_duration_minutes), 2)
    within_tolerance = abs(delta) <= tolerance
    status = "within_tolerance"
    if not within_tolerance:
        status = "over_target" if delta > 0 else "under_target"

    return {
        "schema": DURATION_POLICY_SCHEMA,
        "target_duration_minutes": int(target_duration_minutes),
        "estimated_duration_minutes": estimated_duration,
        "delta_minutes": delta,
        "tolerance_minutes": tolerance,
        "within_tolerance": within_tolerance,
        "status": status,
        "estimated_speech_rate_wpm": speech_rate,
        "script_word_count": word_count,
    }


def _build_response_metadata(
    *,
    script: str,
    target_duration_minutes: int,
    difficulty: str,
    credential_source: str,
    source_metadata: Optional[Dict[str, Any]] = None,
    existing: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    metadata: Dict[str, Any] = dict(existing) if isinstance(existing, dict) else {}
    metadata["duration_policy"] = _build_duration_policy(
        script=script,
        target_duration_minutes=target_duration_minutes,
        difficulty=difficulty,
    )
    metadata["credential_source"] = credential_source
    if source_metadata:
        metadata["source_context"] = source_metadata
    return metadata


def _byok_key_error_detail(
    *,
    code: str,
    message: str,
    providers: Optional[List[str]] = None,
    hint: Optional[str] = None,
) -> Dict[str, Any]:
    detail: Dict[str, Any] = {
        "schema": BYOK_KEY_ERROR_SCHEMA,
        "code": code,
        "message": message,
        "execution_mode": "byok",
    }
    if providers:
        detail["providers"] = providers
    if hint:
        detail["hint"] = hint
    return detail


def _v2_provider_error_detail(exc: PipelineExecutionError, *, execution_mode: str) -> Dict[str, Any]:
    detail: Dict[str, Any] = {
        "schema": V2_GENERATION_ERROR_SCHEMA,
        "code": "provider_execution_failed",
        "message": exc.message,
        "stage": exc.stage,
        "provider": exc.provider,
        "execution_mode": execution_mode,
        "retryable": bool(exc.retryable),
    }
    if exc.status_code is not None:
        detail["provider_http_status"] = exc.status_code
    if exc.cause_type:
        detail["cause_type"] = exc.cause_type
    return detail


def _resolve_v2_audio_url(result: Dict[str, Any], request: Request) -> Optional[str]:
    explicit = result.get("audio_url")
    if isinstance(explicit, str) and explicit.startswith("http"):
        return explicit

    audio = result.get("audio") if isinstance(result.get("audio"), dict) else None
    file_path = audio.get("file_path") if audio else None
    if not isinstance(file_path, str) or not file_path:
        return None

    if file_path.startswith("http"):
        return file_path

    filename = os.path.basename(file_path)
    if not filename:
        return None

    return f"{str(request.base_url).rstrip('/')}/api/lectures/audio/v2/{filename}"


def _storage_source_type(source_type: str) -> LectureSourceType:
    normalized = (source_type or "").lower()
    if normalized == "pdf":
        return LectureSourceType.PDF
    return LectureSourceType.TEXT


async def _persist_v2_lecture_metadata(
    *,
    db,
    user_id: int,
    source_name: str,
    source_type: str,
    source_metadata: Dict[str, Any],
    context: Optional[str],
    duration: int,
    difficulty: str,
    script: str,
    audio_url: Optional[str],
    llm_usage: Optional[Dict[str, Any]] = None,
) -> Optional[int]:
    if db is None:
        return None

    context_payload = {
        "user_context": context,
        "source_metadata": source_metadata,
    }
    lecture = Lecture(
        user_id=user_id,
        title="V2 Generated Lecture",
        topic=source_name,
        difficulty=difficulty,
        duration_requested=duration,
        duration_actual=duration,
        source_type=_storage_source_type(source_type),
        source_file_name=source_name[:255] if source_name else None,
        custom_context=json.dumps(context_payload),
        status=LectureStatus.COMPLETED,
        lecture_script=script,
        audio_file_url=audio_url,
        llm_tokens_used=(llm_usage or {}).get("total_tokens"),
    )

    try:
        db.add(lecture)
        await db.commit()
        await db.refresh(lecture)
        lecture_id = getattr(lecture, "id", None)
        return lecture_id if isinstance(lecture_id, int) else None
    except Exception as exc:
        logger.warning("V2 lecture metadata persistence skipped due to DB error: %s", str(exc))
        try:
            await db.rollback()
        except Exception:
            pass
        return None


def _classify_url_source(source_uri: str) -> str:
    parsed = urlparse(source_uri)
    host = (parsed.netloc or "").lower()
    path = (parsed.path or "").lower()

    if any(domain in host for domain in ["youtube.com", "youtu.be", "vimeo.com"]):
        return "video"
    if _looks_like_feed_url(source_uri):
        return "podcast"
    if any(domain in host for domain in ["spotify.com", "soundcloud.com", "podcasts.apple.com"]):
        return "podcast"
    if any(path.endswith(ext) for ext in [".mp3", ".wav", ".m4a", ".aac"]):
        return "audio"
    return "web"


def _probe_url_availability(source_uri: str) -> Dict[str, Any]:
    request = UrlRequest(source_uri, method="GET", headers={"User-Agent": "LearnOnTheGo/diagnostics"})
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
    request: Request,
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
    db = Depends(get_async_db),
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
    source_metadata = source_input.get("source_metadata") or {}
    citations = _build_citations(source_metadata)

    if dry_run:
        _emit_generation_telemetry(
            user_id=current_user.id,
            route="generate-document-v2",
            execution_mode="environment",
            source_type=normalized_source_type,
            source_class=source_metadata.get("source_class"),
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            outcome="dry_run_success",
        )
        return _build_v2_dry_run_response(
            source=source_name,
            source_type=normalized_source_type,
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            key_source="environment",
            execution_mode="environment",
            source_metadata=source_metadata,
        )

    execution_mode = "environment"
    key_source = "environment"
    llm_api_key: Optional[str] = None
    tts_api_key: Optional[str] = None

    if _byok_priority_for_paid_enabled():
        provider_map = {
            "openrouter": APIProvider.OPENROUTER,
            "elevenlabs": APIProvider.ELEVENLABS,
        }
        llm_enum = provider_map.get((llm_provider or "").lower())
        tts_enum = provider_map.get((tts_provider or "").lower())
        if llm_enum and tts_enum:
            llm_api_key = await _get_user_api_key(db, current_user.id, llm_enum)
            tts_api_key = await _get_user_api_key(db, current_user.id, tts_enum)
            if llm_api_key and tts_api_key:
                execution_mode = "byok"
                key_source = "user-encrypted-storage"

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
            llm_api_key=llm_api_key,
            tts_api_key=tts_api_key,
        )

        logger.info(
            "V2 generation completed for user %s with llm=%s tts=%s source=%s",
            current_user.id,
            llm_provider,
            tts_provider,
            source_name,
        )
        resolved_audio_url = _resolve_v2_audio_url(result, request)
        lecture_id = await _persist_v2_lecture_metadata(
            db=db,
            user_id=current_user.id,
            source_name=source_name,
            source_type=normalized_source_type,
            source_metadata=source_metadata,
            context=context,
            duration=duration,
            difficulty=difficulty,
            script=result.get("script", ""),
            audio_url=resolved_audio_url,
            llm_usage=result.get("llm", {}).get("usage") if isinstance(result.get("llm"), dict) else None,
        )
        llm_result = result.get("llm") if isinstance(result.get("llm"), dict) else {}
        resolved_llm_model = llm_result.get("model") if isinstance(llm_result, dict) else None
        _emit_generation_telemetry(
            user_id=current_user.id,
            route="generate-document-v2",
            execution_mode=execution_mode,
            source_type=normalized_source_type,
            source_class=source_metadata.get("source_class"),
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=resolved_llm_model or llm_model,
            tts_provider=tts_provider,
            outcome="success",
        )
        return {
            "success": True,
            "id": str(lecture_id) if lecture_id is not None else None,
            "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
            "source": source_name,
            "source_type": normalized_source_type,
            "duration": duration,
            "difficulty": difficulty,
            "key_source": key_source,
            "execution_mode": execution_mode,
            "summary": _build_script_summary(result.get("script", "")),
            "script_sections": _build_script_sections(result.get("script", ""), citations),
            "citations": citations,
            "source_metadata": source_metadata,
            **result,
            "audio_url": resolved_audio_url,
            "metadata": _build_response_metadata(
                script=result.get("script", ""),
                target_duration_minutes=duration,
                difficulty=difficulty,
                credential_source=execution_mode,
                source_metadata=source_metadata,
                existing=result.get("metadata"),
            ),
        }
    except PipelineExecutionError as e:
        _emit_generation_telemetry(
            user_id=current_user.id,
            route="generate-document-v2",
            execution_mode=execution_mode,
            source_type=normalized_source_type,
            source_class=source_metadata.get("source_class"),
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            outcome="failure",
            error_code="provider_execution_failed",
            error_stage=e.stage,
        )
        logger.error(
            "V2 generation provider failure for user %s stage=%s provider=%s status=%s cause=%s",
            current_user.id,
            e.stage,
            e.provider,
            e.status_code,
            e.cause_type,
        )
        raise HTTPException(status_code=502, detail=_v2_provider_error_detail(e, execution_mode=execution_mode))
    except ValueError as e:
        _emit_generation_telemetry(
            user_id=current_user.id,
            route="generate-document-v2",
            execution_mode=execution_mode,
            source_type=normalized_source_type,
            source_class=source_metadata.get("source_class"),
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            outcome="failure",
            error_code="validation_error",
        )
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        _emit_generation_telemetry(
            user_id=current_user.id,
            route="generate-document-v2",
            execution_mode=execution_mode,
            source_type=normalized_source_type,
            source_class=source_metadata.get("source_class"),
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            outcome="failure",
            error_code="unexpected_error",
        )
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


@router.get("/audio/v2/{filename}")
async def download_v2_audio_file(
    filename: str,
    current_user = Depends(get_current_user),
):
    """Serve V2 generated audio files from temp storage for authenticated playback probes."""
    if os.path.basename(filename) != filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    audio_path = os.path.join("temp_audio", filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    media_type = "audio/mpeg" if filename.lower().endswith(".mp3") else "application/octet-stream"
    return FileResponse(audio_path, media_type=media_type, filename=filename)


@router.post("/generate-document-v2-byok", response_model=None)
async def generate_document_audio_v2_byok(
    request: Request,
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
            detail=_byok_key_error_detail(
                code="unsupported_provider",
                message="Unsupported BYOK LLM provider.",
                providers=[llm_provider],
                hint="BYOK endpoint currently supports LLM provider: openrouter",
            ),
        )
    if not tts_enum:
        raise HTTPException(
            status_code=400,
            detail=_byok_key_error_detail(
                code="unsupported_provider",
                message="Unsupported BYOK TTS provider.",
                providers=[tts_provider],
                hint="BYOK endpoint currently supports TTS provider: elevenlabs",
            ),
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
            detail=_byok_key_error_detail(
                code="missing_or_invalid_provider_key",
                message="Missing or invalid BYOK provider keys.",
                providers=missing,
                hint="Add and validate the missing provider keys in Settings, then retry.",
            ),
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
    source_metadata = source_input.get("source_metadata") or {}
    citations = _build_citations(source_metadata)

    if dry_run:
        _emit_generation_telemetry(
            user_id=current_user.id,
            route="generate-document-v2-byok",
            execution_mode="byok",
            source_type=normalized_source_type,
            source_class=source_metadata.get("source_class"),
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            outcome="dry_run_success",
        )
        return _build_v2_dry_run_response(
            source=source_name,
            source_type=normalized_source_type,
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            key_source="user-encrypted-storage",
            execution_mode="byok",
            source_metadata=source_metadata,
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
        resolved_audio_url = _resolve_v2_audio_url(result, request)
        lecture_id = await _persist_v2_lecture_metadata(
            db=db,
            user_id=current_user.id,
            source_name=source_name,
            source_type=normalized_source_type,
            source_metadata=source_metadata,
            context=context,
            duration=duration,
            difficulty=difficulty,
            script=result.get("script", ""),
            audio_url=resolved_audio_url,
            llm_usage=result.get("llm", {}).get("usage") if isinstance(result.get("llm"), dict) else None,
        )
        llm_result = result.get("llm") if isinstance(result.get("llm"), dict) else {}
        resolved_llm_model = llm_result.get("model") if isinstance(llm_result, dict) else None
        _emit_generation_telemetry(
            user_id=current_user.id,
            route="generate-document-v2-byok",
            execution_mode="byok",
            source_type=normalized_source_type,
            source_class=source_metadata.get("source_class"),
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=resolved_llm_model or llm_model,
            tts_provider=tts_provider,
            outcome="success",
        )
        return {
            "success": True,
            "id": str(lecture_id) if lecture_id is not None else None,
            "contract_version": SOURCE_INTAKE_CONTRACT_VERSION,
            "source": source_name,
            "source_type": normalized_source_type,
            "duration": duration,
            "difficulty": difficulty,
            "key_source": "user-encrypted-storage",
            "execution_mode": "byok",
            "summary": _build_script_summary(result.get("script", "")),
            "script_sections": _build_script_sections(result.get("script", ""), citations),
            "citations": citations,
            "source_metadata": source_metadata,
            **result,
            "audio_url": resolved_audio_url,
            "metadata": _build_response_metadata(
                script=result.get("script", ""),
                target_duration_minutes=duration,
                difficulty=difficulty,
                credential_source="byok",
                source_metadata=source_metadata,
                existing=result.get("metadata"),
            ),
        }
    except PipelineExecutionError as e:
        _emit_generation_telemetry(
            user_id=current_user.id,
            route="generate-document-v2-byok",
            execution_mode="byok",
            source_type=normalized_source_type,
            source_class=source_metadata.get("source_class"),
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            outcome="failure",
            error_code="provider_execution_failed",
            error_stage=e.stage,
        )
        logger.error(
            "V2 BYOK generation provider failure for user %s stage=%s provider=%s status=%s cause=%s",
            current_user.id,
            e.stage,
            e.provider,
            e.status_code,
            e.cause_type,
        )
        raise HTTPException(status_code=502, detail=_v2_provider_error_detail(e, execution_mode="byok"))
    except ValueError as e:
        _emit_generation_telemetry(
            user_id=current_user.id,
            route="generate-document-v2-byok",
            execution_mode="byok",
            source_type=normalized_source_type,
            source_class=source_metadata.get("source_class"),
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            outcome="failure",
            error_code="validation_error",
        )
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        _emit_generation_telemetry(
            user_id=current_user.id,
            route="generate-document-v2-byok",
            execution_mode="byok",
            source_type=normalized_source_type,
            source_class=source_metadata.get("source_class"),
            duration=duration,
            difficulty=difficulty,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tts_provider=tts_provider,
            outcome="failure",
            error_code="unexpected_error",
        )
        logger.error("V2 BYOK generation failed for user %s: %s", current_user.id, str(e))
        raise HTTPException(status_code=500, detail="V2 BYOK generation failed")
