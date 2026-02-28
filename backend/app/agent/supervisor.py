from .intent_router import detect_intent

def execute_agent(request_data: dict):

    intent = detect_intent(request_data["message"])

    return {
        "response": f"Agent received request. Detected intent: {intent}",
        "intent": intent
    }
