"""
scheme_feed_service.py

Builds a personalized, auto-refreshable scheme feed for the dashboard.
Sources:
1) SQLite Scheme table (if present)
2) app/data/schemes_config.yaml (authoritative fallback)
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any, Dict, List, Optional

import yaml

from app.models.models import Scheme, UserProfile


class SchemeFeedService:
    """Aggregates and personalizes scheme cards for the UI."""

    def __init__(self) -> None:
        self._cache: List[Dict[str, Any]] = []
        self._cache_at: Optional[datetime] = None
        self._lock = Lock()
        self._refresh_interval_seconds = int(os.getenv("SCHEME_FEED_REFRESH_SECONDS", "120"))

    @property
    def refresh_interval_seconds(self) -> int:
        return self._refresh_interval_seconds

    def get_feed(self, user_id: str) -> Dict[str, Any]:
        base_schemes = self._get_base_schemes()
        profile = UserProfile.query.get(user_id)

        scored: List[Dict[str, Any]] = []
        for scheme in base_schemes:
            enriched = self._personalize_scheme(scheme, profile)
            scored.append(enriched)

        scored.sort(
            key=lambda item: (
                item.get("eligibility_score", 0.0),
                item.get("last_updated_at", ""),
            ),
            reverse=True,
        )

        return {
            "schemes": scored,
            "count": len(scored),
            "personalization": {
                "user_id": user_id,
                "profile_found": profile is not None,
                "engine": "rule_agent_v1",
            },
            "meta": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "refresh_interval_seconds": self._refresh_interval_seconds,
                "data_sources": ["sqlite:Scheme", "yaml:schemes_config"],
            },
        }

    def _get_base_schemes(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        with self._lock:
            if self._cache_at and now - self._cache_at < timedelta(seconds=self._refresh_interval_seconds):
                return [dict(item) for item in self._cache]

            merged = self._load_from_db()
            merged.extend(self._load_from_yaml())

            # De-duplicate by id while keeping richer DB rows first.
            seen = set()
            deduped: List[Dict[str, Any]] = []
            for item in merged:
                sid = item["id"]
                if sid in seen:
                    continue
                seen.add(sid)
                deduped.append(item)

            self._cache = deduped
            self._cache_at = now
            return [dict(item) for item in deduped]

    def _load_from_db(self) -> List[Dict[str, Any]]:
        rows = Scheme.query.all()
        out: List[Dict[str, Any]] = []
        for row in rows:
            data = row.to_dict()
            out.append(
                {
                    "id": str(data.get("id") or "").strip(),
                    "title": str(data.get("title") or "").strip(),
                    "benefit": str(data.get("benefit") or "Benefits as per official guidelines"),
                    "ministry": str(data.get("ministry") or "Government of India"),
                    "category": self._normalize_category(str(data.get("category") or "")),
                    "keywords": data.get("keywords") if isinstance(data.get("keywords"), list) else [],
                    "description": str(data.get("text") or ""),
                    "apply_link": str(data.get("link") or ""),
                    "official_source": str(data.get("link") or "https://www.india.gov.in"),
                    "last_updated_at": datetime.now(timezone.utc).isoformat(),
                    "source": "database",
                }
            )
        return [s for s in out if s["id"] and s["title"]]

    def _load_from_yaml(self) -> List[Dict[str, Any]]:
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "schemes_config.yaml",
        )
        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as f:
            parsed = yaml.safe_load(f) or {}
        schemes = parsed.get("schemes", {})
        out: List[Dict[str, Any]] = []

        for sid, item in schemes.items():
            if not isinstance(item, dict):
                continue
            display_name = str(item.get("display_name") or sid.replace("_", " ").title())
            desc = str(item.get("description") or "")
            sources = item.get("sources") if isinstance(item.get("sources"), list) else []
            source_url = ""
            if sources and isinstance(sources[0], dict):
                source_url = str(sources[0].get("url") or "")
            out.append(
                {
                    "id": sid,
                    "title": display_name,
                    "benefit": desc or "Check official portal for latest benefits",
                    "ministry": self._guess_ministry(display_name),
                    "category": self._infer_category(display_name, desc),
                    "keywords": self._keywords_from_text(display_name, desc),
                    "description": desc,
                    "apply_link": source_url or "https://www.india.gov.in",
                    "official_source": source_url or "https://www.india.gov.in",
                    "last_updated_at": datetime.now(timezone.utc).isoformat(),
                    "source": "yaml",
                }
            )
        return out

    def _personalize_scheme(self, scheme: Dict[str, Any], profile: Optional[UserProfile]) -> Dict[str, Any]:
        score = 0.45
        reasons: List[str] = []

        title = str(scheme.get("title", "")).lower()
        category = str(scheme.get("category", "")).lower()
        keywords = [str(k).lower() for k in (scheme.get("keywords") or [])]

        if profile:
            occupation = (profile.occupation or "").lower()
            income = profile.annual_income or 0
            land = profile.land_holding_acres or 0

            if occupation:
                if "farmer" in occupation and (
                    "agriculture" in category or "kisan" in title or "farmer" in " ".join(keywords)
                ):
                    score += 0.35
                    reasons.append("Matches your farming occupation")
                if "student" in occupation and ("education" in category or "scholar" in title):
                    score += 0.35
                    reasons.append("Matches your student profile")
                if "worker" in occupation and ("labour" in title or "shram" in title):
                    score += 0.35
                    reasons.append("Matches unorganised worker support")

            if income and income <= 300000:
                if any(word in (title + " " + " ".join(keywords)) for word in ["subsidy", "insurance", "benefit", "pm"]):
                    score += 0.15
                    reasons.append("Suitable for lower-income households")

            if land and land < 2 and ("kisan" in title or "agriculture" in category):
                score += 0.15
                reasons.append("Landholding-based eligibility likely")
        else:
            reasons.append("Complete profile for stronger personalization")

        score = max(0.0, min(score, 0.99))
        status = "eligible" if score >= 0.75 else "likely_eligible" if score >= 0.55 else "check_criteria"

        enriched = dict(scheme)
        enriched["eligibility_score"] = round(score, 2)
        enriched["eligibility_status"] = status
        enriched["why_recommended"] = reasons[:3]
        return enriched

    @staticmethod
    def _normalize_category(raw: str) -> str:
        raw = raw.lower().strip()
        if raw in {"agriculture", "housing", "education", "health"}:
            return raw
        if "agri" in raw or "farm" in raw:
            return "agriculture"
        if "house" in raw or "awas" in raw:
            return "housing"
        if "edu" in raw or "student" in raw:
            return "education"
        if "health" in raw or "medical" in raw:
            return "health"
        return "general"

    @staticmethod
    def _infer_category(name: str, desc: str) -> str:
        text = f"{name} {desc}".lower()
        if "kisan" in text or "farm" in text or "agri" in text:
            return "agriculture"
        if "awas" in text or "house" in text:
            return "housing"
        if "school" in text or "scholar" in text or "education" in text:
            return "education"
        if "health" in text or "hospital" in text or "insurance" in text:
            return "health"
        return "general"

    @staticmethod
    def _guess_ministry(name: str) -> str:
        low = name.lower()
        if "kisan" in low or "agri" in low:
            return "Ministry of Agriculture"
        if "awas" in low or "house" in low:
            return "Ministry of Housing"
        if "health" in low or "ayushman" in low:
            return "Ministry of Health"
        if "shram" in low or "worker" in low:
            return "Ministry of Labour"
        return "Government of India"

    @staticmethod
    def _keywords_from_text(name: str, desc: str) -> List[str]:
        tokens = f"{name} {desc}".lower().replace("-", " ").replace("/", " ").split()
        filtered = [t for t in tokens if len(t) > 3]
        # Keep deterministic order, unique values.
        seen = set()
        uniq: List[str] = []
        for token in filtered:
            if token in seen:
                continue
            seen.add(token)
            uniq.append(token)
        return uniq[:8]
