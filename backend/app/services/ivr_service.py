"""
ivr_service.py – IVR & Amazon Connect interaction layer.

Extends the original TwiML generator with:
  - handle_connect_invocation: delegates to connect_webhook
  - start_slot_collection: kicks off schema-driven data gathering
  - process_dtmf_input: DTMF digit → slot answer conversion
  - Active session listing for the IVR Monitor dashboard
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from app.core.utils import logger as app_logger

logger = logging.getLogger(__name__)

# ─── Active session store (in-memory; swap for DynamoDB in prod) ──────────────
_active_sessions: dict = {}

VOICE_MAP = {
    "hi": "Aditi",
    "ta": "Valluvar",
    "kn": "Kajal",
    "en": "Raveena",
}


class IVRService:
    """
    Voice-first interaction layer for JanSathi IVR.

    Supports:
      - Amazon Connect Lambda invocation routing
      - Schema-driven slot collection with DTMF fallback
      - TwiML generation (for optional Twilio path)
      - Active session tracking for admin dashboard
    """

    def __init__(self):
        self.enabled = (
            os.getenv("TWILIO_ACCOUNT_SID") is not None
            or os.getenv("CONNECT_INSTANCE_ID") is not None
        )

    # ── Amazon Connect entry point ─────────────────────────────────────────────

    def handle_connect_invocation(self, event: dict) -> dict:
        """
        Delegate to connect_webhook handler.
        Updates the active session table on every invocation.
        """
        from app.services.connect_webhook import handle_connect_invocation

        result = handle_connect_invocation(event)

        # Track session for admin IVR monitor
        contact_id = event.get("contactId", "unknown")
        session_id = f"ivr-{contact_id}"
        self._upsert_session(
            session_id=session_id,
            caller_number=event.get("callerNumber", "unknown"),
            language=result.get("language", "hi"),
            current_state=result.get("intent", "greeting"),
            last_transcript=event.get("text", ""),
        )

        return result

    # ── Slot collection ────────────────────────────────────────────────────────

    def start_slot_collection(self, session_id: str, scheme_name: str, language: str = "hi") -> dict:
        """
        Load the slot schema for a scheme and return the first question.
        Stores pending slots in the active-session map.
        """
        slots = self._load_slots(scheme_name)
        if not slots:
            return {"prompt": "I couldn't find details for that scheme. Please try again.", "done": False}

        _active_sessions.setdefault(session_id, {})
        _active_sessions[session_id]["pending_slots"] = [s["key"] for s in slots]
        _active_sessions[session_id]["slot_schemas"] = {s["key"]: s for s in slots}
        _active_sessions[session_id]["collected"] = {}
        _active_sessions[session_id]["scheme"] = scheme_name

        first = slots[0]
        prompt = first.get("dtmf_prompt" if language != "en" else "prompt", first["prompt"])
        return {"prompt": prompt, "slot": first["key"], "done": False}

    def process_slot_answer(self, session_id: str, user_input: str, language: str = "hi") -> dict:
        """
        Store the answer to the current pending slot, then return:
          - next slot prompt, OR
          - {"done": True, "collected": {...}} if all slots filled
        Handles DTMF input (digits) using dtmf_map if present.
        """
        sess = _active_sessions.get(session_id, {})
        pending = sess.get("pending_slots", [])
        schemas = sess.get("slot_schemas", {})
        collected = sess.get("collected", {})

        if not pending:
            return {"done": True, "collected": collected}

        current_key = pending[0]
        schema = schemas.get(current_key, {})

        # DTMF mapping
        value = user_input.strip()
        if value.startswith("DTMF:"):
            digit = value[5:]
            dtmf_map = schema.get("dtmf_map", {})
            value = dtmf_map.get(digit, digit)

        # Type coercion
        try:
            field_type = schema.get("type", "string")
            if field_type == "float":
                value = float(value.replace(",", ""))
            elif field_type == "int":
                value = int(value)
            elif field_type == "boolean":
                value = value.lower() in ("yes", "1", "true", "हाँ", "ஆம்")
        except (ValueError, TypeError):
            pass  # keep as string

        collected[current_key] = value
        pending.pop(0)

        sess["collected"] = collected
        sess["pending_slots"] = pending

        if not pending:
            return {"done": True, "collected": collected}

        next_key = pending[0]
        next_schema = schemas.get(next_key, {})
        lang_prompt = next_schema.get("dtmf_prompt") if language != "en" else next_schema.get("prompt")
        prompt = lang_prompt or next_schema.get("prompt", f"Please provide your {next_key}")
        return {"done": False, "slot": next_key, "prompt": prompt, "collected": collected}

    # ── TwiML (Twilio optional path) ──────────────────────────────────────────

    def generate_twiml(self, text: str, language: str = "hi-IN") -> str:
        """Creates a TwiML response to 'Say' the text using Polly voice."""
        voice = VOICE_MAP.get(language[:2], "Aditi")
        return (
            f'<?xml version="1.0" encoding="UTF-8"?>'
            f'<Response><Say voice="Polly.{voice}" language="{language}">{text}</Say></Response>'
        )

    def handle_incoming_call(self, from_number: str) -> dict:
        """Initial call handler — checks if returning user."""
        logger.info(f"Incoming IVR call from {from_number[:6]}xxxx")
        session_id = f"ivr-{from_number[-6:]}"
        self._upsert_session(session_id, from_number, "hi", "greeting", "")
        return {
            "is_returning": False,
            "session_id": session_id,
            "message": "Namaste! Welcome to JanSathi. How can I help you with government schemes today?",
        }

    # ── Admin: Active session listing ─────────────────────────────────────────

    def get_active_sessions(self) -> list:
        """Return all active IVR sessions for the admin IVR Monitor."""
        return list(_active_sessions.values())

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _upsert_session(
        self, session_id: str, caller_number: str,
        language: str, current_state: str, last_transcript: str,
        last_audio_url: str = "",
    ):
        """Insert or update session in the in-memory active sessions table."""
        existing = _active_sessions.get(session_id, {})
        _active_sessions[session_id] = {
            **existing,
            "session_id": session_id,
            "caller_number": caller_number[:3] + "XXXXX" + caller_number[-4:] if len(caller_number) > 7 else "unknown",
            "start_time": existing.get("start_time", datetime.now(timezone.utc).isoformat()),
            "last_seen": datetime.now(timezone.utc).isoformat(),
            "language": language,
            "current_state": current_state,
            "last_transcript": last_transcript,
            "last_audio_url": last_audio_url,
            "channel": "ivr",
        }

    def _load_slots(self, scheme_name: str) -> list:
        """Load slot schema from schemes_config.yaml for the given scheme."""
        try:
            import yaml
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", "schemes_config.yaml"
            )
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            scheme = config.get("schemes", {}).get(scheme_name, {})
            return scheme.get("slots", [])
        except Exception as e:
            logger.error(f"[IVRService] Failed to load slot schema for {scheme_name}: {e}")
            return []
