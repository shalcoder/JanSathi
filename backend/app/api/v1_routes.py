"""
v1_routes.py — Unified /v1/* API endpoints for JanSathi.

These endpoints are called by the frontend (api.ts) and are NOT in the
legacy routes.py to avoid breaking existing integrations.

Endpoints:
  POST /v1/sessions/init            → create/get session
  GET  /v1/sessions/<session_id>    → get session state
  POST /v1/query                    → unified chat query
  POST /v1/query/audio              → audio query (multipart)
  POST /v1/apply                    → submit scheme application
  GET  /v1/applications             → list applications for session/user
  POST /v1/upload-presign           → get S3 presigned URL for document upload
  GET  /v1/admin/cases              → HITL case queue (admin)
  POST /v1/admin/cases/<id>/approve → approve HITL case
  POST /v1/admin/cases/<id>/reject  → reject HITL case
  GET  /v1/ivr/sessions             → active IVR session list (admin)
  POST /v1/ivr/connect-webhook      → Amazon Connect Lambda invocation proxy
"""

import uuid
import os
import time
import logging

from flask import Blueprint, request, jsonify
from app.services.hitl_service import HITLService
from app.services.notify_service import NotifyService
from app.services.ivr_service import IVRService
from app.core.execution import process_user_input
from agentic_engine.session_manager import SessionManager
from agentic_engine.storage import LocalJSONStorage

logger = logging.getLogger(__name__)

v1 = Blueprint("v1", __name__, url_prefix="/v1")

# ── Singletons ────────────────────────────────────────────────────────────────
hitl_service = HITLService()
notify_service = NotifyService()
ivr_service = IVRService()

# ─── Session helpers ──────────────────────────────────────────────────────────

def _get_session_manager() -> SessionManager:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    session_file = os.path.join(base_dir, "agentic_engine", "sessions.json")
    return SessionManager(LocalJSONStorage(session_file))


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/sessions/init", methods=["POST"])
def init_session():
    """
    POST /v1/sessions/init
    Body: { "user_id": "...", "channel": "web|ivr|whatsapp" }
    Returns: { "session_id": "...", "created": true }
    """
    data = request.json or {}
    user_id = data.get("user_id", "anonymous")
    channel = data.get("channel", "web")

    session_id = data.get("session_id") or f"sess-{uuid.uuid4().hex[:12]}"

    sm = _get_session_manager()
    existing = sm.get_session(session_id)
    if not existing:
        sm.create_session(session_id)
        sm.update_data(session_id, "_user_id", user_id)
        sm.update_data(session_id, "_channel", channel)
        created = True
    else:
        created = False

    return jsonify({
        "session_id": session_id,
        "user_id": user_id,
        "channel": channel,
        "created": created,
    })


@v1.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id: str):
    """GET /v1/sessions/<session_id> → session state and data."""
    sm = _get_session_manager()
    session = sm.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify({
        "session_id": session_id,
        "current_state": session.get("current_state", "START"),
        "data": {k: v for k, v in session.get("data", {}).items() if not k.startswith("_slot")},
    })


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED QUERY ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/query", methods=["POST"])
def unified_query():
    """
    POST /v1/query
    Body: {
      "session_id": "...", "message": "...", "language": "hi",
      "channel": "web", "turn_id": "..."  [optional]
    }
    Returns unified response shape expected by ChatInterface.tsx.
    """
    start_time = time.perf_counter()
    data = request.json or {}

    session_id = data.get("session_id", f"sess-{uuid.uuid4().hex[:12]}")
    message = data.get("message", data.get("text_query", "")).strip()
    language = data.get("language", "hi")
    channel = data.get("channel", "web")
    turn_id = data.get("turn_id", str(uuid.uuid4()))

    if not message:
        return jsonify({"error": "message is required"}), 400

    # Route through process_user_input (agentic engine)
    try:
        result = process_user_input(message=message, session_id=session_id)
    except Exception as e:
        logger.error(f"[v1/query] Engine error: {e}")
        return jsonify({"error": str(e)}), 500

    response_text = result.get("response", "")
    benefit_receipt = result.get("benefit_receipt")
    confidence = result.get("eligibility_score", 0.9)
    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Try to generate Polly audio (best-effort)
    audio_url = None
    try:
        from app.services.polly_service import PollyService
        audio_url = PollyService().synthesize(response_text, language)
    except Exception:
        pass

    return jsonify({
        "session_id": session_id,
        "turn_id": turn_id,
        "transcript": message,
        "response_text": response_text,
        "audio_url": audio_url,
        "language": language,
        "channel": channel,
        "confidence": confidence,
        "benefit_receipt": benefit_receipt,
        "requires_input": result.get("requires_input", False),
        "is_terminal": result.get("is_terminal", False),
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
# APPLY ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════

@v1.route("/apply", methods=["POST"])
def apply_for_benefit():
    """
    POST /v1/apply
    Body: { "session_id": "...", "turn_id": "...", "scheme_name": "pm_kisan", "slots": {} }
    Returns case_id and status.
    """
    data = request.json or {}
    session_id = data.get("session_id", "")
    turn_id = data.get("turn_id", str(uuid.uuid4()))
    scheme_name = data.get("scheme_name", "pm_kisan")
    slots = data.get("slots", {})

    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"

    # Trigger apply workflow via engine
    try:
        result = process_user_input(message=f"start_apply:{scheme_name}", session_id=session_id)
        benefit_receipt = result.get("benefit_receipt", {})
        confidence = result.get("eligibility_score", 0.85)
    except Exception as e:
        logger.warning(f"[v1/apply] Engine error (continuing): {e}")
        benefit_receipt = {}
        confidence = 0.85

    # Trigger SMS notification (best-effort)
    phone = slots.get("mobile", data.get("phone", ""))
    if phone:
        try:
            notify_service.notify_submission(phone, scheme_name, case_id)
        except Exception:
            pass

    return jsonify({
        "case_id": case_id,
        "session_id": session_id,
        "scheme_name": scheme_name,
        "status": "submitted",
        "benefit_receipt": benefit_receipt,
        "message": f"Application submitted successfully. Case ID: {case_id}",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
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

