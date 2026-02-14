'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Users, IndianRupee, Map, ArrowUpRight, Activity } from 'lucide-react';
import OutreachSimulator from '@/components/features/chat/OutreachSimulator';
import ModerationLoop from '@/components/features/chat/ModerationLoop';

const AdminDashboard = () => {
    const [stats, setStats] = useState<any>(null);

    useEffect(() => {
        fetch('http://localhost:5000/api/stats')
            .then(res => res.json())
            .then(data => setStats(data));
    }, []);

    if (!stats) return <div className="p-12 text-white/50 text-center uppercase tracking-widest text-xs">Loading Telemetry...</div>;

    return (
        <div className="min-h-screen bg-[#050505] text-white p-8">
            <header className="mb-12 flex justify-between items-end">
                <div>
                    <h1 className="text-4xl font-black tracking-tighter mb-2">JanSathi Pulse</h1>
                    <p className="text-white/40 text-sm font-medium">REAL-TIME GOVERNMENT STAKEHOLDER TELEMETRY</p>
                </div>
                <div className="flex gap-2">
                    <div className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-xs font-bold text-indigo-400 flex items-center gap-2">
                        <Activity className="w-3 h-3 animate-pulse" />
                        LIVE AWS INFRASTRUCTURE
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                <StatCard
                    title="Total Benefits Claimed"
                    value={stats.impact.total_benefits_claimed}
                    sub="+₹45L today"
                    icon={<IndianRupee className="text-emerald-400" />}
                />
                <StatCard
                    title="Active Citizens"
                    value={stats.impact.active_users.toLocaleString()}
                    sub="+12% this week"
                    icon={<Users className="text-blue-400" />}
                />
                <StatCard
                    title="Discovery Success Rate"
                    value={stats.impact.success_rate}
                    sub="Elite Performance"
                    icon={<ArrowUpRight className="text-indigo-400" />}
                />
                <StatCard
                    title="Top District"
                    value={stats.impact.top_district}
                    sub="Regional Leader"
                    icon={<Map className="text-orange-400" />}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <OutreachSimulator />
                <ModerationLoop />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-white/5 border border-white/10 rounded-3xl p-8">
                    <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-indigo-400" />
                        Scheme Dropout Analysis
                    </h3>
                    <div className="space-y-6">
                        {stats.dropouts.map((d: any, idx: number) => (
                            <div key={idx} className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-white/70 font-medium">{d.scheme}</span>
                                    <span className="text-red-400 font-bold">{d.rate} Dropout</span>
                                </div>
                                <div className="h-2 rounded-full bg-white/5 overflow-hidden">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: d.rate }}
                                        className="h-full bg-gradient-to-r from-red-500/50 to-red-400"
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-3xl p-8 relative overflow-hidden">
                    <div className="relative z-10">
                        <h3 className="text-lg font-bold mb-6">Regional Impact Heatmap</h3>
                        <p className="text-white/40 text-sm mb-8">Concentration of digital benefit discovery across districts.</p>
                        <div className="flex items-center justify-center p-12 border-2 border-dashed border-white/10 rounded-2xl bg-white/5">
                            <Map className="w-12 h-12 text-white/20" />
                            <span className="ml-4 text-xs font-bold text-white/30 uppercase tracking-widest">Interactive QuickSight View</span>
                        </div>
                    </div>
                    {/* Decorative Background Map Glow */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-indigo-500/20 blur-[100px] pointer-events-none" />
                </div>
            </div>
        </div>
    );
};

const StatCard = ({ title, value, sub, icon }: any) => (
    <div className="bg-white/5 border border-white/10 rounded-3xl p-6 hover:bg-white/[0.07] transition-colors group">
        <div className="flex justify-between items-start mb-4">
            <div className="p-2 rounded-xl bg-white/5 border border-white/10 group-hover:scale-110 transition-transform">
                {icon}
            </div>
            <span className="text-[10px] font-bold text-white/20 uppercase tracking-widest">{title}</span>
        </div>
        <div className="text-2xl font-black mb-1">{value}</div>
        <div className="text-[10px] font-medium text-white/40 flex items-center gap-1">
            <ArrowUpRight className="w-3 h-3 text-emerald-500" />
            {sub}
        </div>
    </div>
);

export default AdminDashboard;
