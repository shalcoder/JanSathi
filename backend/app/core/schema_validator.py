from functools import wraps
from flask import request, jsonify, g
from pydantic import ValidationError
from typing import Any, Dict, Optional
from app.automation.l1_integration.schema import UnifiedEventObject

def validate_unified_event(f):
    """
    Decorator to validate that the request body matches the UnifiedEventObject schema (Layer 1).
    Automatically normalizes the request into g.unified_event.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                "status": "error",
                "error": "BAD_REQUEST",
                "message": "Content-Type must be application/json",
                "correlation_id": getattr(g, "correlation_id", None)
            }), 400
            
        try:
            body = request.get_json()
            # Construct the UnifiedEventObject
            event = UnifiedEventObject(**body)
            g.unified_event = event
        except ValidationError as e:
            return jsonify({
                "status": "error",
                "error": "VALIDATION_ERROR",
                "message": "Request does not match Layer 1 Unified Event Contract",
                "details": e.errors(),
                "correlation_id": getattr(g, "correlation_id", None)
            }), 400
        except Exception as e:
            return jsonify({
                "status": "error",
                "error": "INTERNAL_ERROR",
                "message": str(e),
                "correlation_id": getattr(g, "correlation_id", None)
            }), 500
            
        return f(*args, **kwargs)
    return decorated

class UnifiedResponse:
    """
    Helper to generate standardized API responses with Correlation IDs.
    """
    @staticmethod
    def success(data: Any, message: str = "Success", status: int = 200):
        return jsonify({
            "status": "success",
            "message": message,
            "data": data,
            "correlation_id": getattr(g, "correlation_id", None)
        }), status

    @staticmethod
    def error(message: str, error_code: str = "INTERNAL_ERROR", status: int = 500, details: Any = None):
        response = {
            "status": "error",
            "error": error_code,
            "message": message,
            "correlation_id": getattr(g, "correlation_id", None)
        }
        if details:
            response["details"] = details
        return jsonify(response), status
