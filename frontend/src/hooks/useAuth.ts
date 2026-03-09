'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState, useCallback } from 'react';
import {
    getCurrentUser,
    fetchAuthSession,
    signOut as amplifySignOut,
    type AuthUser,
} from 'aws-amplify/auth';

interface AuthUserInfo {
    id: string;
    name: string;
    email: string;
    username?: string;
}

export function useAuth() {
    const router = useRouter();
    const [user, setUser] = useState<AuthUserInfo | null>(null);
    const [loading, setLoading] = useState(true);

    const checkUser = useCallback(async () => {
        try {
            const cognito = await getCurrentUser();
            const session = await fetchAuthSession();
            const idToken = session.tokens?.idToken;
            const email   = (idToken?.payload?.email as string) || cognito.username;
            const name    = (idToken?.payload?.name as string)
                         || (idToken?.payload?.['cognito:username'] as string)
                         || email.split('@')[0];
            setUser({
                id:       cognito.userId || cognito.username,
                name,
                email,
                username: cognito.username,
            });
        } catch {
            // Not signed in
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        checkUser();
    }, [checkUser]);

    const signOut = useCallback(async () => {
        try {
            await amplifySignOut({ global: true });
        } catch {
            // best-effort
        }
        setUser(null);
        router.push('/auth/signin');
    }, [router]);

    const requireAuth = useCallback(() => {
        if (!loading && !user) {
            router.push('/auth/signin');
        }
    }, [loading, user, router]);

    return {
        user,
        loading,
        signOut,
        requireAuth,
        isAuthenticated: !!user,
        refresh: checkUser,
    };
}

/**
 * Returns the current Cognito IdToken JWT string, or null.
 * Works in both browser and server components via Amplify session.
 */
export const getToken = async (): Promise<string | null> => {
    try {
        const session = await fetchAuthSession();
        return session.tokens?.idToken?.toString() ?? null;
    } catch {
        return null;
    }
};
