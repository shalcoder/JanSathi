"""
middleware.py — Production-grade middleware for JanSathi.

Provides:
1. JWT Authentication (Clerk JWKS-based, dev-bypass available)
2. Correlation ID injection per request
3. Normalized request/response envelope
4. Structured per-request logging (CloudWatch compatible)
"""

import os
import uuid
import time
import json
import logging
from functools import wraps
from typing import Optional

from flask import request, jsonify, g

logger = logging.getLogger("jansathi.middleware")

# ═══════════════════════════════════════════════════════════════
# CORRELATION ID
# ═══════════════════════════════════════════════════════════════

def inject_correlation_id():
    """
    Inject a correlation ID into flask.g for every request.
    Uses X-Correlation-Id header if provided by caller (API Gateway / frontend),
    otherwise generates a new UUID.
    """
    g.correlation_id = request.headers.get("X-Correlation-Id") or str(uuid.uuid4())
    g.request_start = time.perf_counter()


def log_request_lifecycle(response):
    """
    After-request hook: logs method, path, status, latency, and correlation ID
    in a structured JSON format compatible with CloudWatch Logs Insights.
    """
    latency_ms = round((time.perf_counter() - getattr(g, "request_start", time.perf_counter())) * 1000, 2)
    log_entry = {
        "event": "http_request",
        "correlation_id": getattr(g, "correlation_id", "unknown"),
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "latency_ms": latency_ms,
        "user_id": getattr(g, "user_id", "anonymous"),
    }
    logger.info(json.dumps(log_entry))
    # Propagate correlation ID in response so the frontend can trace requests
    response.headers["X-Correlation-Id"] = getattr(g, "correlation_id", "unknown")
    return response


# ═══════════════════════════════════════════════════════════════
# JWT AUTHENTICATION
# ═══════════════════════════════════════════════════════════════

_DEV_MODE = os.getenv("NODE_ENV", "development") != "production"

def _decode_clerk_jwt(token: str) -> Optional[dict]:
    """
    Decode and verify a Clerk-issued JWT.
    In dev mode, returns a dummy payload without verification.
    In production, verifies against Clerk's JWKS endpoint.
    """
    if _DEV_MODE:
        # Dev bypass: accept any token, return a dummy payload
        return {"sub": "dev-user", "email": "dev@jansathi.local", "role": "user"}

    try:
        import jwt
        import requests as req

        jwks_url = os.getenv("CLERK_JWKS_URL")
        if not jwks_url:
            logger.warning("CLERK_JWKS_URL not set — auth verification skipped.")
            return {"sub": "unverified-user", "role": "user"}

        jwks = req.get(jwks_url, timeout=5).json()
        header = jwt.get_unverified_header(token)
        key = next((k for k in jwks["keys"] if k.get("kid") == header.get("kid")), None)
        if not key:
            return None

        from jwt.algorithms import RSAAlgorithm
        public_key = RSAAlgorithm.from_jwk(json.dumps(key))
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_exp": True},
        )
        return payload
    except Exception as e:
        logger.warning(f"JWT decode failed: {e}")
        return None


def require_auth(f):
    """
    Decorator: Validates Bearer JWT token.
    Sets g.user_id and g.user_role for downstream route use.
    Returns 401 if token is missing or invalid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": "Unauthorized",
                "message": "Missing or invalid Authorization header.",
                "correlation_id": getattr(g, "correlation_id", None),
            }), 401

        token = auth_header.split(" ", 1)[1]
        payload = _decode_clerk_jwt(token)
        if payload is None:
            return jsonify({
                "error": "Unauthorized",
                "message": "Invalid or expired token.",
                "correlation_id": getattr(g, "correlation_id", None),
            }), 401

        g.user_id = payload.get("sub", "anonymous")
        g.user_role = payload.get("role", "user")
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """
    Decorator: Requires user to carry role='admin'.
    Must be applied AFTER @require_auth.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if getattr(g, "user_role", "user") != "admin":
            return jsonify({
                "error": "Forbidden",
                "message": "Admin role required.",
                "correlation_id": getattr(g, "correlation_id", None),
            }), 403
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════════
# REQUEST SCHEMA VALIDATION
# ═══════════════════════════════════════════════════════════════

def validate_json_body(required_fields: list):
    """
    Decorator: Validates that the request body is JSON and contains all required fields.
    Returns 400 with a structured error if validation fails.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    "error": "BadRequest",
                    "message": "Content-Type must be application/json.",
                    "correlation_id": getattr(g, "correlation_id", None),
                }), 400

            body = request.get_json(silent=True) or {}
            missing = [field for field in required_fields if field not in body]
            if missing:
                return jsonify({
                    "error": "ValidationError",
                    "message": f"Missing required fields: {missing}",
                    "correlation_id": getattr(g, "correlation_id", None),
                }), 400

            return f(*args, **kwargs)
        return decorated
    return decorator


# ═══════════════════════════════════════════════════════════════
# NORMALIZED RESPONSE ENVELOPE
# ═══════════════════════════════════════════════════════════════

def success_response(data: dict, status: int = 200) -> tuple:
    """Return a standardized success response envelope."""
    return jsonify({
        "status": "success",
        "correlation_id": getattr(g, "correlation_id", None),
        "data": data,
    }), status


def error_response(message: str, error_code: str = "ERROR", status: int = 400) -> tuple:
    """Return a standardized error response envelope."""
    return jsonify({
        "status": "error",
        "correlation_id": getattr(g, "correlation_id", None),
        "error": error_code,
        "message": message,
    }), status


# ═══════════════════════════════════════════════════════════════
# REGISTER WITH FLASK APP
# ═══════════════════════════════════════════════════════════════

def register_middleware(app):
    """
    Register all middleware hooks with the Flask app.
    Call this from create_app() in main.py.
    """
    app.before_request(inject_correlation_id)
    app.after_request(log_request_lifecycle)
    logger.info("JanSathi middleware registered: correlation IDs, request logging, auth decorators ready.")
