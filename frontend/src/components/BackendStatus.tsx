'use client';

import React, { useEffect, useState } from 'react';
import { checkHealth } from '@/services/api';
import { Activity, ShieldCheck, ShieldAlert } from 'lucide-react';

export default function BackendStatus() {
    const [status, setStatus] = useState<'loading' | 'online' | 'offline'>('loading');

    useEffect(() => {
        const verify = async () => {
            const isHealthy = await checkHealth();
            setStatus(isHealthy ? 'online' : 'offline');
        };
        verify();
        const interval = setInterval(verify, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className={`fixed bottom-6 right-6 z-50 px-4 py-2 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] flex items-center gap-3 shadow-premium transition-all duration-700 backdrop-blur-2xl border ${status === 'online'
            ? 'glass-panel text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
            : status === 'loading'
                ? 'glass-panel text-primary border-primary/20 bg-primary/5'
                : 'bg-red-500 text-white border-red-400'
            }`}>
            {status === 'online' ? <ShieldCheck className="w-4 h-4" /> : status === 'offline' ? <ShieldAlert className="w-4 h-4" /> : <Activity className="w-4 h-4 animate-pulse" />}

            <div className="flex items-center gap-2">
                <span className={`w-1.5 h-1.5 rounded-full ${status === 'online' ? 'bg-emerald-500 animate-pulse' : status === 'loading' ? 'bg-primary' : 'bg-white'
                    }`}></span>
                {status === 'online' ? 'Cluster Stable' : status === 'loading' ? 'Handshaking...' : 'Node Failure'}
            </div>
        </div>
    );
}
