import json
import sys
import os

# Ensure the current directory is in path for relative imports to work in Lambda
# (Optional: depends on how the Lambda is packaged, but safe to include)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.execution import process_user_input

def lambda_handler(event, context):
    """
    AWS Lambda entry point for JanSathi Agentic Engine.
    Exposes the engine as a serverless function without Flask.
    """
    try:
        # 1. Parse Event Body
        body = event.get("body", "{}")
        
        # Lambda Proxy Integration sends body as a string
        if isinstance(body, str):
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid JSON in request body"})
                }
        else:
            data = body

        # 2. Extract and Validate Input
        message = data.get("message")
        session_id = data.get("session_id") or data.get("user_id")

        if message is None or session_id is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing message or session_id"})
            }

        # 3. Process Input via Pure Execution Layer
        result = process_user_input(message=str(message), session_id=str(session_id))

        # 4. Return Structured Response
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
