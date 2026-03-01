'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    BarChart3, Users, IndianRupee, Map, ArrowUpRight,
    Activity, CheckCircle, XCircle, Play, RefreshCw, AlertTriangle
} from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import OutreachSimulator from '@/components/features/chat/OutreachSimulator';
import ModerationLoop from '@/components/features/chat/ModerationLoop';
import IVRMonitor from '@/components/features/dashboard/IVRMonitor';
import {
    getHITLCases, approveHITLCase, rejectHITLCase,
    type HITLCase
} from '@/services/api';

// ─── HITL Queue ────────────────────────────────────────────────────────────────

function HITLQueue() {
    const { getToken } = useAuth();
    const [cases, setCases] = useState<HITLCase[]>([]);
    const [loading, setLoading] = useState(true);
    const [actioningId, setActioningId] = useState<string | null>(null);

    const fetchCases = useCallback(async () => {
        setLoading(true);
        try {
            const token = await getToken();
            const data = await getHITLCases('pending_review', token ?? undefined);
            setCases(data);
        } catch {
            // Backend may not have this endpoint yet; show empty state gracefully
            setCases([]);
        } finally {
            setLoading(false);
        }
    }, [getToken]);

    useEffect(() => { fetchCases(); }, [fetchCases]);

    const handleApprove = async (caseId: string) => {
        setActioningId(caseId);
        try {
            const token = await getToken();
            await approveHITLCase(caseId, token ?? undefined);
            setCases(prev => prev.filter(c => c.id !== caseId));
        } catch { /* noop */ }
        finally { setActioningId(null); }
    };

    const handleReject = async (caseId: string) => {
        setActioningId(caseId);
        try {
            const token = await getToken();
            await rejectHITLCase(caseId, 'Rejected by admin review', token ?? undefined);
            setCases(prev => prev.filter(c => c.id !== caseId));
        } catch { /* noop */ }
        finally { setActioningId(null); }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-10 text-white/30 text-xs uppercase tracking-widest">
                <RefreshCw className="w-4 h-4 animate-spin mr-2" /> Loading HITL queue…
            </div>
        );
    }

    if (cases.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-10 gap-3 text-white/30">
                <CheckCircle className="w-8 h-8 text-emerald-500/40" />
                <p className="text-xs uppercase tracking-widest">No pending cases — queue is clear</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <AnimatePresence>
                {cases.map(c => (
                    <motion.div
                        key={c.id}
                        layout
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.97 }}
                        className="rounded-2xl border border-white/10 bg-white/5 p-5 space-y-3"
                    >
                        {/* Header */}
                        <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                                <p className="text-xs font-bold text-white/50 uppercase tracking-wider mb-1">
                                    Session {c.session_id.slice(-8)} · Turn {c.turn_id.slice(-6)}
                                </p>
                                <p className="text-sm text-white/80 font-medium leading-snug">{c.transcript}</p>
                            </div>
                            <span className={`shrink-0 text-xs font-bold px-2.5 py-1 rounded-full border ${
                                c.confidence < 0.5
                                    ? 'bg-red-500/10 text-red-300 border-red-500/30'
                                    : 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                            }`}>
                                {(c.confidence * 100).toFixed(0)}% conf
                            </span>
                        </div>

                        {/* Response preview */}
                        <p className="text-xs text-white/50 bg-white/5 rounded-xl px-4 py-2 leading-relaxed line-clamp-3">
                            {c.response_text}
                        </p>

                        {/* Benefit Receipt summary */}
                        {c.benefit_receipt && (
                            <div className="flex flex-wrap gap-1.5">
                                <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${c.benefit_receipt.eligible ? 'bg-emerald-500/15 text-emerald-300' : 'bg-red-500/15 text-red-300'}`}>
                                    {c.benefit_receipt.eligible ? '✅ Eligible' : '❌ Not Eligible'}
                                </span>
                                {c.benefit_receipt.rules.slice(0, 2).map((r, i) => (
                                    <span key={i} className="text-xs px-2.5 py-1 rounded-full bg-white/5 text-white/50 border border-white/10">{r}</span>
                                ))}
                            </div>
                        )}

                        {/* Audio */}
                        {c.audio_url && (
                            <div className="flex items-center gap-2">
                                <Play className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                                <audio controls src={c.audio_url} className="h-8 w-full opacity-80" />
                            </div>
                        )}

                        {/* Actions */}
                        <div className="flex gap-2 pt-1">
                            <button
                                disabled={actioningId === c.id}
                                onClick={() => handleApprove(c.id)}
                                className="flex-1 flex items-center justify-center gap-2 py-2 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 text-sm font-semibold border border-emerald-500/20 transition-all active:scale-95 disabled:opacity-50"
                            >
                                <CheckCircle className="w-4 h-4" /> Approve
                            </button>
                            <button
                                disabled={actioningId === c.id}
                                onClick={() => handleReject(c.id)}
                                className="flex-1 flex items-center justify-center gap-2 py-2 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-300 text-sm font-semibold border border-red-500/20 transition-all active:scale-95 disabled:opacity-50"
                            >
                                <XCircle className="w-4 h-4" /> Reject
                            </button>
                        </div>
                    </motion.div>
                ))}
            </AnimatePresence>
        </div>
    );
}

// ─── Stat Card ────────────────────────────────────────────────────────────────

interface StatCardProps {
    title: string;
    value: string | number;
    sub: string;
    icon: React.ReactNode;
}

const StatCard = ({ title, value, sub, icon }: StatCardProps) => (
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

// ─── Page ─────────────────────────────────────────────────────────────────────

interface ImpactStats {
    total_benefits_claimed: number;
    active_users: number;
    success_rate: string;
    top_district: string;
}

interface Dropout {
    scheme: string;
    rate: string;
}

interface Stats {
    impact: ImpactStats;
    dropouts: Dropout[];
}

const AdminDashboard = () => {
    const [stats, setStats] = useState<Stats | null>(null);
    const [activeTab, setActiveTab] = useState<'overview' | 'hitl' | 'ivr'>('overview');

    useEffect(() => {
        fetch('/api/stats')
            .then(res => res.json())
            .then((data: Stats) => setStats(data))
            .catch(() => {
                // Use mock data if endpoint unavailable
                setStats({
                    impact: {
                        total_benefits_claimed: 14832,
                        active_users: 3241,
                        success_rate: '87%',
                        top_district: 'Pune'
                    },
                    dropouts: [
                        { scheme: 'PM-Kisan', rate: '22%' },
                        { scheme: 'PM Awas Yojana', rate: '35%' },
                        { scheme: 'E-Shram', rate: '18%' },
                    ]
                });
            });
    }, []);

    if (!stats) return (
        <div className="p-12 text-white/50 text-center uppercase tracking-widest text-xs">
            Loading Telemetry...
        </div>
    );

    const tabs = [
        { id: 'overview', label: 'Overview' },
        { id: 'hitl', label: 'HITL Queue' },
        { id: 'ivr', label: 'IVR Monitor' },
    ] as const;

    return (
        <div className="min-h-screen bg-[#050505] text-white p-8">
            <header className="mb-10 flex flex-wrap justify-between items-end gap-4">
                <div>
                    <h1 className="text-4xl font-black tracking-tighter mb-2">JanSathi Admin</h1>
                    <p className="text-white/40 text-sm font-medium">REAL-TIME GOVERNMENT STAKEHOLDER TELEMETRY</p>
                </div>
                <div className="flex gap-2 items-center">
                    <div className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-xs font-bold text-indigo-400 flex items-center gap-2">
                        <Activity className="w-3 h-3 animate-pulse" />
                        LIVE AWS INFRASTRUCTURE
                    </div>
                </div>
            </header>

            {/* Tabs */}
            <div className="flex gap-2 mb-8 border-b border-white/10">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-5 py-2.5 text-sm font-bold rounded-t-xl transition-colors border-b-2 -mb-px ${
                            activeTab === tab.id
                                ? 'border-blue-400 text-white'
                                : 'border-transparent text-white/40 hover:text-white/70'
                        }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* TAB: Overview */}
            {activeTab === 'overview' && (
                <div className="space-y-8">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <StatCard title="Total Benefits Claimed" value={stats.impact.total_benefits_claimed} sub="+₹45L today" icon={<IndianRupee className="text-emerald-400" />} />
                        <StatCard title="Active Citizens" value={stats.impact.active_users.toLocaleString()} sub="+12% this week" icon={<Users className="text-blue-400" />} />
                        <StatCard title="Discovery Success Rate" value={stats.impact.success_rate} sub="Elite Performance" icon={<ArrowUpRight className="text-indigo-400" />} />
                        <StatCard title="Top District" value={stats.impact.top_district} sub="Regional Leader" icon={<Map className="text-orange-400" />} />
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
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
                                {stats.dropouts.map((d, idx) => (
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
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-indigo-500/20 blur-[100px] pointer-events-none" />
                        </div>
                    </div>
                </div>
            )}

            {/* TAB: HITL Queue */}
            {activeTab === 'hitl' && (
                <div className="max-w-3xl mx-auto space-y-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-xl font-bold">Human-in-the-Loop Review Queue</h2>
                            <p className="text-white/40 text-sm mt-1">Cases with confidence score below threshold requiring manual review</p>
                        </div>
                        <div className="flex items-center gap-1.5 text-amber-400 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-full text-xs font-bold">
                            <AlertTriangle className="w-3.5 h-3.5" />
                            Pending Review
                        </div>
                    </div>
                    <div className="bg-white/5 border border-white/10 rounded-3xl p-6">
                        <HITLQueue />
                    </div>
                </div>
            )}

            {/* TAB: IVR Monitor */}
            {activeTab === 'ivr' && (
                <div className="space-y-6">
                    <div>
                        <h2 className="text-xl font-bold">IVR Session Monitor</h2>
                        <p className="text-white/40 text-sm mt-1">Live active call sessions across all channels</p>
                    </div>
                    <IVRMonitor />
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;
