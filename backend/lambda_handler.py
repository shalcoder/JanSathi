"""
JanSathi Lambda Handler — Mangum Wrapper
Wraps the existing Flask app for AWS Lambda + API Gateway.
This is the ONLY change needed to go from Flask → Serverless.
"""
import os
import sys

# Ensure backend modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment for production
os.environ.setdefault("NODE_ENV", "production")


def _create_app():
    """Create Flask app (imported lazily to avoid cold-start overhead from unused imports)."""
    from main import create_app
    return create_app()


# ============================================================
# MANGUM HANDLER (Flask → Lambda adapter)
# ============================================================
try:
    from mangum import Mangum
    
    # Create app once (reused across Lambda invocations)
    _app = _create_app()
    
    # Mangum wraps Flask's WSGI interface for Lambda
    handler = Mangum(_app, lifespan="off")
    
except ImportError:
    # Fallback: If mangum is not installed (local dev), use the old handler
    import json
    from app.services.bedrock_service import BedrockService
    from app.services.rag_service import RagService
    from app.core.utils import setup_logging, logger, normalize_query

    setup_logging()
    bedrock_service = BedrockService()
    rag_service = RagService()

    def handler(event, context):
        """Fallback Lambda handler without Mangum."""
        try:
            body = event.get("body", event)
            if isinstance(body, str):
                body = json.loads(body)

            user_query = body.get("text_query", body.get("input_content", ""))
            language = body.get("language", "hi")

            if not user_query:
                return _response(400, {"error": "No query provided"})

            normalized = normalize_query(user_query)
            documents = rag_service.retrieve(normalized)
            context_text = "\n".join(documents)

            result = bedrock_service.generate_response(
                query=normalized,
                context_text=context_text,
                language=language,
            )
            answer_text = result['text']

            return _response(200, {
                "status": "success",
                "query": normalized,
                "answer": {"text": answer_text, "audio": None},
                "meta": {"language": language},
            })

        except Exception as e:
            logger.error(f"Lambda error: {e}")
            return _response(500, {"error": "Something went wrong."})

    def _response(status_code, body):
        return {
            "statusCode": status_code,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            },
            "body": json.dumps(body),
        }
