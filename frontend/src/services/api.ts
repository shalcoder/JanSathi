import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

// ─────────────────────────────────────────────────────────────────────────────
// Correlation ID — one per browser session, carried on every request.
// Echoed back by the backend in X-Correlation-Id response header.
// Used to trace a full user journey across CloudWatch logs.
// ─────────────────────────────────────────────────────────────────────────────
const _genCid = (): string =>
  typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2) + Date.now().toString(36);

const CORRELATION_ID: string =
  typeof window !== "undefined"
    ? (sessionStorage.getItem("jansathi_cid") ||
       (() => { const id = _genCid(); sessionStorage.setItem("jansathi_cid", id); return id; })())
    : _genCid();

export const getCorrelationId = () => CORRELATION_ID;

// ─────────────────────────────────────────────────────────────────────────────
// Shared API client factory – call buildClient() wherever you need a request
// to carry auth headers (token + session-id).
// ─────────────────────────────────────────────────────────────────────────────
export const buildClient = (token?: string, sessionId?: string) => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Correlation-Id": CORRELATION_ID,
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (sessionId) headers["X-Session-Id"] = sessionId;
  return axios.create({ baseURL: BASE_URL, headers });
};

// Default unauthenticated client (legacy / health checks)
const apiClient = buildClient();

// ─────────────────────────────────────────────────────────────────────────────
// LEGACY TYPES (kept for backward compat with existing components)
// ─────────────────────────────────────────────────────────────────────────────
export interface QueryResponse {
  query: string;
  answer: {
    text: string;
    audio: string;
    provenance?: string;
    explainability?: {
      confidence: number;
      matching_criteria: string[];
      privacy_protocol: string;
    };
  };
  context: string[];
  structured_sources?: {
    title: string;
    text: string;
    link: string;
    benefit: string;
    logo: string;
  }[];
  meta?: {
    language: string;
  };
}

export interface QueryRequest {
  text_query: string;
  language?: string;
  userId?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// UNIFIED API TYPES (new backend)
// ─────────────────────────────────────────────────────────────────────────────
export interface BenefitReceiptSource {
  title: string;
  url: string;
  page?: number;
}

export interface BenefitReceipt {
  eligible: boolean;
  rules: string[];
  sources: BenefitReceiptSource[];
}

export interface UnifiedQueryRequest {
  session_id: string;
  channel: "web" | "ivr" | "whatsapp";
  input: {
    text?: string;
    audio_s3_key?: string | null;
  };
  metadata?: {
    lang?: string;
    user_id?: string;
  };
}

export interface UnifiedQueryResponse {
  session_id: string;
  turn_id: string;
  transcript: string;
  response_text: string;
  audio_url?: string;
  benefit_receipt?: BenefitReceipt;
  confidence?: number;
  rules_override?: boolean;
  next_actions?: string[];
  debug?: {
    model: string;
    latency_ms: number;
    asr_confidence?: number;
    cache_hit?: boolean;
    token_count?: number;
    thoughts?: Thought[];
  };
  citations?: Citation[];
}

export interface Thought {
  type: "rationale" | "tool_call" | "observation";
  text?: string;
  tool?: string;
  input?: string;
}

export interface Citation {
  text: string;
  sources: string[];
}

export interface ApplyRequest {
  session_id: string;
  turn_id: string;
  application_payload?: Record<string, unknown>;
}

export interface ApplyResponse {
  case_id: string;
  status: string;
  expected_actions?: string[];
}

export interface SessionState {
  session_id: string;
  user_id?: string;
  current_state?: string;
  last_turn?: UnifiedQueryResponse;
  pending_hitl?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface PresignResponse {
  url: string;
  key: string;
}

export interface HITLCase {
  id: string;
  session_id: string;
  turn_id: string;
  transcript: string;
  response_text: string;
  confidence: number;
  benefit_receipt?: BenefitReceipt;
  audio_url?: string;
  status: "pending_review" | "approved" | "rejected";
  created_at: string;
}

export interface IVRSession {
  session_id: string;
  caller_number: string; // masked, e.g. "+91-XXXXX12345"
  start_time: string;
  current_state: string;
  last_transcript?: string;
  last_audio_url?: string;
  channel: "ivr";
}

// ─────────────────────────────────────────────────────────────────────────────
// UNIFIED API FUNCTIONS
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Main entry: send text or audio to the backend and get a unified response.
 * Pass `token` (Clerk JWT) and `sessionId` so they are forwarded as headers.
 */
interface RawAgentResponse {
  session_id: string;
  response_text: string;
  turn_id?: string;
  benefit_receipt?: BenefitReceipt;
  confidence?: number;
  audio_url?: string;
  mode?: string;
  model?: string;
  latency_ms?: number;
  citations?: Citation[];
  thoughts?: Thought[];
  provenance?: string;
}

export const sendUnifiedQuery = async (
  params: UnifiedQueryRequest,
  token?: string,
  sessionId?: string,
): Promise<UnifiedQueryResponse> => {
  const client = buildClient(token, sessionId ?? params.session_id);
  
  // Route to the new intelligent agent endpoint
  const response = await client.post<RawAgentResponse>("/v1/agent/invoke", {
    session_id: params.session_id,
    message: params.input.text || "",
    language: params.metadata?.lang || "en",
    channel: params.channel || "web",
    userId: params.metadata?.user_id,
  });

  const data = response.data;

  // Map backend AgentState to UnifiedQueryResponse for UI compatibility
  return {
    session_id: data.session_id,
    turn_id: data.turn_id || `turn-${Date.now()}`,
    transcript: params.input.text || "",
    response_text: data.response_text,
    benefit_receipt: data.benefit_receipt,
    confidence: data.confidence || 0.9,
    audio_url: data.audio_url,
    // Carry over any extra fields like citations or provenance if they exist
    ...(data.citations ? { citations: data.citations } : {}),
    ...(data.provenance ? { provenance: data.provenance } : { provenance: "AI Analysis" }),
    debug: {
      model: data.mode || data.model || "agentcore",
      latency_ms: data.latency_ms || 0,
      thoughts: data.thoughts
    }
  };
};

/**
 * Send audio blob to backend via /v1/query with multipart/form-data.
 */
export const sendAudioQuery = async (
  audioBlob: Blob,
  sessionId: string,
  lang: string = "hi",
  token?: string,
): Promise<UnifiedQueryResponse> => {
  const client = buildClient(token, sessionId);
  const fd = new FormData();
  fd.append("audio", audioBlob, "recording.webm");
  fd.append("session_id", sessionId);
  fd.append("channel", "web");
  fd.append("lang", lang);
  const response = await client.post<UnifiedQueryResponse>("/v1/query", fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

/**
 * Trigger a benefit application.
 */
export const applyForBenefit = async (
  params: ApplyRequest,
  token?: string,
): Promise<ApplyResponse> => {
  const client = buildClient(token, params.session_id);
  const response = await client.post<ApplyResponse>("/v1/apply", params);
  return response.data;
};

/**
 * Read session state.
 */
export const getSessionState = async (
  sessionId: string,
  token?: string,
): Promise<SessionState> => {
  const client = buildClient(token, sessionId);
  const response = await client.get<SessionState>(`/v1/sessions/${sessionId}`);
  return response.data;
};

/**
 * Initialize a new session (or retrieve existing one) for a user.
 */
export const initSession = async (
  token: string,
): Promise<{ session_id: string }> => {
  const client = buildClient(token);
  const response = await client.post<{ session_id: string }>(
    "/v1/sessions/init",
  );
  return response.data;
};

/**
 * Get presigned S3 upload URL for a document.
 */
export const getPresignedUpload = async (
  sessionId: string,
  filename: string,
  token?: string,
): Promise<PresignResponse> => {
  const client = buildClient(token, sessionId);
  const response = await client.post<PresignResponse>("/v1/upload-presign", {
    session_id: sessionId,
    filename,
  });
  return response.data;
};

/**
 * Fetch HITL pending review cases (admin only).
 */
export const getHITLCases = async (
  status: "pending_review" | "approved" | "rejected" = "pending_review",
  token?: string,
): Promise<HITLCase[]> => {
  const client = buildClient(token);
  const response = await client.get<HITLCase[]>(
    `/v1/admin/cases?status=${status}`,
  );
  return response.data;
};

/**
 * Approve a HITL case.
 */
export const approveHITLCase = async (
  caseId: string,
  token?: string,
): Promise<void> => {
  const client = buildClient(token);
  await client.post(`/v1/admin/cases/${caseId}/approve`);
};

/**
 * Reject a HITL case.
 */
export const rejectHITLCase = async (
  caseId: string,
  reason?: string,
  token?: string,
): Promise<void> => {
  const client = buildClient(token);
  await client.post(`/v1/admin/cases/${caseId}/reject`, { reason });
};

/**
 * Fetch active IVR sessions (admin only).
 */
export const getIVRSessions = async (token?: string): Promise<IVRSession[]> => {
  const client = buildClient(token);
  const response = await client.get<IVRSession[]>("/v1/ivr/sessions");
  return response.data;
};

/**
 * Fetch user applications by session ID.
 */
export const getApplicationsBySession = async (
  sessionId: string,
  token?: string,
): Promise<ApplyResponse[]> => {
  const client = buildClient(token, sessionId);
  const response = await client.get<ApplyResponse[]>(
    `/v1/applications?session_id=${sessionId}`,
  );
  return response.data;
};

// ─────────────────────────────────────────────────────────────────────────────
// TELEMETRY & OBSERVABILITY
// ─────────────────────────────────────────────────────────────────────────────

export interface TelemetryEvent {
  event_type: string;
  session_id?: string;
  turn_id?: string;
  latency_ms?: number;
  confidence?: number;
  channel?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Post a telemetry event to the backend for CloudWatch / QuickSight dashboards.
 */
export const postTelemetry = async (
  event: TelemetryEvent,
  token?: string,
): Promise<void> => {
  try {
    const client = buildClient(token);
    await client.post("/v1/telemetry", event);
  } catch {
    // Telemetry failures are non-blocking — never throw
  }
};

// DEPRECATED: getAuditLogs was here

export interface HealthStatus {
  status: "ok" | "degraded" | "down";
  version?: string;
  services: { name: string; status: "ok" | "degraded" | "down" }[];
}

/**
 * Health check with structured response.
 */
export const getHealth = async (): Promise<HealthStatus> => {
  try {
    const response = await apiClient.get<HealthStatus>("/health");
    return response.data;
  } catch {
    return { status: "down", services: [] };
  }
};

// ─────────────────────────────────────────────────────────────────────────────
// LEGACY FUNCTIONS (preserved for backward compatibility)
// ─────────────────────────────────────────────────────────────────────────────

export const sendQuery = async (
  params: QueryRequest | FormData,
): Promise<QueryResponse> => {
  const response = await apiClient.post("/query", params, {
    headers:
      params instanceof FormData
        ? { "Content-Type": "multipart/form-data" }
        : {},
  });
  return response.data;
};

export interface HistoryItem {
  id: string;
  query: string;
  timestamp: string;
}

export const getHistory = async (
  userId?: string,
  limit: number = 10,
): Promise<HistoryItem[]> => {
  try {
    const url = userId
      ? `/history?userId=${userId}&limit=${limit}`
      : `/history?limit=${limit}`;
    const response = await apiClient.get(url);
    return response.data;
  } catch {
    return [];
  }
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get("/v1/health");
    return response.status === 200;
  } catch {
    return false;
  }
};

export interface AnalyzeResponse {
  analysis: { text: string; audio?: string };
}

export const analyzeImage = async (
  imageFile: File,
  language: string = "hi",
): Promise<AnalyzeResponse> => {
  const formData = new FormData();
  formData.append("image", imageFile);
  formData.append("language", language);
  formData.append(
    "prompt",
    "Explain this document simply and identify next steps.",
  );
  const response = await apiClient.post("/analyze", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export interface MarketRate {
  crop: string;
  market: string;
  price: string;
  unit: string;
  change: string;
  trend: "up" | "down";
}

export const getMarketRates = async (): Promise<MarketRate[]> => {
  try {
    const response = await apiClient.get("/market-rates");
    return response.data;
  } catch {
    return [];
  }
};

export interface LiveScheme {
  id: string;
  title: string;
  benefit: string;
  ministry: string;
  category: string;
  keywords: string[];
  apply_link: string;
  official_source: string;
  eligibility_status: "eligible" | "likely_eligible" | "check_criteria";
  eligibility_score: number;
  why_recommended?: string[];
  last_updated_at?: string;
}

export interface LiveSchemesResponse {
  schemes: LiveScheme[];
  count: number;
  personalization?: {
    user_id: string;
    profile_found: boolean;
    engine: string;
  };
  meta?: {
    generated_at: string;
    refresh_interval_seconds: number;
    data_sources: string[];
  };
}

export const getSchemes = async (token?: string): Promise<LiveSchemesResponse> => {
  try {
    const client = buildClient(token);
    const response = await client.get<LiveSchemesResponse>("/v1/schemes");
    return response.data;
  } catch {
    return { schemes: [], count: 0 };
  }
};

export interface LifeWorkflowResponse {
  event_key: string;
  event_label: string;
  workflow_steps: string[];
  suggested_schemes: string[];
  profile_context: Record<string, unknown>;
}

export interface ProactiveAlert {
  id: string;
  title: string;
  message: string;
  priority: "high" | "medium" | "low";
  channel: string;
}

export interface ProactiveAlertsResponse {
  alerts: ProactiveAlert[];
  count: number;
}

export interface CommunityInsightsResponse {
  location: string;
  posts_analyzed: number;
  top_scheme_topics: Array<{ topic: string; count: number }>;
  common_document_issue: string;
  recommended_action: string;
}

export interface CivicNavigatorResponse {
  service: string;
  location: string;
  nearest_center: {
    name: string;
    address: string;
    hours: string;
    contact: string;
    maps_url: string;
  };
  required_documents: string[];
}

export interface CivicJourneyResponse {
  journey: Array<{ stage: string; status: string; updated_at?: string | null }>;
}

export interface LifeEventStep {
  step_id: string;
  title: string;
  service_key: string;
  status: "pending" | "active" | "completed" | "blocked";
  reason?: string;
  eta_minutes?: number;
  updated_at?: string;
}

export interface LifeEventCaseResponse {
  case_id: string;
  session_id: string;
  user_id?: string;
  event_key: string;
  event_label: string;
  status: "queued" | "in_progress" | "completed" | "blocked";
  current_step: number;
  suggested_schemes: string[];
  steps: LifeEventStep[];
  created_at?: string;
  updated_at?: string;
}

export interface CivicImpactMetrics {
  citizens_served: number;
  applications_processed: number;
  community_posts: number;
  fraud_reports: number;
  estimated_benefits_unlocked_inr: number;
  estimated_trips_avoided: number;
  grievances_resolved: number;
}

export const getLifeWorkflow = async (
  eventKey: string,
  userId?: string,
  token?: string
): Promise<LifeWorkflowResponse> => {
  const client = buildClient(token);
  const suffix = userId ? `&user_id=${encodeURIComponent(userId)}` : "";
  const response = await client.get<LifeWorkflowResponse>(`/v1/civic/life-workflow?event=${encodeURIComponent(eventKey)}${suffix}`);
  return response.data;
};

export const createLifeEventCase = async (
  payload: { session_id: string; event_key?: string; event_text?: string; user_id?: string; language?: string },
  token?: string
): Promise<LifeEventCaseResponse> => {
  const client = buildClient(token, payload.session_id);
  const response = await client.post<LifeEventCaseResponse>("/v1/civic/life-event-cases", payload);
  return response.data;
};

export const getLifeEventCase = async (
  caseId: string,
  token?: string
): Promise<LifeEventCaseResponse> => {
  const client = buildClient(token);
  const response = await client.get<LifeEventCaseResponse>(`/v1/civic/life-event-cases/${encodeURIComponent(caseId)}`);
  return response.data;
};

export const getProactiveAlerts = async (
  userId?: string,
  token?: string
): Promise<ProactiveAlertsResponse> => {
  const client = buildClient(token);
  const query = userId ? `?user_id=${encodeURIComponent(userId)}` : "";
  const response = await client.get<ProactiveAlertsResponse>(`/v1/civic/proactive-alerts${query}`);
  return response.data;
};

export const getCommunityInsights = async (
  location: string,
  token?: string
): Promise<CommunityInsightsResponse> => {
  const client = buildClient(token);
  const response = await client.get<CommunityInsightsResponse>(`/v1/civic/community-insights?location=${encodeURIComponent(location)}`);
  return response.data;
};

export const getCivicNavigator = async (
  location: string,
  service: string = "csc",
  token?: string
): Promise<CivicNavigatorResponse> => {
  const client = buildClient(token);
  const response = await client.get<CivicNavigatorResponse>(
    `/v1/civic/navigator?location=${encodeURIComponent(location)}&service=${encodeURIComponent(service)}`
  );
  return response.data;
};

export const getCivicJourney = async (
  params: { userId?: string; sessionId?: string },
  token?: string
): Promise<CivicJourneyResponse> => {
  const client = buildClient(token);
  const q = new URLSearchParams();
  if (params.userId) q.set("user_id", params.userId);
  if (params.sessionId) q.set("session_id", params.sessionId);
  const suffix = q.toString() ? `?${q.toString()}` : "";
  const response = await client.get<CivicJourneyResponse>(`/v1/civic/journey${suffix}`);
  return response.data;
};

export const createCivicArtifacts = async (
  payload: { session_id: string; workflow: string; language?: string },
  token?: string
): Promise<{ packet_id: string; artifacts: Array<{ type: string; status: string }> }> => {
  const client = buildClient(token, payload.session_id);
  const response = await client.post("/v1/civic/artifacts", payload);
  return response.data;
};

export const reportFraud = async (
  payload: { location: string; details: string; amount?: number; contact?: string },
  token?: string
): Promise<{ report_id: string }> => {
  const client = buildClient(token);
  const response = await client.post("/v1/civic/fraud-report", payload);
  return response.data;
};

export const getCivicImpact = async (token?: string): Promise<CivicImpactMetrics> => {
  const client = buildClient(token);
  const response = await client.get<CivicImpactMetrics>("/v1/civic/impact");
  return response.data;
};

export const seedDatabase = async (): Promise<unknown> => {
  const response = await apiClient.post("/admin/seed");
  return response.data;
};

export const applyForScheme = async (
  user_id: string,
  scheme_name: string,
): Promise<unknown> => {
  const response = await apiClient.post("/apply", { user_id, scheme_name });
  return response.data;
};

// ─────────────────────────────────────────────────────────────────────────────
// ADMIN & DEMO: IVR Live Sync
// ─────────────────────────────────────────────────────────────────────────────

export interface IvrSession {
  session_id: string;
  caller_number: string;
  start_time: string;
  last_seen: string;
  language: string;
  current_state: string;
  last_transcript: string;
  last_audio_url: string;
  channel: string;
}

export const getIvrSessions = async (token?: string | null): Promise<IvrSession[]> => {
  try {
    const api = buildClient(token || undefined);
    const response = await api.get("/ivr/sessions");
    return response.data;
  } catch (err) {
    console.error("Failed to fetch IVR sessions", err);
    return [];
  }
};

export const simulateIvrCall = async (payload: Record<string, unknown>, token?: string | null): Promise<Record<string, unknown>> => {
  try {
    const api = buildClient(token || undefined);
    const response = await api.post("/ivr/connect-webhook", payload);
    return response.data;
  } catch (err) {
    console.error("Failed to simulate IVR call", err);
    throw err;
  }
};

export interface HitlCase {
  id: string;
  session_id: string;
  transcript: string;
  response_text: string;
  confidence: number;
  status: string;
  created_at: string;
}

export const getHitlCases = async (token?: string | null): Promise<HitlCase[]> => {
  try {
    const api = buildClient(token || undefined);
    const response = await api.get("/admin/cases");
    return response.data;
  } catch (err) {
    console.error("Failed to fetch HITL cases", err);
    return [];
  }
};

export const resolveHitlCase = async (caseId: string, action: "approve" | "reject", token?: string | null): Promise<void> => {
  try {
    const api = buildClient(token || undefined);
    await api.post(`/admin/cases/${caseId}/${action}`);
  } catch (err) {
    console.error(`Failed to resolve HITL case ${caseId}`, err);
    throw err;
  }
};

export interface AuditRecord {
  record_id: string;
  record_type: string;
  session_id: string;
  ts: string;
  payload: Record<string, unknown>;
  integrity_hash: string;
}

export const getAuditLogs = async (token?: string | null): Promise<AuditRecord[]> => {
  try {
    const api = buildClient(token || undefined);
    const response = await api.get("/admin/audit");
    return response.data.records || [];
  } catch (err) {
    console.error("Failed to fetch audit records", err);
    return [];
  }
};

export const getApplications = async (
  user_id: string = "demo-user",
): Promise<unknown[]> => {
  try {
    const response = await apiClient.get(`/applications?user_id=${user_id}`);
    return response.data;
  } catch {
    return [];
  }
};

// ─────────────────────────────────────────────────────────────────────────────
// DOCUMENT UPLOAD (Bedrock Context)
// ─────────────────────────────────────────────────────────────────────────────
export const uploadDocumentContext = async (
  file: File,
  sessionId: string,
  token?: string
): Promise<{ status: string; extracted_length: number }> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("session_id", sessionId);

  const client = buildClient(token, sessionId);
  try {
    const response = await client.post("/v1/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  } catch (error) {
    console.warn("Failed to upload document context", error);
    throw error;
  }
};
