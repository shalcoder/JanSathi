"use client";
/**
 * LifeEventWorkflow.tsx
 * Renders the cascaded multi-service workflow when a citizen describes
 * a life event (crop failure, child birth, job loss, etc.).
 *
 * Triggered from ChatInterface when response contains `life_event` data.
 */
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronDown,
  ChevronUp,
  ExternalLink,
  AlertTriangle,
  CheckCircle,
  Circle,
  FileText,
} from "lucide-react";

export interface LifeEventStep {
  id: string;
  label: string;
  description: string;
  action: string;
  link?: string | null;
  priority: "urgent" | "high" | "medium" | "low";
  documents?: string[];
  scheme_hint?: string;
}

export interface LifeEventData {
  detected: boolean;
  event_id: string;
  label: string;
  icon: string;
  summary: string;
  workflow: LifeEventStep[];
}

const PRIORITY_CONFIG = {
  urgent: { label: "URGENT",  badge: "bg-red-500/15 text-red-400 border border-red-500/25",   dot: "bg-red-500",    order: 0 },
  high:   { label: "HIGH",    badge: "bg-orange-500/15 text-orange-400 border border-orange-500/25", dot: "bg-orange-400", order: 1 },
  medium: { label: "MEDIUM",  badge: "bg-yellow-500/15 text-yellow-400 border border-yellow-500/25", dot: "bg-yellow-400", order: 2 },
  low:    { label: "LOW",     badge: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/25", dot: "bg-emerald-500", order: 3 },
};

function StepCard({ step, index, total }: { step: LifeEventStep; index: number; total: number }) {
  const [expanded, setExpanded] = useState(index === 0);
  const cfg = PRIORITY_CONFIG[step.priority] ?? PRIORITY_CONFIG.medium;

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.07 }}
      className="relative"
    >
      {/* Connector line */}
      {index < total - 1 && (
        <div className="absolute left-5 top-12 bottom-0 w-px bg-zinc-700/60 z-0" />
      )}

      <div className="relative z-10 flex gap-3">
        {/* Step number bubble */}
        <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 font-black text-sm border-2 ${
          index === 0
            ? "bg-primary border-primary text-white"
            : "bg-zinc-800 border-zinc-600 text-zinc-300"
        }`}>
          {index + 1}
        </div>

        {/* Card */}
        <div className="flex-1 mb-3">
          <button
            onClick={() => setExpanded((v) => !v)}
            className="w-full text-left bg-zinc-900/60 border border-zinc-700/60 rounded-xl p-3.5 hover:border-zinc-600 transition-all"
          >
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <div className={`w-2 h-2 rounded-full shrink-0 ${cfg.dot}`} />
                <span className="text-sm font-bold text-zinc-100 truncate">{step.label}</span>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className={`text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full ${cfg.badge}`}>
                  {cfg.label}
                </span>
                {expanded ? <ChevronUp className="w-3.5 h-3.5 text-zinc-500" /> : <ChevronDown className="w-3.5 h-3.5 text-zinc-500" />}
              </div>
            </div>
            <p className="text-xs text-zinc-400 mt-1 pl-4">{step.description}</p>
          </button>

          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="bg-zinc-900/40 border border-zinc-700/40 border-t-0 rounded-b-xl px-4 py-3 space-y-3">
                  {/* Action */}
                  <div className="flex items-start gap-2 text-xs">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    <span className="text-zinc-300">{step.action}</span>
                  </div>

                  {/* Documents checklist */}
                  {step.documents && step.documents.length > 0 && (
                    <div>
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <FileText className="w-3 h-3 text-zinc-500" />
                        <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-500">Documents needed</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {step.documents.map((doc, di) => (
                          <span key={di} className="text-[10px] bg-zinc-800 border border-zinc-700 text-zinc-300 px-2 py-0.5 rounded-full">
                            {doc}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Apply link */}
                  {step.link && (
                    <a
                      href={step.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 text-[10px] font-bold text-primary hover:underline"
                    >
                      <ExternalLink className="w-3 h-3" />
                      Official Portal
                    </a>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
}

export function LifeEventWorkflow({ data }: { data: LifeEventData }) {
  const [collapsed, setCollapsed] = useState(false);
  const urgentCount = data.workflow.filter((s) => s.priority === "urgent").length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-4 rounded-2xl border border-zinc-700/60 bg-zinc-900/70 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-zinc-700/50">
        <div className="flex items-center gap-2.5">
          <span className="text-2xl">{data.icon}</span>
          <div>
            <div className="text-sm font-black text-zinc-100">{data.label}</div>
            <div className="text-[10px] text-zinc-400 font-medium">
              {data.workflow.length} services triggered automatically
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {urgentCount > 0 && (
            <div className="flex items-center gap-1 text-[9px] font-black uppercase text-red-400 bg-red-500/10 border border-red-500/20 px-2 py-1 rounded-full">
              <AlertTriangle className="w-2.5 h-2.5" />
              {urgentCount} urgent
            </div>
          )}
          <button
            onClick={() => setCollapsed((v) => !v)}
            className="text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            {collapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {!collapsed && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: "auto" }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            {/* Summary */}
            <div className="px-4 pt-3 pb-1">
              <p className="text-xs text-zinc-300 leading-relaxed">{data.summary}</p>
            </div>

            {/* Steps */}
            <div className="px-4 pt-2 pb-4">
              {data.workflow.map((step, i) => (
                <StepCard key={step.id} step={step} index={i} total={data.workflow.length} />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
