# JanSathi Design Document

## 1. System Vision

JanSathi is a telecom-native, voice-first civic readiness infrastructure designed to bridge the digital divide for rural Indian communities. It provides simplified access to government schemes and public services through an intelligent, deterministic 9-agent pipeline.

## 2. Architecture Overview

### 2.1 Multi-Channel Entry

- **Voice (IVR)**: Amazon Connect handles incoming calls, capturing user intent via speech (Transcribe) or DTMF.
- **Web/PWA**: A modern React frontend using a unified `/v1` API layer.
- **SMS**: Primary outbound channel for receipts, confirmations, and checklists.

### 2.2 The 9-Agent Pipeline (Linear & Deterministic)

The system operates as a sequential orchestration of specialized agents:

1.  **Telecom Entry Agent**: Handles session initialization, consent, and ASR.
2.  **Intent Agent**: Classifies user requests (Apply, Info, Status) using Bedrock Haiku.
3.  **Scheme Retrieval Agent**: RAG-based search (Kendra) for scheme details.
4.  **Slot Collection Agent**: Managed state machine for gathering required eligibility data.
5.  **Deterministic Rules Agent**: Hard-coded logic that validates slots against official criteria.
6.  **Verifier Agent**: Risk-scoring engine that decides between Auto-Submit, HITL, or Rejection.
7.  **Workflow Orchestrator**: Manages state transitions via Step Functions or local logic.
8.  **Notification Agent**: Emits SMS/receipts to close the loop with the citizen.
9.  **HITL Agent**: Administrative dashboard for human review of edge cases.

## 3. API Layer (Unified v1)

The backend exposes a consolidated API under `/v1` and `/agent`:

- `/v1/query`: Unified text/audio processing.
- `/v1/orchestrate`: Universal entry point for the 9-agent supervisor.
- `/v1/ivr/*`: In-call state management (consent, turn-by-turn).
- `/v1/admin/*`: HITL and monitoring tools.

## 4. Data & Compliance

- **Immutable Audit**: Every turn, consent, and eligibility decision is logged with SHA-256 chaining.
- **Telemetry**: 14 distinct KPIs emitted to CloudWatch for real-time impact monitoring.
- **Storage**: Hybrid support for Local JSON (dev) and DynamoDB (production).

## 5. Security

- **Consent Gate**: No PII is collected before explicit user consent.
- **PII Scrubbing**: Logs are filtered to remove sensitive data before emission.
- **Role-Based Access**: Admin endpoints restricted to authorized controllers.
