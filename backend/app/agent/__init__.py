from flask import Blueprint, request, jsonify
from .schemas import validate_agent_request
from .supervisor import execute_agent

agent_bp = Blueprint("agent", __name__)

@agent_bp.route("/execute", methods=["POST"])
def agent_execute():

    data = request.get_json()

    is_valid, error = validate_agent_request(data)

    if not is_valid:
        return jsonify({"error": error}), 400

    result = execute_agent(data)

    return jsonify(result), 200
