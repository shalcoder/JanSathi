import json
import sys
import os

# Ensure the current directory is in path for relative imports to work in Lambda
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.execution import process_user_input

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",  # For production, replace with specific origins
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Session-Id,X-Correlation-Id"
}

def lambda_handler(event, context):
    """
    AWS Lambda entry point for JanSathi Agentic Engine.
    """
    # 1. Handle Preflight OPTIONS request
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": ""
        }

    try:
        # 2. Extract Metadata
        path = event.get("rawPath", event.get("path", ""))
        
        # 3. Simple Routing
        if path == "/" or path == "":
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": "JanSathi Agentic Engine API is Live",
                    "version": "1.0.0",
                    "status": "active"
                })
            }

        if path.endswith("/health"):
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({"status": "ok", "action_type": "HEALTH_CHECK"})
            }

        # 4. Parse Event Body
        body = event.get("body", "{}")
        if isinstance(body, str):
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"error": "Invalid JSON in request body"})
                }
        else:
            data = body

        # 5. Extract and Validate Input (for chat/query)
        message = data.get("message")
        session_id = data.get("session_id") or data.get("user_id")

        if message is None or session_id is None:
            # If not a chat query, maybe return 404 for unknown paths
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Missing message or session_id", "path": path})
            }

        # 6. Process Input via Pure Execution Layer
        result = process_user_input(message=str(message), session_id=str(session_id))

        # 7. Return Structured Response
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }
