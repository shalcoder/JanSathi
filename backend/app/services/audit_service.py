"""
audit_service.py — Immutable audit log for DPDP / regulatory compliance.

Writes SHA-256-chained JSON records to:
  - S3 bucket (production)  →  audit/{consent|turns|eligibility|submissions}/{session}_{ts}.json
  - Local file (dev)        →  agentic_engine/audit_log.jsonl

Each record contains a SHA-256 integrity digest of (previous_hash + payload)
to detect tampering (simplified digest chain).
"""

import os
import json
import uuid
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

AUDIT_LOCAL_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "agentic_engine", "audit_log.jsonl"
)

_last_hash = "genesis"           # digest chain seed
_audit_bucket = os.getenv("AUDIT_BUCKET", "jansathi-audit")


def _get_s3():
    try:
        import boto3
        return boto3.client("s3", region_name=os.getenv("AWS_REGION", "ap-south-1"))
    except Exception:
        return None


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _write(record_type: str, session_id: str, payload: dict) -> dict:
    """Core writer: add metadata, compute hash, persist to S3 or local file."""
    global _last_hash

    ts = datetime.now(timezone.utc).isoformat()
    record = {
        "record_id": str(uuid.uuid4()),
        "record_type": record_type,
        "session_id": session_id,
        "ts": ts,
        "payload": payload,
    }
    serialised = json.dumps(record, default=str, sort_keys=True)
    record["integrity_hash"] = _sha256(_last_hash + serialised)
    _last_hash = record["integrity_hash"]

    # ── S3 path ───────────────────────────────────────────────────────────────
    s3_key = f"audit/{record_type}/{session_id}_{record['record_id'][:8]}.json"
    s3 = _get_s3()
    if s3:
        try:
            s3.put_object(
                Bucket=_audit_bucket,
                Key=s3_key,
                Body=json.dumps(record, default=str),
                ContentType="application/json",
                ServerSideEncryption="aws:kms",
            )
            logger.info(f"[Audit] Written to s3://{_audit_bucket}/{s3_key}")
        except Exception as e:
            logger.warning(f"[Audit] S3 write failed, falling back to local: {e}")
            _write_local(record)
    else:
        _write_local(record)

    # Emit telemetry
    try:
        from app.services.telemetry_service import get_telemetry
        get_telemetry().emit("AuditLogWritten", 1.0, {"record_type": record_type})
    except Exception:
        pass

    return record


def _write_local(record: dict):
    os.makedirs(os.path.dirname(AUDIT_LOCAL_FILE), exist_ok=True)
    with open(AUDIT_LOCAL_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")
    logger.info(f"[Audit] Written locally: {record['record_type']} / {record['record_id'][:8]}")


# ── Public API ────────────────────────────────────────────────────────────────

class AuditService:
    """Immutable audit trail for JanSathi sessions."""

    def log_consent(self, session_id: str, caller_hash: str, language: str, consent: bool) -> dict:
        """Record user consent (DPDP mandatory)."""
        from app.services.telemetry_service import get_telemetry
        get_telemetry().emit("ConsentCaptured", 1.0, {"language": language})
        return _write("consent", session_id, {
            "caller_hash": caller_hash,
            "language": language,
            "consent": consent,
        })

    def log_turn(self, session_id: str, turn_id: str, transcript: str,
                 intent: str, confidence: float, asr_confidence: float = 1.0) -> dict:
        """Record a single conversation turn."""
        return _write("turn", session_id, {
            "turn_id": turn_id,
            "transcript": transcript[:500],          # truncate for PII safety
            "intent": intent,
            "intent_confidence": confidence,
            "asr_confidence": asr_confidence,
        })

    def log_slot(self, session_id: str, slot_key: str, method: str, confidence: float) -> dict:
        """Record a slot that was filled (value omitted for PII safety)."""
        return _write("slot", session_id, {
            "slot_key": slot_key,
            "method": method,                        # speech | dtmf
            "confidence": confidence,
        })

    def log_eligibility(self, session_id: str, scheme: str, eligible: bool,
                        rules_score: float, rules_trace: list, case_id: Optional[str] = None) -> dict:
        """Record eligibility evaluation result."""
        return _write("eligibility", session_id, {
            "scheme": scheme,
            "eligible": eligible,
            "rules_score": rules_score,
            "rules_trace": rules_trace,
            "case_id": case_id,
        })

    def log_submission(self, session_id: str, case_id: str, scheme: str, status: str) -> dict:
        """Record final submission or queuing."""
        return _write("submission", session_id, {
            "case_id": case_id,
            "scheme": scheme,
            "status": status,
        })

    def log_hitl(self, session_id: str, case_id: str, reason: str) -> dict:
        """Record HITL escalation event."""
        return _write("hitl", session_id, {
            "case_id": case_id,
            "reason": reason,
        })

    def get_local_records(self, session_id: Optional[str] = None) -> list:
        """Read audit records from local JSONL file (dev only)."""
        records = []
        if not os.path.exists(AUDIT_LOCAL_FILE):
            return records
        with open(AUDIT_LOCAL_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if session_id is None or r.get("session_id") == session_id:
                        records.append(r)
                except json.JSONDecodeError:
                    pass
        return records
