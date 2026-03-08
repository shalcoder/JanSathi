# JanSathi Civic Upgrade Execution Backlog

## Objective
Ship JanSathi as an AI Life Event Civic Assistant: one citizen life event triggers a multi-service workflow, proactive eligibility alerts, guided offline navigation, artifact generation, journey tracking, fraud signal detection, and impact reporting.

## Release Plan
1. `R1 (2 weeks)`: Life Event Orchestration + Journey tracking backbone.
2. `R2 (2 weeks)`: Proactive matcher + Notification scheduler + Artifact packet v2.
3. `R3 (2 weeks)`: Community intelligence + Fraud analytics + Admin insights.
4. `R4 (1 week)`: Demo hardening, offline mode, metric QA, pitch script.

## Ticket Backlog

### EPIC A: Life Event Orchestration

1. `A1` Add life-event intent category and entity extraction
- Scope: detect events (`crop_loss`, `child_birth`, `job_loss`) in `intent_service`.
- Files:
  - `backend/app/services/intent_service.py`
  - `backend/app/core/execution.py`
- Acceptance:
  - Citizen message `My crop failed` maps to `life_event` intent and `event_key=crop_loss`.
  - Confidence and telemetry are emitted.

2. `A2` Build orchestration graph for event-to-multi-scheme pipeline
- Scope: replace static workflow response with executable step plan from event templates.
- Files:
  - `backend/app/services/civic_infra_service.py`
  - `backend/app/services/workflow_service.py`
  - `backend/agentic_engine/workflow_engine.py`
  - `backend/docs/step_functions_asl.json`
- Acceptance:
  - For `crop_loss`, at least 5 steps are generated with state transitions: `queued -> in_progress -> completed/blocked`.

3. `A3` Add API to start and fetch life-event case
- Scope: `POST /v1/civic/life-event-cases`, `GET /v1/civic/life-event-cases/<id>`.
- Files:
  - `backend/app/api/v1_routes.py`
  - `frontend/src/services/api.ts`
- Acceptance:
  - API returns case ID, current step, next action, ETA, and mapped schemes.

### EPIC B: Proactive Scheme Discovery

1. `B1` Build daily matcher service
- Scope: profile + scheme rules scoring + dedupe + priority ranking.
- Files:
  - `backend/app/services/scheme_feed_service.py`
  - `backend/app/services/civic_infra_service.py`
  - `backend/app/services/rules_engine.py`
- Acceptance:
  - User with farmer profile gets contextual alerts (example: solar subsidy) with reason trace.

2. `B2` Notification scheduling + consent-aware dispatch
- Scope: add daily job hook; send SMS only when user consent exists.
- Files:
  - `backend/app/services/notify_service.py`
  - `backend/app/models/models.py`
  - `infrastructure/stacks/workflow_stack.py`
- Acceptance:
  - Alert record status updates: `generated -> queued -> sent/failed`.

3. `B3` Frontend proactive panel with action CTA
- Scope: clickable `Apply now` and `Remind me` actions.
- Files:
  - `frontend/src/components/features/dashboard/SchemesPage.tsx`
  - `frontend/src/services/api.ts`
- Acceptance:
  - User can trigger workflow directly from proactive alert card.

### EPIC C: Civic Artifact Automation + Journey

1. `C1` Artifact packet v2
- Scope: expand packet to include `application_packet`, `complaint_letter`, `appointment_slip`, `office_visit_guide`.
- Files:
  - `backend/app/services/civic_infra_service.py`
  - `backend/app/services/receipt_service.py`
- Acceptance:
  - `/v1/civic/artifacts` returns artifact list with status and URLs (or placeholders in local mode).

2. `C2` Civic journey event store
- Scope: persistent journey timeline across calls/chats.
- Files:
  - `backend/app/models/models.py`
  - `backend/app/services/civic_infra_service.py`
  - `backend/app/api/v1_routes.py`
  - `frontend/src/components/features/dashboard/ApplicationsPage.tsx`
- Acceptance:
  - Journey shows ordered statuses for case lifecycle.

### EPIC D: Community Intelligence + Fraud Signals

1. `D1` Community intelligence aggregation
- Scope: scheme trend counts, document issue hotspots, officer contact data.
- Files:
  - `backend/app/services/civic_infra_service.py`
  - `frontend/src/components/features/dashboard/CommunityPage.tsx`
- Acceptance:
  - `GET /v1/civic/community-insights` returns trends with timestamp and sample size.

2. `D2` Fraud pattern detection
- Scope: normalize reports, cluster by location/scheme/amount, raise signal severity.
- Files:
  - `backend/app/services/civic_infra_service.py`
  - `backend/app/models/models.py`
  - `frontend/src/components/features/dashboard/CommunityPage.tsx`
- Acceptance:
  - Repeated complaint pattern generates `severity=high` signal in impact metrics.

### EPIC E: Metrics + Demo Hardening

1. `E1` Impact metric standardization
- Scope: define metric formulas and timestamp windows.
- Files:
  - `backend/app/services/civic_infra_service.py`
  - `frontend/src/components/features/dashboard/ImpactMode.tsx`
  - `frontend/src/components/features/dashboard/OverviewPage.tsx`
- Acceptance:
  - Dashboard displays consistent backend-calculated KPIs.

2. `E2` Offline civic mode support
- Scope: queue requests and replay when online for key civic actions.
- Files:
  - `frontend/src/services/offlineQueue.ts`
  - `frontend/src/components/features/chat/ChatInterface.tsx`
  - `frontend/src/components/features/dashboard/PhoneEmulatorPage.tsx`
- Acceptance:
  - User can initiate flow offline; queued actions flush on reconnect.

## Dependency Order
1. `A1 -> A2 -> A3`
2. `C2` can start after `A2`
3. `B1 -> B2 -> B3`
4. `D1 -> D2`
5. `E1` after `A/B/C/D` data is stable
6. `E2` parallel with `E1`

## Definition Of Done
1. API contracts implemented and versioned.
2. DB migration applied and rollback script available.
3. Integration tests pass for all civic endpoints.
4. Demo flow (`crop_loss`) completes in under 90 seconds in local simulation.
5. Impact metrics reflect real persisted records (not seeded constants).
