# JanSathi (जनसाथी)

## Agentic Telecom-Native Civic Automation System

![Status](https://img.shields.io/badge/Status-10--Layer_Automation-brightgreen)
![Architecture](https://img.shields.io/badge/Architecture-Hybrid_Intelligence-blue)
![Deployment](https://img.shields.io/badge/Deployment-AWS_Cloud_Ready-success)

---

# 💡 The Vision

JanSathi is not just an AI agent. It is a **Telecom-Native Civic Operating System** designed to bridge the gap between complex government schemes and the millions who need them most.

By combining the natural interface of a Voice Call with a deeply integrated, 10-layered automation pipeline, JanSathi reduces cognitive load, increases civic readiness, and prevents exploitation for communities across India.

---

# 🧱 JAN SATHI – 10-LAYER AGENTIC AUTOMATION ARCHITECTURE

We design JanSathi as a true Agentic Civic Automation System. Moving beyond stateless LLM calls, this architecture relies on triggers, hybrid intelligence, deterministic validation, orchestration, and continuous feedback.

## LAYER 0 — TELECOM TRIGGER (Entry Point)

**Input:** Voice / DTMF / Text  
**Output:** Structured request event  
The workflow trigger layer. Users can access the system via:

- **IVR Call** (Amazon Connect) - Toll-free, feature-phone compatible
- **WhatsApp** (Business API)
- **Web Dashboard** (Next.js)
- **Admin Escalation** (Internal triggers)

## LAYER 1 — INTEGRATION LAYER

Normalizes all incoming requests to make the system transport-agnostic.  
**Components:** API Gateway, Lambda adapters, Connect webhook, WhatsApp webhook, Web frontend API.

```json
// Unified Event Object
{
  "session_id": "uuid",
  "channel": "ivr|whatsapp|web",
  "language": "hi|en|ta|kn",
  "message": "user input",
  "timestamp": "iso-8601"
}
```

## LAYER 2 — DATA INGESTION

Cleans and structures the raw input before intelligence is applied.
**Components:** Amazon Transcribe (ASR), Language normalization, Intent preprocessing, Noise filtering, PII detection, DTMF parsing.

```json
// Structured Input
{
  "intent_candidate": "APPLY_PM_KISAN",
  "slots_detected": {"land_size": "2 acres"},
  "confidence": 0.94,
  "user_context": {...}
}
```

## LAYER 3 — INTELLIGENCE STACK (Hybrid Brain)

This split intelligence model ensures enterprise-safe AI: LLM assists, Rules decide.

- **A) Rule-Based Brain:** Deterministic Rules Engine, Hard eligibility constraints, Fraud heuristics.
- **B) Learning-Based Brain:** Bedrock Intent Classifier, Summarizer, Response generation.
- **C) Agentic Planner Brain:** Slot planner, Workflow selector, Tool selection logic.

## LAYER 4 — DECISION ENGINE

The convergence layer where intelligence dictates the next flow state. Aggregates LLM confidence, rule results, and risk scores to decide:
`AUTO_PROCEED` | `ESCALATE_TO_HITL` | `REJECT_WITH_REASON` | `REQUEST_MORE_SLOTS`

## LAYER 5 — WORKFLOW ORCHESTRATION

AWS Step Functions converts stateless LLM calls into **stateful civic automation**.
Handles: Slot collection loops, retry logic, timeout handling, HITL pause states, and multi-step scheme flows.

## LAYER 6 — ACTION EXECUTION

Executing the actual civic tasks based on the orchestrated workflow.

- **Current Core Actions:** Generate Benefit Receipt, Generate eligibility explanation, Store session state, Send SMS, Update dashboard.
- **Future-Ready Actions:** DigiLocker fetch, eDistrict integration, CSC appointment booking, Grievance filing API.

## LAYER 7 — NOTIFICATION & OUTREACH

**Voice confirms action. SMS delivers the structured artifact.**

- SNS SMS dispatch (Benefit Receipts)
- WhatsApp summaries
- Real-time dashboard updates
- IVR confirmation voice synthesis via Amazon Polly

## LAYER 8 — SECURITY & GOVERNANCE

A horizontal layer running across all stages.
**Components:** Consent enforcement, KMS encryption, IAM least privilege, JWT validation, PII masking, Audit log chaining, Rate limiting, WAF (Web Application Firewall).

## LAYER 9 — MONITORING & OBSERVABILITY

Enterprise-grade monitoring for reliability and insights.

- CloudWatch structured logs
- Correlation IDs per session
- LLM token usage metrics
- Latency tracking per layer
- HITL queue analytics
- Drop-off analysis (where users hang up)

## LAYER 10 — FEEDBACK & IMPROVEMENT LOOP

A continuous cycle to evolve the system without full RL.
**Feedback Sources:** User hang-up patterns, HITL corrections, Eligibility overrides, SMS delivery failures, Misclassified intents.
**Updates Applied To:** Rules engine constraints, Prompt refinements, Slot schema improvements, Confidence threshold tuning.

---

# ⚡ SYSTEM EFFICIENCY & OPTIMIZATION

Speed wins in voice applications. JanSathi is optimized for minimal latency:

1. **Caching:** Kendra retrieval results cached for popular schemes.
2. **Model Routing:** Utilizing Haiku for 85% of turns (speed), and Sonnet only for deep summarization.
3. **In-Memory Schemas:** Pre-loading scheme schemas to avoid S3 reads on every call.
4. **Focused Loops:** Keeping IVR slot collection short (≤ 3 slots per loop).
5. **Fail Fast:** Triggering rule rejection early if hard constraints aren't met.
6. **Pre-Generated Templates:** Using static explanation templates for common resolutions.
7. **Session Expiry:** DynamoDB TTL for efficient session lifecycle management.

---

# 🎯 Hackathon Alignment: Impact & Inclusion

JanSathi was built ground-up to directly address the core challenges of civic inclusion, meeting every criterion of the hackathon prompt:

| #   | Criterion                                                                   | How JanSathi Addresses It                                                                                                                                                               |
| --- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Local-language, voice-first, or low-bandwidth AI**                        | 100% voice-first with zero-bandwidth for users. Any basic 2G feature phone works via toll-free call. Multi-language via Amazon Transcribe + Polly.                                      |
| 2   | **Civic information or public service assistants**                          | The 10-layer pipeline is a resilient public service assistant. Kendra-powered RAG Agent delivers hallucination-free civic information; Rules engine pre-processes real applications.    |
| 3   | **AI systems that help communities access markets, resources, or programs** | Creates a tangible "Benefit Receipt" via SMS — the user can take it to a Local CSC for real government benefits. Market Connect API endpoints are also prepared.                        |
| 4   | **Education, awareness, or skill-development tools**                        | JanSathi educates citizens about their rights by letting them ask "What schemes am I eligible for?" and receiving a spoken, localized answer — bridging literacy and language barriers. |
| 5   | **Focus: Inclusion, accessibility, real-world impact**                      | We skip the app store entirely, reaching the ~500M Indians outside the smartphone ecosystem. Deterministic safety rules ensure government-grade trustworthiness.                        |

---

# 🛠️ Tech Stack & Technology Profile

| Layer                    | Technology                                                |
| ------------------------ | --------------------------------------------------------- |
| **Backend / APIs**       | Python 3.11, Flask, AWS Lambda (Serverless), API Gateway  |
| **Frontend / Dashboard** | Next.js 16, React 19, TailwindCSS, Clerk (Auth)           |
| **Orchestration**        | AWS Step Functions, LangChain Supervisor Pipelines        |
| **Data & State**         | Amazon DynamoDB (NoSQL), Amazon S3                        |
| **Telecom & Voice**      | Amazon Connect, AWS Transcribe, AWS Polly                 |
| **Intelligence**         | Amazon Bedrock (Claude Haiku/Sonnet), Amazon Kendra (RAG) |
| **Communication**        | Amazon SNS & Pinpoint (SMS), Twilio Action Hooks          |

---

# 🚀 Local Development

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
# Runs on http://localhost:5000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```
