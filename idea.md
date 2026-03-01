# JanSathi — Complete user flow **(call-to-close)** + Architectural system design

Below is a single, end-to-end walkthrough (user perspective) **and** the technical architecture that runs it (IVR → AWS → backend agents → frontend). I’ll show **each step**, which **agent / service** handles it, what data moves, what decisions are made, and what fallback/monitoring happens. Use this as your demo runbook and engineering spec.

---

## Quick summary (one line)

A user calls a toll-free JanSathi IVR → Connect records language & consent → Short ASR → Supervisor classifies intent → Slot collection workflow (DTMF fallback) → Deterministic rules verify eligibility → System either queues HITL or submits a case/stores readiness → Notification agent sends SMS with BenefitReceipt → IVR plays final message and call ends. Dashboard updates in real time.

---

# User experience flow (what the person sees/hears)

1. **Call**: The user dials the JanSathi toll-free number.
2. **Welcome & Consent**: “Namaste. This call may collect personal information for benefits assistance. Press 1 to consent.” (DTMF)
3. **Language selection**: “Press 1 for Hindi, 2 for English, 3 for Tamil.”
4. **Short natural query**: “Please tell me how I can apply for PM-Kisan.” (Short spoken sentence)
5. **IVR confirmation**: “Okay — I will ask 3 quick questions to check eligibility.”
6. **Slot collection**: Prompts for land size, income; user answers by voice or presses digits.
7. **Realtime validation**: System says “You appear eligible” or “You are not eligible because…”
8. **Summary & SMS**: IVR: “We will send an SMS with a checklist and next steps.” User hears it. SMS arrives with BenefitReceipt link.
9. **Call end**: IVR says “Dhanyavaad — you will receive SMS. Goodbye.” Call disconnects.
10. **Dashboard**: Admin/judges see session, telemetry, BenefitReceipt, and case ID; if HITL needed, reviewer takes action.

---

# Architectural components (high level)

- **IVR / Telecom**: Amazon Connect (contact flow), Amazon Polly (TTS), Amazon Transcribe (ASR) — Connect invokes Lambda webhooks.
- **Orchestration & Agents** (backend Lambdas + Step Functions):
  - Telecom Entry Agent (connect_webhook.py)
  - Intent Classification Agent (intent_service.py)
  - Slot Collection Agent (ivr_service.py + workflow_engine.py)
  - Deterministic Rules Agent (RulesEngine in workflow_engine.py)
  - Verifier & HITL Agent (hitl_service.py)
  - Submission/Gov-Adapter (submission stubs)
  - Notification Agent (notify_service.py; SNS/Pinpoint/Twilio fallback)
  - RAG Knowledge Agent (Kendra + Bedrock for info queries)

- **LLM**: Amazon Bedrock (Haiku for intent, Sonnet for complex summarization) — used sparingly; rules are primary.
- **Storage**: DynamoDB (sessions, HITL queue, cases), S3 (audio, receipts, uploaded docs), Secrets Manager/KMS (keys), optionally RDS for audit if needed.
- **Frontend**: Next.js 15 (Dashboard, HITL admin, IVR Monitor, Chat UI, DocumentsPage). Uses Clerk for auth.
- **Monitoring / Observability**: CloudWatch logs & metrics, X-Ray traces, QuickSight/CloudWatch dashboards for KPIs.
- **State Machines**: AWS Step Functions for multi-turn apply workflows, retries, and human callbacks.
- **Security & Compliance**: JWT auth, consent logging, PII tokenization, KMS encryption, audit logs in S3.

---

# Detailed step-by-step sequence (technical)

> For each step: what happens, which agent/service acts, what data is exchanged, and where it’s stored.

---

### 0. Precondition: Routing and provisioning

- AWS: Amazon Connect instance configured with contact flow that invokes your Lambda (Telecom Entry Agent) via an **Invoke AWS Lambda** block.
- DNS/Phone: toll-free number assigned.
- Environment: `DEMO_MODE=false` by default; fallback cached responses available.

---

### 1. Call lands in Amazon Connect (Telecom Entry Agent)

**What Connect does**

- Plays greeting (Polly), collects DTMF for consent & language, records audio (short utterance or full conversation based on flow).
- Saves audio to S3 (`audio-bucket/calls/{session}/{turn}.webm`) when recording invoked.
- Sets Contact Attributes: `{session_id, caller_number_masked, language, consent}`.

**Connect -> Lambda payload**
Connect will call your Lambda `connect_webhook` with attributes:

```json
{
  "contactId": "abc123",
  "caller": "+91XXXXXXXXXX",
  "language": "hi",
  "consent": true,
  "audioS3Key": "audio-bucket/calls/abc123/turn1.webm"
}
```

**Agent**: Telecom Entry Agent writes session to DynamoDB (`sessions` table) with `session_id`, `channel=ivr`, `caller_hash`, `consent`, `language`.

---

### 2. ASR & Pre-processing (Language & ASR Agent)

**Lambda** downloads audio from S3 and calls Amazon Transcribe (or a local Whisper fallback) to obtain `transcript` and `asr_confidence`.
Normalized numbers (digits) extraction is performed and returned.

**Output example**

```json
{
  "transcript": "मैं पीएम-किसान के लिये आवेदन करना चाहता हूँ",
  "asr_confidence": 0.88,
  "normalized": { "digits": ["1234"] }
}
```

Stored: add to DynamoDB `sessions.turns` list and write raw audio S3 pointer to audit log.

---

### 3. Intent classification (Intent Agent)

**Lambda** calls Bedrock Haiku with a small classification prompt, including persona info (if any), plus rule-based fallback checker (keywords for PM-KISAN, PDS, grievance).
**Output**: `{ intent: "APPLY_SCHEME", scheme_hint:"PM-KISAN", confidence: 0.92 }`.

If confidence < threshold (e.g., 0.6) → return `intent=clarify` and respond to user: “माफ़ कीजिए, क्या आप पीएम-किसान के लिये आवेदन करना चाहते हैं? तसे Press 1 या बोलें।”

Data: store intent in session.

---

### 4. Short information vs. apply routing (Supervisor decision)

- If intent = `INFORMATION`, call **RAG Agent** (Kendra+Bedrock) to fetch grounded answer and respond with synthesized TTS audio (Polly). End call or ask follow-up.
- If intent = `APPLY_SCHEME`, **start the Step Functions workflow** for that scheme (`StartApplyWorkflow(session_id, scheme)`).

**Start Step Function** input (example):

```json
{
  "session_id":"abc123",
  "caller":"+91XXXXXXXX",
  "language":"hi",
  "scheme":"PM-KISAN",
  "turns":[{...}]
}
```

Step Functions returns `executionArn`.

Respond to Connect: “मैं कुछ जानकारी पूछूंगा। कृपया बने रहें।” (play via Polly). The call remains active while Step Functions controls the flow through Lambda tasks.

---

### 5. Slot collection (Slot Collection Agent via Step Functions + Lambda)

**State:** `CollectSlots` -> Lambda (`ivr_service`) prompts user for each slot defined in `schemes_config.yaml`. Example slots: `land_hectares`, `income_annual`, `bank_last4`.

**Loop**

- For each slot:
  - Connect plays prompt (via Lambda returning TTS text)
  - User replies; audio stored; ASR handles transcript
  - Lambda validates format (numeric length, ranges)
  - If ASR confidence < 0.6 → ask user to press digits (DTMF) or repeat
  - On success, write slot to DynamoDB session record

**Sample slot JSON**

```json
{
  "slot": "land_hectares",
  "value": 1.2,
  "method": "speech",
  "confidence": 0.9
}
```

---

### 6. Deterministic eligibility check (Rules Agent)

Once all required slots are collected, Step Functions invokes `rules-eval` Lambda (Deterministic Rules Agent).
Rules engine evaluates the `schemes_config.yaml` rules for PM-Kisan, returns:

```json
{
  "eligible": true,
  "reasons": ["land_hectares < 2", "income_annual < 200000"],
  "evidence": [{ "doc": "pmkisan.pdf", "page": 12 }]
}
```

Store result on session (`sessions` table).

---

### 7. Verifier & Risk assessment (Verifier Agent)

Compose signals:

- ASR average confidence
- Rules result
- LLM summarization confidence (if used)
- Fraud heuristics (caller blacklists, suspicious pattern)

Compute `risk_score`.

- If `risk_score >= 0.85` → proceed to `Submit` state.
- If `0.6 <= risk_score < 0.85` → create HITL ticket (write to `hitl` table, SQS) and pause Step Function waiting for human approval callback. Respond to user: “आपका आवेदन समीक्षा के लिए भेजा गया है; आपको SMS मिलेगा।”
- If `risk_score < 0.6` → respond: “आप फिलहाल पात्र नहीं हैं” + SMS with reasons.

When paused for HITL, admin sees the ticket in the Dashboard with audio playback, transcript and extracted slots, and an approve/reject button.

---

### 8. Submission / Assisted packet creation (Submission Agent)

Two realistic pathways:

**A. Assisted model (default / recommended)**

- Create prefilled PDF or JSON packet and store S3 under `submissions/session_id/packet.pdf`.
- Notify nearest CSC operator (email or system) or provide a printed ticket with barcode.
- Generate `case_id` as `JS-2026-0001` and store.

**B. Official API (only if onboarded)**

- If connector for the portal exists, format request and call government API. Store response.

Whatever route used, Step Functions records submission outcome: `{case_id, status:"submitted"}` or `{queued:true}`.

---

### 9. Notification (Notification Agent)

Immediately send SMS (via SNS/Pinpoint or Twilio) to caller with short, localized message and a presigned link to BenefitReceipt PDF. Example SMS (Hindi):

> `JanSathi: आपका PM-Kisan आवेदन तैयार है. Case ID JS-2026-0001. आवश्यक दस्तावेज: Aadhaar, भूमि रिकॉर्ड, बैंक पासबुक. रिपोर्ट: https://s3.../receipt.pdf`

Also push a dashboard notification and update the session state.

If SMS fails, fallback: send WhatsApp if available, or email (if user provided).

---

### 10. IVR final response & call end (Telecom Entry Agent)

Lambda responds to Connect with a short TTS message depending on flow result:

- Auto-submitted: “आपका आवेदन सफलतापूर्वक दर्ज हो गया है। आपको एसएमएस मिल गया है। धन्यवाद।”
- HITL: “आपका आवेदन समीक्षा के लिए भेजा गया है; आपको एसएमएस में सूचित किया जायेगा।”
- Not eligible: “आप फिलहाल पात्र नहीं हैं; SMS में कारण भेजा गया है।”

Connect plays the TTS, then ends the call.

---

### 11. Post-call housekeeping

- Audit: write signed audit record to S3 (session + hash chain).
- Telemetry: emit CloudWatch metric events: `CallProcessed`, `EligibilityRate`, `AvgTurns`, `HitlCreated`.
- Dashboard: Next.js polls or uses WebSocket to show session updates in real time.

---

# Data models / example payloads

**Start Step Function**

```json
POST /v1/workflow/start
{
  "session_id":"abc123",
  "scheme":"PM-KISAN",
  "caller_hash":"sha256(...)",
  "language":"hi"
}
```

**Slot fill turn**

```json
POST /v1/ivr/turn
{
  "session_id":"abc123",
  "turn_id":"turn1",
  "slot":"income_annual",
  "value":120000,
  "method":"speech",
  "confidence":0.82
}
```

**Rules eval response**

```json
{
  "eligible": true,
  "reasons": ["income < 200000", "land < 2ha"],
  "trace": [{ "rule": "r1", "passed": true }]
}
```

**Notify SMS**

```json
{
  "to": "+91XXXXXXXX",
  "message": "Your JanSathi PM-Kisan readiness: Eligible. CaseID: JS-2026-0001. Receipt: https://..."
}
```

---

# Fallbacks, failure modes & policies (must have)

- **ASR low confidence:** after 2 attempts switch to DTMF numeric entry. If still failing, create HITL case and inform user.
- **Bedrock timeout / throttling:** `DEMO_MODE` cached response; notify admin about degraded LLM availability.
- **Gov API down:** queue submission, send SMS: “Submission queued; we will retry.” Provide case ID for tracking.
- **SMS failure:** try WhatsApp or email; mark undelivered in session.
- **Privacy breach attempt:** detect pattern, auto-pauses flow and raises security alert.

---

# Observability & KPIs (what judges will ask)

- **Operational metrics**: calls/hour, avg call length, ASR success %, Bedrock latency, Step Function errors, HITL queue length.
- **Impact metrics**: % callers eligible, % who become “ready” (completeness), estimated travel trips saved (modeled).
- **Safety metrics**: % HITL escalations, audit log integrity, PII storage compliance.

---

# Frontend integration points (what the UI shows & calls)

- **IVR Monitor** (`IVRMonitor.tsx`) polls `/v1/ivr/sessions/active` for active calls; shows channel, caller masked, last transcript, session state.
- **Chat Interface** (`ChatInterface.tsx`) posts to `/v1/query` for web users, shows BenefitReceipt and audio playback.
- **ApplicationsPage** uses `/v1/applications?session_id=` to list case statuses.
- **Admin HITL page** calls `/v1/admin/cases` and `POST /v1/admin/cases/{id}/approve` to resume Step Functions.
- **DocumentsPage** requests `/v1/upload-presign` to get S3 presigned URL and then calls vision analysis endpoint `/v1/vision/parse`.

---

# Security & compliance checklist (must ship)

- Capture user consent before collecting PII; store consent token in session.
- Tokenize/AES/KMS-encrypt any PII; store masked values (last-4 digits) in UI only.
- Use Secrets Manager for API keys; use IAM roles for all Lambda → service access.
- Immutable audit logs (S3) with digest chain for DPDP compliance.
- Rate limiting (API Gateway), WAF for public endpoints.

---

# Demo readiness checklist (copy & run before show)

- [ ] Amazon Connect contact flow validated with test number
- [ ] `connect_webhook` Lambda deployed and has IAM role to S3/Transcribe/StepFunctions
- [ ] Step Functions ASL deployed and tested for PM-Kisan happy path
- [ ] DynamoDB table `sessions` operational and has correct indexes & TTL
- [ ] `DEMO_MODE` pre-seeded with cached responses for fallback
- [ ] SNS / Twilio tested for SMS delivery and templates localized
- [ ] Admin dashboard and HITL playback tested (approve/resume path)
- [ ] Prewarm script executed to reduce cold start latency
- [ ] Backup demo video recorded in case phones go rogue

---

# Implementation recommendations & thresholds

- ASR confidence threshold: `0.6` (>=: accept; < : DTMF fallback)
- Verifier risk thresholds: `>=0.85` auto-submit; `0.6-0.85` HITL; `<0.6` auto-notify not eligible
- Bedrock timeouts: `3s` for intent classification (Haiku); if exceeded, fallback to rule keywords
- Step Functions wait for HITL approval: configurable `MAX_HITL_WAIT=48h` with user SMS updates

---

## Final note — one clean diagram (textual)

```
User Phone -> Amazon Connect (Telecom Entry)
    -> Lambda connect_webhook (ASR -> store audio S3)
    -> Intent Agent (Bedrock) -> StepFunctions.start
        StepFunction:
          CollectSlots (Lambda ivr_service -> Transcribe)
          ValidateSlots (Lambda RulesEngine)
          Eligibility (RulesAgent)
          Verifier (VerifierAgent -> HITL? -> Submission)
          Submit (SubmissionAgent -> S3/Portal)
          Notify (NotifyAgent -> SNS/Twilio)
    -> Amazon Connect plays final TTS -> Call ends
Frontend Dashboard <-> DynamoDB & S3 (Realtime updates/WebSocket)
Admin HITL UI -> hitl_service -> StepFunctions callback
Monitoring: CloudWatch, X-Ray, QuickSight
```

---
