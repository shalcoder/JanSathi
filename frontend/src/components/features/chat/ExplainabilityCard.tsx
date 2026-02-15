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
            className="p-4 rounded-2xl bg-secondary/30 border border-border/50 backdrop-blur-md space-y-4 max-w-sm mt-4"
        >
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-accent/20 text-accent">
                        <Target className="w-4 h-4" />
                    </div>
                    <span className="text-sm font-bold text-foreground">AI Match Audit</span>
                </div>
                <div className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider ${confidenceColor}`}>
                    {Math.round(confidence * 100)}% Match
                </div>
            </div>

            <div className="space-y-2">
                <div className="text-[11px] text-muted-foreground flex items-center gap-1.5 font-bold uppercase tracking-wider">
                    <Info className="w-3 h-3" />
                    Why am I eligible?
                </div>
                <div className="space-y-1.5">
                    {criteria.map((item, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-xs text-foreground/80 font-medium">
                            <ShieldCheck className="w-3 h-3 mt-0.5 text-success/70" />
                            {item}
                        </div>
                    ))}
                </div>
            </div>

            <div className="pt-2 border-t border-border/20 flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground font-bold">
                    <Cpu className="w-3 h-3" />
                    <span>{protocol}</span>
                </div>
                <span className="text-[10px] text-accent/70 font-black uppercase tracking-widest">SageMaker Clarify 🛡️</span>
            </div>
        </motion.div>
    );
};

export default ExplainabilityCard;
