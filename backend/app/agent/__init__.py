from flask import Blueprint, request, jsonify
from .schemas import validate_agent_request

agent_bp = Blueprint("agent", __name__)

@agent_bp.route("/execute", methods=["POST"])
def agent_execute():
    """
    /agent/execute — routes through the full JanSathiSupervisor (9-agent pipeline).
    """
    data = request.get_json() or {}
    is_valid, error = validate_agent_request(data)
    if not is_valid:
        return jsonify({"error": error}), 400

    from app.agent.supervisor import execute_agent
    result = execute_agent(data)
    return jsonify(result), 200


@agent_bp.route("/orchestrate", methods=["POST"])
def agent_orchestrate():
    """Alias: /agent/orchestrate — identical to /v1/orchestrate."""
    data = request.get_json() or {}
    from app.agent.supervisor import get_supervisor
    result = get_supervisor().orchestrate(data)
    return jsonify(result), 200

