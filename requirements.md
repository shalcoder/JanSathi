# JanSathi System Requirements

## 1. Functional Requirements

### 1.1 Voice Interaction

- Support for Hindi and multiple local dialects via Amazon Transcribe.
- DTMF fallback for low-confidence ASR or noisy environments.
- Consent-first data collection flow.

### 1.2 Scheme Intelligence

- Real-time eligibility checking for 50+ government schemes (expandable via YAML).
- Citation-backed (RAG) information retrieval to prevent hallucinations.
- Generation of unique Benefit Receipts with eligibility traces and document checklists.

### 1.3 Multi-Channel Support

- Unified session state across IVR, Web, and SMS.
- SMS-based delivery of scheme information and submission numbers.

### 1.4 Administrative & Governance

- Human-in-the-Loop (HITL) queue for cases with risk scores > 0.15.
- Immutable audit trail for DPDP (Digital Personal Data Protection) compliance.
- Real-time telemetry dashboard showing system latency, ASR success, and impact metrics.

## 2. Non-Functional Requirements

### 2.1 Performance

- End-to-end IVR response latency < 3 seconds.
- Support for concurrent call handling via serverless (AWS Lambda) scaling.

### 2.2 Reliability

- Local fallback mode for all critical AWS services (Bedrock, S3, SNS).
- Deterministic rules engine to ensure 100% accurate eligibility results.

### 2.3 Security & Privacy

- Zero-PII storage in standard application logs.
- KMS-encrypted audit logs and data at rest.
- Granular consent tracking per session.

## 3. Technical Constraints

- **Backend**: Python 3.9+ (Flask).
- **Frontend**: Vite + React + TypeScript.
- **Primary Cloud**: AWS (Connect, Bedrock, Kendra, Lambda, DynamoDB).
- **Local Dev**: SQLite + Local JSON Storage + Python console logging.
