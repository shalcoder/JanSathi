'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, Server, Database, Cpu, ShieldCheck, Globe } from 'lucide-react';

const TelemetryPanel = () => {
    const [latency, setLatency] = useState(240);
    const [accuracy, setAccuracy] = useState(98.2);

    useEffect(() => {
        const interval = setInterval(() => {
            setLatency(prev => 200 + Math.floor(Math.random() * 80));
            setAccuracy(prev => 97 + Math.random() * 2.5);
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="hidden xl:flex w-[24rem] flex-col gap-8 p-8 bg-background border-l border-border overflow-y-auto transition-all duration-500 shadow-premium relative">

            {/* Variety 1: Ambient Orb Background */}
            <div className="absolute top-1/4 right-0 w-32 h-32 bg-primary/20 rounded-full blur-[80px] opacity-20 animate-pulse-slow"></div>

            {/* Header Status - Variety: Neumorphic Indicator */}
            <div className="flex items-center justify-between mb-2">
                <div className="flex flex-col">
                    <h2 className="text-[10px] font-black text-secondary-foreground uppercase tracking-[0.4em] opacity-40 mb-1">Compute Cluster</h2>
                    <span className="text-[13px] font-black text-foreground tracking-tighter">BHARAT-AP-S1</span>
                </div>
                <div className="neumorphic-outer p-1 rounded-full px-4 flex items-center gap-2 border border-white/40 dark:border-white/5">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                    <span className="text-[9px] font-black text-emerald-600 dark:text-emerald-400 tracking-widest leading-none">PEAK LOGIC</span>
                </div>
            </div>

            {/* Performance Matrix - Variety: Bento Grid Style */}
            <div className="grid grid-cols-2 gap-4">
                <motion.div
                    whileHover={{ scale: 1.02 }}
                    className="p-5 rounded-[2rem] glass-panel border border-border/50 flex flex-col justify-between h-40 group relative overflow-hidden"
                >
                    <div className="absolute -top-2 -right-2 p-4 opacity-5 group-hover:opacity-20 transition-all group-hover:rotate-12">
                        <Activity className="w-12 h-12" />
                    </div>
                    <span className="text-[9px] font-black text-secondary-foreground uppercase tracking-[0.2em] opacity-60">Latency</span>
                    <div className="flex items-baseline gap-1.5">
                        <span className="text-3xl font-black text-foreground tracking-tighter">{latency}</span>
                        <span className="text-[10px] font-black text-primary uppercase tracking-widest">ms</span>
                    </div>
                    <div className="flex gap-1 h-8 items-end">
                        {[30, 60, 45, 80, 55, 95].map((h, i) => (
                            <div key={i} className="flex-1 bg-primary/10 rounded-t-sm relative h-full">
                                <motion.div
                                    initial={{ height: 0 }}
                                    animate={{ height: `${h}%` }}
                                    className="absolute bottom-0 left-0 right-0 bg-primary/60 rounded-t-sm"
                                />
                            </div>
                        ))}
                    </div>
                </motion.div>

                <motion.div
                    whileHover={{ scale: 1.02 }}
                    className="p-5 rounded-[2rem] glass-panel border border-border/50 flex flex-col justify-between h-40 group relative overflow-hidden"
                >
                    <div className="absolute -top-2 -right-2 p-4 opacity-5 group-hover:opacity-20 transition-all group-hover:rotate-12">
                        <Activity className="w-12 h-12" />
                    </div>
                    <span className="text-[9px] font-black text-secondary-foreground uppercase tracking-[0.2em] opacity-60">Accuracy</span>
                    <div className="flex items-baseline gap-1.5">
                        <span className="text-3xl font-black text-foreground tracking-tighter">{accuracy.toFixed(1)}</span>
                        <span className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">%</span>
                    </div>
                    <div className="w-full bg-secondary/50 h-1.5 rounded-full overflow-hidden self-end">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${accuracy}%` }}
                            className="h-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"
                        />
                    </div>
                </motion.div>
            </div>

            {/* Architectural Stack - Variety: Faux 3D Perspective List */}
            <div className="space-y-4">
                <h3 className="text-[10px] font-black text-secondary-foreground uppercase tracking-[0.3em] opacity-40 ml-1">Logic Stack</h3>
                <div className="space-y-3 perspective-1000">
                    {[
                        { icon: Cpu, name: "Neural Synthesis", sub: "Claude 3.5 Sonnet", color: "text-orange-500" },
                        { icon: Database, name: "Vector Fabric", sub: "AWS Kendra RAG", color: "text-blue-500" },
                        { icon: ShieldCheck, name: "Policy Guard", sub: "Rule-Based Filter", color: "text-emerald-500" },
                        { icon: Server, name: "Edge Compute", sub: "Lambda Mesh", color: "text-purple-500" },
                    ].map((item, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, rotateX: -20, y: 20 }}
                            animate={{ opacity: 1, rotateX: 0, y: 0 }}
                            transition={{ delay: 0.2 + (idx * 0.1) }}
                            whileHover={{ rotateY: 5, x: 5 }}
                            className="flex items-center gap-4 p-4.5 rounded-2xl bg-card border border-border shadow-sm hover:border-primary/30 transition-all cursor-default relative overflow-hidden group"
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                            <div className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center border border-border group-hover:border-primary/20 transition-colors">
                                <item.icon className={`w-5 h-5 ${item.color}`} />
                            </div>
                            <div className="flex-1 min-w-0 relative z-10">
                                <p className="text-xs font-black text-foreground tracking-tight leading-none mb-1.5">{item.name}</p>
                                <p className="text-[9px] text-secondary-foreground font-black uppercase tracking-widest opacity-50">{item.sub}</p>
                            </div>
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 group-hover:scale-150 transition-transform"></div>
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Village Collective Pulse — Live Impact Feed (Extraordinary Feature) */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h3 className="text-[10px] font-black text-secondary-foreground uppercase tracking-[0.3em] opacity-40 ml-1">Collective Pulse</h3>
                    <motion.div animate={{ opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 2 }} className="w-1.5 h-1.5 rounded-full bg-emerald-500"></motion.div>
                </div>
                <div className="space-y-3 p-5 rounded-2xl bg-secondary/20 border border-border/50 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-5">
                        <Globe className="w-12 h-12" />
                    </div>
                    {[
                        { time: "2m ago", text: "Farmer Raichur: ₹6k Beneficiary Audit ✅", color: "text-emerald-500" },
                        { time: "14m ago", text: "Village A: 12 Ayushman Links Formed ⚡", color: "text-blue-500" },
                        { time: "1h ago", text: "Karnataka Node: Mandi Q&A Peak 🌾", color: "text-orange-500" },
                    ].map((item, idx) => (
                        <div key={idx} className="flex flex-col gap-1 border-b border-border/10 pb-2 last:border-0 last:pb-0">
                            <div className="flex justify-between items-center text-[8px] font-bold uppercase tracking-widest opacity-40">
                                <span>Impact Event</span>
                                <span>{item.time}</span>
                            </div>
                            <p className={`text-[10px] font-black ${item.color} leading-tight`}>{item.text}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Region Health - Variety: Glassmorphic Overlay on Map */}
            <div className="mt-2 p-7 pb-12 rounded-[2.5rem] bg-secondary/30 border border-border relative overflow-hidden group shadow-inner">
                <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1524492412937-b28074a5d7da?q=80&w=2071&auto=format&fit=crop')] bg-cover bg-center opacity-10 grayscale group-hover:scale-110 transition-transform duration-[20s] ease-linear"></div>
                <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-transparent to-transparent"></div>
                <div className="relative z-10">
                    <div className="flex items-center gap-2 mb-2">
                        <Globe className="w-4 h-4 text-primary" />
                        <h4 className="text-[11px] font-black text-foreground uppercase tracking-[0.3em]">Bharat Distribution</h4>
                    </div>
                    <p className="text-[10px] text-primary font-black uppercase tracking-[0.6em] mb-8">ap-south-1 Mesh</p>

                    <div className="space-y-4">
                        <div className="flex justify-between items-end">
                            <span className="text-[9px] font-black text-secondary-foreground uppercase tracking-widest opacity-50">Cluster Integrity</span>
                            <span className="text-[11px] font-black text-foreground tracking-tighter">99.98%</span>
                        </div>
                        <div className="neumorphic-inner h-1.5 w-full rounded-full p-[1px]">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: '99%' }}
                                className="h-full bg-gradient-to-r from-primary to-accent rounded-full shadow-[0_0_10px_rgba(249,115,22,0.4)]"
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Professional Footer */}
            <div className="mt-auto pt-8 border-t border-border flex items-center justify-between">
                <span className="text-[8px] font-black text-secondary-foreground uppercase tracking-[0.8em] opacity-20">Sovereign Data Protection Active</span>
                <div className="flex gap-1.5">
                    {[1, 2, 3].map(i => <div key={i} className="w-1 h-1 rounded-full bg-border" />)}
                </div>
            </div>
        </div>
    );
};

export default TelemetryPanel;
