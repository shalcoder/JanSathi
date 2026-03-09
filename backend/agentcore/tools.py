"""
agentcore/tools.py — JanSathi Tool Definitions for Bedrock AgentCore
====================================================================
Each function here becomes an "Action Group" in the Bedrock Agent.
AgentCore will call these tools when orchestrating the agent pipeline.

Tool design: each tool represents one major LangGraph agent node,
with clear input/output schemas that AgentCore can parse and route.
"""
import json
import logging
import sys
import os
import inspect
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# Ensure backend/ is in path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Tool 1: Classify Intent ────────────────────────────────────────────────────

def classify_intent(query: str, language: str = "hi", session_id: str = "") -> dict:
    """
    Classify the user's intent from their query.
    Returns intent, confidence, scheme_hint, and required_slots.
    """
    try:
        from app.services.intent_service import IntentService
        svc = IntentService()
        result = svc.classify_intent_ivr(query, language)
        return {
            "success": True,
            "intent": result.get("intent", "info"),
            "confidence": result.get("confidence", 0.75),
            "scheme_hint": result.get("scheme_hint", "unknown"),
            "language_detected": result.get("language_detected", language),
            "required_slots": result.get("required_slots", []),
        }
    except Exception as e:
        logger.error(f"[Tool:classify_intent] Error: {e}")
        return {"success": False, "error": str(e), "intent": "fallback"}


# ── Tool 2: Retrieve Knowledge ────────────────────────────────────────────────

def retrieve_knowledge(
    query: str,
    scheme_hint: str = "unknown",
    language: str = "hi",
    intent: str = "info",
    session_id: str = "",
    **_extra,
) -> dict:
    """
    Retrieve relevant scheme information from the knowledge base.
    Returns a list of context chunks about the scheme.
    """
    try:
        # Some Agent planners include metadata fields in every tool call.
        # Keep signature tolerant while preserving existing retrieval behavior.
        _ = intent, session_id

        q = (query or "").lower()
        if any(k in q for k in ["available schemes", "what schemes", "list schemes", "all schemes", "yojana list"]):
            # App-context-free fallback: read local YAML catalog directly.
            catalog_path = Path(__file__).resolve().parent.parent / "app" / "data" / "schemes_config.yaml"
            lines = ["Available government schemes you can explore:"]
            if catalog_path.exists():
                with catalog_path.open("r", encoding="utf-8") as f:
                    parsed = yaml.safe_load(f) or {}
                schemes = parsed.get("schemes", {}) if isinstance(parsed, dict) else {}
                for i, (sid, item) in enumerate(schemes.items(), start=1):
                    if i > 8:
                        break
                    if not isinstance(item, dict):
                        continue
                    title = str(item.get("display_name") or sid.replace("_", " ").title())
                    benefit = str(item.get("description") or "Check official portal for details")
                    sources = item.get("sources") if isinstance(item.get("sources"), list) else []
                    link = "https://myscheme.gov.in"
                    if sources and isinstance(sources[0], dict) and sources[0].get("url"):
                        link = str(sources[0].get("url"))
                    lines.append(f"{i}. {title} - {benefit}. Official link: {link}")

            if len(lines) > 1:
                return {
                    "success": True,
                    "context_chunks": lines,
                    "source_count": len(lines),
                }

        if any(k in q for k in ["new scheme", "new schemes", "latest scheme", "latest schemes", "today scheme", "today schemes"]):
            catalog_path = Path(__file__).resolve().parent.parent / "app" / "data" / "schemes_config.yaml"
            lines = ["Latest discoverable schemes and updates (official sources):"]

            # Include currently supported schemes from local verified catalog.
            if catalog_path.exists():
                with catalog_path.open("r", encoding="utf-8") as f:
                    parsed = yaml.safe_load(f) or {}
                schemes = parsed.get("schemes", {}) if isinstance(parsed, dict) else {}
                for i, (sid, item) in enumerate(schemes.items(), start=1):
                    if i > 6:
                        break
                    if not isinstance(item, dict):
                        continue
                    title = str(item.get("display_name") or sid.replace("_", " ").title())
                    desc = str(item.get("description") or "Official scheme details available on portal")
                    sources = item.get("sources") if isinstance(item.get("sources"), list) else []
                    link = "https://www.myscheme.gov.in/"
                    if sources and isinstance(sources[0], dict) and sources[0].get("url"):
                        link = str(sources[0].get("url"))
                    lines.append(f"{i}. {title} - {desc}. Source: {link}")

            # Enrich with live web discovery snippets.
            try:
                from app.services.live_fetch_service import LiveFetchService
                live = LiveFetchService().fetch(query=query, scheme_hint=scheme_hint, max_items=3)
                if live:
                    lines.append("Live source checks:")
                    lines.extend(live)
            except Exception as e:
                logger.warning(f"[Tool:retrieve_knowledge] live fetch for latest schemes skipped: {e}")

            lines.append("For continuously updated catalog, check: https://www.myscheme.gov.in/")
            return {
                "success": True,
                "context_chunks": lines[:8],
                "source_count": len(lines),
            }

        if any(k in q for k in ["pm awas", "pmay", "awas yojana"]) and any(
            k in q for k in ["status", "track", "application status", "beneficiary"]
        ):
            steps = [
                "I cannot directly read your personal PMAY application status from government systems yet because this assistant is not integrated with a citizen-authenticated PMAY status API.",
                "PMAY-Urban: open https://pmaymis.gov.in and go to the beneficiary/application status section.",
                "Keep these ready: application/reference ID, registered mobile, and state/ULB details (as requested on portal).",
                "PMAY-Gramin: open https://pmayg.nic.in and check beneficiary/status details.",
                "If you share your application/reference ID format, I can guide each screen step-by-step.",
            ]
            return {"success": True, "context_chunks": steps, "source_count": len(steps)}

        live_results = []
        try:
            from app.services.live_fetch_service import LiveFetchService
            live_results = LiveFetchService().fetch(query=query, scheme_hint=scheme_hint, max_items=3)
        except Exception as e:
            logger.warning(f"[Tool:retrieve_knowledge] live fetch skipped: {e}")

        from app.services.rag_service import RagService
        rag = RagService()
        enriched_query = f"{scheme_hint.replace('_', ' ')} {query}"
        results = rag.retrieve(enriched_query, language=language)

        generic_kb_only = (
            isinstance(results, list)
            and len(results) > 0
            and all("visit india.gov.in" in str(r).lower() for r in results)
        )

        if live_results:
            # Prioritize fresh official snippets; only append KB chunks when informative.
            tail = []
            if isinstance(results, list) and not generic_kb_only:
                tail = results[:2]
            results = live_results + tail

        no_kb_answer = (not results or all("visit india.gov.in" in str(r).lower() for r in results))

        if no_kb_answer:
            catalog_path = Path(__file__).resolve().parent.parent / "app" / "data" / "schemes_config.yaml"
            if catalog_path.exists():
                with catalog_path.open("r", encoding="utf-8") as f:
                    parsed = yaml.safe_load(f) or {}
                schemes = parsed.get("schemes", {}) if isinstance(parsed, dict) else {}

                matched_id = None
                if any(k in q for k in ["pm awas", "pmay", "awas yojana"]):
                    matched_id = "pm_awas_urban"
                elif any(k in q for k in ["pm-kisan", "pm kisan", "pmkisan"]):
                    matched_id = "pm_kisan"
                elif any(k in q for k in ["e-shram", "eshram", "shram"]):
                    matched_id = "e_shram"

                scheme = schemes.get(matched_id) if matched_id else None
                if isinstance(scheme, dict):
                    display = str(scheme.get("display_name") or matched_id.replace("_", " ").title())
                    description = str(scheme.get("description") or "")
                    rules = scheme.get("rules", {}) if isinstance(scheme.get("rules"), dict) else {}
                    mandatory = rules.get("mandatory", []) if isinstance(rules.get("mandatory"), list) else []
                    sources = scheme.get("sources", []) if isinstance(scheme.get("sources"), list) else []
                    source_url = "https://myscheme.gov.in"
                    if sources and isinstance(sources[0], dict) and sources[0].get("url"):
                        source_url = str(sources[0].get("url"))

                    lines = [f"{display}: {description}"]
                    if "eligib" in q and mandatory:
                        lines.append("Eligibility criteria:")
                        for i, rule in enumerate(mandatory[:6], start=1):
                            if isinstance(rule, dict):
                                lines.append(f"{i}. {rule.get('label', 'Check official guideline criteria')}")
                    elif mandatory:
                        lines.append("Key eligibility checks include income and housing/asset criteria as per official guidelines.")

                    lines.append(f"Official source: {source_url}")
                    results = lines

        if no_kb_answer and (
            "pm-kisan" in q or "pm kisan" in q or "pmkisan" in q
        ) and ("status" in q or "installment" in q):
            results = [
                "To check PM-Kisan status, open https://pmkisan.gov.in/BeneficiaryStatus_New.aspx and use Aadhaar Number, Account Number, or Mobile Number.",
                "You can also check payment details at https://pfms.nic.in via 'Know Your Payments'.",
            ]

        return {
            "success": True,
            "context_chunks": results[:4],
            "source_count": len(results),
        }
    except Exception as e:
        logger.error(f"[Tool:retrieve_knowledge] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "context_chunks": ["Please visit india.gov.in for scheme information."],
        }


# ── Tool 3: Validate Eligibility ──────────────────────────────────────────────

def validate_eligibility(slots: dict, scheme_hint: str = "unknown") -> dict:
    """
    Deterministically validate user eligibility for a scheme.
    Uses the RulesEngine — NO LLM involved.
    Returns eligible (bool), score (0-1), and breakdown.
    """
    # Import embedded rules from rules_agent
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from agents.rules_agent import SCHEME_RULES
        from app.services.rules_engine import RulesEngine

        rules = SCHEME_RULES.get(scheme_hint, SCHEME_RULES.get("unknown", {"mandatory": []}))
        engine = RulesEngine()
        eligible, breakdown, score = engine.evaluate(user_profile=slots, rules=rules)
        return {
            "success": True,
            "eligible": eligible,
            "score": float(score),
            "breakdown": breakdown,
        }
    except Exception as e:
        logger.error(f"[Tool:validate_eligibility] Error: {e}")
        return {"success": False, "error": str(e), "eligible": False, "score": 0.0}


# ── Tool 4: Compute Risk & Route ─────────────────────────────────────────────

def compute_risk_score(
    session_id: str,
    rules_score: float,
    eligible: bool,
    intent_confidence: float = 0.85,
    asr_confidence: float = 1.0,
) -> dict:
    """
    Compute composite risk score and determine routing decision.
    Returns: risk_score, decision (AUTO_SUBMIT|HITL_QUEUE|NOT_ELIGIBLE_NOTIFY), reasons.
    """
    try:
        from app.services.verifier_service import VerifierService
        verifier = VerifierService()
        result = verifier.assess(
            session_id=session_id,
            rules_score=rules_score,
            eligible=eligible,
            asr_confidence=asr_confidence,
            intent_confidence=intent_confidence,
        )
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"[Tool:compute_risk_score] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "decision": "NOT_ELIGIBLE_NOTIFY",
            "risk_score": 0.0,
        }


# ── Tool 5: Generate Response ─────────────────────────────────────────────────

def generate_response(
    query: str,
    context_chunks: list,
    language: str = "hi",
    intent: str = "info",
    scheme_hint: str = "unknown",
    eligibility_status: str = "unknown",
) -> dict:
    """
    Generate the final AI response using Amazon Nova Lite.
    Returns the response text and a Benefit Receipt if eligible.
    """
    try:
        from app.services.bedrock_service import BedrockService
        context_text = "\n\n".join(context_chunks[:3]) if context_chunks else ""
        bedrock = BedrockService()
        result = bedrock.generate_response(
            query,
            context_text,
            language,
            intent,
            scheme_hint=scheme_hint,
        )
        return {
            "success": True,
            "response_text": result.get("text", ""),
            "provenance": result.get("provenance", "unknown"),
        }
    except Exception as e:
        logger.error(f"[Tool:generate_response] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "response_text": "कृपया india.gov.in पर जाएं / Please visit india.gov.in",
        }


def generate_final_response(
    decision: str = "INFO",
    context: str = "",
    query: str = "",
    language: str = "en",
    intent: str = "info",
    **_extra,
) -> dict:
    """Compatibility wrapper for planner calls that use generate_final_response."""
    _ = decision
    text_context = context if isinstance(context, str) else json.dumps(context, ensure_ascii=False)
    inferred_query = query or "User asked for scheme information"
    return generate_response(
        query=inferred_query,
        context_chunks=[text_context] if text_context else [],
        language=language,
        intent=intent,
    )


# ── Tool 6: Send SMS Notification ─────────────────────────────────────────────

def send_sms_notification(
    phone: str, scheme: str, case_id: str, notification_type: str = "submission"
) -> dict:
    """
    Send SMS notification to the citizen via AWS SNS.
    notification_type: 'submission' | 'hitl_queued' | 'rejected'
    """
    try:
        from app.services.notify_service import NotifyService
        notify = NotifyService()
        if notification_type == "submission":
            result = notify.notify_submission(phone, scheme, case_id)
        elif notification_type == "hitl_queued":
            result = notify.notify_hitl_queued(phone, scheme, case_id)
        else:
            result = notify.notify_rejected(phone, scheme, case_id)
        return {"success": result.get("success", False), "message_id": result.get("message_id", "")}
    except Exception as e:
        logger.error(f"[Tool:send_sms_notification] Error: {e}")
        return {"success": False, "error": str(e)}


# ── Tool 7: Enqueue HITL Case ────────────────────────────────────────────────

def enqueue_hitl_case(
    session_id: str,
    transcript: str,
    response_text: str,
    confidence: float,
    slots: dict = None,
) -> dict:
    """
    Escalate a case to the Human-in-the-Loop review queue.
    Returns the HITL case ID.
    """
    try:
        from app.services.hitl_service import HITLService
        hitl = HITLService()
        case = hitl.enqueue_case(
            session_id=session_id,
            turn_id=f"turn-{session_id}",
            transcript=transcript,
            response_text=response_text,
            confidence=confidence,
            slots=slots or {},
        )
        return {"success": True, "case_id": case.get("id", ""), "status": case.get("status", "")}
    except Exception as e:
        logger.error(f"[Tool:enqueue_hitl_case] Error: {e}")
        return {"success": False, "error": str(e), "case_id": ""}


# ── Tool 8: Fetch Live Schemes ────────────────────────────────────────────────

def fetch_live_schemes(
    state: str = "UP",
    occupation: str = "farmer",
    income: int = 120000,
    language: str = "hi",
) -> dict:
    """
    Fetch live, personalised scheme recommendations for the citizen.
    Uses the SchemeFeedService which queries Kendra + rules engine.
    Returns top matching schemes with apply links.
    """
    try:
        from app.services.scheme_feed_service import SchemeFeedService
        user_profile = {"state": state, "occupation": occupation, "income": income}
        result = SchemeFeedService().get_schemes(user_profile=user_profile, language=language)
        schemes = result.get("schemes", [])[:5]
        return {
            "success": True,
            "schemes": [
                {
                    "id": s.get("id", ""),
                    "title": s.get("title", ""),
                    "benefit": s.get("benefit", ""),
                    "apply_link": s.get("apply_link", ""),
                    "eligibility_score": s.get("eligibility_score", 0),
                }
                for s in schemes
            ],
            "count": len(schemes),
        }
    except Exception as e:
        logger.error(f"[Tool:fetch_live_schemes] Error: {e}")
        return {"success": False, "error": str(e), "schemes": []}


def fetch_live_updates(query: str, scheme_hint: str = "unknown") -> dict:
    """Fetch near-real-time snippets from official public scheme sources."""
    try:
        from app.services.live_fetch_service import LiveFetchService
        snippets = LiveFetchService().fetch(query=query, scheme_hint=scheme_hint, max_items=4)
        return {
            "success": True,
            "updates": snippets,
            "count": len(snippets),
        }
    except Exception as e:
        logger.error(f"[Tool:fetch_live_updates] Error: {e}")
        return {"success": False, "error": str(e), "updates": []}


# ── Tool 9: Create Benefit Receipt ───────────────────────────────────────────

def create_benefit_receipt(
    session_id: str,
    scheme_name: str = "pm_kisan",
    eligible: bool = False,
    rules_score: float = 0.0,
    slots: dict = None,
    language: str = "hi",
) -> dict:
    """
    Generate a formal benefit eligibility receipt (HTML + S3 upload).
    Called after eligibility validation is complete.
    Returns receipt URL and case ID.
    """
    try:
        from app.services.receipt_service import ReceiptService
        receipt = ReceiptService().generate_receipt(
            session_id=session_id,
            scheme_name=scheme_name,
            eligible=eligible,
            rules_trace=[],
            rules_score=rules_score,
            slots=slots or {},
            language=language,
        )
        return {
            "success": True,
            "case_id": receipt.get("case_id", ""),
            "receipt_url": receipt.get("receipt_url", ""),
            "eligible": eligible,
        }
    except Exception as e:
        logger.error(f"[Tool:create_benefit_receipt] Error: {e}")
        return {"success": False, "error": str(e), "case_id": ""}


# ── Tool registry (for AgentCore Action Group schema generation) ──────────────

TOOL_REGISTRY = {
    "classify_intent": classify_intent,
    "retrieve_knowledge": retrieve_knowledge,
    "validate_eligibility": validate_eligibility,
    "compute_risk_score": compute_risk_score,
    "generate_response": generate_response,
    "generate_final_response": generate_final_response,
    "send_sms_notification": send_sms_notification,
    "enqueue_hitl_case": enqueue_hitl_case,
    "fetch_live_schemes": fetch_live_schemes,
    "fetch_live_updates": fetch_live_updates,
    "create_benefit_receipt": create_benefit_receipt,
}


def dispatch_tool(tool_name: str, parameters: dict) -> dict:
    """Dispatch a tool call by name. Used by the AgentCore invoke handler."""
    if tool_name not in TOOL_REGISTRY:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    tool_fn = TOOL_REGISTRY[tool_name]
    try:
        # Bedrock may send extra planner metadata (e.g., intent/session_id) that
        # a specific tool does not declare. Filter unknown kwargs to avoid hard-failing.
        signature = inspect.signature(tool_fn)
        accepts_var_kwargs = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in signature.parameters.values()
        )

        if accepts_var_kwargs:
            filtered_params = parameters
        else:
            allowed = set(signature.parameters.keys())
            filtered_params = {k: v for k, v in parameters.items() if k in allowed}

            dropped = [k for k in parameters.keys() if k not in allowed]
            if dropped:
                logger.warning(
                    f"[ActionGroup] Ignoring unsupported params for {tool_name}: {dropped}"
                )

        return tool_fn(**filtered_params)
    except TypeError as e:
        return {"success": False, "error": f"Invalid parameters for {tool_name}: {e}"}


# ── AWS Lambda Entry Point ────────────────────────────────────────────────────
# Deploy this file as a standalone Lambda function (jansathi-action-group).
# Bedrock Agent calls it as an Action Group executor — no Return Control loop needed.
# IAM: this Lambda needs bedrock:InvokeModel, kendra:Query, dynamodb:*, sns:Publish, s3:PutObject

def lambda_handler(event: dict, context) -> dict:
    """
    Bedrock Agent Action Group Lambda handler.

    Bedrock sends one of two formats:
      Function-based: {"actionGroup": "...", "function": "classify_intent", "parameters": [{name, value}, ...]}
      API-schema:     {"actionGroup": "...", "apiPath": "/classify_intent", "httpMethod": "POST", "requestBody": {...}}

    Always returns the Bedrock-expected response envelope.
    """
    action_group = event.get("actionGroup", "JanSathiTools")

    # ── Function-based schema (preferred, no OpenAPI spec needed) ────────────
    if "function" in event:
        function_name = event["function"]
        raw_params = event.get("parameters", [])
        params = {p["name"]: p["value"] for p in raw_params}

        logger.info(f"[ActionGroup] function={function_name} params_keys={list(params.keys())}")
        result = dispatch_tool(function_name, params)

        return {
            "actionGroup": action_group,
            "function": function_name,
            "functionResponse": {
                "responseBody": {
                    "TEXT": {"body": json.dumps(result, ensure_ascii=False)}
                }
            },
        }

    # ── API-path schema fallback ─────────────────────────────────────────────
    api_path    = event.get("apiPath", "").lstrip("/")
    http_method = event.get("httpMethod", "POST")
    params      = {}
    try:
        props = (
            event.get("requestBody", {})
                 .get("content", {})
                 .get("application/json", {})
                 .get("properties", [])
        )
        params = {p["name"]: p["value"] for p in props}
    except Exception:
        pass

    logger.info(f"[ActionGroup] api_path={api_path} params_keys={list(params.keys())}")
    result = dispatch_tool(api_path, params)

    return {
        "actionGroup": action_group,
        "apiPath": f"/{api_path}",
        "httpMethod": http_method,
        "httpStatusCode": 200 if result.get("success") else 500,
        "responseBody": {
            "application/json": {
                "body": json.dumps(result, ensure_ascii=False)
            }
        },
    }

