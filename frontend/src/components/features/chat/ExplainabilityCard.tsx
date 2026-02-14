'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Target, ShieldCheck, Cpu, Info } from 'lucide-react';

interface ExplainabilityProps {
    confidence: number;
    criteria: string[];
    protocol: string;
}

const ExplainabilityCard: React.FC<ExplainabilityProps> = ({ confidence, criteria, protocol }) => {
    const isHighConfidence = confidence >= 0.8;
    const isMediumConfidence = confidence >= 0.5 && confidence < 0.8;

    const confidenceColor = isHighConfidence
        ? 'text-green-400 bg-green-400/10'
        : isMediumConfidence
            ? 'text-yellow-400 bg-yellow-400/10'
            : 'text-red-400 bg-red-400/10';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md space-y-4 max-w-sm mt-4"
        >
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400">
                        <Target className="w-4 h-4" />
                    </div>
                    <span className="text-sm font-medium text-white/90">AI Match Audit</span>
                </div>
                <div className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${confidenceColor}`}>
                    {Math.round(confidence * 100)}% Match
                </div>
            </div>

            <div className="space-y-2">
                <div className="text-[11px] text-white/50 flex items-center gap-1.5">
                    <Info className="w-3 h-3" />
                    Why am I eligible?
                </div>
                <div className="space-y-1.5">
                    {criteria.map((item, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-xs text-white/80">
                            <ShieldCheck className="w-3 h-3 mt-0.5 text-green-500/70" />
                            {item}
                        </div>
                    ))}
                </div>
            </div>

            <div className="pt-2 border-t border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-[10px] text-white/40">
                    <Cpu className="w-3 h-3" />
                    <span>{protocol}</span>
                </div>
                <span className="text-[10px] text-indigo-400/70 font-medium">SageMaker Clarify 🛡️</span>
            </div>
        </motion.div>
    );
};

export default ExplainabilityCard;
