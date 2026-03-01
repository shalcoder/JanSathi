import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const STEPS = [
    { id: 'parse', label: 'Parsing Natural Language Intent...', icon: '🧠' },
    { id: 'rag', label: 'Consulting Kendra Knowledge Base...', icon: '📚' },
    { id: 'check', label: 'Verifying Eligibility Rules...', icon: '✅' },
    { id: 'format', label: 'Structuring Multilingual Response...', icon: '🌐' }
];

export default function MultiAgentThoughtProcess({ onComplete }: { onComplete?: () => void }) {
    const [currentStep, setCurrentStep] = useState(0);

    useEffect(() => {
        let step = 0;
        const interval = setInterval(() => {
            if (step < STEPS.length - 1) {
                step++;
                setCurrentStep(step);
            } else {
                clearInterval(interval);
                if (onComplete) onComplete();
            }
        }, 1200); // 1.2s per step

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bg-black/20 backdrop-blur-md rounded-xl p-3 border border-white/10 w-full max-w-sm mb-4">
            <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse" />
                <span className="text-xs font-bold text-indigo-300 uppercase tracking-widest">Agent Orchestration</span>
            </div>

            <div className="space-y-3 relative">
                {/* Connection Line */}
                <div className="absolute left-[11px] top-2 bottom-4 w-0.5 bg-white/5 -z-10" />

                {STEPS.map((step, index) => {
                    const isActive = index === currentStep;
                    const isCompleted = index < currentStep;

                    return (
                        <motion.div
                            key={step.id}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: isActive || isCompleted ? 1 : 0.3, x: 0 }}
                            className="flex items-center gap-3"
                        >
                            <div className={`
                w-6 h-6 rounded-full flex items-center justify-center text-xs border z-10 
                ${isActive ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300 animate-pulse scale-110' :
                                    isCompleted ? 'bg-green-500/20 border-green-500 text-green-300' :
                                        'bg-slate-800 border-slate-700 text-slate-500'}
                transition-all duration-300
              `}>
                                {isCompleted ? '✓' : step.icon}
                            </div>

                            <span className={`text-xs font-medium transition-colors duration-300 ${isActive ? 'text-white' : isCompleted ? 'text-slate-400' : 'text-slate-600'}`}>
                                {step.label}
                            </span>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}
