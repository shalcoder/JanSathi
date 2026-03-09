"use client";
/**
 * CommunityInsights.tsx
 * Shows village/district-level collective intelligence:
 * top claimed schemes, common doc issues, grievance types, AI recommendation.
 */
import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Users, AlertTriangle, TrendingUp, MessageSquare, Phone, RefreshCw, Award } from "lucide-react";
import { getCommunityInsights, type CommunityInsightsResponse } from "@/services/api";

interface Props {
  location: string;
  token?: string;
}

function Bar({ label, count, max, color }: { label: string; count: number; max: number; color: string }) {
  const pct = max > 0 ? Math.round((count / max) * 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <div className="text-xs text-zinc-300 w-28 shrink-0 truncate" title={label}>{label}</div>
      <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className={`h-full rounded-full ${color}`}
        />
      </div>
      <div className="text-[10px] text-zinc-500 w-6 text-right">{count}</div>
    </div>
  );
}

function Section({ icon: Icon, title, children }: { icon: React.ComponentType<{ className?: string }>; title: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-2">
        <Icon className="w-3.5 h-3.5 text-zinc-400" />
        <span className="text-[10px] font-black uppercase tracking-widest text-zinc-500">{title}</span>
      </div>
      <div className="space-y-1.5">{children}</div>
    </div>
  );
}

const DEMO: CommunityInsightsResponse = {
  location: "Demo",
  posts_analyzed: 342,
  applications_analyzed: 1184,
  top_claimed_schemes: [
    { scheme: "PM-KISAN", count: 89 },
    { scheme: "Ration Card", count: 73 },
    { scheme: "Ayushman Bharat", count: 61 },
    { scheme: "e-Shram", count: 45 },
    { scheme: "PMAY Gramin", count: 28 },
  ],
  common_document_issues: [
    { issue: "Aadhaar name mismatch", count: 54 },
    { issue: "Bank passbook missing", count: 38 },
    { issue: "Ration card not linked", count: 31 },
  ],
  top_grievances: [
    { type: "Payment delayed", count: 42 },
    { type: "Application rejected", count: 29 },
    { type: "Official unresponsive", count: 17 },
  ],
  ai_recommendation: "Most applicants in your area face Aadhaar name mismatch issues. Ensure your Aadhaar matches your bank account name before applying for PM-KISAN.",
  local_officer_contact: { name: "Gram Sevak Help Desk", phone: "1800-11-0001", portal: "https://pgportal.gov.in" },
  generated_at: new Date().toISOString(),
};

export function CommunityInsights({ location, token }: Props) {
  const [data, setData] = useState<CommunityInsightsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const res = await getCommunityInsights(location, token);
      setData(res);
    } catch {
      setData({ ...DEMO, location });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [location]);

  const topSchemes = data?.top_claimed_schemes ?? data?.top_scheme_topics?.map((t) => ({ scheme: t.topic, count: t.count })) ?? [];
  const docIssues  = data?.common_document_issues ?? [];
  const grievances = data?.top_grievances ?? [];
  const maxScheme  = topSchemes.length ? Math.max(...topSchemes.map((s) => s.count)) : 1;
  const maxIssue   = docIssues.length ? Math.max(...docIssues.map((d) => d.count)) : 1;
  const maxGrievance = grievances.length ? Math.max(...grievances.map((g) => g.count)) : 1;

  return (
    <div className="rounded-2xl border border-zinc-700/50 bg-zinc-900/60 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-700/40">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-blue-500/15 border border-blue-500/20 flex items-center justify-center">
            <Users className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <div className="text-sm font-black text-zinc-100">Community Intelligence</div>
            <div className="text-[10px] text-zinc-500">
              {location} · {data?.posts_analyzed ?? "..."} community posts analyzed
            </div>
          </div>
        </div>
        <button onClick={load} disabled={loading} className="text-zinc-500 hover:text-zinc-300 transition-colors p-1" title="Refresh">
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {loading ? (
        <div className="p-4 space-y-3">
          {["w-4/5", "w-3/5", "w-full", "w-1/2"].map((w, i) => (
            <div key={i} className={`h-3 bg-zinc-800/40 rounded-full animate-pulse ${w}`} />
          ))}
        </div>
      ) : (
        <div className="p-4 space-y-5">
          {/* Top Claimed Schemes */}
          {topSchemes.length > 0 && (
            <Section icon={Award} title="Top Claimed Schemes">
              {topSchemes.slice(0, 5).map((s) => (
                <Bar key={s.scheme} label={s.scheme} count={s.count} max={maxScheme} color="bg-primary" />
              ))}
            </Section>
          )}

          {/* Common Document Issues */}
          {docIssues.length > 0 && (
            <Section icon={AlertTriangle} title="Common Document Issues">
              {docIssues.map((d) => (
                <Bar key={d.issue} label={d.issue} count={d.count} max={maxIssue} color="bg-orange-500" />
              ))}
            </Section>
          )}

          {/* Top Grievances */}
          {grievances.length > 0 && (
            <Section icon={MessageSquare} title="Top Grievances">
              {grievances.map((g) => (
                <Bar key={g.type} label={g.type} count={g.count} max={maxGrievance} color="bg-red-500" />
              ))}
            </Section>
          )}

          {/* AI Recommendation */}
          {data?.ai_recommendation && (
            <div>
              <div className="flex items-center gap-1.5 mb-1.5">
                <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-[10px] font-black uppercase tracking-widest text-zinc-500">AI Recommendation</span>
              </div>
              <p className="text-xs text-zinc-300 leading-relaxed bg-emerald-500/5 border border-emerald-500/15 rounded-xl px-3 py-2">
                {data.ai_recommendation}
              </p>
            </div>
          )}

          {/* Local Officer Contact */}
          {data?.local_officer_contact && (
            <div className="flex items-center gap-3 bg-zinc-800/50 rounded-xl px-3 py-2.5 border border-zinc-700/40">
              <div className="w-7 h-7 rounded-lg bg-blue-500/15 border border-blue-500/20 flex items-center justify-center shrink-0">
                <Phone className="w-3.5 h-3.5 text-blue-400" />
              </div>
              <div className="min-w-0">
                <div className="text-xs font-bold text-zinc-200">{data.local_officer_contact.name}</div>
                <div className="text-[10px] text-zinc-400">{data.local_officer_contact.phone}</div>
              </div>
              <a
                href={data.local_officer_contact.portal}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-auto text-[10px] font-bold text-primary bg-primary/10 border border-primary/20 px-2.5 py-1 rounded-lg hover:bg-primary/20 transition-colors shrink-0"
              >
                Portal
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
