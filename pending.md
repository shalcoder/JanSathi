Nice — hybrid it is. Smart choice: deterministic structure for data collection + LLM for intent, summarization and soft follow-ups. Below is a **tactical, prioritized action plan** you can execute now. It’s written as a checklist with owners, exact commands/snippets where useful, and the minimal artifacts you should produce next (contact flow, Step Functions ASL, Lambda handlers, frontend hooks, and demo script). Follow this sequence; each step is small and testable.

---

## Top-level goal (one line)

Build a **Hybrid IVR**: quick intent + language detection with LLM, short guided slot-filling voice flow (DTMF fallback), deterministic rule checks, async submission, SMS summary, and dashboard update — all stable for a 2-minute demo.

---

# IMMEDIATE PRIORITY (deploy & test a working loop today)

### 1. Provision Telephony & Basic AWS infra (AWS Team) — **must do first**

- **Create Amazon Connect instance** (Console) and claim a dev number.
- **Create DynamoDB table** `jansathi-sessions` (partition key `session_id`).
  CLI:

  ```bash
  aws dynamodb create-table \
   --table-name jansathi-sessions \
   --attribute-definitions AttributeName=session_id,AttributeType=S \
   --key-schema AttributeName=session_id,KeyType=HASH \
   --billing-mode PAY_PER_REQUEST \
   --region ap-south-1
  ```

- **Create IAM role** for Lambda with DynamoDB, S3, CloudWatch, SecretsManager permissions.

---

### 2. Connect Contact Flow (IVR) — design & test

**Design** these deterministic contact-flow blocks inside Amazon Connect:

1. Welcome + Language Selection (DTMF 1/2) → store `language` attribute
2. Prompt: “Briefly say your request” → record audio → store audio key
3. Pass audio to Lambda (Invoke) for ASR + Supervisor routing
4. Play short response from Lambda: either immediate answer (info) or “I will collect few details” and enter guided collection loop
5. Final confirmation message + “You will receive SMS” → hang up

**Quick Twilio alternative (if short on AWS Connect time):** use Twilio for dev calls and same Lambda webhooks.

---

### 3. Lambda: `/connect-webhook` (Supervisor entry) — implement now (Backend)

Lambda receives Connect invocation with attributes: `contactId`, `language`, `recordingS3Key` (or audio blob).

**Lambda responsibility:**

- Call ASR (Transcribe) on audio or use direct text if provided.
- Call Bedrock Haiku for **intent + language confidence**:
  - Prompt: `Classify this user utterance into: [intent: apply|info|grievance|track|other], required_slots, language_detected, confidence`

- If `intent == apply` → start Step Function (Apply workflow) and return immediate voice response: “We will collect X pieces of info now.”
- If `intent == info` → run RAG + Bedrock to synthesize short answer and return TTS audio link.
- Return Connect response to play.

**Example pseudo-call:**

```python
# lambda_handler snippet
transcript = transcribe_audio(s3_key)
intent_res = call_bedrock_haiku(f"classify: {transcript}")
if intent_res.intent == 'apply':
    execution = start_step_function(state_machine_arn, input={...})
    return {"playPrompt":"We will collect a few details to complete your application."}
else:
    answer = rag_answer(transcript)
    audio_url = synthesize_polly(answer, lang)
    return {"playPrompt":"<audio src='{}'/>".format(audio_url)}
```

---

### 4. Step Functions: “Apply” state machine (ASL) — minimal ASL you must create

Key states:

- `CollectSlots` (Lambda) — ask 3–5 voice questions (bank acc, Aadhaar last4, land size, consent). Use short prompts.
- `ValidateSlots` (Lambda Rules Engine) — deterministic checks (types, ranges).
- `EligibilityCheck` (Lambda) — run Rules Engine (no LLM) using collected slots.
- `Verifier` (Lambda + Bedrock Guardrails) — final check; if confidence < 0.8 → `HITL` state (send to admin queue & respond “under human review”).
- `Submit` (Lambda) — call gov API stub OR enqueue to submission queue.
- `Notify` (SNS) — send SMS with case ID & Benefit Receipt link.
- `ReturnToIVR` (Task) — send final short status to Connect (via callback).

**Minimal ASL example skeleton (trimmed):**

```json
{
  "StartAt": "CollectSlots",
  "States": {
    "CollectSlots": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:collectSlots",
      "Next": "ValidateSlots"
    },
    "ValidateSlots": {
      "Type": "Task",
      "Resource": "...:validateSlots",
      "Next": "EligibilityCheck"
    },
    "EligibilityCheck": {
      "Type": "Task",
      "Resource": "...:eligibility",
      "Next": "Verifier"
    },
    "Verifier": {
      "Type": "Choice",
      "Choices": [
        { "Variable": "$.confidence", "NumericLessThan": 0.8, "Next": "HITL" }
      ],
      "Default": "Submit"
    },
    "HITL": {
      "Type": "Task",
      "Resource": "...:enqueueHitl",
      "Next": "NotifyUserUnderReview"
    },
    "Submit": { "Type": "Task", "Resource": "...:submit", "Next": "Notify" },
    "Notify": { "Type": "Task", "Resource": "...:notify", "End": true }
  }
}
```

---

### 5. Voice prompts & DTMF design (UX Team)

Keep each IVR prompt short (≤ 6 words ideally). Provide explicit DTMF fallback at each step. Example slot loop:

- Q1: “Please say your bank account number or press 1 to enter digits.”
- Q2: “Please say the last four digits of Aadhaar.” (If low ASR confidence → “Please press digits now.”)
- Confirmation: “You said X, Y. Press 1 to confirm, 2 to repeat.”

---

### 6. Rules Engine (Lambda) — deterministic logic (Backend)

- Implement validation functions and eligibility rules in Python modules already present.
- Keep rules in JSON or YAML config files for quick edits.
- Example rule check:

```python
def pm_kisan_eligible(profile):
    return profile['land_hectares'] < 2 and profile['income_annual'] < 200000
```

- Return structured reasons for Benefit Receipt.

---

### 7. Verifier & HITL queue (Admin) — minimal admin UI (Frontend)

- When Step Functions sends HITL, write HITL ticket to DynamoDB and SQS.
- Admin UI shows queue with playback of audio, transcript, extracted slots, Benefit Receipt.
- Admin can Approve → resumes Step Function via API.

---

### 8. Notifications (SNS/Pinpoint) — implement SMS summary

- After `Submit` or `HITL enqueued`, call SNS to send SMS:

```
"JanSathi: Your PM-Kisan submission is submitted. Case ID: X. BenefitReceipt: <short URL>"
```

- Generate short S3-hosted receipt (HTML or PDF) and shortlink.

---

### 9. Connect ↔ Lambda callback for final IVR reply (integration)

- Use Connect’s **Invoke Lambda** block or **Contact Flow** “Invoke AWS Lambda function” to call your Lambda which returns text-to-speech string to play.
- Include flow to play the final status after Step Function reaches `Notify` (you can use Connect API to send a callback or use an outbound call to the user).

**Pattern**:

- During call, start Step Function, return to IVR “processing” prompt, then when Step Function completes send an **outbound call** to the user or push SMS. For hackathon, SMS is sufficient; then play final short message: “Request accepted — SMS will arrive.”

---

## FRONTEND work (what you must do next)

### A. IVR Session Dashboard

- Add an **Active Calls** widget listing `session_id`, caller (masked), language, state, last transcript, case_id.
- Implement a “Play last audio” button (fetch S3 audio URL).
- Add a “Resume human review” button that triggers API to Step Functions.

### B. HITL Admin UI

- List HITL tickets with filters; on open show transcript, extracted fields, Benefit Receipt, audio playback, Approve/Reject buttons.

### C. Benefit Receipt viewer & download

- Render the deterministic reason items and source citations.
- Provide “Download Receipt (PDF)” using server-side HTML→PDF (Lambda) stored in S3.

### D. Telemetry & demo flags

- Show `channel` = IVR on each chat turn, show `ASR_confidence`, `LLM_confidence`, `rules_result`.
- Add a `Demo Mode` toggle on dashboard to use cached responses if backend times out.

---

## TESTING & FALLBACKS (must be scripted)

1. **Test 1 — Intent & Short Answer:** Call the number, ask an info question. Expect quick RAG answer < 4s. If bedrock slow, return cached answer.
2. **Test 2 — Apply happy path:** Call, choose Hindi, intent=apply, collect slots, eligibility PASS, submit, SMS with CaseID, IVR says “submitted”.
3. **Test 3 — Low confidence path:** Make ASR or slot invalid; get HITL ticket, IVR says “under review”, SMS with ticket ID.
4. **Test 4 — Gov API down:** Step Function queues submission and notifies user of retry with SMS.
5. **Test 5 — DTMF fallback:** Force low ASR and enter via keypad.

Prepare cached audio and cached response JSON for fallbacks.

---

## DEMO SCRIPT (2 minutes) — use this on stage

1. **Hook (10s):** “This is Ramesh, a farmer with no internet. Watch.” (Call number)
2. **Live Call (50s):**
   - IVR: Welcome & Hindi selection (user presses 1)
   - User: “I want to apply for PM-Kisan”
   - System: “We will collect a few details” → collects bank last 4, land size etc (short)
   - System: “Your application is submitted. You will get an SMS with Case ID.”

3. **SMS arrives (10s)** — show SMS on phone and click link to Benefit Receipt on dashboard.
4. **Dashboard (30s):** Show live update: session, case id, telemetry (ASR conf, latency, rules pass). Open Benefit Receipt with rule snippets and citation.
5. **Close (10s):** “This shows inclusive, low-bandwidth, agentic execution — voice in, case out.”

**Practice runs:** rehearse 6x to ensure timings and fallback.

---
