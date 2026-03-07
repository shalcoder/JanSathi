"""
slot_collection_agent.py — Agent 4: Slot Collection
=====================================================
Responsibilities:
  - Identify which required slots are still missing from state["slots"]
  - Generate a conversational question to ask for the next missing slot
  - Use Nova Lite to generate natural, language-appropriate questions
  - Update state["slots"] with any data already provided in user_query
  - Set state["slots_complete"] = True when all required slots are filled

Routing:
  slots_complete=True  → rules_agent
  slots_complete=False → slot_collection_agent (loops back via conditional edge)
"""
import re
import logging
from typing import Optional

from .state import JanSathiState
from .nova_client import nova_converse, nova_converse_json, build_user_message, NOVA_LITE

logger = logging.getLogger(__name__)

# ── Slot question prompts per slot type ───────────────────────────────────────
SLOT_QUESTIONS = {
    "hi": {
        "age": "आपकी उम्र क्या है? (वर्ष में)",
        "land_area_acres": "आपके पास कितनी जमीन है? (एकड़ में)",
        "state": "आप किस राज्य में रहते हैं?",
        "bank_account_linked": "क्या आपका बैंक खाता आधार से लिंक है? (हाँ/नहीं)",
        "aadhaar_linked": "क्या आपका आधार बैंक खाते से लिंक है? (हाँ/नहीं)",
        "annual_income": "आपकी सालाना पारिवारिक आय कितनी है? (रुपये में)",
        "house_ownership": "क्या आपके पास अपना घर है? (हाँ/नहीं)",
        "family_size": "आपके परिवार में कितने सदस्य हैं?",
        "bpl_card": "क्या आपके पास BPL कार्ड है? (हाँ/नहीं)",
        "occupation": "आपका व्यवसाय क्या है? (किसान/मजदूर/व्यापारी/अन्य)",
        "aadhaar": "आपका आधार नंबर क्या है? (अंतिम 4 अंक पर्याप्त हैं)",
        "mobile": "आपका मोबाइल नंबर क्या है?",
        "loan_amount": "आप कितना लोन लेना चाहते हैं? (रुपये में)",
        "business_type": "आपके व्यवसाय का प्रकार क्या है?",
        "application_id": "आपकी आवेदन आईडी क्या है?",
        "issue_type": "आपकी समस्या किस प्रकार की है? (भुगतान नहीं मिला/अस्वीकृत/अन्य)",
    },
    "en": {
        "age": "What is your age? (in years)",
        "land_area_acres": "How much land do you own? (in acres)",
        "state": "Which state do you live in?",
        "bank_account_linked": "Is your bank account linked to Aadhaar? (yes/no)",
        "aadhaar_linked": "Is your Aadhaar linked to your bank account? (yes/no)",
        "annual_income": "What is your annual family income? (in rupees)",
        "house_ownership": "Do you own a house? (yes/no)",
        "family_size": "How many members are in your family?",
        "bpl_card": "Do you have a BPL card? (yes/no)",
        "occupation": "What is your occupation? (farmer/laborer/trader/other)",
        "aadhaar": "What is your Aadhaar number? (last 4 digits are sufficient)",
        "mobile": "What is your mobile number?",
        "loan_amount": "How much loan do you want? (in rupees)",
        "business_type": "What type of business do you have?",
        "application_id": "What is your application ID?",
        "issue_type": "What type of issue are you facing? (payment not received/rejected/other)",
    },
}

EXTRACT_PROMPT = """Extract user-provided data from the following utterance and return ONLY a JSON object.
The JSON should contain only fields the user has explicitly mentioned.

Required fields to look for: {required_slots}
User utterance: {query}

Return format (only include present fields):
{{
  "age": <number or null>,
  "land_area_acres": <number or null>,
  "state": "<state name or null>",
  "bank_account_linked": <true/false or null>,
  "aadhaar_linked": <true/false or null>,
  "annual_income": <number or null>,
  "house_ownership": <true/false or null>,
  "family_size": <number or null>,
  "bpl_card": <true/false or null>,
  "occupation": "<string or null>",
  "mobile": "<string or null>",
  "loan_amount": <number or null>,
  "business_type": "<string or null>",
  "application_id": "<string or null>",
  "issue_type": "<string or null>"
}}
Return ONLY fields the user explicitly stated. Omit null fields."""


def slot_collection_agent(state: JanSathiState) -> JanSathiState:
    """
    Agent 4: Slot Collection Agent.
    Extracts slots from user query, identifies missing ones, generates next question.
    """
    session_id = state.get("session_id", "unknown")
    query = state.get("user_query", "")
    required_slots = state.get("required_slots", [])
    current_slots = dict(state.get("slots", {}))
    language = state.get("language", "hi")
    intent = state.get("intent", "info")

    logger.info(f"[SlotAgent] session={session_id} intent={intent} required={required_slots}")

    # ── Skip slot collection for info/fallback intents ────────────────────────
    if intent in ("info", "fallback") or not required_slots:
        updated = dict(state)
        updated["slots_complete"] = True
        return updated

    # ── Extract new slot values from user_query ───────────────────────────────
    if query:
        extracted = _extract_slots_from_query(query, required_slots)
        for key, value in extracted.items():
            if value is not None and key in required_slots:
                current_slots[key] = value
                logger.info(f"[SlotAgent] Extracted slot '{key}' = {value}")

    # ── Check which slots are still missing ───────────────────────────────────
    missing_slots = [s for s in required_slots if s not in current_slots or current_slots[s] is None]

    updated = dict(state)
    updated["slots"] = current_slots

    if not missing_slots:
        logger.info(f"[SlotAgent] All slots collected: {current_slots}")
        updated["slots_complete"] = True
        return updated

    # ── Generate next question for first missing slot ─────────────────────────
    next_slot = missing_slots[0]
    question = _get_slot_question(next_slot, language)

    logger.info(f"[SlotAgent] Missing slots: {missing_slots}. Asking for '{next_slot}'")

    updated["slots_complete"] = False
    updated["response_text"] = question
    return updated


def _extract_slots_from_query(query: str, required_slots: list) -> dict:
    """Use Nova Micro to extract slot values from user utterance."""
    if not query.strip():
        return {}

    # Quick rule-based extraction for common patterns
    extracted = {}

    # Age extraction
    if "age" in required_slots:
        age_match = re.search(r'\b(\d{1,3})\s*(साल|year|वर्ष|yr)', query.lower())
        if age_match:
            extracted["age"] = int(age_match.group(1))

    # Number extraction (income, land)
    if "annual_income" in required_slots:
        income_match = re.search(r'(\d[\d,]*)\s*(rupees?|rs\.?|₹|रुपये?)', query.lower())
        if income_match:
            extracted["annual_income"] = int(income_match.group(1).replace(",", ""))

    # Land area extraction
    if "land_area_acres" in required_slots:
        land_match = re.search(r'(\d+\.?\d*)\s*(acre|एकड़)', query.lower())
        if land_match:
            extracted["land_area_acres"] = float(land_match.group(1))

    # Yes/No extraction
    yes_words = ["yes", "haan", "हाँ", "ha", "ji haan", "true"]
    no_words = ["no", "nahi", "नहीं", "nhi", "false"]
    query_lower = query.lower()

    for slot in ["bank_account_linked", "aadhaar_linked", "house_ownership", "bpl_card"]:
        if slot in required_slots:
            if any(w in query_lower for w in yes_words):
                extracted[slot] = True
            elif any(w in query_lower for w in no_words):
                extracted[slot] = False

    # State extraction
    if "state" in required_slots:
        states = [
            "Uttar Pradesh", "Maharashtra", "Rajasthan", "Bihar", "Madhya Pradesh",
            "Gujarat", "Karnataka", "Andhra Pradesh", "Tamil Nadu", "Telangana",
            "West Bengal", "Kerala", "Odisha", "Punjab", "Haryana", "Assam",
            "Jharkhand", "Uttarakhand", "Himachal Pradesh", "Chhattisgarh",
        ]
        for s in states:
            if s.lower() in query_lower:
                extracted["state"] = s
                break

    # Family size
    if "family_size" in required_slots:
        family_match = re.search(r'\b([2-9]|1[0-9])\s*(member|log|लोग|सदस्य)', query_lower)
        if family_match:
            extracted["family_size"] = int(family_match.group(1))

    return extracted


def _get_slot_question(slot: str, language: str) -> str:
    """Get the question for a specific slot in the user's language."""
    lang = language if language in SLOT_QUESTIONS else "en"
    return SLOT_QUESTIONS[lang].get(slot, f"Please provide your {slot}.")


def should_continue_slot_collection(state: JanSathiState) -> str:
    """
    Conditional edge after slot_collection_agent.
    Loops back if slots are incomplete, moves forward if done.
    """
    if state.get("slots_complete", False):
        return "rules_agent"
    return "__end__"  # Return early with the question — client must re-invoke with answer
