"""
rules_agent.py — Agent 5: Deterministic Eligibility Engine
===========================================================
Responsibilities:
  - Load scheme eligibility rules (from YAML or DB)
  - Run them through the existing deterministic RulesEngine
  - NO LLM involved — 100% deterministic validation
  - Set state["eligibility_result"] = {eligible, breakdown, score}

JanSathi design principle:
  "Deterministic rules always override LLM outputs."
"""
import os
import json
import logging
import sys

from .state import JanSathiState

logger = logging.getLogger(__name__)

# ── Embedded scheme rules (used when YAML DB not available) ───────────────────
# Each scheme has mandatory rules evaluated against user slots.
SCHEME_RULES: dict = {
    "pm_kisan": {
        "mandatory": [
            {
                "field": "age",
                "operator": "gte",
                "value": 18,
                "label": "Age must be 18 or above",
                "citation": "PM-KISAN Guidelines: Farmer must be 18+ years",
            },
            {
                "field": "land_area_acres",
                "operator": "gt",
                "value": 0,
                "label": "Must own cultivable land",
                "citation": "PM-KISAN Guidelines: Beneficiary must hold cultivable land",
            },
            {
                "field": "bank_account_linked",
                "operator": "eq",
                "value": True,
                "label": "Bank account must be Aadhaar-linked",
                "citation": "PM-KISAN DBT: Bank account with Aadhaar seeding required",
            },
        ]
    },
    "pm_awas_urban": {
        "mandatory": [
            {
                "field": "annual_income",
                "operator": "lte",
                "value": 300000,
                "label": "Annual income ≤ ₹3,00,000 (EWS/LIG)",
                "citation": "PMAY-Urban Guidelines: EWS family income ≤ ₹3 lakh/year",
            },
            {
                "field": "house_ownership",
                "operator": "eq",
                "value": False,
                "label": "Must not already own a pucca house",
                "citation": "PMAY-Urban: Beneficiary must not possess a pucca house",
            },
        ]
    },
    "pm_awas_gramin": {
        "mandatory": [
            {
                "field": "bpl_card",
                "operator": "eq",
                "value": True,
                "label": "Must hold BPL card",
                "citation": "PMAY-Gramin: BPL household priority",
            },
            {
                "field": "house_ownership",
                "operator": "eq",
                "value": False,
                "label": "Must not own a pucca house",
                "citation": "PMAY-Gramin eligibility criteria",
            },
        ]
    },
    "e_shram": {
        "mandatory": [
            {
                "field": "age",
                "operator": "gte",
                "value": 16,
                "label": "Age must be 16 or above",
                "citation": "e-Shram Portal: Workers aged 16-59 eligible",
            },
            {
                "field": "age",
                "operator": "lte",
                "value": 59,
                "label": "Age must be 59 or below",
                "citation": "e-Shram Portal: Workers aged 16-59 eligible",
            },
        ]
    },
    "pmjay": {
        "mandatory": [
            {
                "field": "annual_income",
                "operator": "lte",
                "value": 500000,
                "label": "Annual income ≤ ₹5,00,000",
                "citation": "PM-JAY: Economically vulnerable families",
            },
        ]
    },
    "mudra": {
        "mandatory": [
            {
                "field": "business_type",
                "operator": "ne",
                "value": None,
                "label": "Must have a business type specified",
                "citation": "PM Mudra Yojana: For non-farm enterprise activities",
            },
        ]
    },
    "unknown": {
        "mandatory": []  # No rules for unknown scheme — default eligible
    },
}


def rules_agent(state: JanSathiState) -> JanSathiState:
    """
    Agent 5: Deterministic Rules Agent.
    Evaluates user slots against scheme eligibility rules.
    NO LLM — pure deterministic logic.
    """
    session_id = state.get("session_id", "unknown")
    scheme_hint = state.get("scheme_hint", "unknown")
    slots = state.get("slots", {})
    intent = state.get("intent", "info")

    logger.info(f"[RulesAgent] session={session_id} scheme={scheme_hint} slots={slots}")

    # ── For non-apply intents, skip eligibility rules ─────────────────────────
    if intent not in ("apply",):
        updated = dict(state)
        updated["eligibility_result"] = {
            "eligible": True,
            "breakdown": [{"label": "No eligibility check for this intent", "pass": True}],
            "score": 1.0,
        }
        return updated

    # ── Load scheme rules ─────────────────────────────────────────────────────
    rules = SCHEME_RULES.get(scheme_hint, SCHEME_RULES.get("unknown", {"mandatory": []}))

    # ── Try to load from app DB (optional enrichment) ─────────────────────────
    db_rules = _load_rules_from_db(scheme_hint)
    if db_rules:
        rules = db_rules

    # ── Run deterministic RulesEngine ─────────────────────────────────────────
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from app.services.rules_engine import RulesEngine
        engine = RulesEngine()
        eligible, breakdown, score = engine.evaluate(user_profile=slots, rules=rules)
    except Exception as e:
        logger.error(f"[RulesAgent] RulesEngine failed: {e}")
        eligible, breakdown, score = True, [], 0.75

    logger.info(
        f"[RulesAgent] session={session_id} eligible={eligible} score={score:.2f} "
        f"breakdown_count={len(breakdown)}"
    )

    updated = dict(state)
    updated["eligibility_result"] = {
        "eligible": eligible,
        "breakdown": breakdown,
        "score": float(score),
    }
    return updated


def _load_rules_from_db(scheme_hint: str) -> dict:
    """
    Attempt to load eligibility rules from the scheme DB.
    Returns None if unavailable (falls back to hardcoded SCHEME_RULES).
    """
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from app.models.models import Scheme
        scheme = Scheme.query.filter_by(scheme_id=scheme_hint).first()
        if scheme and hasattr(scheme, "eligibility_rules") and scheme.eligibility_rules:
            rules = scheme.eligibility_rules
            if isinstance(rules, str):
                rules = json.loads(rules)
            return rules
    except Exception:
        pass
    return {}
