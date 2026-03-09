"""
xray_service.py — AWS X-Ray Tracing for Flask / Lambda
=======================================================
Provides:
  - configure_xray(app)   — call once in app/__init__.py
  - xray_capture(name)    — decorator for service functions
  - put_annotation(k, v)  — add searchable annotation to current segment
  - put_metadata(k, v)    — add arbitrary metadata to current segment

Uses aws_xray_sdk.  On Lambda the X-Ray daemon is injected by the
runtime; set XRAY_DAEMON_ADDRESS=127.0.0.1:2000 when running locally
with the X-Ray daemon container.

When aws_xray_sdk is absent or XRAY_ENABLED=false the decorators are
transparent no-ops so local development is unaffected.
"""

import os
import logging
import functools
from typing import Callable, Any

logger = logging.getLogger(__name__)

XRAY_ENABLED   = os.getenv("XRAY_ENABLED", "true").lower() == "true"
SERVICE_NAME   = os.getenv("XRAY_SERVICE_NAME", "jansathi-api")


# ── SDK bootstrap ─────────────────────────────────────────────────────────────

def _load_sdk():
    """Returns (xray_recorder, patch_all, XRayMiddleware) or (None, None, None)."""
    if not XRAY_ENABLED:
        return None, None, None
    try:
        from aws_xray_sdk.core import xray_recorder, patch_all
        from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
        return xray_recorder, patch_all, XRayMiddleware
    except ImportError:
        logger.debug("[X-Ray] aws_xray_sdk not installed — tracing disabled")
        return None, None, None


_recorder, _patch_all, _XRayMiddleware = _load_sdk()


# ── Flask integration ──────────────────────────────────────────────────────────

def configure_xray(app) -> None:
    """
    Wire X-Ray into the Flask app.
    Call once at the end of create_app():
        from app.services.xray_service import configure_xray
        configure_xray(app)
    """
    if not _recorder or not _XRayMiddleware:
        logger.info("[X-Ray] Skipping — SDK not available or XRAY_ENABLED=false")
        return

    # Configure recorder
    _recorder.configure(
        service=SERVICE_NAME,
        sampling=True,
        # On Lambda the daemon address comes from the runtime env var.
        # For local: set XRAY_DAEMON_ADDRESS=127.0.0.1:2000
    )

    # Patch all boto3 clients so DynamoDB / S3 / Bedrock calls are traced
    _patch_all()

    # Attach Flask middleware so every HTTP request creates a segment
    _XRayMiddleware(app, _recorder)
    logger.info(f"[X-Ray] Enabled for service '{SERVICE_NAME}'")


# ── Decorators & helpers ───────────────────────────────────────────────────────

def xray_capture(subsegment_name: str | None = None):
    """
    Decorator — wraps a function in an X-Ray subsegment.

    Usage:
        @xray_capture("rag.retrieve")
        def retrieve_documents(query):
            ...
    """
    def decorator(func: Callable) -> Callable:
        name = subsegment_name or func.__qualname__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not _recorder:
                return func(*args, **kwargs)
            with _recorder.in_subsegment(name):
                return func(*args, **kwargs)

        return wrapper
    return decorator


def put_annotation(key: str, value: Any) -> None:
    """Add a searchable annotation to the current X-Ray (sub)segment."""
    if not _recorder:
        return
    try:
        _recorder.current_segment().put_annotation(key, str(value))
    except Exception:
        pass   # segment may not exist during local testing


def put_metadata(key: str, value: Any, namespace: str = "default") -> None:
    """Add non-searchable metadata to the current X-Ray (sub)segment."""
    if not _recorder:
        return
    try:
        _recorder.current_segment().put_metadata(key, value, namespace)
    except Exception:
        pass


def add_error(error: Exception) -> None:
    """Mark the current subsegment as faulted with exception details."""
    if not _recorder:
        return
    try:
        _recorder.current_segment().add_exception(error, fatal=False)
    except Exception:
        pass
