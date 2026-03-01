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
  };
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
export const sendUnifiedQuery = async (
  params: UnifiedQueryRequest,
  token?: string,
  sessionId?: string,
): Promise<UnifiedQueryResponse> => {
  const client = buildClient(token, sessionId ?? params.session_id);
  const response = await client.post<UnifiedQueryResponse>("/v1/query", params);
  return response.data;
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

export interface AuditLogEntry {
  id: string;
  session_id: string;
  event_type: string;
  timestamp: string;
  user_id?: string;
  details?: Record<string, unknown>;
}

/**
 * Fetch audit logs for a session (admin only).
 */
export const getAuditLogs = async (
  sessionId: string,
  token?: string,
): Promise<AuditLogEntry[]> => {
  const client = buildClient(token);
  const response = await client.get<AuditLogEntry[]>(
    `/v1/audit?session_id=${sessionId}`,
  );
  return response.data;
};

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
    const response = await apiClient.get("/health");
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

export const getSchemes = async (): Promise<Record<string, unknown>> => {
  try {
    const response = await apiClient.get("/schemes");
    return response.data;
  } catch {
    return { schemes: [], count: 0 };
  }
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
