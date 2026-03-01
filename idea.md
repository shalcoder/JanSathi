# 🟢 JanSathi — Canonical Product Definition

## 1️⃣ Product Identity

**JanSathi is a telecom-native civic readiness infrastructure for India.**

It operates over voice networks (IVR), not just the internet.

It does not replace government portals.

It prepares citizens before they reach them.

Its purpose is to reduce:

* Cognitive load
* Information asymmetry
* Rejection due to incomplete documentation
* Dependence on middlemen

---

## 2️⃣ Core Problem Being Solved

In rural India:

* Citizens do not know which schemes apply to them.
* Eligibility criteria are confusing.
* Government portals are complex.
* Many users lack smartphones or stable internet.
* Middlemen charge money for simple information.
* Citizens waste trips to offices due to incomplete documents.

JanSathi solves the **pre-submission gap**.

It automates:

* Intent understanding
* Eligibility screening
* Structured slot collection
* Deterministic rule validation
* Checklist generation
* SMS delivery of readiness summary

It does NOT automate government portals.

---

## 3️⃣ Product Scope (Phase 1 — Current Implementation)

JanSathi is a **Voice-Based Civic Readiness Engine**.

### Channels:

* IVR (Amazon Connect)
* Web Dashboard (Next.js)
* SMS (SNS/Twilio)

### Core Workflow:

1. User calls IVR.
2. Language selected.
3. Intent detected.
4. Slots collected.
5. Eligibility evaluated deterministically.
6. Benefit Receipt generated.
7. SMS summary sent.
8. Case stored in dashboard.
9. Optional HITL escalation.

That is the complete MVP.

---

## 4️⃣ Non-Goals (Very Important)

JanSathi does NOT:

* Bypass CAPTCHA.
* Scrape government portals.
* Auto-submit without authorization.
* Store full Aadhaar numbers.
* Replace official systems.

It is integration-ready but not portal-automation-first.

---

## 5️⃣ System Architecture Overview

### Entry Layer (Telecom Layer)

Amazon Connect → Lambda (connect_webhook)

Handles:

* Consent
* Language
* ASR
* DTMF fallback
* Audio playback

---

### Intelligence Layer (Agent Layer)

9 Specialized Agents:

1. Telecom Entry Agent
2. Intent Classification Agent
3. RAG Knowledge Agent
4. Slot Collection Agent
5. Deterministic Rules Agent
6. Verifier Agent
7. Workflow Orchestrator (Step Functions)
8. Notification Agent
9. HITL Agent

Each agent has single responsibility.

No agent overlaps logic.

---

### Orchestration Layer

AWS Step Functions manages:

* Multi-step slot collection
* Validation
* Eligibility branch
* HITL branch
* Notify branch

---

### Data Layer

DynamoDB:

* sessions
* hitl_cases
* applications

S3:

* audio recordings
* BenefitReceipts
* uploaded documents

---

### LLM Usage Philosophy

LLMs are used for:

* Intent classification
* Information summarization
* Citation generation

LLMs are NOT used for:

* Eligibility logic
* Rule evaluation
* Numeric validation

Deterministic Rules Engine always overrides LLM outputs.

---

## 6️⃣ What Makes JanSathi Unique

1. Telecom-native (works on feature phones)
2. Deterministic eligibility validation
3. Hybrid agent architecture
4. HITL built-in
5. Benefit Receipt with reasoning trace
6. Civic readiness focus instead of portal automation

---

## 7️⃣ Future Integration Roadmap (Not Current Scope)

Phase 2:

* Assisted CSC submission packets
* DigiLocker integration

Phase 3:

* Official API integration (where available)
* State e-District APIs

Phase 4:

* National civic interoperability layer

These are roadmap elements, not MVP requirements.

---

## 8️⃣ Primary Success Metric

JanSathi success is not measured by:

* Number of agents
* Model size
* Complexity

It is measured by:

* Reduction in incomplete applications
* Reduction in wasted office visits
* Increase in scheme awareness
* Increased readiness score
* Improved access for feature phone users

---

## 9️⃣ Complete End-to-End Flow (Single Source of Truth)

User calls →
Consent →
Language →
Intent →
Slot Collection →
Rules Validation →
Eligibility Result →
Benefit Receipt →
SMS →
Dashboard Update →
Call Ends.

No extra branches unless risk/HITL.

---

## 🔟 Product Tone & Positioning

JanSathi is not:

“An AI chatbot.”

It is:

“India’s first telecom-native civic readiness infrastructure.”

---

# 🔵 Instructions for Antigravity

When generating or modifying code:

* Preserve deterministic rule engine authority.
* Never move eligibility logic into LLM.
* Never bypass consent capture.
* Never remove SMS summary generation.
* Maintain separation between agents.
* Keep IVR as primary channel.
* Preserve HITL fallback.
* Never introduce portal scraping.
* Maintain secure PII handling.
* Keep Step Functions as workflow controller.

---

This is the stable definition.

If Antigravity understands this, it will not derail the system.

---

Now I’ll ask you something important:

Do you want me to convert this into:

A) A formal Product Requirement Document (PRD)
B) A System Architecture Spec (SAS)
C) A README.md master blueprint
D) A one-page “AI for Bharat” hackathon submission description

Tell me which format you need.
