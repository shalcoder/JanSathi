'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@clerk/nextjs';
import { initSession } from '@/services/api';

const SESSION_STORAGE_KEY = 'jansathi_session_id';

export interface UseSessionReturn {
    sessionId: string | null;
    isLoading: boolean;
    resetSession: () => void;
    token: string | null;
}

/**
 * Initialises and persists a backend session_id tied to the Clerk user.
 * - On mount: checks localStorage; if missing, calls /v1/sessions/init.
 * - Exposes the Clerk JWT token so callers can forward it to API functions.
 * - resetSession() clears the stored ID and triggers a new init.
 */
export function useSession(): UseSessionReturn {
    const { getToken, isSignedIn } = useAuth();
    const [sessionId, setSessionId] = useState<string | null>(() => {
        if (typeof window !== 'undefined') {
            return localStorage.getItem(SESSION_STORAGE_KEY);
        }
        return null;
    });
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(!sessionId);

    const fetchSession = useCallback(async () => {
        if (!isSignedIn) return;
        setIsLoading(true);
        try {
            const jwt = await getToken();
            setToken(jwt);

            // Reuse stored session if still valid
            const stored = typeof window !== 'undefined'
                ? localStorage.getItem(SESSION_STORAGE_KEY)
                : null;

            if (stored) {
                setSessionId(stored);
                setIsLoading(false);
                return;
            }

            if (!jwt) return;
            const { session_id } = await initSession(jwt);
            localStorage.setItem(SESSION_STORAGE_KEY, session_id);
            setSessionId(session_id);
        } catch (err) {
            console.error('[useSession] Failed to init session:', err);
            // Fallback: generate a client-side ephemeral session id
            const ephemeral = `local-${Date.now()}-${Math.random().toString(36).slice(2)}`;
            localStorage.setItem(SESSION_STORAGE_KEY, ephemeral);
            setSessionId(ephemeral);
        } finally {
            setIsLoading(false);
        }
    }, [getToken, isSignedIn]);

    useEffect(() => {
        fetchSession();
    }, [fetchSession]);

    const resetSession = useCallback(() => {
        if (typeof window !== 'undefined') {
            localStorage.removeItem(SESSION_STORAGE_KEY);
        }
        setSessionId(null);
        fetchSession();
    }, [fetchSession]);

    return { sessionId, isLoading, resetSession, token };
}
