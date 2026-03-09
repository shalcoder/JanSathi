'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, Download, Send, RefreshCw, Banknote, ShieldCheck, ChevronDown, ChevronUp } from 'lucide-react';
import type { BenefitReceipt as BenefitReceiptType } from '@/services/api';

interface BenefitReceiptProps {
    receipt: BenefitReceiptType;
    confidence?: number;
    schemeName?: string;
    turnId?: string;
    sessionId?: string;
    onApply?: () => void;
    onAskAgain?: () => void;
    isApplying?: boolean;
}

// Scheme metadata — amounts, icons, types
const SCHEME_META: Record<string, { amount: string; icon: string; type: string }> = {
    pm_kisan:        { amount: '₹6,000 / year', icon: '🌾', type: 'Direct Bank Transfer' },
    'pm-kisan':      { amount: '₹6,000 / year', icon: '🌾', type: 'Direct Bank Transfer' },
    pmkisan:         { amount: '₹6,000 / year', icon: '🌾', type: 'Direct Bank Transfer' },
    ayushman_bharat: { amount: '₹5 Lakh / year', icon: '🏥', type: 'Health Insurance' },
    pmjay:           { amount: '₹5 Lakh / year', icon: '🏥', type: 'Health Insurance' },
    pm_awas:         { amount: 'Up to ₹2.67 Lakh', icon: '🏠', type: 'Housing Subsidy' },
    pmaymis:         { amount: 'Up to ₹2.67 Lakh', icon: '🏠', type: 'Housing Subsidy' },
    e_shram:         { amount: '₹2 Lakh Insurance', icon: '👷', type: 'Worker Protection' },
    ujjwala:         { amount: 'Free LPG Connection', icon: '🍳', type: 'Direct Benefit' },
    default:         { amount: 'Variable Benefit', icon: '🇮🇳', type: 'Government Scheme' },
};

function getMeta(schemeName?: string) {
    if (!schemeName) return SCHEME_META.default;
    const key = schemeName.toLowerCase().replace(/[\s-]/g, '_');
    return SCHEME_META[key] || SCHEME_META[schemeName.toLowerCase()] || SCHEME_META.default;
}

export default function BenefitReceipt({
    receipt,
    confidence,
    schemeName,
    turnId: _turnId,
    sessionId: _sessionId,
    onApply,
    onAskAgain,
    isApplying = false,
}: BenefitReceiptProps) {
    const [downloading, setDownloading] = useState(false);
    const [showRules, setShowRules] = useState(false);

    const meta = getMeta(schemeName);
    const confidencePct = confidence !== undefined ? Math.round(confidence * 100) : null;
    const confidenceColor = confidencePct !== null
        ? confidencePct >= 80 ? 'bg-emerald-500'
        : confidencePct >= 50 ? 'bg-amber-500'
        : 'bg-red-500'
        : 'bg-slate-500';

    const handleDownloadPDF = () => {
        setDownloading(true);
        window.print();
        setTimeout(() => setDownloading(false), 1000);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="benefit-receipt mt-3 rounded-2xl border overflow-hidden shadow-xl"
            style={{ borderColor: receipt.eligible ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)' }}
        >
            {/* ── Header ── */}
            <div className={`px-5 py-4 flex items-start justify-between gap-3 ${receipt.eligible ? 'bg-emerald-500/10' : 'bg-red-500/10'}`}>
                <div className="flex items-start gap-3">
                    <span className="text-3xl leading-none mt-0.5">{meta.icon}</span>
                    <div>
                        <p className="font-bold text-white text-base leading-snug">
                            {schemeName || 'Government Scheme'}
                        </p>
                        <p className="text-xs text-white/60 mt-0.5">{meta.type}</p>
                        {receipt.eligible && (
                            <div className="flex items-center gap-1.5 mt-1.5">
                                <Banknote className="w-3.5 h-3.5 text-emerald-400" />
                                <span className="text-sm font-bold text-emerald-300">{meta.amount}</span>
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex flex-col items-end gap-1.5 shrink-0">
                    {receipt.eligible ? (
                        <span className="flex items-center gap-1.5 text-sm font-bold text-emerald-400">
                            <CheckCircle2 className="w-5 h-5" /> Eligible
                        </span>
                    ) : (
                        <span className="flex items-center gap-1.5 text-sm font-bold text-red-400">
                            <XCircle className="w-5 h-5" /> Not Eligible
                        </span>
                    )}
                    {receipt.eligible && (
                        <div className="flex items-center gap-1 text-[10px] text-white/60 font-bold uppercase tracking-wider">
                            <ShieldCheck className="w-3 h-3 text-blue-400" /> Direct Transfer
                        </div>
                    )}
                </div>
            </div>

            {/* ── Eligibility score bar ── */}
            {confidencePct !== null && (
                <div className="px-5 py-3 border-b border-white/5 bg-slate-900/40">
                    <div className="flex justify-between text-[10px] font-bold uppercase tracking-wider mb-1.5">
                        <span className="text-white/50">Eligibility Confidence</span>
                        <span className={confidencePct >= 80 ? 'text-emerald-400' : confidencePct >= 50 ? 'text-amber-400' : 'text-red-400'}>
                            {confidencePct}%
                        </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-white/10 overflow-hidden">
                        <motion.div
                            className={`h-full rounded-full ${confidenceColor}`}
                            initial={{ width: 0 }}
                            animate={{ width: `${confidencePct}%` }}
                            transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
                        />
                    </div>
                </div>
            )}

            {/* ── Rules (collapsible) ── */}
            {receipt.rules.length > 0 && (
                <div className="border-b border-white/5">
                    <button
                        onClick={() => setShowRules(v => !v)}
                        className="w-full px-5 py-3 flex items-center justify-between text-xs font-semibold text-white/50 uppercase tracking-wider hover:text-white/70 transition-colors"
                    >
                        <span>Eligibility Rules ({receipt.rules.length})</span>
                        {showRules ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                    {showRules && (
                        <motion.ul
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            className="px-5 pb-3 space-y-1.5 overflow-hidden"
                        >
                            {receipt.rules.map((rule, i) => (
                                <li key={i} className="flex items-start gap-2 text-sm text-white/75">
                                    <span className="mt-1 shrink-0 text-blue-400">›</span>
                                    <span>{rule}</span>
                                </li>
                            ))}
                        </motion.ul>
                    )}
                </div>
            )}

            {/* ── Sources ── */}
            {receipt.sources.length > 0 && (
                <div className="px-5 py-3 border-b border-white/5">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-white/40 mb-2">Verified Sources</p>
                    <div className="flex flex-wrap gap-2">
                        {receipt.sources.map((src, i) => (
                            <a
                                key={i}
                                href={src.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 hover:underline transition-colors"
                            >
                                📄 {src.title}{src.page ? ` (p.${src.page})` : ''}
                            </a>
                        ))}
                    </div>
                </div>
            )}

            {/* ── Actions ── */}
            <div className="px-5 py-4 flex flex-wrap gap-2 bg-slate-900/20">
                {receipt.eligible && onApply && (
                    <button
                        onClick={onApply}
                        disabled={isApplying}
                        className="flex-1 min-w-[120px] py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 active:scale-95 disabled:opacity-60 text-white text-sm font-bold transition-all shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-2"
                    >
                        {isApplying ? (
                            <>
                                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                                </svg>
                                Submitting…
                            </>
                        ) : (
                            <>
                                <Send className="w-4 h-4" /> Apply Now
                            </>
                        )}
                    </button>
                )}
                {onAskAgain && (
                    <button
                        onClick={onAskAgain}
                        className="py-2.5 px-4 rounded-xl bg-white/5 hover:bg-white/10 active:scale-95 text-white/70 hover:text-white text-sm font-medium transition-all border border-white/10 flex items-center gap-1.5"
                    >
                        <RefreshCw className="w-3.5 h-3.5" /> Ask Again
                    </button>
                )}
                <button
                    onClick={handleDownloadPDF}
                    disabled={downloading}
                    className="py-2.5 px-4 rounded-xl bg-white/5 hover:bg-white/10 active:scale-95 text-white/70 hover:text-white text-sm font-medium transition-all border border-white/10 flex items-center gap-1.5"
                >
                    <Download className="w-3.5 h-3.5" />
                    {downloading ? 'Preparing…' : 'Download PDF'}
                </button>
            </div>
        </motion.div>
    );
}
