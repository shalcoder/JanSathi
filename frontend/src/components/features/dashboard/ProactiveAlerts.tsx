"use client";
/**
 * ProactiveAlerts.tsx
 * Shows AI-predicted scheme matches from user profile.
 * "Citizens miss schemes because they never know they exist."
 */
import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, ExternalLink, Zap, RefreshCw, ChevronRight } from "lucide-react";
import { getProactiveAlerts, type ProactiveAlert } from "@/services/api";

const PRIORITY_COLORS = {
  high:   { ring: "border-orange-500/40 bg-orange-500/5",  badge: "bg-orange-500/15 text-orange-400", dot: "bg-orange-400" },
  medium: { ring: "border-yellow-500/30 bg-yellow-500/5",  badge: "bg-yellow-500/15 text-yellow-400",  dot: "bg-yellow-400" },
  low:    { ring: "border-emerald-500/20 bg-emerald-500/5", badge: "bg-emerald-500/15 text-emerald-400", dot: "bg-emerald-400" },
};

export function ProactiveAlerts({ userId, token }: { userId?: string; token?: string }) {
  const [alerts, setAlerts] = useState<ProactiveAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [profileSummary, setProfileSummary] = useState<{ occupation: string; income_bracket: string; state: string } | null>(null);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());
  const [expanded, setExpanded] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const res = await getProactiveAlerts(userId, token ?? undefined);
      setAlerts(res.alerts ?? []);
      if (res.profile_summary) setProfileSummary(res.profile_summary);
    } catch {
      // Fallback demo data
      setAlerts([
        { id: "demo-1", title: "PM-KISAN Samman Nidhi", benefit: "₹6,000/year in 3 installments", sms_alert: "You qualify for PM-KISAN ₹6,000/yr. Say: apply pm kisan", action: "apply pm kisan", link: "https://pmkisan.gov.in", priority: "high" },
        { id: "demo-2", title: "Solar Pump Subsidy (PM-KUSUM)", benefit: "90% subsidy on solar irrigation pump", sms_alert: "90% solar pump subsidy available.", action: "apply solar pump", link: "https://pmkusum.mnre.gov.in", priority: "high" },
        { id: "demo-3", title: "Ayushman Bharat PM-JAY", benefit: "₹5 lakh/year free hospital treatment", sms_alert: "Ayushman Bharat ₹5L free treatment.", action: "apply ayushman", link: "https://pmjay.gov.in", priority: "medium" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [userId]);

  const visible = alerts.filter((a) => !dismissed.has(a.id));

  return (
    <div className="rounded-2xl border border-zinc-700/50 bg-zinc-900/60 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-700/40">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-primary/15 border border-primary/20 flex items-center justify-center">
            <Zap className="w-4 h-4 text-primary" />
          </div>
          <div>
            <div className="text-sm font-black text-zinc-100">Proactive Scheme Discovery</div>
            <div className="text-[10px] text-zinc-500">AI matched {visible.length} scheme{visible.length !== 1 ? "s" : ""} to your profile</div>
          </div>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="text-zinc-500 hover:text-zinc-300 transition-colors p-1"
          title="Refresh"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Profile tag */}
      {profileSummary && (
        <div className="px-4 pt-2.5 flex gap-1.5 flex-wrap">
          {[profileSummary.occupation, profileSummary.income_bracket, profileSummary.state]
            .filter(Boolean)
            .map((tag, i) => (
              <span key={i} className="text-[9px] font-bold uppercase tracking-wider bg-zinc-800 border border-zinc-700 text-zinc-400 px-2 py-0.5 rounded-full">
                {tag}
              </span>
            ))}
        </div>
      )}

      {/* Alerts list */}
      <div className="p-3 space-y-2">
        <AnimatePresence mode="popLayout">
          {loading ? (
            [1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-zinc-800/40 rounded-xl animate-pulse" />
            ))
          ) : visible.length === 0 ? (
            <div className="text-center py-6 text-xs text-zinc-500">
              No new scheme matches found. Complete your profile for better matches.
            </div>
          ) : (
            visible.map((alert) => {
              const cfg = PRIORITY_COLORS[alert.priority ?? "medium"] ?? PRIORITY_COLORS.medium;
              const isExpanded = expanded === alert.id;
              const msg = alert.sms_alert ?? alert.message ?? alert.benefit ?? "";

              return (
                <motion.div
                  key={alert.id}
                  layout
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: 30 }}
                  className={`rounded-xl border p-3 cursor-pointer transition-all ${cfg.ring} ${isExpanded ? "ring-1 ring-primary/20" : ""}`}
                  onClick={() => setExpanded(isExpanded ? null : alert.id)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-2 flex-1 min-w-0">
                      <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${cfg.dot}`} />
                      <div className="min-w-0">
                        <div className="text-sm font-bold text-zinc-100 flex items-center gap-2">
                          <span className="truncate">{alert.title}</span>
                          <span className={`text-[8px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded-full ${cfg.badge} shrink-0`}>
                            {alert.priority}
                          </span>
                        </div>
                        {alert.benefit && (
                          <div className="text-xs text-emerald-400 font-semibold mt-0.5">{alert.benefit}</div>
                        )}
                      </div>
                    </div>
                    <ChevronRight className={`w-3.5 h-3.5 text-zinc-500 shrink-0 transition-transform ${isExpanded ? "rotate-90" : ""}`} />
                  </div>

                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="mt-3 pt-3 border-t border-zinc-700/50 space-y-2.5">
                          {/* SMS preview */}
                          {msg && (
                            <div className="bg-zinc-800/60 rounded-lg px-3 py-2">
                              <div className="text-[9px] font-bold uppercase tracking-wider text-zinc-500 mb-1 flex items-center gap-1">
                                <Bell className="w-2.5 h-2.5" /> SMS Alert Preview
                              </div>
                              <p className="text-xs text-zinc-300">{msg}</p>
                            </div>
                          )}

                          <div className="flex items-center gap-2">
                            {alert.link && (
                              <a
                                href={alert.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => e.stopPropagation()}
                                className="flex items-center gap-1 text-[10px] font-bold text-primary bg-primary/10 border border-primary/20 px-3 py-1.5 rounded-lg hover:bg-primary/20 transition-colors"
                              >
                                <ExternalLink className="w-2.5 h-2.5" />
                                Apply Now
                              </a>
                            )}
                            <button
                              onClick={(e) => { e.stopPropagation(); setDismissed((d) => new Set([...d, alert.id])); }}
                              className="text-[10px] text-zinc-500 hover:text-zinc-400 px-2 py-1.5"
                            >
                              Dismiss
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
