'use client';

import React, { useState } from 'react';
import type { BenefitReceipt as BenefitReceiptType } from '@/services/api';

interface BenefitReceiptProps {
    receipt: BenefitReceiptType;
    confidence?: number;
    turnId?: string;
    sessionId?: string;
    onApply?: () => void;
    onAskAgain?: () => void;
    isApplying?: boolean;
}

export default function BenefitReceipt({
    receipt,
    confidence,
    turnId: _turnId,
    sessionId: _sessionId,
    onApply,
    onAskAgain,
    isApplying = false,
}: BenefitReceiptProps) {
    const [downloading, setDownloading] = useState(false);

    const handleDownloadPDF = () => {
        setDownloading(true);
        // Use browser print dialog for PDF download
        window.print();
        setTimeout(() => setDownloading(false), 1000);
    };

    const confidenceLabel = confidence !== undefined
        ? confidence >= 0.8 ? 'High' : confidence >= 0.5 ? 'Medium' : 'Low'
        : null;

    const confidenceColor = confidence !== undefined
        ? confidence >= 0.8
            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
            : confidence >= 0.5
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                : 'bg-red-500/20 text-red-300 border-red-500/40'
        : '';

    return (
        <div className="benefit-receipt mt-3 rounded-2xl border border-white/10 bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-sm overflow-hidden shadow-xl">
            {/* Header */}
            <div className={`px-4 py-3 flex items-center justify-between ${receipt.eligible
                ? 'bg-emerald-500/10 border-b border-emerald-500/20'
                : 'bg-red-500/10 border-b border-red-500/20'}`}>
                <div className="flex items-center gap-2">
                    <span className="text-xl">{receipt.eligible ? '✅' : '❌'}</span>
                    <div>
                        <p className="text-sm font-bold text-white">
                            {receipt.eligible ? 'Eligible for this Scheme' : 'Not Currently Eligible'}
                        </p>
                        <p className="text-xs text-white/50">Benefit Receipt</p>
                    </div>
                </div>
                {confidenceLabel && (
                    <span className={`text-xs font-semibold px-2 py-1 rounded-full border ${confidenceColor}`}>
                        {confidenceLabel} Confidence
                    </span>
                )}
            </div>

            {/* Rules */}
            {receipt.rules.length > 0 && (
                <div className="px-4 py-3 border-b border-white/5">
                    <p className="text-xs font-semibold text-white/40 uppercase tracking-wider mb-2">
                        Eligibility Rules
                    </p>
                    <ul className="space-y-1">
                        {receipt.rules.map((rule, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-white/75">
                                <span className="mt-0.5 text-blue-400 shrink-0">›</span>
                                <span>{rule}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Sources */}
            {receipt.sources.length > 0 && (
                <div className="px-4 py-3 border-b border-white/5">
                    <p className="text-xs font-semibold text-white/40 uppercase tracking-wider mb-2">
                        Sources
                    </p>
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

            {/* Actions */}
            <div className="px-4 py-3 flex flex-wrap gap-2">
                {receipt.eligible && onApply && (
                    <button
                        onClick={onApply}
                        disabled={isApplying}
                        className="flex-1 min-w-[100px] py-2 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 active:scale-95 disabled:opacity-60 text-white text-sm font-semibold transition-all shadow-lg shadow-blue-600/25"
                    >
                        {isApplying ? (
                            <span className="flex items-center justify-center gap-2">
                                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                                </svg>
                                Applying…
                            </span>
                        ) : 'Apply Now'}
                    </button>
                )}
                {onAskAgain && (
                    <button
                        onClick={onAskAgain}
                        className="py-2 px-4 rounded-xl bg-white/5 hover:bg-white/10 active:scale-95 text-white/70 hover:text-white text-sm font-medium transition-all border border-white/10"
                    >
                        Ask Again
                    </button>
                )}
                <button
                    onClick={handleDownloadPDF}
                    disabled={downloading}
                    className="py-2 px-4 rounded-xl bg-white/5 hover:bg-white/10 active:scale-95 text-white/70 hover:text-white text-sm font-medium transition-all border border-white/10"
                >
                    {downloading ? 'Preparing…' : '📥 Download PDF'}
                </button>
            </div>
        </div>
    );
}
