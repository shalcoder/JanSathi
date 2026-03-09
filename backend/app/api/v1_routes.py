"""
v1_routes.py — Unified /v1/* API endpoints for JanSathi.
"""

import uuid
import os
import time
import logging
from flask import Blueprint, request, jsonify, current_app, g

logger = logging.getLogger(__name__)
v1 = Blueprint("v1", __name__, url_prefix="/v1")

print("DEBUG: v1_routes.py imports starting...", flush=True)

from app.services.hitl_service import HITLService
from app.services.notify_service import NotifyService
from app.services.ivr_service import IVRService
from app.services.rag_service import RagService
from app.services.scheme_feed_service import SchemeFeedService
from app.services.civic_infra_service import CivicInfraService
from app.services.bedrock_service import PDF_CONTEXT_STORE

print("DEBUG: Importing process_user_input from execution...", flush=True)
from app.core.execution import process_user_input
print("DEBUG: process_user_input imported.", flush=True)

from app.core.middleware import require_auth, require_admin
from app.core.schema_validator import validate_unified_event, UnifiedResponse
from app.models.models import db, CommunityPost, UserDocument, Conversation, SchemeApplication
from agentic_engine.session_manager import SessionManager

# ── Singletons ────────────────────────────────────────────────────────────────
hitl_service = HITLService()
notify_service = NotifyService()
ivr_service = IVRService()
rag_service = RagService()
scheme_feed_service = SchemeFeedService()
civic_infra_service = CivicInfraService()

# ─── Session helpers ──────────────────────────────────────────────────────────

def _get_session_manager() -> SessionManager:
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    
    if storage_type == "dynamodb":
        from agentic_engine.storage import DynamoDBStorage
        table_name = os.getenv("DYNAMODB_SESSIONS_TABLE", "JanSathi-Sessions")
        region = os.getenv("AWS_REGION", "us-east-1")
        return SessionManager(DynamoDBStorage(table_name, region))
    else:
        from agentic_engine.storage import LocalJSONStorage
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        session_file = os.path.join(base_dir, "agentic_engine", "sessions.json")
        return SessionManager(LocalJSONStorage(session_file))


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/sessions/init", methods=["POST"])
@require_auth
@validate_unified_event
def init_session():
    """
    POST /v1/sessions/init
    Body: { "session_id": "...", "channel": "...", "language": "..." }
    """
    event = g.unified_event
    user_id = getattr(g, "user_id", "anonymous")
    
    sm = _get_session_manager()
    existing = sm.get_session(event.session_id)
    if not existing:
        sm.create_session(event.session_id)
        sm.update_data(event.session_id, "_user_id", user_id)
        sm.update_data(event.session_id, "_channel", event.channel)
        sm.update_data(event.session_id, "_language", event.language)
        created = True
    else:
        created = False

    return UnifiedResponse.success({
        "session_id": event.session_id,
        "user_id": user_id,
        "channel": event.channel,
        "created": created
    })


@v1.route("/sessions/<session_id>", methods=["GET"])
@require_auth
def get_session(session_id: str):
    """GET /v1/sessions/<session_id> → session state and data."""
    sm = _get_session_manager()
    session = sm.get_session(session_id)
    if not session:
        return UnifiedResponse.error("Session not found", error_code="NOT_FOUND", status=404)

    return UnifiedResponse.success({
        "session_id": session_id,
        "current_state": session.get("current_state", "START"),
        "data": {k: v for k, v in session.get("data", {}).items() if not k.startswith("_slot")}
    })


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED QUERY ENDPOINT
@v1.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "pong"}), 200

# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/schemes", methods=["GET"])
@require_auth
def personalized_schemes_feed():
    """
    GET /v1/schemes
    Returns profile-aware scheme feed with official apply links and freshness metadata.
    """
    user_id = getattr(g, "user_id", "anonymous")
    payload = scheme_feed_service.get_feed(user_id=user_id)
    return jsonify(payload), 200

# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/upload", methods=["POST"])
def upload_document():
    """
    POST /v1/upload
    Accepts multipart/form-data with 'file'. Stores parsed text in global PDF_CONTEXT_STORE
    to be retrieved during /v1/query.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    session_id = request.form.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    try:
        import pypdf
        pdf_reader = pypdf.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        # Store context in memory for Bedrock Service to pick up
        PDF_CONTEXT_STORE[session_id] = text
        logger.info(f"Successfully cached PDF context for {session_id}")
        
        return jsonify({
            "status": "success", 
            "message": "File parsed and cached successfully",
            "extracted_length": len(text)
        }), 200
        
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        return jsonify({"error": "Could not parse PDF"}), 500

# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/query", methods=["POST"])
# @require_auth
@validate_unified_event
def unified_query():
    """
    POST /v1/query  — rate limited: 30/minute per IP
    Body: Layer 1 UnifiedEventObject
    """
    start_time = time.perf_counter()
    event = g.unified_event

    if not event.message:
        return UnifiedResponse.error("message is required", error_code="BAD_REQUEST", status=400)

    # Route through process_user_input (agentic engine)
    try:
        # Use user_profile if provided by client, fallback to user_context
        u_profile = event.user_profile if event.user_profile is not None else event.user_context
        
        result = process_user_input(
            message=event.message, 
            session_id=event.session_id,
            language=event.language,
            user_profile=u_profile,
            channel=event.channel
        )
    except Exception as e:
        logger.error(f"[v1/query] Engine error: {e}")
        _lang = getattr(event, 'language', 'hi')
        _offline = {
            'hi': '🙏 अभी सर्वर से जुड़ने में समस्या है। कृपया कुछ देर बाद पुनः प्रयास करें।\n\n📋 आधिकारिक जानकारी: https://myscheme.gov.in',
            'ta': '🙏 இப்போது சேவையகத்துடன் சிக்கல். 📋 https://myscheme.gov.in',
            'te': '🙏 సర్వర్ సమస్య. 📋 https://myscheme.gov.in',
            'en': '🙏 Having trouble connecting right now. Please try again in a moment.\n\n📋 https://myscheme.gov.in',
        }
        fallback_text = _offline.get(_lang, _offline['en'])
        return UnifiedResponse.success({
            "session_id": event.session_id,
            "transcript": event.message,
            "response_text": fallback_text,
            "audio_url": None,
            "language": _lang,
            "channel": getattr(event, 'channel', 'web'),
            "confidence": 0.0,
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
        }), 200

    response_text = result.get("response", "")
    benefit_receipt = result.get("benefit_receipt")
    confidence = result.get("eligibility_score", 0.9)
    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    audio_url = None
    try:
        from app.services.polly_service import PollyService
        audio_url = PollyService().synthesize(response_text, event.language)
    except Exception:
        pass

    return UnifiedResponse.success({
        "session_id": event.session_id,
        "transcript": event.message,
        "response_text": response_text,
        "audio_url": audio_url,
        "language": event.language,
        "channel": event.channel,
        "confidence": confidence,
        "benefit_receipt": benefit_receipt,
        "requires_input": result.get("requires_input", False),
        "is_terminal": result.get("is_terminal", False),
        # Life Event Workflow — present only when a life event was detected
        "life_event": {
            "detected":  result.get("is_life_event", False),
            "event_id":  result.get("life_event_id"),
            "label":     result.get("life_event_label"),
            "icon":      result.get("life_event_icon"),
            "summary":   result.get("life_event_summary"),
            "workflow":  result.get("life_event_workflow", []),
        } if result.get("is_life_event") else None,
        "debug": {
            "model": "claude-3-haiku / rule-based",
            "latency_ms": latency_ms,
            "cache_hit": False,
            "asr_confidence": 1.0,
            "rules_override": False,
        }
    })


@v1.route("/query/audio", methods=["POST"])
def audio_query():
    """
    POST /v1/query/audio  (multipart/form-data)
    Fields: audio_file (blob), session_id, language
    Transcribes audio then routes through unified_query logic.
    """
    session_id = request.form.get("session_id", f"sess-{uuid.uuid4().hex[:12]}")
    language = request.form.get("language", "hi")

    if "audio_file" not in request.files:
        return jsonify({"error": "audio_file required"}), 400

    audio_file = request.files["audio_file"]
    job_id = uuid.uuid4().hex[:8]
    temp_path = f"/tmp/jansathi_audio_{job_id}.wav"

    try:
        audio_file.save(temp_path)
        from app.services.transcribe_service import TranscribeService
        transcript = TranscribeService().transcribe_audio(temp_path, job_id)
    except Exception as e:
        logger.error(f"[v1/audio-query] Transcription error: {e}")
        return jsonify({"error": "Audio transcription failed"}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # Delegate to the text query path
    request._cached_json = {
        "session_id": session_id,
        "message": transcript,
        "language": language,
        "channel": "web",
    }
    return unified_query()


# ═══════════════════════════════════════════════════════════════════════════════
# IVR VOICE ENDPOINT — real-time speech pipeline with 9-agent trace
# ═══════════════════════════════════════════════════════════════════════════════

# All 9 agents in pipeline order (matches agentcore/tools.py)
_AGENT_ORDER = [
    "IntentClassifier",
    "KnowledgeRetriever",
    "EligibilityValidator",
    "RiskAssessor",
    "ResponseGenerator",
    "SchemeAdvisor",
    "DocumentOrchestrator",
    "NotificationAgent",
    "HITLRouter",
]

# Map local result fields → agents that were invoked
def _derive_agents_local(result: dict) -> list:
    """Infer which agents ran based on local pipeline result fields."""
    action = result.get("action_type", "")
    activated = ["IntentClassifier"]  # always runs
    if result.get("response"):
        activated.append("KnowledgeRetriever")
        activated.append("ResponseGenerator")
    receipt = result.get("benefit_receipt") or {}
    if receipt:
        activated.extend(["EligibilityValidator", "RiskAssessor", "DocumentOrchestrator"])
    if receipt.get("eligible"):
        activated.extend(["SchemeAdvisor", "NotificationAgent"])
    activated.append("HITLRouter")
    # Keep canonical order
    return [a for a in _AGENT_ORDER if a in activated]


# Map AgentCore thoughts (tool_call traces) → agent names
def _derive_agents_agentcore(thoughts: list) -> list:
    _tool_to_agent = {
        "classify_intent":       "IntentClassifier",
        "retrieve_knowledge":    "KnowledgeRetriever",
        "validate_eligibility":  "EligibilityValidator",
        "compute_risk_score":    "RiskAssessor",
        "generate_response":     "ResponseGenerator",
        "fetch_live_schemes":    "SchemeAdvisor",
        "create_benefit_receipt":"DocumentOrchestrator",
        "send_sms_notification": "NotificationAgent",
        "enqueue_hitl_case":     "HITLRouter",
    }
    seen: set = set()
    agents = []
    for t in thoughts:
        if t.get("type") == "tool_call":
            a = _tool_to_agent.get(t.get("tool", ""))
            if a and a not in seen:
                agents.append(a)
                seen.add(a)
    return agents or ["IntentClassifier", "KnowledgeRetriever", "ResponseGenerator"]


@v1.route("/ivr/voice", methods=["POST"])
def ivr_voice():
    """
    POST /v1/ivr/voice
    Real-time agentic voice pipeline with 9-agent trace + Polly TTS.

    Body: { session_id, text, language, channel, user_profile }
    Returns: { response_text, audio_url, agents_activated, telemetry, is_terminal }
    """
    body = request.get_json(silent=True) or {}
    session_id = body.get("session_id") or f"ivr-{uuid.uuid4().hex[:12]}"
    text = (body.get("text") or "").strip()
    language = body.get("language", "hi")
    channel = body.get("channel", "web-ivr")
    user_profile = body.get("user_profile") or {}

    if not text:
        return jsonify({"error": "text is required"}), 400

    start_time = time.perf_counter()
    use_agentcore = os.getenv("USE_AGENTCORE", "false").lower() == "true"

    try:
        if use_agentcore:
            from agentcore.invoke import invoke_agentcore
            result = invoke_agentcore(
                user_message=text,
                session_id=session_id,
                language=language,
                channel=channel,
            )
            response_text = result.get("response_text") or result.get("response") or ""
            agents_activated = _derive_agents_agentcore(result.get("thoughts", []))
            thoughts = result.get("thoughts", [])
            benefit_receipt = result.get("benefit_receipt")
            is_terminal = result.get("is_terminal", False)
        else:
            result = process_user_input(
                message=text,
                session_id=session_id,
                language=language,
                user_profile=user_profile,
                channel=channel,
            )
            response_text = result.get("response") or result.get("response_text") or ""
            agents_activated = _derive_agents_local(result)
            thoughts = []
            benefit_receipt = result.get("benefit_receipt")
            is_terminal = result.get("is_terminal", False)
    except Exception as e:
        logger.error(f"[ivr/voice] Engine error: {e}")
        return jsonify({"error": str(e)}), 500

    # Polly TTS — synthesise in the requested language
    audio_url = None
    try:
        from app.services.polly_service import PollyService
        audio_url = PollyService().synthesize(response_text, language)
    except Exception as pe:
        logger.warning(f"[ivr/voice] Polly synthesis failed (non-fatal): {pe}")

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(f"[ivr/voice] lang={language} agents={agents_activated} latency={latency_ms}ms")

    return jsonify({
        "session_id": session_id,
        "response_text": response_text,
        "audio_url": audio_url,
        "language": language,
        "agents_activated": agents_activated,
        "benefit_receipt": benefit_receipt,
        "is_terminal": is_terminal,
        "telemetry": {
            "latency_ms": latency_ms,
            "intent": result.get("action_type", ""),
            "confidence": result.get("eligibility_score", result.get("confidence", 0.85)),
            "agents_count": len(agents_activated),
        },
        "thoughts": thoughts,
    }), 200


# ═══════════════════════════════════════════════════════════════════════════════
# APPLY ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/apply", methods=["POST"])
@require_auth
@validate_unified_event
def apply_for_benefit():
    """
    POST /v1/apply
    Body: Layer 1 UnifiedEventObject with scheme_name in channel_metadata
    """
    event = g.unified_event
    scheme_name = event.channel_metadata.get("scheme_name", "pm_kisan")
    slots = event.channel_metadata.get("slots", {})

    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"

    # Trigger apply workflow via engine
    try:
        result = process_user_input(message=f"start_apply:{scheme_name}", session_id=event.session_id)
        benefit_receipt = result.get("benefit_receipt", {})
        confidence = result.get("eligibility_score", 0.85)
    except Exception as e:
        logger.warning(f"[v1/apply] Engine error (continuing): {e}")
        benefit_receipt = {}
        confidence = 0.85

    # Trigger SMS notification (best-effort)
    phone = slots.get("mobile", event.channel_metadata.get("phone", ""))
    if phone:
        try:
            notify_service.send_sms(phone, f"JanSathi: Your {scheme_name} application JS-{case_id} is being processed.")
        except Exception:
            pass

    return UnifiedResponse.success({
        "case_id": case_id,
        "status": "PROCESSING",
        "eligibility_score": confidence,
        "benefit_receipt": benefit_receipt
    })


# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATIONS LIST
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/applications", methods=["GET"])
def list_applications():
    """
    GET /v1/applications?session_id=...&user_id=...
    Returns list of application cases for the session.
    """
    session_id = request.args.get("session_id")
    user_id = request.args.get("user_id", "anonymous")

    if not session_id:
        # Fallback: return from SQLite Schemeapplication table if available
        try:
            from app.models.models import SchemeApplication
            apps = SchemeApplication.query.filter_by(user_id=user_id).limit(20).all()
            return jsonify([a.to_dict() for a in apps])
        except Exception:
            return jsonify([])

    # Get from session data
    sm = _get_session_manager()
    session = sm.get_session(session_id)
    if not session:
        return jsonify([])

    data = session.get("data", {})
    # Collect any case_id that was set
    cases = []
    if data.get("benefit_receipt"):
        receipt = data["benefit_receipt"]
        cases.append({
            "case_id": data.get("case_id", f"CASE-{uuid.uuid4().hex[:6].upper()}"),
            "scheme_name": receipt.get("scheme_name", "Unknown"),
            "status": "submitted" if data.get("eligibility_score", 0) >= 0.8 else "under_review",
            "created_at": data.get("_created_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
        })

    return jsonify(cases)


# ═══════════════════════════════════════════════════════════════════════════════
# S3 PRESIGNED UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/upload-presign", methods=["POST"])
def upload_presign():
    """
    POST /v1/upload-presign
    Body: { "session_id": "...", "filename": "aadhaar.pdf", "content_type": "application/pdf" }
    Returns: { "url": "<presigned>", "key": "<s3-key>", "expires_in": 300 }
    """
    data = request.json or {}
    session_id = data.get("session_id", "unknown")
    filename = data.get("filename", "document.pdf")
    content_type = data.get("content_type", "application/octet-stream")

    s3_key = f"documents/{session_id}/{uuid.uuid4().hex[:8]}_{filename}"

    # Try real S3 presigned URL
    try:
        import boto3
        from botocore.config import Config
        bucket = os.getenv("DOCUMENTS_BUCKET", "jansathi-documents")
        region = os.getenv("AWS_REGION", "ap-south-1")
        s3 = boto3.client("s3", region_name=region, config=Config(signature_version="s3v4"))
        url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": s3_key, "ContentType": content_type},
            ExpiresIn=300,
        )
        return jsonify({"url": url, "key": s3_key, "expires_in": 300, "bucket": bucket})
    except Exception as e:
        logger.warning(f"[v1/upload-presign] S3 presign failed (using mock): {e}")
        # Return a mock URL for local dev
        mock_url = f"http://localhost:5000/uploads/{s3_key}"
        return jsonify({"url": mock_url, "key": s3_key, "expires_in": 300, "mock": True})


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN: HITL CASE QUEUE
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/admin/cases", methods=["GET"])
def list_hitl_cases():
    """
    GET /v1/admin/cases?status=pending_review
    Returns list of HITL cases.
    """
    status = request.args.get("status", "pending_review")
    cases = hitl_service.get_cases(status)
    return jsonify(cases)


@v1.route("/admin/cases/<case_id>/approve", methods=["POST"])
def approve_case(case_id: str):
    """POST /v1/admin/cases/<case_id>/approve"""
    data = request.json or {}
    result = hitl_service.resolve_case(case_id, "approve", data.get("reason"))
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@v1.route("/admin/cases/<case_id>/reject", methods=["POST"])
def reject_case(case_id: str):
    """POST /v1/admin/cases/<case_id>/reject"""
    data = request.json or {}
    result = hitl_service.resolve_case(case_id, "reject", data.get("reason"))
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN: IVR SESSION MONITOR
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/ivr/sessions", methods=["GET"])
def get_ivr_sessions():
    """GET /v1/ivr/sessions → active IVR sessions for admin dashboard."""
    sessions = ivr_service.get_active_sessions()
    return jsonify(sessions)


@v1.route("/ivr/connect-webhook", methods=["POST"])
def ivr_connect_webhook():
    """
    POST /v1/ivr/connect-webhook
    Proxies Amazon Connect Lambda invocation events through the full
    9-agent supervisor pipeline.
    """
    event = request.json or {}
    from app.services.connect_webhook import handle_connect_invocation
    result = handle_connect_invocation(event)
    return jsonify(result)


# ═══════════════════════════════════════════════════════════════════════════════
# IVR TURN — per-slot answer update
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/ivr/turn", methods=["POST"])
def ivr_turn():
    """
    POST /v1/ivr/turn
    Records a single slot-fill turn. Called by Connect flow after each user
    answer (speech or DTMF) to advance the slot collection state.

    Body:
      { "session_id": "...", "turn_id": "...", "slot": "land_hectares",
        "value": 1.2, "method": "speech|dtmf", "confidence": 0.85 }

    Returns next prompt or final eligibility result.
    """
    data       = request.json or {}
    session_id = data.get("session_id", "")
    turn_id    = data.get("turn_id", str(uuid.uuid4()))
    slot_key   = data.get("slot", "")
    slot_value = data.get("value")
    method     = data.get("method", "speech")
    confidence = float(data.get("confidence", 0.8))

    if not session_id or not slot_key:
        return jsonify({"error": "session_id and slot are required"}), 400

    # Persist slot into session
    sm = _get_session_manager()
    existing = sm.get_session(session_id)
    if not existing:
        sm.create_session(session_id)
    sm.update_data(session_id, slot_key, slot_value)

    # Audit slot fill (value omitted for PII safety)
    try:
        from app.services.audit_service import AuditService
        AuditService().log_slot(session_id, slot_key, method, confidence)
    except Exception:
        pass

    # Emit telemetry
    try:
        from app.services.telemetry_service import get_telemetry
        get_telemetry().emit("AvgTurnsPerSession", 1.0, {"session": session_id})
    except Exception:
        pass

    # Advance workflow engine with this answer
    try:
        result = process_user_input(
            message=f"SLOT:{slot_key}={slot_value}",
            session_id=session_id,
        )
        return jsonify({
            "session_id":     session_id,
            "turn_id":        turn_id,
            "slot_recorded":  slot_key,
            "next_prompt":    result.get("response", ""),
            "requires_input": result.get("requires_input", True),
            "benefit_receipt": result.get("benefit_receipt"),
        })
    except Exception as e:
        logger.error(f"[v1/ivr/turn] Engine error: {e}")
        return jsonify({
            "session_id": session_id,
            "turn_id": turn_id,
            "slot_recorded": slot_key,
            "next_prompt": "जानकारी प्राप्त हो गई। अगला प्रश्न आ रहा है।",
            "requires_input": True,
        })


# ═══════════════════════════════════════════════════════════════════════════════
# IVR CONSENT — log user consent
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/ivr/consent", methods=["POST"])
def ivr_consent():
    """
    POST /v1/ivr/consent
    Records user consent before any PII collection. Called at start of
    every IVR session when user presses 1.

    Body: { "session_id": "...", "consent": true, "language": "hi" }
    """
    data       = request.json or {}
    session_id = data.get("session_id", "")
    consent    = data.get("consent", False)
    language   = data.get("language", "hi")

    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    if not consent:
        return jsonify({"error": "User did not consent"}), 403

    try:
        from app.services.audit_service import AuditService
        caller_hash = str(hash(session_id))[:16]
        AuditService().log_consent(session_id, caller_hash, language, consent)
    except Exception as e:
        logger.warning(f"[v1/ivr/consent] Audit failed: {e}")

    return jsonify({
        "session_id": session_id,
        "consent":    True,
        "language":   language,
        "status":     "recorded",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATE — universal supervisor entry point
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/orchestrate", methods=["POST"])
def orchestrate():
    """
    POST /v1/orchestrate
    Universal entry point for all channels — delegates directly to
    JanSathiSupervisor (9-agent pipeline).

    Body:
      { "session_id": "...", "message": "...", "language": "hi",
        "channel": "web|ivr|whatsapp", "consent": true,
        "asr_confidence": 0.9, "slots": {} }
    """
    data  = request.json or {}
    if not data.get("message") and not data.get("session_id"):
        return jsonify({"error": "message or session_id required"}), 400

    try:
        from app.agent.supervisor import get_supervisor
        result = get_supervisor().orchestrate(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"[v1/orchestrate] Supervisor error: {e}")
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# TELEMETRY — CloudWatch metric summary for admin
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/telemetry", methods=["GET"])
def get_telemetry_summary():
    """
    GET /v1/telemetry
    Returns in-memory CloudWatch metric summary for the admin dashboard.
    Useful during hackathon demo when CW console is not accessible.
    """
    try:
        from app.services.telemetry_service import get_telemetry
        tel = get_telemetry()
        return jsonify({
            "summary":  tel.get_summary(),
            "raw":      tel.get_local_metrics()[-50:],   # last 50 events
            "namespace": "JanSathi",
        })
    except Exception as e:
        logger.error(f"[v1/telemetry] Error: {e}")
        return jsonify({"summary": {}, "raw": []}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT LOG — read local audit records (dev only)
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/admin/audit", methods=["GET"])
def get_audit_log():
    """
    GET /v1/admin/audit?session_id=...
    Returns local audit log records (dev/demo mode).
    In production, read from S3 audit bucket.
    """
    session_id = request.args.get("session_id")
    try:
        from app.services.audit_service import AuditService
        records = AuditService().get_local_records(session_id)
        return jsonify({"records": records, "count": len(records)})
    except Exception as e:
        return jsonify({"records": [], "error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# CIVIC INFRASTRUCTURE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/civic/life-workflow", methods=["GET"])
def civic_life_workflow():
    event = request.args.get("event", "crop_loss")
    user_id = request.args.get("user_id", getattr(g, "user_id", "anonymous"))
    return jsonify(civic_infra_service.get_life_workflow(event=event, user_id=user_id)), 200


@v1.route("/civic/life-event-cases", methods=["POST"])
def civic_life_event_cases_create():
    data = request.json or {}
    session_id = data.get("session_id", f"sess-{uuid.uuid4().hex[:8]}")
    user_id = data.get("user_id", getattr(g, "user_id", "anonymous"))
    language = data.get("language", "en")
    event_key = (data.get("event_key") or "").strip().lower()

    if not event_key and data.get("event_text"):
        try:
            from app.services.intent_service import IntentService
            intent = IntentService().classify_intent_ivr(str(data["event_text"]), language)
            event_key = intent.get("event_key", "crop_loss")
        except Exception:
            event_key = "crop_loss"
    if not event_key:
        event_key = "crop_loss"

    payload = civic_infra_service.create_life_event_case(
        session_id=session_id,
        event_key=event_key,
        user_id=user_id,
        language=language,
    )
    return jsonify(payload), 201


@v1.route("/civic/life-event-cases/<case_id>", methods=["GET"])
def civic_life_event_case_status(case_id: str):
    payload = civic_infra_service.get_life_event_case(case_id)
    if payload.get("error") == "case_not_found":
        return jsonify(payload), 404
    return jsonify(payload), 200


@v1.route("/civic/proactive-alerts", methods=["GET"])
def civic_proactive_alerts():
    user_id = request.args.get("user_id", getattr(g, "user_id", "anonymous"))
    return jsonify(civic_infra_service.get_proactive_alerts(user_id=user_id)), 200


@v1.route("/civic/community-insights", methods=["GET"])
def civic_community_insights():
    location = request.args.get("location", "India")
    return jsonify(civic_infra_service.get_community_insights(location=location)), 200


@v1.route("/civic/navigator", methods=["GET"])
def civic_navigator():
    location = request.args.get("location", "India")
    service = request.args.get("service", "csc")
    return jsonify(civic_infra_service.get_navigator(location=location, service=service)), 200


@v1.route("/civic/journey", methods=["GET"])
def civic_journey():
    user_id = request.args.get("user_id", getattr(g, "user_id", "anonymous"))
    session_id = request.args.get("session_id", "")
    return jsonify(civic_infra_service.get_civic_journey(user_id=user_id, session_id=session_id)), 200


@v1.route("/civic/artifacts", methods=["POST"])
def civic_artifacts():
    data = request.json or {}
    session_id = data.get("session_id", f"sess-{uuid.uuid4().hex[:8]}")
    workflow_name = data.get("workflow", "life_event_assist")
    language = data.get("language", "en")
    return jsonify(
        civic_infra_service.create_artifacts(
            session_id=session_id,
            workflow_name=workflow_name,
            language=language
        )
    ), 200


@v1.route("/civic/fraud-report", methods=["POST"])
def civic_fraud_report():
    data = request.json or {}
    if not data.get("details"):
        return jsonify({"error": "details is required"}), 400
    return jsonify(civic_infra_service.report_fraud(data)), 201


@v1.route("/civic/impact", methods=["GET"])
def civic_impact():
    try:
        return jsonify(civic_infra_service.get_impact_metrics()), 200
    except Exception as e:
        logger.error(f"[civic/impact] Unexpected error: {e}")
        return jsonify({
            "citizens_served": 0,
            "applications_processed": 0,
            "community_posts": 0,
            "fraud_reports": 0,
            "estimated_benefits_unlocked_inr": 0,
            "estimated_trips_avoided": 0,
            "grievances_resolved": 0,
        }), 200

# ═══════════════════════════════════════════════════════════════════════════════
# COMMUNITY / FORUM ENDPOINTS 
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/community/posts", methods=["GET"])
def get_community_posts():
    """GET /v1/community/posts — fetch crowd-sourced civic awareness posts."""
    try:
        limit = request.args.get("limit", 20, type=int)
        location = request.args.get("location")
        query = db.session.query(CommunityPost)
        if location:
            query = query.filter(CommunityPost.location.ilike(f"%{location}%"))
        posts = query.order_by(CommunityPost.timestamp.desc()).limit(limit).all()
        return jsonify([p.to_dict() for p in posts])
    except Exception as e:
        logger.error(f"[v1/community] Error: {e}")
        return jsonify([])

@v1.route("/community/posts", methods=["POST"])
def create_community_post():
    """POST /v1/community/posts — share a civic success or query."""
    try:
        data = request.json or {}
        if not data.get("title") or not data.get("content"):
            return jsonify({"error": "Title and Content are required"}), 400

        new_post = CommunityPost(
            title=str(data["title"]).strip(),
            content=str(data["content"]).strip(),
            author=data.get("author", "Anonymous Citizen"),
            author_role=data.get("role", "Citizen"),
            location=data.get("location", "India")
        )
        db.session.add(new_post)
        db.session.commit()
        return jsonify({"status": "success", "post": new_post.to_dict()}), 201
    except Exception as e:
        logger.error(f"[v1/community] Create error: {e}")
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT MANAGEMENT (Local Fallback)
# ═══════════════════════════════════════════════════════════════════════════════

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@v1.route("/upload", methods=["POST"])
def upload_file_legacy():
    """POST /v1/upload — legacy multipart upload for mobile compatibility."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    user_id = request.form.get("user_id", "anonymous")
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    filename = f"{uuid.uuid4().hex[:6]}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Track in DB
    try:
        doc = UserDocument(
            id=str(uuid.uuid4()),
            user_id=user_id,
            filename=file.filename,
            file_path=filepath,
            document_type=request.form.get("type", "Other")
        )
        db.session.add(doc)
        db.session.commit()
    except Exception as e:
        logger.error(f"[v1/upload] DB tracking failed: {e}")

    return jsonify({"message": "File uploaded", "filename": filename, "status": "Indexed"})

@v1.route("/documents", methods=["GET"])
def list_documents():
    """GET /v1/documents?user_id=..."""
    user_id = request.args.get("user_id", "anonymous")
    try:
        docs = UserDocument.query.filter_by(user_id=user_id).order_by(UserDocument.uploaded_at.desc()).all()
        return jsonify([d.to_dict() for d in docs])
    except Exception:
        return jsonify([])

@v1.route("/documents/<doc_id>", methods=["DELETE"])
def delete_document(doc_id: str):
    """DELETE /v1/documents/<doc_id>"""
    try:
        doc = UserDocument.query.get(doc_id)
        if doc and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
            db.session.delete(doc)
            db.session.commit()
            return jsonify({"status": "deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Not found"}), 404


# ═══════════════════════════════════════════════════════════════════════════════
# MARKET / LIVELIHOOD CONNECT
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/market/connect", methods=["POST"])
def connect_market():
    """POST /v1/market/connect — Livelihood matching for farmers/workers."""
    try:
        data = request.json or {}
        crop = data.get("crop", "unknown")
        # Reuse RAG matching logic if present
        match = "Local Mandi"
        if hasattr(rag_service, "match_livelihood"):
            matches = rag_service.match_livelihood(crop)
            if matches: match = matches[0]
        
        return jsonify({
            "status": "success",
            "connection_id": f"CONN-{uuid.uuid4().hex[:6].upper()}-JS",
            "provider": match,
            "message": f"Matching complete. Connection established with {match}."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH / STATS
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/health", methods=["GET"])
def health():
    """GET /v1/health — service health and unified dashboard stats."""
    return jsonify({
        "status": "healthy",
        "service": "JanSathi Unified API",
        "version": "2.1.0",
        "timestamp": time.time(),
        "impact": {
            "active_users": 84500,  # Mocked for demo
            "benefits_processed": "₹12.5 Cr",
            "success_rate": "92%"
        }
    })


# ═══════════════════════════════════════════════════════════════════════════════
# LANGGRAPH AGENT ENDPOINT — Full 9-agent pipeline
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/agent/invoke", methods=["POST"])
def agent_invoke():
    """
    POST /v1/agent/invoke
    Runs the full JanSathi LangGraph 9-agent pipeline (or routes to
    Bedrock AgentCore if USE_AGENTCORE=true).

    Body:
      {
        "session_id":     "sess-abc123",      // unique session ID
        "message":        "PM Kisan apply",   // user's query
        "language":       "hi",               // hi|en|ta|kn...
        "channel":        "web",              // web|ivr|sms
        "consent_given":  true,               // DPDP consent
        "phone":          "+918888888888",    // optional, for SMS
        "slots":          {},                 // previously collected slots
        "asr_confidence": 1.0                 // 1.0 for text; 0-1 for IVR
      }

    Returns:
      {
        "session_id":         str,
        "response_text":      str,
        "intent":             str,
        "scheme_hint":        str,
        "slots":              dict,
        "slots_complete":     bool,
        "eligibility_result": dict,
        "verifier_result":    dict,
        "benefit_receipt":    dict,
        "hitl_case_id":       str,
        "sms_sent":           bool,
        "mode":               "langgraph" | "agentcore" | "fallback"
      }
    """
    start_time = time.perf_counter()
    data = request.json or {}

    session_id = data.get("session_id") or f"sess-{uuid.uuid4().hex[:12]}"
    message = data.get("message", data.get("text_query", "")).strip()
    language = data.get("language", "hi")
    channel = data.get("channel", "web")
    consent_given = data.get("consent_given", True)
    phone = data.get("phone", "")
    slots = data.get("slots", {})
    asr_confidence = float(data.get("asr_confidence", 1.0))

    if not message:
        return jsonify({"error": "message is required", "session_id": session_id}), 400

    use_agentcore = os.getenv("USE_AGENTCORE", "false").lower() == "true"

    # ── Mode A: Bedrock AgentCore (production) ────────────────────────────────
    if use_agentcore:
        try:
            from agentcore.invoke import invoke_agentcore
            result = invoke_agentcore(
                user_message=message,
                session_id=session_id,
                language=language,
                channel=channel,
                slots=slots,
            )
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return jsonify({
                "session_id": session_id,
                "response_text": result.get("response", ""),
                "mode": "agentcore",
                "latency_ms": latency_ms,
                "citations": result.get("citations", []),
                "thoughts": result.get("thoughts", []),
            })
        except Exception as e:
            logger.error(f"[v1/agent/invoke] AgentCore failed, falling back to LangGraph: {e}")

    # ── Mode B: Local LangGraph pipeline (development / fallback) ─────────────
    try:
        try:
            from agents.supervisor import run_pipeline
            final_state = run_pipeline(
                session_id=session_id,
                user_query=message,
                channel=channel,
                language=language,
                phone=phone,
                consent_given=consent_given,
                slots=slots if slots else None,
                asr_confidence=asr_confidence,
            )
            mode = "langgraph"
        except ImportError:
            # LangGraph not installed — run fallback sequential pipeline
            from agents.supervisor import run_pipeline_fallback
            final_state = run_pipeline_fallback(
                session_id=session_id,
                user_query=message,
                channel=channel,
                language=language,
            )
            mode = "fallback"

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return jsonify({
            "session_id":         final_state.get("session_id", session_id),
            "turn_id":            final_state.get("turn_id", f"turn-{uuid.uuid4().hex[:8]}"),
            "response_text":      final_state.get("response_text", ""),
            "intent":             final_state.get("intent", ""),
            "intent_confidence":  final_state.get("intent_confidence", 0),
            "scheme_hint":        final_state.get("scheme_hint", ""),
            "language":           final_state.get("language", language),
            "slots":              final_state.get("slots", {}),
            "slots_complete":     final_state.get("slots_complete", False),
            "eligibility_result": final_state.get("eligibility_result", {}),
            "verifier_result":    final_state.get("verifier_result", {}),
            "benefit_receipt":    final_state.get("benefit_receipt", {}),
            "hitl_case_id":       final_state.get("hitl_case_id", ""),
            "sms_sent":           final_state.get("sms_sent", False),
            "error":              final_state.get("error", ""),
            "mode":               mode,
            "latency_ms":         latency_ms,
        })

    except Exception as e:
        logger.error(f"[v1/agent/invoke] Pipeline error: {e}")
        return jsonify({
            "error": str(e),
            "session_id": session_id,
            "response_text": "⚠️ System error. Please visit india.gov.in",
        }), 500



# ═══════════════════════════════════════════════════════════════════════════════
# SMART RAG ADMIN ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/admin/rag/stats", methods=["GET"])
@require_admin
def get_rag_stats():
    """
    GET /v1/admin/rag/stats
    
    Returns statistics about the Smart RAG service:
    - Kendra hits vs Bedrock generations
    - Cache performance
    - Learned Q&A pairs stored
    """
    try:
        from app.services.smart_rag_service import SmartRAGService
        
        smart_rag = SmartRAGService()
        stats = smart_rag.get_stats()
        
        return jsonify({
            "status": "success",
            "stats": stats,
            "timestamp": time.time()
        }), 200
        
    except Exception as e:
        logger.error(f"RAG stats error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@v1.route("/admin/rag/sync-kendra", methods=["POST"])
@require_admin
def trigger_kendra_sync():
    """
    POST /v1/admin/rag/sync-kendra
    
    Triggers Kendra data source sync to index newly learned Q&A pairs.
    This should be called periodically or after a batch of new Q&A pairs.
    """
    try:
        from app.services.smart_rag_service import SmartRAGService
        
        smart_rag = SmartRAGService()
        success = smart_rag.trigger_kendra_sync()
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Kendra sync triggered successfully",
                "timestamp": time.time()
            }), 200
        else:
            return jsonify({
                "status": "warning",
                "message": "Kendra sync not configured or failed",
                "hint": "Set KENDRA_DATA_SOURCE_ID environment variable"
            }), 200
            
    except Exception as e:
        logger.error(f"Kendra sync error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@v1.route("/admin/rag/test-query", methods=["POST"])
@require_admin
def test_rag_query():
    """
    POST /v1/admin/rag/test-query
    Body: { "query": "...", "language": "en" }
    
    Test the Smart RAG pipeline with a specific query.
    Returns detailed breakdown of the RAG process.
    """
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        language = data.get('language', 'en')
        
        if not query:
            return jsonify({
                "status": "error",
                "error": "Query is required"
            }), 400
        
        from app.services.smart_rag_service import SmartRAGService
        
        smart_rag = SmartRAGService()
        result = smart_rag.query(
            user_query=query,
            language=language,
            session_id="admin-test"
        )
        
        return jsonify({
            "status": "success",
            "query": query,
            "result": result,
            "timestamp": time.time()
        }), 200
        
    except Exception as e:
        logger.error(f"RAG test query error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMES ENDPOINT - Return available schemes
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/schemes", methods=["GET"])
def get_schemes():
    """
    GET /v1/schemes
    Returns list of available government schemes from schemes_config.yaml
    """
    try:
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), '../data/schemes_config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        schemes = config.get('schemes', {})
        return jsonify({"schemes": schemes, "count": len(schemes)})
    except Exception as e:
        logger.error(f"Failed to load schemes: {e}")
        return jsonify({"schemes": {}, "count": 0, "error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# MARKET RATES ENDPOINT - Mock market rates for farmers
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/market-rates", methods=["GET"])
def get_market_rates():
    """
    GET /v1/market-rates
    Returns current market rates for agricultural products (mock data)
    """
    mock_rates = [
        {"commodity": "Wheat", "price": 2100, "unit": "quintal", "market": "Delhi Mandi", "trend": "up"},
        {"commodity": "Rice", "price": 1950, "unit": "quintal", "market": "Punjab Mandi", "trend": "stable"},
        {"commodity": "Cotton", "price": 6500, "unit": "quintal", "market": "Gujarat Mandi", "trend": "down"},
        {"commodity": "Sugarcane", "price": 350, "unit": "quintal", "market": "UP Mandi", "trend": "up"},
        {"commodity": "Potato", "price": 800, "unit": "quintal", "market": "West Bengal", "trend": "stable"},
    ]
    return jsonify(mock_rates)


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN SEED ENDPOINT - Seed database with test data
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/admin/seed", methods=["POST"])
@require_admin
def seed_database():
    """
    POST /v1/admin/seed
    Seeds database with test data for development
    """
    try:
        # Add some test data
        from app.models.models import db, CommunityPost
        
        test_posts = [
            {
                "title": "PM-Kisan Success Story",
                "content": "Received my first installment within 2 weeks!",
                "author": "Ramesh Kumar",
                "category": "success"
            },
            {
                "title": "Document Checklist Help",
                "content": "What documents are needed for PM Awas Yojana?",
                "author": "Priya Sharma",
                "category": "question"
            }
        ]
        
        for post_data in test_posts:
            post = CommunityPost(**post_data)
            db.session.add(post)
        
        db.session.commit()
        
        return jsonify({
            "message": "Database seeded successfully",
            "posts_added": len(test_posts)
        })
    except Exception as e:
        logger.error(f"Failed to seed database: {e}")
        return jsonify({"error": str(e)}), 500
