'use client';

import React, { useEffect, useState } from 'react';
import { checkHealth } from '@/services/api';

export default function BackendStatus() {
    const [status, setStatus] = useState<'loading' | 'online' | 'offline'>('loading');

    useEffect(() => {
        const verify = async () => {
            const isHealthy = await checkHealth();
            setStatus(isHealthy ? 'online' : 'offline');
        };
        verify();
        const interval = setInterval(verify, 30000); // Check every 30s
        return () => clearInterval(interval);
    }, []);

    // if (status === 'online') return null; // Logic fix: Keep visible for verification 

    // Actually, for this task, let's show a small badge always
    return (
        <div className={`fixed bottom-4 right-4 z-50 px-3 py-1.5 rounded-full text-xs font-medium flex items-center gap-2 shadow-lg backdrop-blur-md border ${status === 'online'
            ? 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800'
            : status === 'loading'
                ? 'bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800'
                : 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800'
            }`}>
            <span className={`w-2 h-2 rounded-full ${status === 'online' ? 'bg-green-500' : status === 'loading' ? 'bg-blue-500 animate-pulse' : 'bg-red-500'
                }`}></span>
            {status === 'online' ? 'System Online' : status === 'loading' ? 'Connecting...' : 'System Offline (Check Backend)'}
        </div>
    );
}
