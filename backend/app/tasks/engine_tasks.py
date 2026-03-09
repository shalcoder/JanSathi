"""
engine_tasks.py — Step Functions: Eligibility Audit & Artifact Generation Lambdas
==================================================================================
Lambda task handlers referenced by infrastructure/stacks/workflow_stack.py:
  - evaluate_eligibility  →  EligibilityAuditFn
  - generate_artifact     →  ArtifactGenFn

Input flows from the bank_verify task output:
  {
    "case_id":        "uuid",
    "session_id":     "uuid",
    "scheme":         "PM-KISAN",
    "slots":          {...},
    "aadhaar_status": "VERIFIED",
    "bank_status":    "VERIFIED",
    "bank_details":   {...},
  }

evaluate_eligibility adds:
  "eligible": bool, "score": float, "breakdown": list

generate_artifact adds:
  "receipt_url": "s3://...", "receipt_s3_key": "..."
"""

import os
import json
import logging
import uuid
import boto3
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

SESSIONS_TABLE  = os.getenv("DYNAMODB_SESSIONS_TABLE", "JanSathi-Sessions")
HITL_TABLE      = os.getenv("HITL_TABLE", "JanSathi-HITL-Cases")
UPLOADS_BUCKET  = os.getenv("S3_UPLOADS_BUCKET", "jansathi-uploads")
AWS_REGION      = os.getenv("AWS_REGION", "us-east-1")


# ── Scheme eligibility rules (inline; production loads from S3/DynamoDB) ──────

SCHEME_RULES: dict[str, dict] = {
    "PM-KISAN": {
        "max_land_hectares":  2.0,
        "max_annual_income":  200_000,
        "required_docs":      ["aadhaar", "land_record", "bank_account"],
        "description":        "PM-KISAN Samman Nidhi — ₹6000/year for small farmers",
    },
    "PMJDY": {
        "max_annual_income":  150_000,
        "required_docs":      ["aadhaar", "address_proof"],
        "description":        "Pradhan Mantri Jan Dhan Yojana — zero-balance bank account",
    },
    "MGNREGS": {
        "min_age":            18,
        "max_age":            60,
        "required_docs":      ["aadhaar", "job_card"],
        "description":        "MGNREGS — 100 days guaranteed rural employment",
    },
}


# ── evaluate_eligibility ───────────────────────────────────────────────────────

def evaluate_eligibility(event: dict, context: Any) -> dict:
    """
    Lambda Task: Run deterministic eligibility rules against collected slots.
    Reads session profile from DynamoDB if slots are incomplete.
    """
    logger.info(f"[EligibilityAudit] case_id={event.get('case_id')}")

    scheme    = event.get("scheme", "PM-KISAN")
    rules     = SCHEME_RULES.get(scheme, SCHEME_RULES["PM-KISAN"])
    slots     = event.get("slots", {})
    session_id = event.get("session_id", "")

    # Augment slots from DynamoDB session if available
    if session_id:
        try:
            session_data = _load_session(session_id)
            merged = {**session_data, **slots}  # slots from event take priority
            slots = merged
        except Exception as e:
            logger.warning(f"[EligibilityAudit] DDB session load failed: {e}")

    breakdown: list[dict] = []
    passed    = 0
    total     = 0

    # Income check
    if "max_annual_income" in rules:
        total += 1
        try:
            income = float(slots.get("annual_income", rules["max_annual_income"] + 1))
        except (TypeError, ValueError):
            income = rules["max_annual_income"] + 1
        ok = income <= rules["max_annual_income"]
        if ok:
            passed += 1
        breakdown.append({
            "rule":   "Annual income ≤ ₹{:,}".format(int(rules["max_annual_income"])),
            "value":  income,
            "passed": ok,
        })

    # Land holding check
    if "max_land_hectares" in rules:
        total += 1
        try:
            land = float(slots.get("land_hectares", rules["max_land_hectares"] + 1))
        except (TypeError, ValueError):
            land = rules["max_land_hectares"] + 1
        ok = land <= rules["max_land_hectares"]
        if ok:
            passed += 1
        breakdown.append({
            "rule":   "Land holding ≤ {}ha".format(rules["max_land_hectares"]),
            "value":  land,
            "passed": ok,
        })

    # Age check
    if "min_age" in rules or "max_age" in rules:
        total += 1
        try:
            age = int(slots.get("age", 0))
        except (TypeError, ValueError):
            age = 0
        ok = (
            age >= rules.get("min_age", 0) and
            age <= rules.get("max_age", 200)
        )
        if ok:
            passed += 1
        breakdown.append({
            "rule":   "Age {}-{}".format(rules.get("min_age", 0), rules.get("max_age", 200)),
            "value":  age,
            "passed": ok,
        })

    # Verification checks
    a_status = event.get("aadhaar_status", "SKIPPED")
    b_status = event.get("bank_status",    "SKIPPED")
    if a_status == "VERIFIED":
        passed += 1
    total += 1
    breakdown.append({"rule": "Aadhaar verified", "value": a_status, "passed": a_status == "VERIFIED"})

    if b_status == "VERIFIED":
        passed += 1
    total += 1
    breakdown.append({"rule": "Bank account verified", "value": b_status, "passed": b_status == "VERIFIED"})

    score   = round(passed / total, 3) if total else 0.0
    eligible = score >= 0.6  # at least 60 % of rules must pass

    logger.info(f"[EligibilityAudit] scheme={scheme} score={score} eligible={eligible}")

    _update_hitl_case(event.get("case_id", ""), eligible, score)

    return {
        **event,
        "eligible":    eligible,
        "score":       score,
        "breakdown":   breakdown,
        "audited_at":  datetime.now(timezone.utc).isoformat(),
    }


# ── generate_artifact ─────────────────────────────────────────────────────────

def generate_artifact(event: dict, context: Any) -> dict:
    """
    Lambda Task: Generate a benefit receipt PDF/HTML and upload to S3.
    Returns the S3 pre-signed URL so Step Functions can include it in the response.
    """
    logger.info(f"[ArtifactGen] case_id={event.get('case_id')}")

    case_id    = event.get("case_id",    str(uuid.uuid4()))
    session_id = event.get("session_id", "")
    scheme     = event.get("scheme",     "PM-KISAN")
    eligible   = event.get("eligible",   False)
    score      = event.get("score",      0.0)
    breakdown  = event.get("breakdown",  [])
    slots      = event.get("slots",      {})

    # Build receipt HTML
    receipt_html = _build_receipt_html(
        case_id=case_id,
        scheme=scheme,
        eligible=eligible,
        score=score,
        breakdown=breakdown,
        slots=slots,
        scheme_desc=SCHEME_RULES.get(scheme, {}).get("description", ""),
    )

    s3_key = f"receipts/{session_id}/{case_id}.html"
    receipt_url = _upload_to_s3(s3_key, receipt_html, "text/html")
    presigned   = _presign_url(s3_key)

    logger.info(f"[ArtifactGen] Uploaded receipt → s3://{UPLOADS_BUCKET}/{s3_key}")

    return {
        **event,
        "receipt_s3_key":  s3_key,
        "receipt_url":     receipt_url,
        "receipt_presigned": presigned,
        "generated_at":    datetime.now(timezone.utc).isoformat(),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_session(session_id: str) -> dict:
    """Load session collected_data from DynamoDB."""
    ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
    resp = ddb.Table(SESSIONS_TABLE).get_item(Key={"session_id": session_id})
    item = resp.get("Item", {})
    return item.get("collected_data", {})


def _update_hitl_case(case_id: str, eligible: bool, score: float) -> None:
    """Write eligibility result back to the HITL case record."""
    if not case_id:
        return
    try:
        ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
        ddb.Table(HITL_TABLE).update_item(
            Key={"case_id": case_id},
            UpdateExpression="SET eligibility_result = :e, confidence = :c",
            ExpressionAttributeValues={":e": eligible, ":c": str(score)},
        )
    except Exception as e:
        logger.warning(f"[ArtifactGen] HITL update failed: {e}")


def _build_receipt_html(case_id: str, scheme: str, eligible: bool,
                         score: float, breakdown: list, slots: dict,
                         scheme_desc: str) -> str:
    status_color = "#16a34a" if eligible else "#dc2626"
    status_text  = "APPROVED — Eligible" if eligible else "NOT ELIGIBLE"
    rows = "".join(
        f"<tr><td>{r['rule']}</td>"
        f"<td>{'✅' if r['passed'] else '❌'} {r.get('value', '')}</td></tr>"
        for r in breakdown
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>JanSathi — Benefit Receipt</title>
<style>
  body{{font-family:Arial,sans-serif;max-width:700px;margin:40px auto;padding:20px}}
  .header{{background:#1e3a5f;color:#fff;padding:20px;border-radius:8px}}
  .status{{font-size:24px;font-weight:bold;color:{status_color};margin:20px 0}}
  table{{width:100%;border-collapse:collapse;margin:20px 0}}
  th,td{{border:1px solid #ddd;padding:10px;text-align:left}}
  th{{background:#f3f4f6}}
  .footer{{color:#6b7280;font-size:12px;margin-top:30px}}
</style></head>
<body>
<div class="header">
  <h1>JanSathi — Benefit Eligibility Receipt</h1>
  <p>Case ID: {case_id}</p>
</div>
<div class="status">{status_text}</div>
<h2>{scheme}</h2>
<p>{scheme_desc}</p>
<p><strong>Eligibility Score:</strong> {score:.1%}</p>
<h3>Eligibility Breakdown</h3>
<table><tr><th>Rule</th><th>Result</th></tr>{rows}</table>
<div class="footer">
  Generated by JanSathi AI Platform · {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
  <br>This is a system-generated document. For appeals, contact your nearest Jan Seva Kendra.
</div>
</body></html>"""


def _upload_to_s3(key: str, content: str, content_type: str) -> str:
    """Upload content to S3 and return the s3:// URI."""
    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)
        s3.put_object(
            Bucket=UPLOADS_BUCKET,
            Key=key,
            Body=content.encode("utf-8"),
            ContentType=content_type,
        )
        return f"s3://{UPLOADS_BUCKET}/{key}"
    except Exception as e:
        logger.error(f"[ArtifactGen] S3 upload failed: {e}")
        return ""


def _presign_url(key: str, expires: int = 3600) -> str:
    """Generate a pre-signed S3 URL valid for `expires` seconds."""
    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": UPLOADS_BUCKET, "Key": key},
            ExpiresIn=expires,
        )
    except Exception as e:
        logger.warning(f"[ArtifactGen] Presign failed: {e}")
        return ""
