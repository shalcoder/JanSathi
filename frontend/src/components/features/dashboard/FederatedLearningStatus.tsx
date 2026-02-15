import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function FederatedLearningStatus() {
    const [isTraining, setIsTraining] = useState(false);
    const [progress, setProgress] = useState(0);
    const [round, setRound] = useState(1);
    const [privacyBudget, setPrivacyBudget] = useState(100);
    const [lastContribution, setLastContribution] = useState<string | null>(null);

    // Simulate Federated Learning Cycle
    useEffect(() => {
        const cycle = setInterval(() => {
            startTrainingRound();
        }, 15000); // New round every 15 seconds

        return () => clearInterval(cycle);
    }, []);

    const startTrainingRound = () => {
        setIsTraining(true);
        setProgress(0);

        // Simulate training progress
        let p = 0;
        const interval = setInterval(() => {
            p += Math.random() * 20;
            if (p >= 100) {
                clearInterval(interval);
                finishRound();
            } else {
                setProgress(p);
            }
        }, 500);
    };

    const finishRound = () => {
        setIsTraining(false);
        setProgress(100);
        setRound(prev => prev + 1);
        setPrivacyBudget(prev => Math.max(0, prev - 0.5)); // Consumpte privacy budget
        setLastContribution(new Date().toLocaleTimeString());
    };

    return (
        <div className="bg-gradient-to-br from-slate-900 to-slate-950 rounded-xl border border-white/10 p-4 shadow-xl overflow-hidden relative group">
            {/* Background Pulse Effect */}
            <div className={`absolute inset-0 bg-blue-500/5 transition-opacity duration-1000 ${isTraining ? 'opacity-100' : 'opacity-0'}`} />

            <div className="flex items-center justify-between mb-4 relative z-10">
                <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${isTraining ? 'bg-green-400 animate-pulse' : 'bg-slate-500'}`} />
                    <h3 className="font-bold text-white text-sm tracking-wide">FEDERATED LEARNING NODE</h3>
                </div>
                <span className="text-[10px] font-mono text-slate-400 border border-white/10 px-2 py-1 rounded bg-black/20">
                    ROUND #{round}
                </span>
            </div>

            <div className="space-y-4 relative z-10">
                {/* Status Display */}
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
                        <span className="text-2xl animate-spin-slow">{isTraining ? '🔄' : '🌸'}</span>
                    </div>
                    <div>
                        <div className="text-slate-300 text-xs font-medium">Current Status</div>
                        <div className={`font-bold ${isTraining ? 'text-blue-400' : 'text-slate-400'}`}>
                            {isTraining ? 'Training Local Model...' : 'Waiting for Global Aggregation'}
                        </div>
                    </div>
                </div>

                {/* Progress Bar (Only visible when training) */}
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                    <motion.div
                        className="h-full bg-gradient-to-r from-blue-500 to-indigo-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${isTraining ? progress : 0}%` }}
                        transition={{ duration: 0.5 }}
                    />
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 gap-2 mt-2">
                    <div className="bg-white/5 rounded-lg p-2 border border-white/5">
                        <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Privacy Budget (ε)</div>
                        <div className="text-white font-mono font-bold">{privacyBudget.toFixed(1)}%</div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-2 border border-white/5">
                        <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Last Sync</div>
                        <div className="text-white font-mono font-bold text-xs">{lastContribution || 'Pending...'}</div>
                    </div>
                </div>

                {/* Technical Label */}
                <div className="flex items-center gap-1.5 justify-center mt-2 opacity-50 hover:opacity-100 transition-opacity cursor-help" title="Using Flower Framework for decentralized training">
                    <span className="text-[10px] text-slate-500">Powered by</span>
                    <span className="text-[10px] font-bold text-slate-400 bg-white/5 px-1.5 py-0.5 rounded border border-white/5">Flower 🌸</span>
                </div>
            </div>
        </div>
    );
}
