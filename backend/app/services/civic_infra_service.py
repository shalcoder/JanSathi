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
        profile = self._get_profile(user_id)
        state = (profile.get("state") or "India").lower()
        occupation = (profile.get("occupation") or "").lower()

        alerts: List[Dict[str, Any]] = []
        if "farmer" in occupation or "agri" in occupation:
            alerts.append({
                "id": f"AL-{uuid.uuid4().hex[:8].upper()}",
                "title": "Solar Pump Subsidy Match",
                "message": "You may qualify for a solar irrigation subsidy. Say: apply solar pump.",
                "priority": "high",
                "channel": "sms",
            })
        alerts.append({
            "id": f"AL-{uuid.uuid4().hex[:8].upper()}",
            "title": "PDS / Ration Card Renewal Window",
            "message": "Renewal cycle is open in your district. Check documents now to avoid rejection.",
            "priority": "medium",
            "channel": "ivr+sms",
        })
        if "tamil" in state or "nad" in state:
            alerts.append({
                "id": f"AL-{uuid.uuid4().hex[:8].upper()}",
                "title": "Tamil Nadu Farmer Support Add-on",
                "message": "A state add-on support workflow is available for eligible small farmers.",
                "priority": "medium",
                "channel": "sms",
            })

        self._append_json(self._alerts_file, {
            "ts": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id or "anonymous",
            "count": len(alerts),
        })
        return {"alerts": alerts, "count": len(alerts)}

    def get_community_insights(self, location: str = "India") -> Dict[str, Any]:
        posts = (
            db.session.query(CommunityPost)
            .filter(CommunityPost.location.ilike(f"%{location}%"))
            .order_by(CommunityPost.timestamp.desc())
            .limit(100)
            .all()
        )
        by_title_keywords = {}
        for p in posts:
            title = (p.title or "").lower()
            for kw in ("pm-kisan", "ration", "ayushman", "awas", "e-shram"):
                if kw in title:
                    by_title_keywords[kw] = by_title_keywords.get(kw, 0) + 1

        top_issue = max(by_title_keywords.items(), key=lambda x: x[1])[0] if by_title_keywords else "document mismatch"
        return {
            "location": location,
            "posts_analyzed": len(posts),
            "top_scheme_topics": sorted(
                [{"topic": k, "count": v} for k, v in by_title_keywords.items()],
                key=lambda x: x["count"],
                reverse=True,
            )[:5],
            "common_document_issue": top_issue,
            "recommended_action": "Run a local document-check camp and IVR awareness blast.",
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

    def get_impact_metrics(self) -> Dict[str, Any]:
        total_conv = db.session.query(Conversation).count()
        total_apps = db.session.query(SchemeApplication).count()
        total_posts = db.session.query(CommunityPost).count()
        fraud_reports = len(self._read_json(self._fraud_file))
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
