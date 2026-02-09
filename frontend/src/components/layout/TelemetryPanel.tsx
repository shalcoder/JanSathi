'use client';

import React, { useEffect, useState } from 'react';
import { Activity, Server, Zap, Database, Globe, Cpu } from 'lucide-react';

const TelemetryPanel = () => {
    // Simulate real-time metrics
    const [latency, setLatency] = useState(240);
    const [tokens, setTokens] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setLatency(prev => 200 + Math.floor(Math.random() * 80));
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="hidden xl:flex w-80 flex-col gap-5 p-7 bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-white/5 overflow-y-auto transition-all duration-500 shadow-premium">

            <div className="flex items-center justify-between mb-2">
                <h2 className="text-[10px] font-black text-slate-500 dark:text-slate-400 uppercase tracking-[0.2em]">System Telemetry</h2>
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 shadow-sm">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                    <span className="text-[8px] font-black text-emerald-700 dark:text-emerald-400 uppercase tracking-widest">ONLINE</span>
                </div>
            </div>

            {/* Main Stats Grid */}
            <div className="grid grid-cols-2 gap-3">
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 flex flex-col transition-all shadow-inner">
                    <div className="flex items-center gap-2 mb-2 text-slate-500 dark:text-slate-400">
                        <Zap className="w-3.5 h-3.5" />
                        <span className="text-[9px] font-black uppercase tracking-widest">Latency</span>
                    </div>
                    <span className="text-2xl font-black text-slate-900 dark:text-white transition-colors tracking-tighter">{latency}<span className="text-[10px] text-slate-500 ml-1">ms</span></span>
                </div>
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 flex flex-col transition-all shadow-inner">
                    <div className="flex items-center gap-2 mb-2 text-slate-500 dark:text-slate-400">
                        <Activity className="w-3.5 h-3.5" />
                        <span className="text-[9px] font-black uppercase tracking-widest">Uptime</span>
                    </div>
                    <span className="text-2xl font-black text-slate-900 dark:text-white transition-colors tracking-tighter">99.8<span className="text-[10px] text-slate-500 ml-1">%</span></span>
                </div>
            </div>

            {/* AWS Stack Visualization */}
            <div className="mt-4">
                <h3 className="text-[10px] font-black text-slate-500 dark:text-slate-400 uppercase tracking-[0.2em] mb-4 ml-1">Architecture Stack</h3>
                <div className="space-y-3">
                    {[
                        { icon: Cpu, name: "Claude 3.5 Sonnet", status: "Active", color: "text-blue-600 dark:text-blue-400" },
                        { icon: Globe, name: "AWS Polly AI", status: "Neural", color: "text-purple-600 dark:text-purple-400" },
                        { icon: Database, name: "Knowledge Base", status: "RAG", color: "text-emerald-600 dark:text-emerald-400" },
                        { icon: Server, name: "Lambda Cluster", status: "Scaling", color: "text-orange-600 dark:text-orange-400" },
                    ].map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between p-4 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-white/5 group hover:bg-slate-50 dark:hover:bg-white/[0.08] transition-all duration-300 shadow-sm hover:translate-x-1">
                            <div className="flex items-center gap-4">
                                <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-white/5 flex items-center justify-center border border-slate-200 dark:border-white/10 group-hover:scale-110 transition-transform">
                                    <item.icon className={`w-4 h-4 ${item.color}`} />
                                </div>
                                <span className="text-xs font-black text-slate-900 dark:text-slate-100 transition-colors tracking-tight">{item.name}</span>
                            </div>
                            <span className="text-[8px] font-black uppercase tracking-widest text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors">{item.status}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Region Map Placeholder */}
            <div className="mt-6 p-5 rounded-[2rem] bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-white/10 relative overflow-hidden transition-all duration-500 shadow-premium group">
                <div className="absolute inset-0 bg-[url('https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/India_satellite_image.jpg/1200px-India_satellite_image.jpg')] bg-cover bg-center opacity-5 dark:opacity-20 mix-blend-overlay group-hover:scale-110 transition-transform duration-[10s]"></div>
                <div className="relative z-10">
                    <h3 className="text-[10px] font-black text-slate-900 dark:text-white mb-1 uppercase tracking-widest">Region: ap-south-1</h3>
                    <p className="text-[8px] text-slate-500 font-black uppercase tracking-[0.2em]">Mumbai AWS Cluster</p>
                    <div className="mt-4 flex items-center gap-3">
                        <div className="h-1.5 flex-1 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden shadow-inner">
                            <div className="h-full bg-emerald-500 w-[85%] rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                        </div>
                        <span className="text-[8px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest">Optimal</span>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="mt-auto pt-6 border-t border-slate-200 dark:border-white/5 text-center transition-colors">
                <p className="text-[10px] font-black text-slate-400 dark:text-slate-600 uppercase tracking-[0.3em]">JanSathi Enterprise</p>
                <p className="text-[8px] text-slate-400 font-black mt-1 uppercase tracking-widest">Build 2024.0.1</p>
            </div>
        </div>
    );
};

export default TelemetryPanel;
