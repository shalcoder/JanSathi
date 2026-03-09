"""
life_events.py — Life Event Workflow Definitions
=================================================
Maps real-life citizen events to cascaded government service workflows.

Citizens don't think in schemes — they think in life events.
"My crop failed" → 5 government services triggered automatically.
"""
from typing import List, Dict, Any

# ── Life event → cascaded service workflow definitions ─────────────────────────

LIFE_EVENT_WORKFLOWS: Dict[str, Dict[str, Any]] = {
    "crop_failure": {
        "event_label": "Crop Loss / Failure",
        "icon": "🌾",
        "trigger_keywords": [
            "crop failed", "fasal barbad", "fasal kharab", "crop loss", "khet mein nuksan",
            "baarish se nuksan", "sukha", "drought", "flood damage", "pest attack",
            "फसल बर्बाद", "फसल खराब", "सूखा", "बाढ़", "कीट", "crop damaged",
            "फसल नुकसान", "खेत बर्बाद"
        ],
        "steps": [
            {
                "id": "crop_insurance",
                "label": "Pradhan Mantri Fasal Bima Yojana",
                "description": "File crop insurance claim for loss compensation",
                "action": "File insurance claim within 72 hours of crop loss",
                "link": "https://pmfby.gov.in",
                "priority": "urgent",
                "scheme_hint": "pmfby",
                "documents": ["Aadhaar", "Land records (Khasra/Khatauni)", "Bank passbook", "Crop loss photo"],
            },
            {
                "id": "pm_kisan",
                "label": "PM-KISAN Emergency Support",
                "description": "Verify next PM-KISAN installment (₹2,000) is credited",
                "action": "Check installment status and raise grievance if pending",
                "link": "https://pmkisan.gov.in",
                "priority": "high",
                "scheme_hint": "pm_kisan",
                "documents": ["Aadhaar", "Bank account linked to PM-KISAN"],
            },
            {
                "id": "state_sdrf",
                "label": "State Disaster Relief Fund (SDRF)",
                "description": "Apply for state government compensation for crop loss",
                "action": "Visit local tehsildar office with Girdawari (crop inspection report)",
                "link": "https://ndma.gov.in",
                "priority": "high",
                "scheme_hint": "sdrf",
                "documents": ["Aadhaar", "Land records", "Girdawari report from Patwari"],
            },
            {
                "id": "kcc_moratorium",
                "label": "Kisan Credit Card Loan Moratorium",
                "description": "Apply for loan repayment deferral at your bank",
                "action": "Visit bank branch with crop loss certificate",
                "link": "https://pmkisan.gov.in/kcc.aspx",
                "priority": "medium",
                "scheme_hint": "kcc",
                "documents": ["KCC passbook", "Crop loss certificate", "Aadhaar"],
            },
            {
                "id": "doc_checklist",
                "label": "Document Checklist & Preparation",
                "description": "Complete document list for all above claims",
                "action": "Collect all documents: Aadhaar, Khasra, Bank passbook, Photos",
                "link": None,
                "priority": "low",
                "scheme_hint": "documents",
                "documents": ["Aadhaar card", "Khasra/Khatauni (land record)", "Bank passbook", "Crop loss photograph (date-stamped)", "Girdawari report"],
            },
        ],
        "summary_template": "Crop loss detected. I've found {count} government services that can help you. Starting with urgent insurance claim (72-hour deadline).",
    },

    "child_birth": {
        "event_label": "New Child Birth",
        "icon": "👶",
        "trigger_keywords": [
            "baby born", "bachcha hua", "bacha paida hua", "delivery hua", "prasav hua",
            "naya bachcha", "new baby", "child birth", "born", "delivery",
            "बच्चा पैदा हुआ", "बच्चे का जन्म", "प्रसव", "शिशु", "नवजात",
            "mera beta hua", "meri beti hui", "pregnant delivery"
        ],
        "steps": [
            {
                "id": "birth_certificate",
                "label": "Birth Certificate Registration",
                "description": "Register birth within 21 days at local municipal office",
                "action": "Visit nearest municipal/gram panchayat office",
                "link": "https://crsorgi.gov.in",
                "priority": "urgent",
                "scheme_hint": "birth_cert",
                "documents": ["Hospital discharge slip", "Parents Aadhaar", "Marriage certificate"],
            },
            {
                "id": "aadhaar_child",
                "label": "Child Aadhaar (Baal Aadhaar)",
                "description": "Enroll child for Baal Aadhaar (blue card for under-5)",
                "action": "Visit Aadhaar enrollment center with birth certificate",
                "link": "https://uidai.gov.in",
                "priority": "high",
                "scheme_hint": "aadhaar",
                "documents": ["Birth certificate", "One parent's Aadhaar"],
            },
            {
                "id": "jsy",
                "label": "Janani Suraksha Yojana",
                "description": "₹1,400 cash incentive for institutional delivery (BPL mothers)",
                "action": "Apply at ASHA worker or ANM within 1 month",
                "link": "https://nhm.gov.in/index1.php?lang=1&level=3&sublinkid=841&lid=309",
                "priority": "high",
                "scheme_hint": "jsy",
                "documents": ["Mother's Aadhaar", "BPL card", "Hospital discharge summary", "Bank passbook"],
            },
            {
                "id": "poshan_abhiyan",
                "label": "Poshan Abhiyan / ICDS Nutrition",
                "description": "Free nutrition support and health checkups via Anganwadi",
                "action": "Register at nearest Anganwadi center",
                "link": "https://poshanabhiyaan.gov.in",
                "priority": "medium",
                "scheme_hint": "poshan",
                "documents": ["Child's birth certificate", "Mother's Aadhaar"],
            },
            {
                "id": "vaccination",
                "label": "Routine Immunization Schedule",
                "description": "Free vaccines: BCG, Polio, DPT, Hepatitis B at government hospital",
                "action": "Visit PHC/government hospital for immunization card",
                "link": "https://hmnhsrc.in",
                "priority": "medium",
                "scheme_hint": "vaccination",
                "documents": ["Birth certificate"],
            },
        ],
        "summary_template": "Congratulations! I've identified {count} important registrations and benefits for your newborn. Starting with birth certificate (must be done within 21 days).",
    },

    "job_loss": {
        "event_label": "Job Loss / Unemployment",
        "icon": "💼",
        "trigger_keywords": [
            "job gaya", "naukri gayi", "lost job", "naukri chali gayi", "unemployed",
            "kaam nahi hai", "kaam chut gaya", "fired", "laid off", "retrenchment",
            "नौकरी गई", "बेरोजगार", "काम नहीं", "नौकरी छूट गई",
            "company band ho gayi", "job loss", "work loss"
        ],
        "steps": [
            {
                "id": "eshram",
                "label": "e-Shram Registration",
                "description": "Register as unorganized worker (₹2 lakh accident insurance free)",
                "action": "Register online at eshram.gov.in with Aadhaar + bank details",
                "link": "https://eshram.gov.in",
                "priority": "urgent",
                "scheme_hint": "e_shram",
                "documents": ["Aadhaar", "Bank account number", "Mobile linked to Aadhaar"],
            },
            {
                "id": "pmkvy",
                "label": "PM Kaushal Vikas Yojana (Skill Training)",
                "description": "Free skill certification in 300+ job roles with ₹8,000 reward",
                "action": "Find nearest PMKVY training center",
                "link": "https://pmkvyofficial.org",
                "priority": "high",
                "scheme_hint": "pmkvy",
                "documents": ["Aadhaar", "Educational certificates", "Passport photo"],
            },
            {
                "id": "ncs_portal",
                "label": "National Career Service Portal",
                "description": "Free job placement, resume building, career counseling",
                "action": "Register at ncs.gov.in and upload your CV",
                "link": "https://www.ncs.gov.in",
                "priority": "high",
                "scheme_hint": "ncs",
                "documents": ["Aadhaar", "Educational certificates", "Work experience documents"],
            },
            {
                "id": "mudra_loan",
                "label": "PM MUDRA Yojana (Self-Employment Loan)",
                "description": "Collateral-free loan ₹50K–₹10L to start your own business",
                "action": "Apply at nearest bank or MUDRA portal",
                "link": "https://mudra.org.in",
                "priority": "medium",
                "scheme_hint": "mudra",
                "documents": ["Aadhaar", "PAN card", "Business plan (brief)", "Bank statement 6 months"],
            },
            {
                "id": "ration_card",
                "label": "NFSA Ration Card Check",
                "description": "Ensure your ration card is active for subsidized food grains",
                "action": "Check ration card status at your state food portal",
                "link": "https://nfsa.gov.in",
                "priority": "medium",
                "scheme_hint": "nfsa",
                "documents": ["Aadhaar", "Existing ration card (if any)"],
            },
        ],
        "summary_template": "I've mapped {count} government services to help you get back on track. Priority: e-Shram registration (immediate free insurance coverage).",
    },

    "house_damage": {
        "event_label": "House Damage / Homeless",
        "icon": "🏚️",
        "trigger_keywords": [
            "ghar toot gaya", "house damaged", "ghar girh gaya", "flood damaged house",
            "fire mein ghar jala", "ghar nahi hai", "homeless", "no house",
            "घर टूट गया", "घर बह गया", "बाढ़ में घर", "घर नहीं है",
            "natural disaster house", "earthquake damage"
        ],
        "steps": [
            {
                "id": "pmay_gramin",
                "label": "PM Awas Yojana - Gramin",
                "description": "₹1.2 lakh grant to construct permanent house (rural)",
                "action": "Apply through Gram Panchayat or pmayg.nic.in",
                "link": "https://pmayg.nic.in",
                "priority": "urgent",
                "scheme_hint": "pm_awas_gramin",
                "documents": ["Aadhaar", "Bank passbook", "Land ownership proof", "BPL/SECC list inclusion proof"],
            },
            {
                "id": "sdrf_house",
                "label": "SDRF Disaster Compensation",
                "description": "State government compensation for disaster-damaged house",
                "action": "File claim at District Collector office within 30 days",
                "link": "https://ndma.gov.in",
                "priority": "urgent",
                "scheme_hint": "sdrf",
                "documents": ["Aadhaar", "House ownership documents", "Damage photos", "FIR (for fire/theft)"],
            },
            {
                "id": "pmay_urban",
                "label": "PM Awas Yojana - Urban",
                "description": "Subsidy on home loan for urban EWS/LIG households",
                "action": "Apply via CSC center or pmaymis.gov.in",
                "link": "https://pmaymis.gov.in",
                "priority": "high",
                "scheme_hint": "pm_awas_urban",
                "documents": ["Aadhaar", "Income certificate", "Bank statement", "Property documents"],
            },
        ],
        "summary_template": "House damage detected. I've found {count} housing schemes. SDRF compensation application has a 30-day deadline.",
    },

    "marriage": {
        "event_label": "Marriage",
        "icon": "💍",
        "trigger_keywords": [
            "shaadi ho gayi", "marriage", "wedding", "vivah", "nikah", "byah",
            "शादी हुई", "विवाह", "निकाह", "मेरी शादी",
            "daughter marriage", "beti ki shaadi", "son marriage", "inter-caste marriage"
        ],
        "steps": [
            {
                "id": "marriage_cert",
                "label": "Marriage Certificate Registration",
                "description": "Legal marriage registration at Sub-Registrar office",
                "action": "Register within 1 year of marriage",
                "link": "https://egrass.maharashtra.gov.in",
                "priority": "high",
                "scheme_hint": "marriage_cert",
                "documents": ["Both Aadhaar cards", "Age proof", "Passport photos", "2 witnesses"],
            },
            {
                "id": "inter_caste",
                "label": "Dr. Ambedkar Inter-Caste Marriage Scheme",
                "description": "₹2.5 lakh incentive for inter-caste marriages",
                "action": "Apply within 1 year at District Social Welfare Office",
                "link": "https://socialjustice.nic.in",
                "priority": "medium",
                "scheme_hint": "intercaste_marriage",
                "documents": ["Marriage certificate", "Caste certificates of both", "Joint bank account", "Aadhaar"],
            },
        ],
        "summary_template": "Marriage registered! I've found {count} important services including legal registration and potential incentives.",
    },

    "health_emergency": {
        "event_label": "Health Emergency / Illness",
        "icon": "🏥",
        "trigger_keywords": [
            "bimaar hun", "hospital mein hun", "bemar ho gaya", "operation chahiye",
            "cancer", "heart attack", "dialysis", "illness", "sick", "surgery needed",
            "बीमार हूं", "अस्पताल", "ऑपरेशन", "इलाज नहीं कर सकते",
            "medical help", "health problem", "serious illness"
        ],
        "steps": [
            {
                "id": "ayushman",
                "label": "Ayushman Bharat PM-JAY",
                "description": "₹5 lakh/year free health insurance at 25,000+ empanelled hospitals",
                "action": "Check eligibility and get Ayushman card at nearest CSC",
                "link": "https://pmjay.gov.in",
                "priority": "urgent",
                "scheme_hint": "pmjay",
                "documents": ["Aadhaar", "Ration card / SECC inclusion", "Mobile number"],
            },
            {
                "id": "cghs",
                "label": "Rashtriya Arogya Nidhi / State Health Scheme",
                "description": "Financial assistance for BPL patients with life-threatening diseases",
                "action": "Apply through treating hospital's social worker",
                "link": "https://nhp.gov.in",
                "priority": "high",
                "scheme_hint": "ran",
                "documents": ["BPL card", "Doctor's prescription", "Hospital estimate", "Aadhaar"],
            },
        ],
        "summary_template": "Health emergency detected. Ayushman Bharat can cover up to ₹5 lakh in hospital costs. Checking your eligibility now.",
    },
}


def detect_life_event(query: str, language: str = "hi") -> Dict[str, Any] | None:
    """
    Detect if a user query describes a life event.
    Returns the matching workflow dict or None if no event detected.

    Uses keyword matching. Works offline, no LLM needed.
    """
    q = query.lower().strip()

    for event_id, workflow in LIFE_EVENT_WORKFLOWS.items():
        for keyword in workflow["trigger_keywords"]:
            if keyword.lower() in q:
                return {
                    "event_id": event_id,
                    "event_label": workflow["event_label"],
                    "icon": workflow["icon"],
                    "steps": workflow["steps"],
                    "summary": workflow["summary_template"].format(count=len(workflow["steps"])),
                    "step_count": len(workflow["steps"]),
                }

    return None


def get_workflow(event_id: str) -> Dict[str, Any] | None:
    """Return full workflow definition by event_id."""
    wf = LIFE_EVENT_WORKFLOWS.get(event_id)
    if not wf:
        return None
    return {
        "event_id": event_id,
        **wf,
    }
