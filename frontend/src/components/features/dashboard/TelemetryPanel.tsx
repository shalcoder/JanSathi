'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronUp, ChevronDown, Activity, Brain, Target, Shield, GitBranch, AlertTriangle } from 'lucide-react';

export interface TelemetryData {
  intent?: string;
  confidence?: number;
  slots?: Record<string, unknown>;
  rule_trace?: Array<{ rule: string; pass: boolean; citation?: string }>;
  workflow_stage?: string;
  risk_score?: number;
  latency_ms?: number;
  tokens_used?: number;
}

interface TelemetryPanelProps {
  data: TelemetryData;
}

const Badge = ({ pass }: { pass: boolean }) => (
  <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider ${pass ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'}`}>
    {pass ? 'PASS' : 'FAIL'}
  </span>
);

const ConfidenceBar = ({ value, label }: { value: number; label: string }) => (
  <div className="space-y-1">
    <div className="flex justify-between text-[10px] font-bold">
      <span className="text-white/50 uppercase tracking-widest">{label}</span>
      <span className={value >= 0.8 ? 'text-emerald-400' : value >= 0.6 ? 'text-amber-400' : 'text-red-400'}>
        {Math.round(value * 100)}%
      </span>
    </div>
    <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${Math.round(value * 100)}%` }}
        transition={{ duration: 0.6 }}
        className={`h-full rounded-full ${value >= 0.8 ? 'bg-emerald-400' : value >= 0.6 ? 'bg-amber-400' : 'bg-red-400'}`}
      />
    </div>
  </div>
);

export default function TelemetryPanel({ data }: TelemetryPanelProps) {
  const [open, setOpen] = useState(false);

  const hasData = data.intent || data.workflow_stage;
  if (!hasData) return null;

  return (
    <div className="rounded-2xl border border-emerald-500/20 bg-[#0a0a0a] overflow-hidden shadow-[0_0_20px_rgba(16,185,129,0.08)]">
      {/* Toggle Header */}
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-3 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-emerald-400" />
          <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-widest">Agentic Telemetry</span>
          {data.workflow_stage && (
            <span className="px-2 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/25 text-[9px] font-bold text-emerald-300 uppercase tracking-wider">
              {data.workflow_stage}
            </span>
          )}
        </div>
        {open ? <ChevronDown className="w-4 h-4 text-emerald-400" /> : <ChevronUp className="w-4 h-4 text-emerald-400" />}
      </button>

      {/* Absolute grid background */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 grid grid-cols-1 sm:grid-cols-2 gap-4 border-t border-emerald-500/10">
              {/* Left column */}
              <div className="space-y-4 pt-4">
                {/* Intent */}
                {data.intent && (
                  <div className="flex items-start gap-3">
                    <Brain className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                    <div>
                      <p className="text-[9px] font-bold uppercase tracking-widest text-white/40 mb-0.5">Intent Classification</p>
                      <p className="text-sm font-bold text-white/90 font-mono">{data.intent}</p>
                    </div>
                  </div>
                )}

                {/* Confidence */}
                {data.confidence !== undefined && (
                  <div className="flex items-start gap-3">
                    <Target className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                    <div className="flex-1">
                      <p className="text-[9px] font-bold uppercase tracking-widest text-white/40 mb-2">Confidence</p>
                      <ConfidenceBar value={data.confidence} label="Intent Confidence" />
                    </div>
                  </div>
                )}

                {/* Risk Score */}
                {data.risk_score !== undefined && (
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
                    <div className="flex-1">
                      <p className="text-[9px] font-bold uppercase tracking-widest text-white/40 mb-2">Risk Score</p>
                      <ConfidenceBar value={data.risk_score} label="Risk" />
                    </div>
                  </div>
                )}

                {/* Latency + Tokens */}
                <div className="flex gap-4">
                  {data.latency_ms !== undefined && (
                    <div>
                      <p className="text-[9px] font-bold uppercase tracking-widest text-white/40">Latency</p>
                      <p className="text-sm font-bold text-white/80 font-mono">{data.latency_ms}ms</p>
                    </div>
                  )}
                  {data.tokens_used !== undefined && (
                    <div>
                      <p className="text-[9px] font-bold uppercase tracking-widest text-white/40">Tokens</p>
                      <p className="text-sm font-bold text-white/80 font-mono">{data.tokens_used}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Right column */}
              <div className="space-y-4 pt-4">
                {/* Slots */}
                {data.slots && Object.keys(data.slots).length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <GitBranch className="w-4 h-4 text-emerald-400" />
                      <p className="text-[9px] font-bold uppercase tracking-widest text-white/40">Slot Extraction</p>
                    </div>
                    <div className="space-y-1.5">
                      {Object.entries(data.slots).map(([k, v]) => (
                        <div key={k} className="flex items-center justify-between text-[11px] font-mono">
                          <span className="text-white/40">{k}</span>
                          <span className="text-emerald-300 font-bold">{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Rule Trace */}
                {data.rule_trace && data.rule_trace.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Shield className="w-4 h-4 text-emerald-400" />
                      <p className="text-[9px] font-bold uppercase tracking-widest text-white/40">Rule Evaluation</p>
                    </div>
                    <div className="space-y-1.5">
                      {data.rule_trace.map((r, i) => (
                        <div key={i} className="flex items-center justify-between gap-2">
                          <span className="text-[11px] text-white/60 font-mono truncate flex-1">{r.rule}</span>
                          <Badge pass={r.pass} />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
