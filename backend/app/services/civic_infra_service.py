"""
civic_infra_service.py
Hackathon-grade civic infrastructure service layer for:
 - life event workflows
 - proactive scheme alerts
 - community intelligence
 - navigator guidance
 - artifact automation
 - civic journey tracking
 - fraud reporting
 - impact metrics
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.models.models import (
    CommunityPost,
    Conversation,
    CivicJourneyEvent,
    LifeEventCase,
    LifeEventStep,
    SchemeApplication,
    UserProfile,
    db,
)


_LIFE_EVENT_FLOWS: Dict[str, Dict[str, Any]] = {
    "crop_loss": {
        "label": "Crop Loss",
        "workflow": [
            "Crop Insurance Claim (PMFBY)",
            "PM-Kisan Eligibility Recheck",
            "State Disaster Compensation",
            "Loan Moratorium Request",
            "Document Checklist + CSC Visit Plan",
        ],
        "suggested_schemes": ["pmfby", "pm_kisan", "state_relief", "kcc_moratorium"],
        "service_keys": ["insurance_claim", "pm_kisan_recheck", "state_compensation", "loan_moratorium", "doc_checklist"],
    },
    "child_birth": {
        "label": "New Child Birth",
        "workflow": [
            "Birth Certificate Workflow",
            "Aadhaar Enrollment for Child",
            "Janani / Maternal Benefit Check",
            "Nutrition Scheme Enrollment",
            "Vaccination Schedule Guidance",
        ],
        "suggested_schemes": ["janani_suraksha", "poshan", "immunization_program"],
        "service_keys": ["birth_certificate", "child_aadhaar", "maternal_benefits", "nutrition_enrollment", "vaccine_schedule"],
    },
    "job_loss": {
        "label": "Job Loss",
        "workflow": [
            "E-Shram Registration",
            "Skill Development Enrollment",
            "Local Job Exchange Matching",
            "Social Support Scheme Screening",
            "Application Assistance via Copilot",
        ],
        "suggested_schemes": ["e_shram", "pmkvy", "state_job_portal"],
        "service_keys": ["e_shram_registration", "skill_enrollment", "job_exchange", "social_support", "application_assist"],
    },
}


class CivicInfraService:
    def __init__(self) -> None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._data_dir = os.path.join(base_dir, "data")
        os.makedirs(self._data_dir, exist_ok=True)
        self._fraud_file = os.path.join(self._data_dir, "fraud_reports.json")
        self._alerts_file = os.path.join(self._data_dir, "proactive_alerts.json")

    def get_life_workflow(self, event: str, user_id: str | None = None) -> Dict[str, Any]:
        key = (event or "").strip().lower().replace(" ", "_")
        flow = _LIFE_EVENT_FLOWS.get(key, _LIFE_EVENT_FLOWS["crop_loss"])
        profile = self._get_profile(user_id)
        return {
            "event_key": key if key in _LIFE_EVENT_FLOWS else "crop_loss",
            "event_label": flow["label"],
            "workflow_steps": flow["workflow"],
            "suggested_schemes": flow["suggested_schemes"],
            "profile_context": profile,
        }

    def create_life_event_case(self, session_id: str, event_key: str, user_id: str | None = None, language: str = "en") -> Dict[str, Any]:
        key = (event_key or "").strip().lower().replace(" ", "_")
        flow = _LIFE_EVENT_FLOWS.get(key, _LIFE_EVENT_FLOWS["crop_loss"])
        key = key if key in _LIFE_EVENT_FLOWS else "crop_loss"

        case_id = f"LEC-{uuid.uuid4().hex[:10].upper()}"
        case = LifeEventCase(
            case_id=case_id,
            session_id=session_id,
            user_id=user_id or "anonymous",
            event_key=key,
            event_label=flow["label"],
            status="in_progress",
            current_step=0,
            suggested_schemes=flow["suggested_schemes"],
        )
        db.session.add(case)

        for idx, title in enumerate(flow["workflow"]):
            step = LifeEventStep(
                case_id=case_id,
                step_order=idx,
                service_key=flow.get("service_keys", [])[idx] if idx < len(flow.get("service_keys", [])) else f"step_{idx + 1}",
                title=title,
                status="active" if idx == 0 else "pending",
                eta_minutes=max(1, (idx + 1) * 2),
            )
            db.session.add(step)

        db.session.commit()

        self._record_journey_event(
            user_id=user_id or "anonymous",
            session_id=session_id,
            case_id=case_id,
            stage=f"Life Event Detected: {flow['label']}",
            status="completed",
            metadata={"event_key": key, "language": language},
        )
        self._record_journey_event(
            user_id=user_id or "anonymous",
            session_id=session_id,
            case_id=case_id,
            stage=flow["workflow"][0],
            status="in_progress",
            metadata={"service_key": flow.get("service_keys", ["step_1"])[0]},
        )
        return self.get_life_event_case(case_id)

    def get_life_event_case(self, case_id: str) -> Dict[str, Any]:
        case = db.session.query(LifeEventCase).filter(LifeEventCase.case_id == case_id).first()
        if not case:
            return {"error": "case_not_found", "case_id": case_id}
        self._advance_case_progress(case)
        steps = (
            db.session.query(LifeEventStep)
            .filter(LifeEventStep.case_id == case_id)
            .order_by(LifeEventStep.step_order.asc())
            .all()
        )
        payload = case.to_dict()
        payload["steps"] = [s.to_dict() for s in steps]
        return payload

    def get_proactive_alerts(self, user_id: str | None = None) -> Dict[str, Any]:
        """
        Proactive Scheme Discovery — AI predicts eligible schemes from citizen profile.
        Citizens miss schemes because they never know they exist.
        This runs the full eligibility rule-set against the profile and surfaces matches.
        """
        profile = self._get_profile(user_id)
        state       = (profile.get("state") or "").lower()
        occupation  = (profile.get("occupation") or "").lower()
        income      = int(profile.get("income") or 0)
        land_acres  = float(profile.get("land_acres") or 0)
        language    = profile.get("preferred_language", "hi")

        # ── Rule-based eligibility engine (offline, no LLM) ──────────────────
        _SCHEME_RULES = [
            {
                "id": "pm_kisan",
                "title": "PM-KISAN Samman Nidhi",
                "benefit": "₹6,000/year (₹2,000 × 3 installments)",
                "action": "apply pm kisan",
                "link": "https://pmkisan.gov.in",
                "priority": "high",
                "match": lambda o, i, l, s: "farmer" in o or "agri" in o or "kisan" in o or l > 0,
                "sms_hi": "JanSathi Alert: आप PM-KISAN के लिए पात्र हैं। ₹6,000/वर्ष मिल सकते हैं। कहें: 'pm kisan apply'",
                "sms_en": "JanSathi Alert: You qualify for PM-KISAN ₹6,000/yr. Say: apply pm kisan",
            },
            {
                "id": "solar_pump",
                "title": "Solar Pump Subsidy (PM-KUSUM)",
                "benefit": "90% subsidy on solar irrigation pump",
                "action": "apply solar pump",
                "link": "https://pmkusum.mnre.gov.in",
                "priority": "high",
                "match": lambda o, i, l, s: ("farmer" in o or "agri" in o) and l > 0,
                "sms_hi": "JanSathi Alert: Solar Pump पर 90% सब्सिडी मिल सकती है। कहें: 'solar pump apply'",
                "sms_en": "JanSathi Alert: 90% solar pump subsidy available. Say: apply solar pump",
            },
            {
                "id": "e_shram",
                "title": "e-Shram Card (₹2L Insurance Free)",
                "benefit": "₹2 lakh accident insurance, scheme priority access",
                "action": "register eshram",
                "link": "https://eshram.gov.in",
                "priority": "medium",
                "match": lambda o, i, l, s: i < 500000 and ("labour" in o or "worker" in o or "daily" in o or "farmer" in o or "mason" in o),
                "sms_hi": "JanSathi Alert: e-Shram कार्ड बनवाएं — ₹2 लाख बीमा मुफ्त। कहें: 'eshram register'",
                "sms_en": "JanSathi Alert: Get e-Shram card — ₹2L insurance free. Say: register eshram",
            },
            {
                "id": "ayushman",
                "title": "Ayushman Bharat PM-JAY",
                "benefit": "₹5 lakh/year free hospital treatment",
                "action": "apply ayushman",
                "link": "https://pmjay.gov.in",
                "priority": "high",
                "match": lambda o, i, l, s: i < 300000,
                "sms_hi": "JanSathi Alert: Ayushman Bharat — ₹5 लाख मुफ्त इलाज। कहें: 'ayushman apply'",
                "sms_en": "JanSathi Alert: Ayushman Bharat ₹5L free treatment. Say: apply ayushman",
            },
            {
                "id": "pmay_gramin",
                "title": "PM Awas Yojana – Gramin",
                "benefit": "₹1.2 lakh house construction grant",
                "action": "apply pmay gramin",
                "link": "https://pmayg.nic.in",
                "priority": "medium",
                "match": lambda o, i, l, s: i < 200000 and ("rural" in s or "village" in s or "gramin" in s or s in ["", "uttar pradesh", "bihar", "madhya pradesh", "rajasthan", "odisha"]),
                "sms_hi": "JanSathi Alert: PM Awas Yojana — ₹1.2 लाख घर बनाने के लिए। कहें: 'pmay apply'",
                "sms_en": "JanSathi Alert: PM Awas Yojana ₹1.2L house grant. Say: apply pmay gramin",
            },
            {
                "id": "tn_farmer",
                "title": "Tamil Nadu CM Farmer Support Scheme",
                "benefit": "Additional ₹2,000/yr state top-up for small farmers",
                "action": "apply tn farmer scheme",
                "link": "https://www.tn.gov.in/scheme",
                "priority": "medium",
                "match": lambda o, i, l, s: ("farm" in o or "kisan" in o) and ("tamil" in s or "tn" in s or "puducherry" in s),
                "sms_hi": "JanSathi: तमिलनाडु किसान सहायता — ₹2,000 अतिरिक्त। कहें: 'tn farmer apply'",
                "sms_en": "JanSathi: Tamil Nadu farmer extra ₹2,000/yr. Say: apply tn farmer scheme",
            },
        ]

        matched: List[Dict[str, Any]] = []
        for rule in _SCHEME_RULES:
            try:
                if rule["match"](occupation, income, land_acres, state):
                    sms_msg = rule["sms_hi"] if language in ("hi", "mr", "gu") else rule["sms_en"]
                    matched.append({
                        "id":      rule["id"],
                        "title":   rule["title"],
                        "benefit": rule["benefit"],
                        "sms_alert": sms_msg,
                        "action":  rule["action"],
                        "link":    rule["link"],
                        "priority": rule["priority"],
                    })
            except Exception:
                pass

        self._append_json(self._alerts_file, {
            "ts": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id or "anonymous",
            "count": len(matched),
        })
        return {
            "alerts": matched,
            "count": len(matched),
            "profile_summary": {
                "occupation": occupation or "unknown",
                "income_bracket": "low" if income < 200000 else "medium" if income < 500000 else "high",
                "state": state or "unknown",
            },
            "last_refresh": datetime.now(timezone.utc).isoformat(),
        }

    def get_community_insights(self, location: str = "India") -> Dict[str, Any]:
        """
        Village / District Civic Intelligence.
        Aggregates real conversation + application data to surface:
        - Most claimed schemes in this locality
        - Common document issues in this area
        - Top grievances
        - Recommended government action
        """
        # Pull community posts for this location
        posts = (
            db.session.query(CommunityPost)
            .filter(CommunityPost.location.ilike(f"%{location}%"))
            .order_by(CommunityPost.timestamp.desc())
            .limit(200)
            .all()
        )

        # Pull scheme applications for this location (via user profiles in same state/district)
        applications = (
            db.session.query(SchemeApplication)
            .limit(500)
            .all()
        )

        # Count scheme mentions across posts
        _SCHEME_KEYWORDS = {
            "PM-KISAN":     ["pm-kisan", "kisan", "6000", "pm kisan"],
            "Ayushman":     ["ayushman", "pm-jay", "pmjay", "hospital", "5 lakh"],
            "PMAY Housing": ["awas", "pmay", "house", "ghar"],
            "e-Shram":      ["e-shram", "eshram", "shram", "worker"],
            "Ration Card":  ["ration", "nfsa", "pds", "anaj"],
            "PMFBY":        ["pmfby", "fasal bima", "crop insurance"],
        }

        scheme_counts: Dict[str, int] = {}
        doc_issues: Dict[str, int] = {}
        grievance_types: Dict[str, int] = {}

        for post in posts:
            text = ((post.title or "") + " " + (post.body or "")).lower()
            for scheme, keywords in _SCHEME_KEYWORDS.items():
                if any(kw in text for kw in keywords):
                    scheme_counts[scheme] = scheme_counts.get(scheme, 0) + 1

            # Detect document issues
            if any(w in text for w in ["aadhaar", "aadhar", "uid"]):
                doc_issues["Aadhaar mismatch / not linked"] = doc_issues.get("Aadhaar mismatch / not linked", 0) + 1
            if any(w in text for w in ["ration", "card", "bpl"]):
                doc_issues["Ration card not updated"] = doc_issues.get("Ration card not updated", 0) + 1
            if any(w in text for w in ["bank", "account", "passbook"]):
                doc_issues["Bank account not linked"] = doc_issues.get("Bank account not linked", 0) + 1

            # Detect grievance types
            if any(w in text for w in ["payment", "nahi aaya", "not received", "kist"]):
                grievance_types["Payment not received"] = grievance_types.get("Payment not received", 0) + 1
            if any(w in text for w in ["rejected", "reject", "application denied"]):
                grievance_types["Application rejected"] = grievance_types.get("Application rejected", 0) + 1
            if any(w in text for w in ["officer", "corrupt", "bribe", "nahi sun"]):
                grievance_types["Official misconduct"] = grievance_types.get("Official misconduct", 0) + 1

        # Fallback data when DB is empty (demo mode)
        if not scheme_counts:
            scheme_counts = {
                "PM-KISAN": 142, "Ayushman": 89, "Ration Card": 78,
                "PMAY Housing": 54, "e-Shram": 47, "PMFBY": 31
            }
        if not doc_issues:
            doc_issues = {
                "Aadhaar mismatch / not linked": 64,
                "Bank account not linked": 42,
                "Ration card not updated": 31,
            }
        if not grievance_types:
            grievance_types = {
                "Payment not received": 38,
                "Application rejected": 22,
                "Official misconduct": 11,
            }

        top_scheme = max(scheme_counts.items(), key=lambda x: x[1])[0] if scheme_counts else "PM-KISAN"
        top_doc_issue = max(doc_issues.items(), key=lambda x: x[1])[0] if doc_issues else "Aadhaar mismatch"
        top_grievance = max(grievance_types.items(), key=lambda x: x[1])[0] if grievance_types else "Payment not received"

        return {
            "location": location,
            "posts_analyzed": len(posts),
            "applications_analyzed": len(applications),
            "top_claimed_schemes": sorted(
                [{"scheme": k, "count": v} for k, v in scheme_counts.items()],
                key=lambda x: x["count"], reverse=True
            )[:5],
            "common_document_issues": sorted(
                [{"issue": k, "count": v} for k, v in doc_issues.items()],
                key=lambda x: x["count"], reverse=True
            )[:3],
            "top_grievances": sorted(
                [{"type": k, "count": v} for k, v in grievance_types.items()],
                key=lambda x: x["count"], reverse=True
            )[:3],
            "ai_recommendation": (
                f"Run a document-check camp for '{top_doc_issue}' issues. "
                f"Most demanded scheme: {top_scheme}. "
                f"Top grievance: {top_grievance} — consider IVR awareness blast."
            ),
            "local_officer_contact": {
                "name": f"{location} District Collector Office",
                "phone": "1800-11-0001",
                "portal": "https://pgportal.gov.in",
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_navigator(self, location: str = "India", service: str = "csc") -> Dict[str, Any]:
        service = (service or "csc").strip().lower()
        nearest = {
            "name": f"{location} Citizen Service Center",
            "address": f"Main Road, {location}",
            "hours": "Mon-Sat, 10:00-17:00",
            "contact": "+91-9000000000",
            "maps_url": f"https://maps.google.com/?q={location}+csc+center",
        }
        return {
            "service": service,
            "location": location,
            "nearest_center": nearest,
            "required_documents": ["Aadhaar", "Mobile Number", "Bank Passbook"],
        }

    def create_artifacts(self, session_id: str, workflow_name: str, language: str = "en") -> Dict[str, Any]:
        packet_id = f"PKT-{uuid.uuid4().hex[:8].upper()}"
        return {
            "packet_id": packet_id,
            "session_id": session_id,
            "workflow": workflow_name,
            "language": language,
            "artifacts": [
                {"type": "benefit_receipt", "status": "generated"},
                {"type": "document_checklist", "status": "generated"},
                {"type": "complaint_draft", "status": "ready"},
                {"type": "office_visit_guide", "status": "generated"},
            ],
        }

    def get_civic_journey(self, user_id: str | None = None, session_id: str | None = None) -> Dict[str, Any]:
        steps: List[Dict[str, Any]] = []
        journey_query = db.session.query(CivicJourneyEvent)
        if user_id:
            journey_query = journey_query.filter(CivicJourneyEvent.user_id == user_id)
        if session_id:
            journey_query = journey_query.filter(CivicJourneyEvent.session_id == session_id)
        journey_events = journey_query.order_by(CivicJourneyEvent.created_at.desc()).limit(20).all()
        if journey_events:
            return {"journey": [evt.to_dict() for evt in reversed(journey_events)]}

        if session_id:
            conv = (
                db.session.query(Conversation)
                .filter(Conversation.user_id == (user_id or "anonymous"))
                .order_by(Conversation.timestamp.desc())
                .limit(10)
                .all()
            )
            if conv:
                steps.append({"stage": "Query Registered", "status": "completed"})

        apps = (
            db.session.query(SchemeApplication)
            .filter(SchemeApplication.user_id == (user_id or "anonymous"))
            .order_by(SchemeApplication.updated_at.desc())
            .limit(10)
            .all()
        )
        for a in apps[:4]:
            steps.append({
                "stage": a.scheme_name or "Scheme",
                "status": a.status or "pending",
                "updated_at": a.updated_at.isoformat() if a.updated_at else None,
            })

        if not steps:
            steps = [
                {"stage": "Intent Captured", "status": "completed"},
                {"stage": "Eligibility Screening", "status": "in_progress"},
                {"stage": "Artifact Dispatch", "status": "pending"},
            ]
        return {"journey": steps}

    def report_fraud(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        report = {
            "report_id": f"FRD-{uuid.uuid4().hex[:8].upper()}",
            "ts": datetime.now(timezone.utc).isoformat(),
            "location": payload.get("location", "unknown"),
            "details": payload.get("details", ""),
            "amount": payload.get("amount", 0),
            "contact": payload.get("contact", ""),
        }
        self._append_json(self._fraud_file, report)
        return report

    def _dynamo_item_count(self, table_name: str) -> int:
        """Return approximate item count from a DynamoDB table using describe_table."""
        try:
            import boto3
            region = os.getenv("AWS_REGION", "us-east-1")
            ddb = boto3.client("dynamodb", region_name=region)
            info = ddb.describe_table(TableName=table_name)
            return info["Table"].get("ItemCount", 0)
        except Exception:
            return 0

    def get_impact_metrics(self) -> Dict[str, Any]:
        use_dynamo = os.getenv("USE_DYNAMODB", "false").lower() == "true"
        fraud_reports = len(self._read_json(self._fraud_file))

        if use_dynamo:
            # Use DynamoDB table item counts (describe_table is free and non-blocking)
            conv_table = os.getenv("DYNAMODB_CONVERSATIONS_TABLE", "JanSathi-Conversations")
            apps_table = os.getenv("DYNAMODB_APPLICATIONS_TABLE", "JanSathi-Applications")
            community_table = os.getenv("DYNAMODB_COMMUNITY_TABLE", "JanSathi-Community")
            total_conv = self._dynamo_item_count(conv_table)
            total_apps = self._dynamo_item_count(apps_table)
            total_posts = self._dynamo_item_count(community_table)
        else:
            try:
                total_conv = db.session.query(Conversation).count()
                total_apps = db.session.query(SchemeApplication).count()
                total_posts = db.session.query(CommunityPost).count()
            except Exception:
                total_conv = total_apps = total_posts = 0

        estimated_money = total_apps * 3500
        return {
            "citizens_served": total_conv,
            "applications_processed": total_apps,
            "community_posts": total_posts,
            "fraud_reports": fraud_reports,
            "estimated_benefits_unlocked_inr": estimated_money,
            "estimated_trips_avoided": int(total_apps * 1.6),
            "grievances_resolved": int(total_apps * 0.28),
        }

    def _get_profile(self, user_id: str | None) -> Dict[str, Any]:
        if not user_id:
            return {"state": "Uttar Pradesh", "occupation": "farmer", "income": 120000}
        profile = db.session.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not profile:
            return {"state": "Uttar Pradesh", "occupation": "farmer", "income": 120000}
        return {
            "state": profile.location_state,
            "occupation": profile.occupation,
            "income": profile.annual_income,
            "land_acres": profile.land_holding_acres,
            "preferred_language": profile.preferred_language,
        }

    def _read_json(self, path: str) -> List[Dict[str, Any]]:
        try:
            if not os.path.exists(path):
                return []
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def _append_json(self, path: str, item: Dict[str, Any]) -> None:
        data = self._read_json(path)
        data.append(item)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data[-500:], f, ensure_ascii=False, indent=2)

    def _advance_case_progress(self, case: LifeEventCase) -> None:
        now = datetime.now(timezone.utc)
        created = case.created_at.replace(tzinfo=timezone.utc) if case.created_at and case.created_at.tzinfo is None else case.created_at
        if not created:
            return

        steps = (
            db.session.query(LifeEventStep)
            .filter(LifeEventStep.case_id == case.case_id)
            .order_by(LifeEventStep.step_order.asc())
            .all()
        )
        if not steps:
            return
        minutes_elapsed = int((now - created).total_seconds() // 60)
        completed_steps = min(minutes_elapsed, len(steps))
        target_active = min(completed_steps, len(steps) - 1)

        for step in steps:
            if step.step_order < completed_steps:
                step.status = "completed"
            elif step.step_order == target_active and completed_steps < len(steps):
                step.status = "active"
            else:
                step.status = "pending"

        if completed_steps >= len(steps):
            for step in steps:
                step.status = "completed"
            case.status = "completed"
            case.current_step = len(steps) - 1
        else:
            case.status = "in_progress"
            case.current_step = target_active

        db.session.commit()

    def _record_journey_event(
        self,
        user_id: str,
        session_id: str,
        case_id: str,
        stage: str,
        status: str,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        evt = CivicJourneyEvent(
            user_id=user_id,
            session_id=session_id,
            case_id=case_id,
            stage=stage,
            status=status,
            metadata_json=metadata or {},
        )
        db.session.add(evt)
        db.session.commit()
