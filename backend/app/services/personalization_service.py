"""
Personalization Service – JanSathi Round 2
Enriches LLM prompts with profile-aware context before agent processing.
"""
from typing import Optional


def build_personalization_context(user_profile: dict) -> dict:
    """
    Input:  user_profile dict from /v1/query request body
    Output: personalization context injected into the LLM system prompt
    """
    state = (user_profile.get("state") or "").lower()
    occupation = (user_profile.get("occupation") or "").lower()
    income_bracket = (user_profile.get("income_bracket") or "").lower()
    region = (user_profile.get("region") or user_profile.get("district") or "").lower()
    language = (user_profile.get("language") or "hi").lower()

    # ── Tone modifier ────────────────────────────────────────────────────────
    tone = "formal_hindi"
    if language.startswith("en"):
        tone = "formal_english"
    elif language.startswith("ta"):
        tone = "formal_tamil"

    # ── CSC / Portal recommendation ──────────────────────────────────────────
    csc_link: Optional[str] = None
    portal_link: Optional[str] = None

    if state in ("uttar pradesh", "up", "bihar", "rajasthan", "madhya pradesh", "mp"):
        csc_link = "https://locator.csccloud.in/"
    elif state in ("maharashtra", "karnataka", "telangana", "andhra pradesh"):
        portal_link = "https://mahadbt.maharashtra.gov.in" if state == "maharashtra" else "https://apna.gov.in"
    elif state in ("tamil nadu", "tn"):
        portal_link = "https://www.tn.gov.in/scheme"
    else:
        csc_link = "https://locator.csccloud.in/"

    # ── System prompt injection ───────────────────────────────────────────────
    lines = [
        f"User Profile: state={state or 'unknown'}, occupation={occupation or 'unknown'}, income={income_bracket or 'unknown'}.",
        f"Respond in {tone.replace('_', ' ')} language, keeping answers concise and actionable.",
    ]

    if occupation in ("farmer", "kisan", "agricultural"):
        lines.append("User is a small farmer. Mention PM-Kisan, Kisan Credit Card, and crop insurance schemes where relevant.")
    elif occupation in ("labourer", "worker", "daily wage", "unorganised"):
        lines.append("User is an unorganised worker. Mention E-Shram, PMGKY, and BOCW schemes where relevant.")
    elif occupation in ("urban", "salaried", "govt"):
        lines.append("User is likely urban. Prefer online portal links over CSC recommendations.")

    if income_bracket in ("low", "bpl", "ews"):
        lines.append("User is in low income / EWS bracket. Prioritise zero-cost schemes and BPL entitlements.")

    if csc_link:
        lines.append(f"Nearest service option: Common Service Centre (CSC) at {csc_link}")
    elif portal_link:
        lines.append(f"Preferred online portal: {portal_link}")

    return {
        "system_prompt_injection": " ".join(lines),
        "tone_modifier": tone,
        "suggested_csc_link": csc_link,
        "suggested_portal_link": portal_link,
        "resolved_state": state,
        "resolved_occupation": occupation,
    }
