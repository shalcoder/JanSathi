'use client';

import { useState, useEffect } from 'react';

/**
 * OfflineNotice — Banner that appears when the user is offline.
 * Shows a subtle amber bar at the top of the screen with a pulsing dot.
 * Auto-hides when back online.
 */
export default function OfflineNotice() {
    const [isOffline, setIsOffline] = useState(false);

    useEffect(() => {
        const handleOnline = () => setIsOffline(false);
        const handleOffline = () => setIsOffline(true);

        // Check initial state
        const checkOnlineStatus = () => {
            if (typeof navigator !== 'undefined') {
                setIsOffline(!navigator.onLine);
            }
        };
        checkOnlineStatus();

        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);

    if (!isOffline) return null;

    return (
        <div
            id="offline-notice"
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                zIndex: 9999,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '8px 16px',
                backgroundColor: '#f59e0b',
                color: '#1a1a1a',
                fontSize: '13px',
                fontWeight: 600,
                fontFamily: 'system-ui, sans-serif',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            }}
        >
            {/* Pulsing offline dot */}
            <span
                style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: '#dc2626',
                    animation: 'pulse 1.5s ease-in-out infinite',
                }}
            />
            <span>📡 You are offline — Cached data will be shown</span>

            {/* Inline keyframes */}
            <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(0.8); }
        }
      `}</style>
        </div>
    );
}
