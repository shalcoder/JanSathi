"""
lambda_handler.py — AWS Lambda entry point for JanSathi API
============================================================
Uses Mangum to adapt the Flask WSGI app to Lambda / API Gateway proxy events.
X-Ray tracing is initialised here (aws_xray_sdk patches boto3 automatically).

Handler:   lambda_handler.handler
Env vars:  XRAY_ENABLED=true | false  (default: true on Lambda)
"""

import sys
import os
import logging

# Ensure backend/ is on sys.path so all local imports resolve in Lambda
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ── X-Ray bootstrap (must happen before boto3 is imported by the app) ─────────
_XRAY_ENABLED = os.getenv("XRAY_ENABLED", "true").lower() == "true"
if _XRAY_ENABLED:
    try:
        from aws_xray_sdk.core import patch_all
        patch_all()
        logger.info("[X-Ray] boto3 patching complete")
    except ImportError:
        logger.info("[X-Ray] aws_xray_sdk not installed — tracing disabled")

# ── Flask app + Mangum adapter ─────────────────────────────────────────────────
try:
    from app import create_app
    _flask_app = create_app()

    from mangum import Mangum
    handler = Mangum(_flask_app, lifespan="off")
    logger.info("[Lambda] Flask app loaded via Mangum")

except Exception as _bootstrap_err:
    # Critical failure: log it and fall through to the minimal health handler
    logger.error(f"[Lambda] App bootstrap failed: {_bootstrap_err}", exc_info=True)
    _flask_app = None
    handler     = None


# ── Minimal fallback handler (used when Flask bootstrap fails) ─────────────────
import json

_CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Session-Id",
}


def lambda_handler(event, context):
    """
    Primary Lambda entry point (registered in CDK as lambda_handler.handler).
    When Flask + Mangum are available this is never called directly — Mangum
    is registered as `handler` above and CDK uses lambda_handler.handler.

    This fallback handles:
    • /health  — always returns 200 (load-balancer health checks)
    • other    — returns 503 with bootstrap error detail
    """
    path   = event.get("rawPath", event.get("path", "/"))
    method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod", "GET")
    )

    # CORS preflight
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": _CORS, "body": ""}

    if path in ("/", "/health"):
        body = {
            "status":  "ok" if handler else "degraded",
            "service": "JanSathi API",
            "version": "2.0.0",
        }
        return {"statusCode": 200, "headers": _CORS, "body": json.dumps(body)}

    if handler is None:
        return {
            "statusCode": 503,
            "headers": _CORS,
            "body": json.dumps({"error": "Service temporarily unavailable"}),
        }

    # Delegate to Mangum (should not normally reach here)
    return handler(event, context)

