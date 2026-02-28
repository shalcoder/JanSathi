# JanSathi (जनसाथी)
## Voice-First AI Civic Assistant for India  
### Production-Hardened Agentic Backend (Phase 2 Complete)

![Status](https://img.shields.io/badge/Status-Cloud_Ready-brightgreen)
![Architecture](https://img.shields.io/badge/Architecture-Agentic_Core-blue)
![Deployment](https://img.shields.io/badge/Deployment-Lambda_Ready-success)

---

# 📌 Overview

**JanSathi** is a deterministic, voice-first civic AI assistant designed to help Indian citizens access government schemes, certificates, and public services through structured conversational workflows.

The backend is built as a **transport-agnostic agentic engine** capable of running on:

- Flask (Web deployment)
- AWS Lambda (Serverless deployment)
- Future IVR adapters
- WhatsApp integrations
- Any transport layer

The core engine remains independent from the execution layer.

---

# 🏗️ Architecture (Current Production State)


Flask Adapter
↓
Lambda Adapter
↓
process_user_input() ← Unified Execution Layer
↓
AgenticWorkflowEngine (Deterministic FSM)
↓
SessionManager
↓
Storage Abstraction
├── LocalJSONStorage
└── DynamoDBStorage


## Core Engineering Principles

- Deterministic finite-state workflow
- Storage abstraction (Local ↔ DynamoDB via env)
- Fail-fast cloud validation
- Transport-layer independence
- Serverless compatibility
- Production-grade error handling
- Clean separation of concerns

---

# ✅ Completed Phases

---

## Phase 1 — Agentic Core (Completed)

- Deterministic finite state workflow engine
- PM-Kisan eligibility workflow
- Grievance handling workflow
- Restart support
- Structured event output contract
- Session persistence layer
- Pluggable storage architecture
- Environment-based storage switching

---

## Phase 2 — Cloud Hardening (Completed)

### 1️⃣ Unified Execution Layer

File:

backend/app/core/execution.py


Provides:

```python
def process_user_input(message: str, session_id: str) -> dict

This is now the single execution entry point for:

Flask

Lambda

Future adapters
```
2️⃣ Flask Refactor

Flask routes now act as thin wrappers:

Flask → process_user_input() → AgenticWorkflowEngine

No business logic inside routes.

3️⃣ Lambda Adapter (Serverless Ready)

File:

backend/lambda_handler.py

Features:

Fully independent from Flask

Compatible with Lambda Proxy Integration

Proper statusCode + JSON response

No AWS SDK logic inside

Pure transport-layer adapter

Lambda Handler:

lambda_handler.lambda_handler
4️⃣ DynamoDB Production Hardening

DynamoDBStorage now:

Validates AWS_REGION

Validates DYNAMODB_TABLE

Performs table existence check (self.table.load())

Fails fast if credentials are missing

Raises explicit errors for:

Missing credentials

Missing table

Region mismatch

No silent fallback to local storage

Guarantee:

If AWS credentials are correct → system works immediately
If misconfigured → clear explicit failure

5️⃣ Lambda Deployment Hardening

Added:

backend/requirements-lambda.txt
backend/LAMBDA_DEPLOYMENT.md

Minimal dependency bundle

Flask excluded from Lambda build

Sterile packaging verified

Cold-start optimized

🚀 Local Development
Backend Setup
cd backend
pip install -r requirements.txt
python main.py

Runs on:

http://localhost:5000
Lambda Local Simulation
cd backend
python
from lambda_handler import lambda_handler

event = {
    "body": '{"message":"hello","session_id":"test123"}'
}

print(lambda_handler(event, None))
☁️ AWS Deployment (Handled Separately)
Lambda Configuration

Runtime: Python 3.11

Architecture: x86_64

Handler:

lambda_handler.lambda_handler

Memory: 512 MB (recommended)

Timeout: 15 seconds

Required Environment Variables
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

Scoped to the DynamoDB table.

📂 Backend Structure
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

No hardcoded AWS credentials

No silent fallback storage

Explicit cloud validation

Deterministic workflows

Lambda independent from Flask

Single unified execution entry

Proper error propagation

⚠️ Pending Work
🔲 API Contract Hardening

Versioned request schema

Payload normalization layer

🔲 Observability

Structured logging standard

Request correlation IDs

CloudWatch JSON logging

🔲 DynamoDB Scaling Enhancements

TTL for inactive sessions

Partition key strategy

Secondary indexes (GSI)

🔲 Authentication Enforcement

JWT validation middleware

User-session binding

Multi-tenant safety

🔲 Rate Limiting & WAF

API Gateway throttling

DDoS protection

🔲 Frontend–Backend Full Integration
🎯 System Maturity
Layer	Status
Agent Core	✅ Production-Ready
Storage Layer	✅ Hardened
Lambda	✅ Verified
Flask	✅ Refactored
AWS Deployment	🔲 Pending Setup
Observability	🔲 Basic
Authentication	🔲 Pending
📄 License

MIT License
