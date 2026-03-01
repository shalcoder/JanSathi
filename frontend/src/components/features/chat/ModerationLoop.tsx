'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, Check, X, UserCheck, AlertTriangle, Scale } from 'lucide-react';

const ModerationLoop = () => {
    const [flaggedItems, setFlaggedItems] = useState([
        { id: 1, user: 'User_4921', query: 'PM Kisan amount wrong?', flag: 'Factual Accuracy', confidence: 0.42 },
        { id: 2, user: 'User_8812', query: 'How to bypass OTP?', flag: 'Security Policy', confidence: 0.15 },
    ]);

    const resolveItem = (id: number, approved: boolean) => {
        setFlaggedItems(prev => prev.filter(item => item.id !== id));
    };

    return (
        <div className="bg-white/5 border border-white/10 rounded-3xl p-8 h-full">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-bold flex items-center gap-2">
                    <Scale className="w-5 h-5 text-orange-400" />
                    Community Moderation Loop
                </h3>
                <span className="text-[10px] bg-orange-500/10 text-orange-400 px-2 py-1 rounded-full border border-orange-500/20 font-bold uppercase tracking-widest">
                    {flaggedItems.length} Pending Actions
                </span>
            </div>

            <div className="space-y-4">
                <AnimatePresence>
                    {flaggedItems.map((item) => (
                        <motion.div
                            key={item.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all group lg:flex lg:items-center lg:justify-between gap-4"
                        >
                            <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                    <ShieldAlert className="w-3 h-3 text-red-400" />
                                    <span className="text-[10px] font-bold text-white/40 uppercase tracking-tighter">{item.flag}</span>
                                    <span className="text-[10px] font-black text-red-400">{(100 - (item.confidence * 100)).toFixed(0)}% Risk</span>
                                </div>
                                <p className="text-xs font-medium text-white/80 italic">&quot;{item.query}&quot;</p>
                                <p className="text-[10px] text-white/20 font-bold uppercase tracking-widest">Citizen: {item.user}</p>
                            </div>

                            <div className="flex gap-2 mt-4 lg:mt-0">
                                <button
                                    onClick={() => resolveItem(item.id, true)}
                                    className="flex-1 lg:flex-none p-2 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition-colors border border-emerald-500/20"
                                    title="Approve Fact Change"
                                >
                                    <Check className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={() => resolveItem(item.id, false)}
                                    className="flex-1 lg:flex-none p-2 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors border border-red-500/20"
                                    title="Reject False Claim"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {flaggedItems.length === 0 && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="py-12 text-center"
                    >
                        <UserCheck className="w-12 h-12 text-white/5 mx-auto mb-4" />
                        <p className="text-xs font-bold text-white/20 uppercase tracking-widest">Consensus Achieved</p>
                    </motion.div>
                )}
            </div>

            <div className="mt-6 pt-6 border-t border-white/5 flex items-center gap-2 text-white/30">
                <AlertTriangle className="w-3 h-3" />
                <span className="text-[9px] font-medium leading-tight">Approved changes are live-synced to Kendra via incremental sync.</span>
            </div>
        </div>
    );
};

export default ModerationLoop;
