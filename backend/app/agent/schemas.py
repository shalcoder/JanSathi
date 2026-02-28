def validate_agent_request(data: dict):
    required_fields = ["user_id", "channel", "input_type", "message"]

    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"

    return True, None
