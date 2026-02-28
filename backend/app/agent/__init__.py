from flask import Blueprint, request, jsonify
from .schemas import validate_agent_request
from app.core.execution import process_user_input

agent_bp = Blueprint("agent", __name__)

@agent_bp.route("/execute", methods=["POST"])
def agent_execute():
    """
    Refactored endpoint to use the deterministic Agentic Core Engine.
    Uses app.core.execution as a bridge to decapitate Flask dependencies.
    """
    data = request.get_json()

    is_valid, error = validate_agent_request(data)

    if not is_valid:
        return jsonify({"error": error}), 400

    # Extract required fields for the engine
    message = data.get("message")
    session_id = data.get("user_id")

    # Bridge to the pure execution layer
    result = process_user_input(message=message, session_id=session_id)

    return jsonify(result), 200
