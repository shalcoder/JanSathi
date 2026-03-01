import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, ArrowRight, PhoneCall, Zap, AlertTriangle, Layers } from 'lucide-react';
import BackendStatus from '@/components/BackendStatus';

export default function OverviewPage({ onNavigate }: { onNavigate: (page: string) => void }) {
    const stats = [
        { label: "Calls Processed (24h)", value: "1,492", icon: PhoneCall, color: "text-blue-500", bg: "bg-blue-500/10" },
        { label: "Eligibility Rate", value: "78.4%", icon: CheckCircle, color: "text-emerald-500", bg: "bg-emerald-500/10" },
        { label: "HITL Escalation", value: "4.2%", icon: AlertTriangle, color: "text-red-500", bg: "bg-red-500/10" },
        { label: "Bedrock Spend", value: "₹248.50", icon: Zap, color: "text-purple-500", bg: "bg-purple-500/10" },
    ];

    return (
        <div className="space-y-8 p-6 lg:p-10 max-w-7xl mx-auto">
            {/* API Connection Status */}
            <div className="mb-2">
                 <BackendStatus />
            </div>

            {/* Welcome Section */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-black tracking-tight text-foreground">Command Center</h1>
                    <p className="text-secondary-foreground font-medium mt-1">Real-time operational metrics for JanSathi.</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={() => onNavigate('ivr-console')}
                        className="px-6 py-3 bg-secondary/50 hover:bg-secondary text-foreground rounded-xl font-bold transition-all border border-border flex items-center gap-2"
                    >
                        <span>IVR Live</span>
                    </button>
                    <button
                        onClick={() => onNavigate('simulator')}
                        className="px-6 py-3 bg-rose-500 hover:bg-rose-600 text-white rounded-xl font-bold transition-all shadow-lg active:scale-95 flex items-center gap-2"
                    >
                        <span>Call Simulator</span>
                        <ArrowRight className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {stats.map((stat, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-6 rounded-2xl bg-card/60 backdrop-blur-xl border border-border/50 hover:border-primary/50 transition-all group hover:shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:hover:shadow-[0_8px_30px_rgb(255,255,255,0.02)] relative overflow-hidden"
                    >
                        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                        <div className="flex justify-between items-start mb-4 relative z-10">
                            <div className={`p-3 rounded-xl ${stat.bg} ${stat.color} transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3 shadow-inner`}>
                                <stat.icon className="w-6 h-6" />
                            </div>
                        </div>
                        <h3 className="text-3xl font-black text-foreground mb-1 relative z-10 tracking-tight">{stat.value}</h3>
                        <p className="text-sm font-semibold text-secondary-foreground relative z-10">{stat.label}</p>
                    </motion.div>
                ))}
            </div>

            {/* Recent Activity & Recommendations */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Operational Funnel */}
                <div className="lg:col-span-2 space-y-6">
                    <h2 className="text-xl font-bold flex items-center gap-2">
                        <Layers className="w-5 h-5 text-indigo-500" />
                        Benefit Gap Funnel (Live)
                    </h2>
                    <div className="bg-card border border-border/50 rounded-2xl p-6 shadow-sm">
                        <div className="space-y-5 font-mono text-sm max-w-lg">
                            <div className="flex flex-col gap-2">
                               <div className="flex justify-between text-secondary-foreground font-semibold"><span>Calls Initiated</span> <span className="text-blue-500 font-bold tracking-widest text-base">1,492</span></div>
                               <div className="w-full bg-secondary/50 rounded-full h-3 overflow-hidden border border-border/50 shadow-inner">
                                  <motion.div initial={{ width: 0 }} animate={{ width: "100%" }} transition={{ duration: 1, delay: 0.2 }} className="bg-gradient-to-r from-blue-600 to-blue-400 h-full w-full rounded-full"></motion.div>
                               </div>
                            </div>
                            <div className="flex flex-col gap-2">
                               <div className="flex justify-between text-secondary-foreground font-semibold"><span>Intents Extracted</span> <span className="text-emerald-400 font-bold tracking-widest text-base">1,417</span></div>
                               <div className="w-full bg-secondary/50 rounded-full h-3 overflow-hidden border border-border/50 shadow-inner">
                                  <motion.div initial={{ width: 0 }} animate={{ width: "95%" }} transition={{ duration: 1, delay: 0.4 }} className="bg-gradient-to-r from-emerald-600 to-emerald-400 h-full w-[95%] rounded-full"></motion.div>
                               </div>
                            </div>
                            <div className="flex flex-col gap-2">
                               <div className="flex justify-between text-secondary-foreground font-semibold"><span>Rules Passed</span> <span className="text-emerald-500 font-bold tracking-widest text-base">1,163</span></div>
                               <div className="w-full bg-secondary/50 rounded-full h-3 overflow-hidden border border-border/50 shadow-inner">
                                  <motion.div initial={{ width: 0 }} animate={{ width: "78%" }} transition={{ duration: 1, delay: 0.6 }} className="bg-gradient-to-r from-emerald-500 to-emerald-300 h-full w-[78%] rounded-full"></motion.div>
                               </div>
                            </div>
                            <div className="flex flex-col gap-2">
                               <div className="flex justify-between text-secondary-foreground font-semibold"><span>Receipts Dispatched</span> <span className="text-purple-500 font-bold tracking-widest text-base">1,148</span></div>
                               <div className="w-full bg-secondary/50 rounded-full h-3 overflow-hidden border border-border/50 shadow-inner">
                                  <motion.div initial={{ width: 0 }} animate={{ width: "77%" }} transition={{ duration: 1, delay: 0.8 }} className="bg-gradient-to-r from-purple-600 to-purple-400 h-full w-[77%] rounded-full"></motion.div>
                               </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* System Alarms */}
                <div className="space-y-6">
                    <h2 className="text-xl font-bold flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-amber-500" />
                        System Health
                    </h2>
                    <div className="bg-card/60 backdrop-blur-xl border border-border/50 rounded-2xl p-6 relative overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.04)] group hover:border-amber-500/50 transition-colors">
                        <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity duration-500">
                            <Zap className="w-32 h-32 text-amber-500" />
                        </div>
                        <div className="flex items-center gap-2 mb-4">
                            <span className="flex h-2 w-2 relative">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                            </span>
                            <span className="px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-500 text-[10px] font-bold uppercase tracking-widest">
                                AWS Connect Optimal
                            </span>
                        </div>
                        <h3 className="text-xl font-black mb-4 text-foreground tracking-tight">Latency & Load</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center bg-background/50 p-2.5 rounded-lg border border-border/50">
                                <span className="font-bold text-foreground text-sm flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>ASR</span>
                                <span className="text-sm text-secondary-foreground font-mono">410ms <span className="text-[10px] opacity-50">(p95)</span></span>
                            </div>
                            <div className="flex justify-between items-center bg-background/50 p-2.5 rounded-lg border border-border/50">
                                <span className="font-bold text-foreground text-sm flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-purple-500"></div>LLM</span>
                                <span className="text-sm text-secondary-foreground font-mono">1.2s <span className="text-[10px] opacity-50">(Haiku)</span></span>
                            </div>
                            <div className="flex justify-between items-center bg-background/50 p-2.5 rounded-lg border border-border/50">
                                <span className="font-bold text-foreground text-sm flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>DB</span>
                                <span className="text-sm text-secondary-foreground font-mono">12ms <span className="text-[10px] opacity-50">(Dynamo)</span></span>
                            </div>
                        </div>
                        <button onClick={() => onNavigate('security')} className="mt-6 text-sm font-bold text-primary flex items-center gap-2 transition-all hover:gap-3">
                            View CloudWatch Logs <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
