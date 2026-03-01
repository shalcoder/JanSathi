'use client';

import React, { useState } from 'react';
import type { UnifiedQueryResponse } from '@/services/api';

interface TelemetryPanelProps {
    debug?: UnifiedQueryResponse['debug'];
    confidence?: number;
}

export default function TelemetryPanel({ debug, confidence }: TelemetryPanelProps) {
    const [isOpen, setIsOpen] = useState(false);

    if (!debug && confidence === undefined) return null;

    return (
        <div className="mt-2 text-xs">
            <button
                onClick={() => setIsOpen(v => !v)}
                className="flex items-center gap-1.5 text-white/30 hover:text-white/60 transition-colors"
            >
                <span className={`transition-transform ${isOpen ? 'rotate-90' : ''}`}>›</span>
                <span className="font-mono uppercase tracking-widest text-[10px]">Telemetry</span>
            </button>

            {isOpen && (
                <div className="mt-2 rounded-xl border border-white/5 bg-black/30 p-3 space-y-3">
                    {/* Metrics Grid */}
                    <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                        {debug?.model && (
                            <Metric label="Model" value={debug.model} />
                        )}
                        {debug?.latency_ms !== undefined && (
                            <Metric label="Latency" value={`${debug.latency_ms} ms`} />
                        )}
                        {confidence !== undefined && (
                            <Metric
                                label="Confidence"
                                value={`${(confidence * 100).toFixed(0)}%`}
                                color={
                                    confidence >= 0.8
                                        ? 'text-emerald-400'
                                        : confidence >= 0.5
                                            ? 'text-amber-400'
                                            : 'text-red-400'
                                }
                            />
                        )}
                        {debug?.asr_confidence !== undefined && (
                            <Metric
                                label="ASR Conf"
                                value={`${(debug.asr_confidence * 100).toFixed(0)}%`}
                            />
                        )}
                        {debug?.cache_hit !== undefined && (
                            <Metric
                                label="Cache"
                                value={debug.cache_hit ? 'HIT' : 'MISS'}
                                color={debug.cache_hit ? 'text-emerald-400' : 'text-slate-400'}
                            />
                        )}
                        {debug?.token_count !== undefined && (
                            <Metric label="Tokens" value={String(debug.token_count)} />
                        )}
                    </div>

                    {/* Token usage mini-bar */}
                    {debug?.token_count !== undefined && (
                        <div>
                            <div className="flex justify-between text-[10px] text-white/30 mb-1">
                                <span>Token Usage</span>
                                <span>{debug.token_count} / 4096</span>
                            </div>
                            <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
                                <div
                                    className="h-full rounded-full bg-blue-500/60 transition-all duration-500"
                                    style={{ width: `${Math.min((debug.token_count / 4096) * 100, 100)}%` }}
                                />
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

function Metric({ label, value, color }: { label: string; value: string; color?: string }) {
    return (
        <div className="flex flex-col gap-0.5">
            <span className="text-[10px] text-white/30 uppercase tracking-wider">{label}</span>
            <span className={`font-mono font-medium ${color ?? 'text-white/70'}`}>{value}</span>
        </div>
    );
}
