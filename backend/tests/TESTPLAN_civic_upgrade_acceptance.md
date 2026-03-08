# Civic Upgrade Acceptance Test Plan

## Scope
Validate life-event orchestration, proactive discovery, journey tracking, artifact generation, fraud signals, and impact metrics.

## Environment
1. Backend running on `http://localhost:5000`.
2. Frontend running on `http://localhost:3000`.
3. Migration `backend/docs/migrations/20260308_civic_upgrade.sql` applied.
4. Seeded user profile:
- `occupation=farmer`
- `annual_income=120000`
- `land_holding_acres=1.2`
- `location_state=Tamil Nadu`

## Contract Tests

1. `POST /v1/civic/life-event-cases`
- Input:
```json
{
  "session_id": "sess-life-001",
  "user_id": "user-001",
  "event_key": "crop_loss",
  "language": "ta"
}
```
- Expect:
  - HTTP `201`
  - `case_id` present
  - `status` is `queued` or `in_progress`
  - `steps.length >= 5`

2. `GET /v1/civic/life-event-cases/{case_id}`
- Expect:
  - HTTP `200`
  - Includes `current_step`
  - Contains mapped schemes: `pmfby`, `pm_kisan`

3. `GET /v1/civic/proactive-alerts?user_id=user-001`
- Expect:
  - HTTP `200`
  - `count >= 1`
  - at least one alert with `priority=high`
  - message includes action phrase like `apply`

4. `POST /v1/civic/artifacts`
- Input:
```json
{
  "session_id": "sess-life-001",
  "workflow": "crop_loss",
  "language": "ta"
}
```
- Expect:
  - HTTP `200`
  - `packet_id` present
  - artifacts include `office_visit_guide` and `application_packet`

5. `GET /v1/civic/journey?user_id=user-001&session_id=sess-life-001`
- Expect:
  - HTTP `200`
  - ordered events
  - at least one `in_progress` or `completed` stage

6. `POST /v1/civic/fraud-report`
- Input:
```json
{
  "location": "Pollachi",
  "details": "Agent asked Rs 2000 for free PM-Kisan enrollment",
  "amount": 2000
}
```
- Expect:
  - HTTP `201`
  - `report_id` present
  - `signal_severity` present in response

## Workflow E2E Tests

1. Crop loss scenario
- Trigger life-event case.
- Verify step progression to:
  - insurance claim stage
  - PM-Kisan recheck
  - compensation guidance
  - document checklist
  - navigator guidance
- Pass criteria:
  - SMS summary generated
  - journey timeline updated
  - trip-saving estimate incremented

2. Child birth scenario
- Trigger event `child_birth`.
- Verify required steps include birth certificate, Aadhaar enrollment, nutrition, vaccination guidance.

3. Job loss scenario
- Trigger event `job_loss`.
- Verify steps include e-Shram, skilling, job exchange.

## Dashboard Validation

1. Schemes page
- Life workflow panel renders selected event steps.
- Proactive alerts load and CTA visible.
- Navigator block shows center address + maps URL.

2. Community page
- Community insight cards load counts and top issue.
- Fraud report submission shows success state.

3. Impact dashboard
- Metrics reflect stored records:
  - `applications_processed`
  - `estimated_benefits_unlocked_inr`
  - `fraud_reports`
  - `estimated_trips_avoided`

## Non-Functional Checks
1. P95 `/v1/civic/life-event-cases` response under 1200 ms (local target).
2. No PII in logs for `details` and contact fields.
3. Duplicate proactive alerts are deduped per user per day.
