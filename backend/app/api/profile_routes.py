"""
profile_routes.py — User Profile API

DynamoDB-first when USE_DYNAMODB=true, falls back to SQLAlchemy for local dev.

Endpoints:
  GET  /v1/profile           → authenticated user's profile
  PUT  /v1/profile           → upsert profile fields
  GET  /v1/profile/by-phone  → IVR caller-context lookup
"""

import os
import re
import logging
from datetime import datetime

from flask import Blueprint, request, jsonify, g
from app.core.middleware import require_auth

logger = logging.getLogger(__name__)

profile_bp = Blueprint("profile", __name__, url_prefix="/v1/profile")

# ── Runtime mode ─────────────────────────────────────────────────────────────
_USE_DYNAMO  = os.getenv("USE_DYNAMODB", "false").lower() == "true"
_USERS_TABLE = os.getenv("DYNAMODB_USERS_TABLE", "JanSathi-Users")
_AWS_REGION  = os.getenv("AWS_REGION", "us-east-1")


# ── Response helpers ──────────────────────────────────────────────────────────

def success_response(data: dict, status: int = 200):
    return jsonify({"status": "success", "data": data}), status


def error_response(message: str, status: int = 400):
    return jsonify({"status": "error", "message": message}), status


def normalize_phone(phone: str) -> str:
    if not phone:
        return ""
    clean = re.sub(r"[^\d+]", "", phone)
    if clean.startswith("0") and len(clean) == 11:
        clean = "+91" + clean[1:]
    elif len(clean) == 10 and not clean.startswith("+"):
        clean = "+91" + clean
    return clean


# ── DynamoDB helpers ──────────────────────────────────────────────────────────

def _dynamo_table():
    import boto3
    ddb = boto3.resource("dynamodb", region_name=_AWS_REGION)
    return ddb.Table(_USERS_TABLE)


def _dynamo_get(user_id: str) -> dict | None:
    try:
        resp = _dynamo_table().get_item(Key={"user_id": user_id})
        return resp.get("Item")
    except Exception as e:
        logger.error(f"[profile/dynamo] get_item failed for {user_id}: {e}")
        return None


def _dynamo_save(user_id: str, item: dict) -> dict:
    now = datetime.utcnow().isoformat()
    item = {**item, "user_id": user_id, "updated_at": now}
    if "created_at" not in item:
        item["created_at"] = now
    _dynamo_table().put_item(Item=item)
    return item


def _dynamo_to_dict(item: dict) -> dict:
    """Normalise a DynamoDB item to the canonical profile shape."""
    return {
        "id":                 item.get("user_id"),
        "full_name":          item.get("full_name"),
        "phone":              item.get("phone_e164", item.get("phone")),
        "age":                item.get("age"),
        "gender":             item.get("gender"),
        "state":              item.get("state"),
        "district":           item.get("district"),
        "village":            item.get("village"),
        "pincode":            item.get("pincode"),
        "occupation":         item.get("occupation", "Farmer"),
        "category":           item.get("category", "General"),
        "annual_income":      item.get("annual_income"),
        "land_holding_acres": item.get("land_holding_acres"),
        "has_aadhaar":        bool(item.get("has_aadhaar", False)),
        "has_ration_card":    bool(item.get("has_ration_card", False)),
        "has_bank_account":   bool(item.get("has_bank_account", False)),
        "has_pm_kisan":       bool(item.get("has_pm_kisan", False)),
        "preferred_language": item.get("preferred_language", "hi"),
        "income_bracket":     item.get("income_bracket"),
        "profile_complete":   bool(item.get("profile_complete", False)),
        "onboarding_completed_at": item.get("onboarding_completed_at"),
        "created_at":         item.get("created_at", datetime.utcnow().isoformat()),
        "updated_at":         item.get("updated_at", datetime.utcnow().isoformat()),
    }


def _merge_updates(existing: dict, data: dict) -> dict:
    """Apply inbound request fields onto an existing DynamoDB item dict."""
    field_map = [
        "full_name", "age", "gender", "state", "district", "village",
        "pincode", "occupation", "category", "annual_income",
        "land_holding_acres", "has_aadhaar", "has_ration_card",
        "has_bank_account", "has_pm_kisan", "preferred_language", "income_bracket",
    ]
    result = dict(existing)
    for key in field_map:
        if key in data:
            result[key] = data[key]

    if "phone" in data:
        result["phone_e164"] = normalize_phone(data["phone"])

    if data.get("profile_complete") and not existing.get("profile_complete"):
        result["profile_complete"] = True
        result["onboarding_completed_at"] = datetime.utcnow().isoformat()

    return result


# ── SQLAlchemy helpers (local / SQLite dev) ───────────────────────────────────

def _sql_upsert(user_id: str, data: dict):
    from app.models.models import db, UserProfile
    profile = UserProfile.query.get(user_id)
    if not profile:
        profile = UserProfile(id=user_id)
        db.session.add(profile)

    if "full_name"          in data: profile.full_name          = data["full_name"]
    if "phone"              in data: profile.phone_e164         = normalize_phone(data["phone"])
    if "age"                in data: profile.age                = int(data["age"]) if data["age"] else None
    if "gender"             in data: profile.gender             = data["gender"]
    if "state"              in data: profile.location_state     = data["state"]
    if "district"           in data: profile.location_district  = data["district"]
    if "village"            in data: profile.village            = data["village"]
    if "pincode"            in data: profile.pincode            = data["pincode"]
    if "occupation"         in data: profile.occupation         = data["occupation"]
    if "category"           in data: profile.category           = data["category"]
    if "annual_income"      in data: profile.annual_income      = int(data["annual_income"]) if data["annual_income"] else None
    if "land_holding_acres" in data: profile.land_holding_acres = float(data["land_holding_acres"]) if data["land_holding_acres"] else None
    if "has_aadhaar"        in data: profile.has_aadhaar        = bool(data["has_aadhaar"])
    if "has_ration_card"    in data: profile.has_ration_card    = bool(data["has_ration_card"])
    if "has_bank_account"   in data: profile.has_bank_account   = bool(data["has_bank_account"])
    if "has_pm_kisan"       in data: profile.has_pm_kisan       = bool(data["has_pm_kisan"])
    if "preferred_language" in data: profile.preferred_language = data["preferred_language"]
    if "income_bracket"     in data: profile.income_bracket     = data["income_bracket"]

    if data.get("profile_complete") and not profile.profile_complete:
        profile.profile_complete = True
        profile.onboarding_completed_at = datetime.utcnow()

    db.session.commit()
    return profile


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@profile_bp.route("", methods=["GET"])
@require_auth
def get_profile():
    """Fetch profile for the currently authenticated user."""
    user_id = g.user_id

    if _USE_DYNAMO:
        item = _dynamo_get(user_id)
        if not item:
            return success_response({"profile_complete": False})
        return success_response(_dynamo_to_dict(item))

    # SQLAlchemy path
    try:
        from app.models.models import db, UserProfile
        profile = UserProfile.query.get(user_id)
        if not profile:
            return success_response({"profile_complete": False})
        return success_response(profile.to_dict())
    except Exception as e:
        logger.warning(f"[profile] SQL get error (DynamoDB mode may be partially active): {e}")
        return success_response({"profile_complete": False})


@profile_bp.route("", methods=["PUT"])
@require_auth
def update_profile():
    """Create or update profile fields (partial update supported)."""
    user_id = g.user_id
    data    = request.json or {}

    if _USE_DYNAMO:
        existing = _dynamo_get(user_id) or {}
        try:
            merged = _merge_updates(existing, data)
            saved  = _dynamo_save(user_id, merged)
            return success_response(_dynamo_to_dict(saved))
        except Exception as e:
            logger.error(f"[profile] DynamoDB PUT failed for {user_id}: {e}")
            return error_response(str(e), status=500)

    # SQLAlchemy path
    try:
        profile = _sql_upsert(user_id, data)
        return success_response(profile.to_dict())
    except Exception as e:
        logger.error(f"[profile] SQL upsert failed: {e}")
        if "UNIQUE constraint" in str(e) or "Duplicate entry" in str(e):
            return error_response("Phone number already associated with another account.", status=409)
        return error_response(str(e), status=500)


@profile_bp.route("/by-phone", methods=["GET"])
def lookup_by_phone():
    """
    Lookup profile by phone number. Used by IVR caller-context enrichment.
    Requires X-Internal-Secret header or admin JWT.
    """
    valid_key    = os.getenv("INTERNAL_API_SECRET", "dev_internal_secret")
    internal_key = request.headers.get("X-Internal-Secret", "")
    is_internal  = (internal_key == valid_key)

    if not is_internal:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return error_response("Unauthorized", 401)
        from app.core.middleware import _decode_cognito_jwt
        payload = _decode_cognito_jwt(auth_header.split(" ", 1)[1])
        if not payload or payload.get("role") != "admin":
            return error_response("Forbidden", 403)

    phone_raw = request.args.get("phone", "")
    if not phone_raw:
        return error_response("phone query param required", 400)

    phone = normalize_phone(phone_raw)

    if _USE_DYNAMO:
        try:
            from boto3.dynamodb.conditions import Attr
            result = _dynamo_table().scan(
                FilterExpression=Attr("phone_e164").eq(phone),
                Limit=1,
            )
            items = result.get("Items", [])
            if not items:
                return success_response({"found": False})
            profile_dict = _dynamo_to_dict(items[0])
            return success_response({"found": True, "profile": profile_dict})
        except Exception as e:
            logger.error(f"[profile/by-phone] DynamoDB scan error: {e}")
            return error_response(str(e), 500)

    # SQLAlchemy path
    try:
        from app.models.models import UserProfile
        profile = UserProfile.query.filter_by(phone_e164=phone).first()
        if not profile:
            return success_response({"found": False})
        return success_response({"found": True, "profile": profile.to_dict()})
    except Exception as e:
        logger.error(f"[profile/by-phone] SQL lookup error: {e}")
        return error_response(str(e), 500)
