from app.services.intent_service import IntentService

def route_request(user_query: str):
    """
    Routes the user request to the appropriate agent based on detected intent.
    Uses IntentService for classification.
    """
    intent_service = IntentService()
    intent_result = intent_service.classify_intent(user_query)
    intent = intent_result["intent"]

    if intent == "eligibility_check":
        return handle_eligibility_agent(user_query)
    elif intent == "document_required":
        return handle_document_agent(user_query)
    elif intent == "scheme_lookup":
        return handle_scheme_agent(user_query)
    else:
        return handle_general_agent(user_query)

def handle_eligibility_agent(query: str):
    return {
        "response": "Eligibility Agent: Checking your eligibility for schemes...",
        "intent": "eligibility_check"
    }

def handle_document_agent(query: str):
    return {
        "response": "Document Agent: Listing required documents for your request...",
        "intent": "document_required"
    }

def handle_scheme_agent(query: str):
    return {
        "response": "Scheme Agent: Looking up the specified scheme details...",
        "intent": "scheme_lookup"
    }

def handle_general_agent(query: str):
    return {
        "response": "General Agent: How can I help you today with JanSathi?",
        "intent": "general_query"
    }
