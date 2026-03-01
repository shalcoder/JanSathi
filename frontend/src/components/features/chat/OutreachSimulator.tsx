'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Phone, MessageSquare, Send, CheckCircle2, Loader2, Signal } from 'lucide-react';

const OutreachSimulator = () => {
    const [activeSim, setActiveSim] = useState<'none' | 'ivr' | 'whatsapp'>('none');
    const [status, setStatus] = useState<'idle' | 'calling' | 'texting' | 'completed'>('idle');

    const simulateIVR = () => {
        setActiveSim('ivr');
        setStatus('calling');
        setTimeout(() => setStatus('completed'), 3000);
    };

    const simulateWhatsApp = () => {
        setActiveSim('whatsapp');
        setStatus('texting');
        setTimeout(() => setStatus('completed'), 2000);
    };

    return (
        <div className="bg-white/5 border border-white/10 rounded-3xl p-8 relative overflow-hidden">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-bold flex items-center gap-2">
                    <Signal className="w-5 h-5 text-emerald-400" />
                    Outreach Channels (Cloud Connect)
                </h3>
                <div className="flex gap-2">
                    <button
                        onClick={simulateIVR}
                        className="px-4 py-2 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 rounded-xl text-xs font-bold transition-all border border-indigo-500/20 flex items-center gap-2"
                    >
                        <Phone className="w-3 h-3" /> Call IVR
                    </button>
                    <button
                        onClick={simulateWhatsApp}
                        className="px-4 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 rounded-xl text-xs font-bold transition-all border border-emerald-500/20 flex items-center gap-2"
                    >
                        <MessageSquare className="w-3 h-3" /> WhatsApp
                    </button>
                </div>
            </div>

            <div className="min-h-[160px] flex items-center justify-center border-2 border-dashed border-white/5 rounded-2xl bg-black/20">
                <AnimatePresence mode="wait">
                    {status === 'idle' && (
                        <motion.div
                            key="idle"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="text-white/20 text-xs font-black uppercase tracking-[0.2em]"
                        >
                            Standby • Waiting for Event
                        </motion.div>
                    )}

                    {(status === 'calling' || status === 'texting') && (
                        <motion.div
                            key="processing"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="flex flex-col items-center gap-4"
                        >
                            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
                            <p className="text-xs font-bold text-white/50 animate-pulse">
                                {activeSim === 'ivr' ? 'ESTABLISHING VOICE TUNNEL...' : 'SYNCHRONIZING WHATSAPP NODE...'}
                            </p>
                        </motion.div>
                    )}

                    {status === 'completed' && (
                        <motion.div
                            key="done"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-center space-y-3"
                        >
                            <div className="mx-auto w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">
                                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                            </div>
                            <div>
                                <h4 className="font-bold text-sm">Outreach Successful</h4>
                                <p className="text-[10px] text-white/40">Packet delivered via {activeSim?.toUpperCase()} Gateway</p>
                            </div>
                            <button
                                onClick={() => setStatus('idle')}
                                className="text-[10px] font-bold text-indigo-400 hover:underline"
                            >
                                Reset Simulator
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Background Glow */}
            <div className={`absolute -bottom-20 -right-20 w-64 h-64 blur-[100px] pointer-events-none transition-colors duration-1000 ${activeSim === 'ivr' ? 'bg-indigo-500/20' : activeSim === 'whatsapp' ? 'bg-emerald-500/20' : 'bg-transparent'
                }`} />
        </div>
    );
};

export default OutreachSimulator;
