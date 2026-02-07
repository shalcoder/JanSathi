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
        <div className="hidden xl:flex w-80 flex-col gap-4 p-6 glass-panel border-l border-white/10 overflow-y-auto">

            <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-bold text-slate-500 uppercase tracking-wider">System Telemetry</h2>
                <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                    <span className="text-[10px] font-bold text-emerald-500">ONLINE</span>
                </div>
            </div>

            {/* Main Stats Grid */}
            <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-white/5 border border-white/5 flex flex-col">
                    <div className="flex items-center gap-2 mb-2 text-slate-400">
                        <Zap className="w-3.5 h-3.5" />
                        <span className="text-[10px] font-medium">Latency</span>
                    </div>
                    <span className="text-xl font-bold text-slate-200">{latency}<span className="text-xs text-slate-500 ml-1">ms</span></span>
                </div>
                <div className="p-3 rounded-xl bg-white/5 border border-white/5 flex flex-col">
                    <div className="flex items-center gap-2 mb-2 text-slate-400">
                        <Activity className="w-3.5 h-3.5" />
                        <span className="text-[10px] font-medium">Throughput</span>
                    </div>
                    <span className="text-xl font-bold text-slate-200">99.8<span className="text-xs text-slate-500 ml-1">%</span></span>
                </div>
            </div>

            {/* AWS Stack Visualization */}
            <div className="mt-4">
                <h3 className="text-xs font-semibold text-slate-400 mb-3 ml-1">Active Architecture</h3>
                <div className="space-y-2">
                    {[
                        { icon: Cpu, name: "Claude 3 Sonnet", status: "Active", color: "text-orange-400" },
                        { icon: Globe, name: "AWS Polly (Neural)", status: "Standby", color: "text-blue-400" },
                        { icon: Database, name: "Kendra Index", status: "Synced", color: "text-purple-400" },
                        { icon: Server, name: "Lambda (Python)", status: "Running", color: "text-yellow-400" },
                    ].map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5 group hover:bg-white/10 transition-colors">
                            <div className="flex items-center gap-3">
                                <item.icon className={`w-4 h-4 ${item.color}`} />
                                <span className="text-xs font-medium text-slate-300">{item.name}</span>
                            </div>
                            <span className="text-[10px] font-mono text-slate-500 group-hover:text-slate-300 transition-colors">{item.status}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Region Map Placeholder */}
            <div className="mt-4 p-4 rounded-xl bg-gradient-to-br from-indigo-900/40 to-slate-900/40 border border-white/10 relative overflow-hidden">
                <div className="absolute inset-0 bg-[url('https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/India_satellite_image.jpg/1200px-India_satellite_image.jpg')] bg-cover bg-center opacity-20 mix-blend-overlay"></div>
                <div className="relative z-10">
                    <h3 className="text-xs font-bold text-slate-300 mb-1">Region: ap-south-1</h3>
                    <p className="text-[10px] text-slate-500">Mumbai AWS Data Center</p>
                    <div className="mt-3 flex items-center gap-2">
                        <div className="h-1 flex-1 bg-slate-700 rounded-full overflow-hidden">
                            <div className="h-full bg-emerald-500 w-[80%] rounded-full"></div>
                        </div>
                        <span className="text-[10px] text-emerald-400">Good</span>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="mt-auto pt-4 text-center">
                <p className="text-[10px] text-slate-600">JanSathi Enterprise v2.0</p>
                <p className="text-[9px] text-slate-700 font-mono mt-0.5">Build: hacking_win_2024</p>
            </div>
        </div>
    );
};

export default TelemetryPanel;
