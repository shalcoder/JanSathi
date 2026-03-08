-- JanSathi civic upgrade schema migration
-- Date: 2026-03-08

BEGIN;

CREATE TABLE IF NOT EXISTS life_event_case (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id VARCHAR(40) UNIQUE NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100),
    event_key VARCHAR(50) NOT NULL,
    event_label VARCHAR(120),
    status VARCHAR(30) NOT NULL DEFAULT 'queued',
    current_step INTEGER NOT NULL DEFAULT 0,
    suggested_schemes JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_life_event_case_user_id ON life_event_case(user_id);
CREATE INDEX IF NOT EXISTS idx_life_event_case_session_id ON life_event_case(session_id);
CREATE INDEX IF NOT EXISTS idx_life_event_case_event_key ON life_event_case(event_key);

CREATE TABLE IF NOT EXISTS life_event_step (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id VARCHAR(40) NOT NULL,
    step_order INTEGER NOT NULL,
    service_key VARCHAR(80) NOT NULL,
    title VARCHAR(200) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    reason TEXT,
    eta_minutes INTEGER,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES life_event_case(case_id)
);

CREATE INDEX IF NOT EXISTS idx_life_event_step_case_id ON life_event_step(case_id);

CREATE TABLE IF NOT EXISTS proactive_alert (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id VARCHAR(40) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    scheme_id VARCHAR(100),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    reason_trace JSON,
    status VARCHAR(20) NOT NULL DEFAULT 'generated',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME
);

CREATE INDEX IF NOT EXISTS idx_proactive_alert_user_id ON proactive_alert(user_id);
CREATE INDEX IF NOT EXISTS idx_proactive_alert_status ON proactive_alert(status);

CREATE TABLE IF NOT EXISTS civic_artifact_packet (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    packet_id VARCHAR(40) UNIQUE NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100),
    workflow VARCHAR(120) NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    artifacts JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_civic_artifact_packet_session ON civic_artifact_packet(session_id);

CREATE TABLE IF NOT EXISTS civic_journey_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    case_id VARCHAR(40),
    stage VARCHAR(120) NOT NULL,
    status VARCHAR(30) NOT NULL,
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_civic_journey_event_user_id ON civic_journey_event(user_id);
CREATE INDEX IF NOT EXISTS idx_civic_journey_event_session_id ON civic_journey_event(session_id);
CREATE INDEX IF NOT EXISTS idx_civic_journey_event_case_id ON civic_journey_event(case_id);

CREATE TABLE IF NOT EXISTS fraud_report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id VARCHAR(40) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    location VARCHAR(120) NOT NULL,
    details TEXT NOT NULL,
    amount NUMERIC DEFAULT 0,
    contact VARCHAR(100),
    scheme_hint VARCHAR(100),
    signal_cluster_key VARCHAR(120),
    signal_severity VARCHAR(20) DEFAULT 'low',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fraud_report_location ON fraud_report(location);
CREATE INDEX IF NOT EXISTS idx_fraud_report_cluster_key ON fraud_report(signal_cluster_key);
CREATE INDEX IF NOT EXISTS idx_fraud_report_severity ON fraud_report(signal_severity);

COMMIT;
