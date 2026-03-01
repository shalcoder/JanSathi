'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Phone, Play, Radio, RefreshCw, ArrowRight } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import { getIVRSessions, type IVRSession } from '@/services/api';

const CHANNEL_COLORS = {
    ivr: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
    web: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
    whatsapp: 'bg-green-500/15 text-green-300 border-green-500/30',
};

function timeSince(iso: string): string {
    const diffMs = Date.now() - new Date(iso).getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    return `${Math.floor(diffMins / 60)}h ${diffMins % 60}m ago`;
}

// Mock sessions for demo (shown when backend isn't live)
const MOCK_SESSIONS: IVRSession[] = [
    {
        session_id: 'ivr-abc12345',
        caller_number: '+91-XXXXX12345',
        start_time: new Date(Date.now() - 3 * 60000).toISOString(),
        current_state: 'eligibility_check',
        last_transcript: 'मुझे पीएम-किसान के बारे में जानकारी चाहिए',
        channel: 'ivr',
    },
    {
        session_id: 'ivr-def67890',
        caller_number: '+91-XXXXX67890',
        start_time: new Date(Date.now() - 8 * 60000).toISOString(),
        current_state: 'document_collection',
        last_transcript: 'मेरा राशन कार्ड नंबर क्या है?',
        channel: 'ivr',
    },
];

export default function IVRMonitor() {
    const { getToken } = useAuth();
    const [sessions, setSessions] = useState<IVRSession[]>([]);
    const [loading, setLoading] = useState(true);
    const [isDemoData, setIsDemoData] = useState(false);

    const fetchSessions = useCallback(async () => {
        setLoading(true);
        try {
            const token = await getToken();
            const data = await getIVRSessions(token ?? undefined);
            setSessions(data);
            setIsDemoData(false);
        } catch {
            setSessions(MOCK_SESSIONS);
            setIsDemoData(true);
        } finally {
            setLoading(false);
        }
    }, [getToken]);

    useEffect(() => { fetchSessions(); }, [fetchSessions]);

    // Auto-refresh every 10s
    useEffect(() => {
        const interval = setInterval(fetchSessions, 10000);
        return () => clearInterval(interval);
    }, [fetchSessions]);

    return (
        <div className="rounded-3xl border border-white/10 bg-white/5 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
                <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${loading ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400 animate-pulse'}`} />
                    <span className="text-sm font-bold text-white/70 uppercase tracking-wider">
                        {loading ? 'Syncing…' : `${sessions.length} Active Session${sessions.length !== 1 ? 's' : ''}`}
                    </span>
                    {isDemoData && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full border border-amber-500/30 text-amber-400 font-bold">Demo Data</span>
                    )}
                </div>
                <button
                    onClick={fetchSessions}
                    disabled={loading}
                    className="p-2 rounded-xl hover:bg-white/10 text-white/40 hover:text-white transition-colors disabled:opacity-40"
                >
                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {/* Sessions list */}
            <div className="divide-y divide-white/5">
                <AnimatePresence>
                    {sessions.length === 0 && !loading ? (
                        <div className="flex flex-col items-center justify-center py-12 gap-3 text-white/20">
                            <Radio className="w-8 h-8" />
                            <p className="text-xs uppercase tracking-widest">No active sessions</p>
                        </div>
                    ) : (
                        sessions.map((session) => (
                            <motion.div
                                key={session.session_id}
                                initial={{ opacity: 0, x: -8 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 8 }}
                                className="px-6 py-5 hover:bg-white/[0.03] transition-colors"
                            >
                                <div className="flex flex-col sm:flex-row sm:items-start gap-4">
                                    {/* Left: Phone icon + caller */}
                                    <div className="flex items-center gap-3 shrink-0">
                                        <div className="w-10 h-10 rounded-2xl bg-purple-500/15 border border-purple-500/20 flex items-center justify-center">
                                            <Phone className="w-4 h-4 text-purple-400" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-bold text-white">
                                                {session.caller_number}
                                            </p>
                                            <p className="text-[11px] text-white/40">
                                                Started {timeSince(session.start_time)}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Middle: state + transcript */}
                                    <div className="flex-1">
                                        <div className="flex flex-wrap items-center gap-2 mb-2">
                                            {/* Channel badge */}
                                            <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${CHANNEL_COLORS[session.channel] ?? CHANNEL_COLORS.ivr}`}>
                                                {session.channel.toUpperCase()}
                                            </span>
                                            {/* State */}
                                            <span className="text-[10px] text-white/50 font-mono bg-white/5 px-2.5 py-0.5 rounded-full border border-white/10">
                                                {session.current_state.replace(/_/g, ' ')}
                                            </span>
                                        </div>
                                        {session.last_transcript && (
                                            <p className="text-sm text-white/60 leading-snug line-clamp-2">
                                                ❝ {session.last_transcript} ❞
                                            </p>
                                        )}
                                    </div>

                                    {/* Right: audio + takeover */}
                                    <div className="flex items-center gap-2 shrink-0">
                                        {session.last_audio_url && (
                                            <audio
                                                controls
                                                src={session.last_audio_url}
                                                className="h-8 opacity-70"
                                                title="Play last response"
                                            />
                                        )}
                                        <button
                                            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 text-blue-300 text-xs font-semibold transition-all active:scale-95"
                                            title="Take over as human reviewer"
                                        >
                                            <Play className="w-3 h-3" />
                                            Takeover
                                            <ArrowRight className="w-3 h-3" />
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        ))
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
