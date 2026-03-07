"""
nova_client.py — Amazon Nova via Bedrock Converse API
======================================================
Central wrapper for all Nova model calls.
ALL agents use this — never invoke_model directly.

Nova model IDs:
  - amazon.nova-micro-v1:0  → fast intent classification
  - amazon.nova-lite-v1:0   → chat, RAG synthesis, slot questions
  - amazon.nova-pro-v1:0    → reasoning, HITL summaries, vision
"""
import os
import json
import logging
from typing import Optional, List, Dict, Any

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

# ── Model ID constants ─────────────────────────────────────────────────────────
NOVA_MICRO = "amazon.nova-micro-v1:0"
NOVA_LITE  = "amazon.nova-lite-v1:0"
NOVA_PRO   = "amazon.nova-pro-v1:0"

# ── Singleton Bedrock client ───────────────────────────────────────────────────
_bedrock_client = None


def get_bedrock_client():
    """Lazy-init Bedrock runtime client (singleton)."""
    global _bedrock_client
    if _bedrock_client is None:
        region = os.getenv("AWS_REGION", "us-east-1")
        try:
            _bedrock_client = boto3.client("bedrock-runtime", region_name=region)
            logger.info(f"[NovaClient] Bedrock runtime initialised (region={region})")
        except NoCredentialsError:
            logger.error("[NovaClient] No AWS credentials found")
            _bedrock_client = None
    return _bedrock_client


# ── Core Converse wrapper ──────────────────────────────────────────────────────

def nova_converse(
    messages: List[Dict[str, Any]],
    model_id: str = NOVA_LITE,
    system_prompt: str = "",
    max_tokens: int = 1000,
    temperature: float = 0.1,
) -> str:
    """
    Send messages to a Nova model via the Converse API.

    Args:
        messages:      List of {"role": "user"|"assistant", "content": [{"text": "..."}]}
        model_id:      Nova model ID (use NOVA_MICRO / NOVA_LITE / NOVA_PRO constants)
        system_prompt: Optional system instruction string
        max_tokens:    Max output tokens
        temperature:   0.0 = deterministic, 1.0 = creative

    Returns:
        Response text string, or fallback error message.
    """
    client = get_bedrock_client()
    if client is None:
        return _offline_fallback(messages)

    # Build converse kwargs
    kwargs: Dict[str, Any] = {
        "modelId": model_id,
        "messages": messages,
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": temperature,
        },
    }

    if system_prompt:
        kwargs["system"] = [{"text": system_prompt}]

    try:
        response = client.converse(**kwargs)
        output = response["output"]["message"]["content"]
        # output is a list of content blocks; grab first text block
        for block in output:
            if "text" in block:
                return block["text"].strip()
        return ""
    except ClientError as e:
        code = e.response["Error"]["Code"]
        logger.error(f"[NovaClient] Bedrock ClientError ({code}): {e}")
        return _offline_fallback(messages)
    except Exception as e:
        logger.error(f"[NovaClient] Unexpected error: {e}")
        return _offline_fallback(messages)


def nova_converse_json(
    messages: List[Dict[str, Any]],
    model_id: str = NOVA_LITE,
    system_prompt: str = "",
    max_tokens: int = 512,
) -> dict:
    """
    Same as nova_converse but parses the response as JSON.
    Returns {} on parse failure.
    """
    raw = nova_converse(messages, model_id, system_prompt, max_tokens, temperature=0.0)
    # Strip markdown code fences if present
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning(f"[NovaClient] JSON parse failed. Raw: {raw[:200]}")
        return {}


# ── Vision (Nova Pro only) ────────────────────────────────────────────────────

def nova_analyze_image(image_bytes: bytes, prompt: str, language: str = "hi") -> str:
    """
    Analyze an image using Nova Pro (vision-capable).
    Returns descriptive text about the document/image.
    """
    import base64
    client = get_bedrock_client()
    if client is None:
        return "AI Vision not connected."

    encoded = base64.b64encode(image_bytes).decode("utf-8")

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "image": {
                        "format": "jpeg",
                        "source": {"bytes": image_bytes},
                    }
                },
                {"text": f"{prompt}\n\nRespond in {language}."},
            ],
        }
    ]

    system = (
        "You are JanSathi, an AI Citizen Assistant for India. "
        "Analyze government documents and explain their contents clearly and simply."
    )

    return nova_converse(messages, model_id=NOVA_PRO, system_prompt=system, max_tokens=1000)


# ── Helpers ───────────────────────────────────────────────────────────────────

def build_user_message(text: str) -> Dict[str, Any]:
    """Build a properly formatted user message for nova_converse."""
    return {"role": "user", "content": [{"text": text}]}


def build_assistant_message(text: str) -> Dict[str, Any]:
    """Build a properly formatted assistant message for nova_converse."""
    return {"role": "assistant", "content": [{"text": text}]}


def _offline_fallback(messages: List[Dict]) -> str:
    """Minimal offline response when Bedrock is unavailable."""
    return (
        "🔄 AI service is temporarily unavailable. "
        "Please visit india.gov.in or call 1800-111-555 for assistance."
    )
