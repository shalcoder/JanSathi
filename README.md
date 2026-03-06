# 🇮🇳 JanSathi — India's First Real-Time Speech-to-Speech Agentic Civic Automation System

<div align="center">

[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2016-black?logo=next.js)](https://nextjs.org)
[![Flask](https://img.shields.io/badge/Backend-Flask%20%2B%20Python-blue?logo=python)](https://flask.palletsprojects.com)
[![AWS Bedrock](https://img.shields.io/badge/AI-AWS%20Bedrock%20Claude-orange?logo=amazon-aws)](https://aws.amazon.com/bedrock)
[![Amazon Kendra](https://img.shields.io/badge/RAG-Amazon%20Kendra-orange?logo=amazon-aws)](https://aws.amazon.com/kendra)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**A voice-first, multilingual AI system that helps rural Indians check government scheme eligibility, draft grievances, and receive civic artifacts — all through a phone call.**

[Live Demo](#running-locally) · [Architecture](#system-architecture) · [API Reference](#api-reference) · [Features](#features)

</div>

---

## 🎯 The Problem

In rural India:

- **65% of citizens** cannot navigate government portals
- Citizens waste trips to offices due to **incomplete documents**
- Eligibility criteria are confusing and **written in bureaucratic language**
- Middlemen charge for information that should be **free**
- Many users have **feature phones**, not smartphones

JanSathi solves the **pre-submission gap** — preparing citizens before they ever reach a government office.

---

## 💡 The Solution

JanSathi is a **telecom-native civic readiness infrastructure**. A citizen makes a phone call (or uses the web emulator), speaks naturally in their language, and within 90 seconds receives:

- ✅ An eligibility verdict with reasoning trace
- 📄 A downloadable HTML BenefitReceipt
- 📋 A document checklist for their next CSC visit
- 📱 An SMS summary dispatched to their phone

No app. No smartphone. No middleman. No literacy required.

---

## ✨ Features

### 🎙️ Core Interaction

| Feature                    | Description                                                            |
| -------------------------- | ---------------------------------------------------------------------- |
| Real-Time Speech-to-Speech | Citizen speaks, system responds in voice via Web Speech API + TTS      |
| Multi-lingual IVR          | Hindi, Tamil, English — expandable to 10+ Indian languages             |
| Web Phone Emulator         | Browser-based phone with mic, DTMF keypad, call timer, live transcript |
| Amazon Connect Integration | Full IVR telephony via AWS Connect + Lambda webhook                    |

### 🤖 AI & Agent Engine

| Feature                    | Description                                                                    |
| -------------------------- | ------------------------------------------------------------------------------ |
| Intent Classification      | AWS Bedrock Claude Haiku (LLM) or keyword fallback classifier                  |
| Slot Collection FSM        | Conversational question-answer loop to collect scheme-specific data            |
| Deterministic Rules Engine | Eligibility evaluated against official Government Orders — no AI hallucination |
| Agentic RAG Retrieval      | Amazon Kendra retrieves live government scheme documents                       |
| Grievance Auto-Draft       | Bedrock LLM generates a formal grievance letter with reference ID              |
| Personalization Engine     | Adapts tone and suggestions by state, income, occupation, language             |

### 📋 Civic Workflows (3 Automated Pipelines)

| Workflow                     | What it does                                                            |
| ---------------------------- | ----------------------------------------------------------------------- |
| **PM-Kisan Eligibility**     | Land ownership + income + state → ELIGIBLE/NOT ELIGIBLE verdict in <30s |
| **PM Awas Yojana Readiness** | Housing eligibility check + document gap analysis                       |
| **Grievance Registration**   | Formal complaint drafted by LLM with GRV-XXXXXX reference ID            |

### 📄 Artifacts Generated

| Artifact              | Description                                                                    |
| --------------------- | ------------------------------------------------------------------------------ |
| BenefitReceipt (HTML) | Eligibility verdict + rules trace + document checklist (S3-hosted, 7-day link) |
| Grievance Draft       | Formal government complaint letter, ready for CSC submission                   |
| Scheme Checklist      | Missing documents clearly listed in the citizen's language                     |

### 📊 Admin & Observability

| Feature              | Description                                                              |
| -------------------- | ------------------------------------------------------------------------ |
| Live Admin Dashboard | Calls processed, eligibility rate, HITL rate, latency metrics            |
| Telemetry Panel      | Intent, confidence score, slot values, rule trace, risk score — per call |
| HITL Verifier Queue  | Human-in-the-loop escalation for edge cases and low-confidence decisions |
| Audit Trail          | Every interaction logged with consent record for DPDP compliance         |

### 🔒 Security

| Feature             | Description                                                 |
| ------------------- | ----------------------------------------------------------- |
| PII Masking         | Aadhaar, phone, income masked in all UI components          |
| DPDP Compliance     | Data protection hash + consent capture at call start        |
| Hallucination Guard | AI responses validated against known government domain list |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ENTRY LAYER                                  │
│   📞 Amazon Connect IVR  ──────  🌐 Web Phone Emulator (Next.js)    │
│         │                                    │                        │
│         └──── Lambda (connect_webhook) ──────┘                       │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ POST /v1/query
┌─────────────────────────────▼───────────────────────────────────────┐
│                       INTELLIGENCE LAYER                             │
│                                                                       │
│  1. Intent Agent (BedrockIntentClassifier / RuleBasedClassifier)     │
│  2. RAG Agent  (Amazon Kendra → scheme documents)                    │
│  3. Slot Agent (FSM slot collection per scheme)                      │
│  4. Rules Agent (Deterministic RulesEngine — no LLM)                 │
│  5. Verifier Agent (confidence < 0.8 → HITL escalation)             │
│  6. Orchestrator (AWS Step Functions / local FSM)                    │
│  7. Notification Agent (AWS SNS → SMS)                               │
│  8. Receipt Agent (ReceiptService → HTML → S3)                       │
│  9. HITL Agent (Human review queue)                                   │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                         DATA LAYER                                   │
│                                                                       │
│   DynamoDB: sessions, hitl_cases, applications, users                │
│   S3: BenefitReceipts, audio recordings, uploaded documents          │
│   SQLite/PostgreSQL: community posts, scheme applications (dev)      │
└─────────────────────────────────────────────────────────────────────┘
```

### LLM Philosophy

- ✅ **LLMs are used for**: Intent classification, grievance drafting, information summarization
- ❌ **LLMs are NOT used for**: Eligibility logic, rule evaluation, numeric validation
- The **Deterministic Rules Engine always overrides LLM outputs** on eligibility decisions

---

## 🗄️ Project Structure

```
JanSathi/
├── frontend/                   # Next.js 16 app (App Router)
│   └── src/
│       ├── app/
│       │   ├── dashboard/      # Protected dashboard
│       │   └── (auth)/         # Clerk auth pages
│       └── components/
│           ├── features/
│           │   ├── dashboard/
│           │   │   ├── PhoneEmulatorPage.tsx   # Web IVR emulator
│           │   │   ├── SMSSimulator.tsx        # Animated SMS inbox
│           │   │   ├── TelemetryPanel.tsx      # Live agent debug panel
│           │   │   ├── ImpactMode.tsx          # Impact metrics dashboard
│           │   │   ├── OverviewPage.tsx        # Admin command center
│           │   │   └── ...
│           │   └── chat/
│           │       └── BenefitReceipt.tsx      # Eligibility receipt display
│           └── layout/
│               └── Sidebar.tsx                 # Navigation
│
├── backend/                    # Flask + Python
│   ├── app/
│   │   ├── api/
│   │   │   └── v1_routes.py    # All /v1/* endpoints
│   │   ├── core/
│   │   │   └── execution.py    # Main agentic execution pipeline
│   │   ├── services/
│   │   │   ├── intent_service.py        # Bedrock + keyword classification
│   │   │   ├── bedrock_service.py       # Claude LLM integration
│   │   │   ├── rag_service.py           # Amazon Kendra RAG
│   │   │   ├── rules_engine.py          # Deterministic eligibility engine
│   │   │   ├── receipt_service.py       # HTML receipt + S3 upload
│   │   │   ├── notify_service.py        # AWS SNS SMS dispatch
│   │   │   ├── personalization_service.py # Profile-aware prompting
│   │   │   └── hitl_service.py          # Human-in-the-loop queue
│   │   └── data/
│   │       └── schemes_config.yaml      # Scheme definitions (slots + rules)
│   ├── agentic_engine/
│   │   ├── workflow_engine.py   # FSM orchestration
│   │   ├── state_machine.py     # Valid state transitions
│   │   └── session_manager.py   # Session persistence
│   └── main.py
│
├── infrastructure/              # AWS CDK stacks
│   └── stacks/
│       ├── api_stack.py
│       └── frontend_stack.py
│
└── scripts/                    # Dev utilities
```

---

## 🚀 Running Locally

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- **AWS account** (optional — falls back gracefully without credentials)

### 1. Clone & Install

```bash
git clone https://github.com/shalcoder/JanSathi.git
cd JanSathi
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your AWS credentials (optional for local dev)
python main.py
# Backend runs on http://localhost:5000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Add NEXT_PUBLIC_API_URL=http://localhost:5000
npm run dev
# Frontend runs on http://localhost:3000
```

### 4. Test the Phone Emulator

1. Open `http://localhost:3000` in **Chrome or Edge** (required for mic input)
2. Sign in via Clerk
3. Navigate to **Dashboard → "2. Web Phone Emulator"**
4. Select language → Press **Call**
5. Say: _"PM Kisan check karna hai"_

---

## ⚙️ Environment Variables

### Backend (`backend/.env`)

```env
# AWS (optional — system works locally without these)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-south-1

# AI Models
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
INTENT_CLASSIFIER=rule_based       # or "bedrock" for LLM classification
KENDRA_INDEX_ID=your_kendra_index  # or "mock-index" for local

# Storage
STORAGE_TYPE=local                 # or "dynamodb"
DATABASE_URL=sqlite:///jansathi.db

# Notifications
SNS_TOPIC_ARN=arn:aws:sns:...
RECEIPT_BUCKET=jansathi-receipts
RECEIPT_BASE_URL=https://your-domain.com/receipt

# Flask
SECRET_KEY=your-secret-key
PORT=5000
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
```

---

## 📡 API Reference

### Core Endpoints

#### `POST /v1/query` — Main agentic pipeline

```json
{
  "session_id": "sess-abc123",
  "message": "PM Kisan ke liye apply karna hai",
  "language": "hi",
  "channel": "web-ivr",
  "user_profile": {
    "name": "Ramesh Kumar",
    "state": "up",
    "occupation": "farmer",
    "income_bracket": "low"
  }
}
```

**Response:**

```json
{
  "response_text": "PM-Kisan के लिए आपकी पात्रता जांची जा रही है...",
  "workflow_stage": "COLLECT_SLOTS",
  "slots": { "state": "uttar pradesh" },
  "rule_trace": [
    {
      "label": "Land < 2 hectares",
      "pass": true,
      "citation": "PM-Kisan GO 2019"
    }
  ],
  "artifact_generated": {
    "type": "receipt",
    "url": "https://...",
    "eligible": true
  },
  "sms_payload": { "body": "JanSathi: ELIGIBLE ✅ — Case JS-2024-..." },
  "telemetry": {
    "intent": "apply",
    "confidence": 0.9,
    "latency_ms": 420,
    "risk_score": 0.1
  }
}
```

#### `POST /v1/sessions/init` — Create session

#### `GET /v1/sessions/:id` — Get session state

#### `POST /v1/apply` — Submit scheme application

#### `GET /v1/applications` — List applications

#### `GET /v1/admin/cases` — HITL case queue

#### `GET /v1/admin/dashboard-stats` — Live KPI aggregates

#### `POST /v1/ivr/connect-webhook` — Amazon Connect Lambda proxy

---

## 🔁 End-to-End Call Flow

```
Citizen Calls
     │
     ▼
Consent Captured → Language Selected
     │
     ▼
Speech-to-Text (Amazon Transcribe / Web Speech API)
     │
     ▼
IntentService.classify() ──► Bedrock Claude Haiku
     │                   └──► Keyword Fallback (offline)
     │
     ▼
Route by Intent:
  ├── "apply"     → start_apply:<scheme> → FSM Slot Collection
  ├── "grievance" → Bedrock LLM Draft → GRV-XXXXXX Reference ID
  └── "track"     → Session Status Lookup
     │
     ▼
RulesEngine.evaluate() ──► Official GO Criteria (YAML config)
     │                      (Deterministic — no LLM)
     │
     ▼
ReceiptService.generate_receipt() → HTML → S3 Presigned URL
     │
     ▼
NotifyService.send_sms() → AWS SNS → Citizen's Phone
     │
     ▼
Dashboard Updated → HITL Queue (if confidence < 0.8)
```

---

## 🧪 Supported Schemes

Defined in `backend/app/data/schemes_config.yaml`:

| Scheme                 | Key             | Slots                                   | Status  |
| ---------------------- | --------------- | --------------------------------------- | ------- |
| PM-Kisan Samman Nidhi  | `pm_kisan`      | land_hectares, annual_income, state     | ✅ Live |
| PM Awas Yojana (Urban) | `pm_awas_urban` | family_income, housing_status, district | ✅ Live |
| E-Shram Card           | `e_shram`       | aadhaar_linked, occupation, state       | ✅ Live |

**Adding a new scheme:**

```yaml
# backend/app/data/schemes_config.yaml
schemes:
  my_new_scheme:
    display_name: "My New Scheme"
    slots:
      - key: income
        prompt: "What is your annual family income?"
        type: number
    rules:
      mandatory:
        - field: income
          operator: lte
          value: 180000
          label: "Annual income ≤ ₹1.8 lakh"
          citation: "Scheme GO 2023, Section 3(b)"
```

---

## 🧱 Tech Stack

| Layer              | Technology                                                      |
| ------------------ | --------------------------------------------------------------- |
| **Frontend**       | Next.js 16, TypeScript, Tailwind CSS, Framer Motion, Clerk Auth |
| **Backend**        | Python 3.10, Flask, SQLAlchemy                                  |
| **AI / LLM**       | AWS Bedrock (Claude 3 Haiku / Sonnet 3.5)                       |
| **RAG**            | Amazon Kendra (with keyword fallback)                           |
| **IVR**            | Amazon Connect + AWS Lambda                                     |
| **Database**       | DynamoDB (prod) / SQLite (dev)                                  |
| **Storage**        | Amazon S3 (receipts, audio, documents)                          |
| **SMS**            | AWS SNS Transactional                                           |
| **Auth**           | Clerk (frontend) + JWT middleware (backend)                     |
| **Infrastructure** | AWS CDK (Python), Docker                                        |
| **Speech (Web)**   | Web Speech API (STT) + SpeechSynthesis API (TTS)                |

---

## 📈 Impact Metrics (Prototype)

| Metric           | Value |
| ---------------- | ----- |
| Calls Processed  | 47+   |
| Eligibility Rate | 68%   |
| Avg Latency      | 420ms |
| Travel Avoided   | 82 km |
| Trips Saved      | 18    |
| Families Reached | 32+   |

## 🏗️ Project Status & Technical Debt

While the system is advanced, the following items reflect the current engineering focus and future horizons:

### ✅ Completed in Phase 3 (Recent)

*   **Production Auth Hardening**:
    *   **Status**: **IMPLEMENTED**.
    *   **Detail**: Enforced `ENABLE_DEV_BYPASS` security guard. Bypass is strictly disabled in `NODE_ENV=production`. `X-Correlation-Id` is now propagated for all requests.
*   **API Contract Normalization (L1 Enforcement)**:
    *   **Status**: **IMPLEMENTED**.
    *   **Detail**: Centralized `schema_validator.py` now enforces the `UnifiedEventObject` contract on all core `/v1/` routes.

### 🚧 In Progress / Pending

*   **Step Functions ASL Production Wiring**:
    *   **Status**: The `workflow_stack.py` uses "Pass" states and mock tasks for Aadhaar/Bank verification steps.
    *   **Need**: Replacing placeholders with live Lambda tasks that perform real external validation.
*   **Kendra RAG Integration**:
    *   **Status**: `RagService` is structured, but AWS Kendra indexing is currently documented as a manual setup guide.
    *   **Need**: Finalizing the connection between the backend and a live Kendra index for scheme retrieval.
*   **Multi-channel Adapters**:
    *   **Status**: IVR (Amazon Connect) is the primary focus; WhatsApp and Mobile adapters are documented as future horizons.
    *   **Need**: Implementation of the specific L1 integration handlers for non-IVR channels.
*   **DynamoDB Scale Performance**:
    *   **Status**: Simple HASH/RANGE keys are used.
    *   **Need**: Implementation of TTL (Time-To-Live) for inactive sessions and GSIs for complex admin analytics.
*   **Rate Limiting & WAF**:
    *   **Status**: API Gateway is configured, but specific throttling rules and AWS WAF protection are not yet deployed.
    *   **Need**: Defining `UsagePlan` and `Throttling` quotas to prevent abuse.

---

## 🗺️ Roadmap

| Phase                 | Features                                                       |
| --------------------- | -------------------------------------------------------------- |
| **Phase 1 (Current)** | Voice IVR, PM-Kisan, PM Awas, E-Shram, Grievance, Web Emulator |
| **Phase 2**           | DigiLocker integration, CSC submission packet, 8 more states   |
| **Phase 3**           | State e-District API integration, multi-district RAG index     |
| **Phase 4**           | National civic interoperability layer, UIDAI linkage           |

---

## 🤝 Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Make changes and commit: `git commit -m 'feat: add your feature'`
4. Push and open a Pull Request against the `vishal` branch

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👥 Team

Built for the **AI for Bharat** initiative.

> _"JanSathi is not an AI chatbot. It is India's first telecom-native civic readiness infrastructure."_

---

<div align="center">
  <strong>🇮🇳 Har Ghar, Har Haq — Every Home, Every Right</strong>
</div>
