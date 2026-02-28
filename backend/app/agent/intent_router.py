def detect_intent(message: str) -> str:
    msg = message.lower()

    if "apply" in msg:
        return "APPLY"
    elif "status" in msg:
        return "STATUS"
    elif "eligible" in msg:
        return "ELIGIBILITY"
    else:
        return "DISCOVER"
