'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, AlertCircle, ShieldCheck, FileCheck, Info } from 'lucide-react';

interface ScorecardProps {
    scores: {
        accuracy: number;
        integrity: number;
        eligibility: number;
    };
    docType: string;
    vulnerabilities?: string[];
}

export default function DocumentScorecard({ scores, docType, vulnerabilities = [] }: ScorecardProps) {
    const getGrade = (score: number) => {
        if (score > 85) return { label: 'Excellent', color: 'text-emerald-500', bg: 'bg-emerald-500/10' };
        if (score > 60) return { label: 'Good', color: 'text-blue-500', bg: 'bg-blue-500/10' };
        return { label: 'Needs Clarity', color: 'text-orange-500', bg: 'bg-orange-500/10' };
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-6 bg-card border border-border/50 rounded-3xl shadow-2xl space-y-6"
        >
            <div className="flex items-center justify-between border-b border-border/10 pb-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-primary/10">
                        <FileCheck className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                        <h4 className="font-bold text-foreground">Kagaz Auditor Pro</h4>
                        <p className="text-[10px] text-secondary-foreground opacity-50 uppercase tracking-widest font-black">{docType}</p>
                    </div>
                </div>
                <div className="flex items-center gap-2 px-3 py-1 bg-emerald-500/10 rounded-full border border-emerald-500/20">
                    <ShieldCheck className="w-3 h-3 text-emerald-500" />
                    <span className="text-[9px] font-bold text-emerald-500 uppercase tracking-tighter">Verified Integrity</span>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
                {[
                    { label: 'Accuracy', val: scores.accuracy },
                    { label: 'Integrity', val: scores.integrity },
                    { label: 'Eligibility', val: scores.eligibility },
                ].map((s, idx) => {
                    const grade = getGrade(s.val);
                    return (
                        <div key={idx} className="space-y-2 text-center">
                            <p className="text-[10px] font-bold text-secondary-foreground opacity-40 uppercase">{s.label}</p>
                            <div className={`p-3 rounded-2xl ${grade.bg} animate-pulse-slow`}>
                                <span className={`text-xl font-black ${grade.color}`}>{s.val}%</span>
                            </div>
                        </div>
                    );
                })}
            </div>

            {vulnerabilities.length > 0 && (
                <div className="p-4 rounded-2xl bg-orange-500/5 border border-orange-500/10 space-y-2">
                    <div className="flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-orange-500" />
                        <span className="text-[10px] font-bold text-orange-600 uppercase">Attention Required</span>
                    </div>
                    {vulnerabilities.map((v, i) => (
                        <p key={i} className="text-xs text-orange-600/80 font-medium tracking-tight">• {v}</p>
                    ))}
                </div>
            )}

            <div className="flex items-center justify-between pt-2">
                <div className="flex items-center gap-1.5 opacity-60">
                    <Info className="w-3 h-3" />
                    <span className="text-[9px] font-medium">Sovereign Bharat Cloud Nodes</span>
                </div>
                <button className="px-4 py-1.5 bg-primary/10 hover:bg-primary/20 text-primary text-[10px] font-bold rounded-lg transition-colors border border-primary/20">
                    Secure AI Audit Report
                </button>
            </div>
        </motion.div>
    );
}
