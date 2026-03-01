JanSathi (जनसाथी)
Voice-First AI Civic Assistant for India
Production-Hardened Agentic Backend (Phase 2 Complete)






📌 Project Overview

JanSathi is a deterministic, voice-first civic AI assistant designed to help Indian citizens access government schemes, certificates, and services through structured conversational workflows.

The backend is built as a transport-agnostic agentic engine, capable of running via:

Flask (Web deployment)

AWS Lambda (Serverless deployment)

Future IVR / WhatsApp adapters

Any transport layer

🏗️ Current Architecture (Production State)
Flask Adapter
        ↓
Lambda Adapter
        ↓
process_user_input()  ← Unified Execution Layer
        ↓
AgenticWorkflowEngine (Deterministic FSM)
        ↓
SessionManager
        ↓
Storage Abstraction
    ├── LocalJSONStorage
    └── DynamoDBStorage
Key Engineering Principles

✅ Deterministic state machine (no hidden LLM drift)

✅ Storage abstraction (Local ↔ DynamoDB via env)

✅ Fail-fast cloud validation

✅ Transport-layer independence

✅ Serverless compatible

✅ Production-hardened error handling

✅ Clean separation of concerns

✅ What Has Been Completed
Phase 1 — Agentic Core (Completed)

Deterministic finite state workflow

PM-Kisan eligibility flow

Grievance workflow

Restart support

Structured event contract

Session persistence layer

Pluggable storage architecture

Environment-based storage switching

Phase 2 — Cloud Hardening (Completed)
1️⃣ Unified Execution Layer

Created:

backend/app/core/execution.py

Provides:

def process_user_input(message: str, session_id: str) -> dict

This is now the single entry point for all execution.

Both Flask and Lambda use this.

2️⃣ Flask Refactor

Flask routes now act as thin wrappers:

Flask → process_user_input() → Engine

No business logic inside routes.

3️⃣ Lambda Adapter (Serverless Ready)

Created:

backend/lambda_handler.py

Fully independent from Flask

Compatible with Lambda Proxy Integration

Returns proper statusCode + JSON body

No AWS SDK logic inside

Pure transport layer

Handler:

lambda_handler.lambda_handler
4️⃣ DynamoDB Production Hardening

DynamoDBStorage now:

Validates AWS_REGION

Validates DYNAMODB_TABLE

Performs table existence check

Fails fast if credentials missing

Raises explicit RuntimeError for:

Missing credentials

Missing table

Region mismatch

Does NOT silently fallback to local storage

This ensures:

If AWS credentials are correct → system works immediately
If misconfigured → clear failure

5️⃣ Lambda Deployment Hardening

Added:

backend/requirements-lambda.txt
backend/LAMBDA_DEPLOYMENT.md

Minimal dependency bundle

Flask excluded from Lambda

Sterile packaging verified

Cold-start optimized

6️⃣ Full Local Lambda Simulation (Verified)

Simulated:

Clean packaging

Clean import

No Flask loading

Successful invocation

Structured JSON response

System is fully Lambda-ready.

☁️ AWS Deployment (Friend’s Responsibility)

Your role: Implementation
AWS console: Handled separately

Lambda Configuration

Runtime: Python 3.11

Architecture: x86_64

Handler:

lambda_handler.lambda_handler

Memory: 512 MB

Timeout: 15 seconds

Environment Variables Required
STORAGE_TYPE=dynamodb
AWS_REGION=ap-south-1
DYNAMODB_TABLE=your_table_name
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

(Or use IAM role instead of keys.)

Required IAM Permissions
dynamodb:GetItem
dynamodb:PutItem
dynamodb:UpdateItem

Scoped to your DynamoDB table.

🚀 Local Development
Backend
cd backend
pip install -r requirements.txt
python main.py
Lambda Local Simulation
cd backend
python
from lambda_handler import lambda_handler

event = {
    "body": '{"message":"hello","session_id":"test123"}'
}

print(lambda_handler(event, None))
📂 Updated Backend Structure
backend/
│
├── main.py
├── lambda_handler.py
├── requirements.txt
├── requirements-lambda.txt
├── LAMBDA_DEPLOYMENT.md
│
├── app/
│   ├── api/
│   ├── agent/
│   ├── core/
│   │   └── execution.py
│   └── services/
│
├── agentic_engine/
│   ├── workflow_engine.py
│   ├── storage.py
│   ├── session_manager.py
│   └── ...
🔐 Production Safety Guarantees

No hardcoded AWS keys

No silent fallback

Clear error propagation

Explicit cloud validation

Single execution entry

No Flask dependency in Lambda

Deterministic workflow logic

⚠️ What Is Still Pending
🔲 1. API Gateway Normalization Layer

Currently Lambda expects:

{
  "message": "...",
  "session_id": "..."
}

We should later:

Add schema normalization

Add versioned request contracts

🔲 2. Observability (Production Level)

To implement:

Structured JSON logging standard

Request IDs

Correlation tracing

CloudWatch structured logs

🔲 3. DynamoDB Schema Optimization

Currently using simple session storage.

Future improvements:

TTL for inactive sessions

GSI for analytics

Audit trail table

Partition key scaling strategy

🔲 4. API Gateway Rate Limiting

Needs:

Throttling rules

WAF integration

Basic DDoS protection

🔲 5. Real Authentication Integration

Currently:

No production auth enforcement at backend layer

To implement:

JWT validation middleware

Session binding to user identity

Multi-tenant safety

🔲 6. Frontend–Backend Full Integration

Backend agentic core complete.
Full frontend wiring pending.

🎯 System Maturity Level
Layer	Status
Agent Core	✅ Production-Ready
Storage Layer	✅ Hardened
Lambda	✅ Verified
Flask	✅ Refactored
AWS Integration	🔲 Pending Deployment
Observability	🔲 Basic
Auth	🔲 Pending
🔮 Next Technical Milestones

API contract hardening

Observability layer

Auth enforcement

Multi-channel adapter layer

Performance benchmarking

Load testing

Rate limiting

Cloud monitoring integration

🏁 Final Status

JanSathi backend is:

Agentic

Deterministic

Cloud-ready

Lambda-ready

Fail-fast hardened

Production structured

Cleanly version controlled

Ready for AWS deployment
