'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState, useCallback } from 'react';
import { fetchAuthSession, getCurrentUser, signOut as amplifySignOut } from 'aws-amplify/auth';
import { Hub } from 'aws-amplify/utils';

export function useAuth() {
    const router = useRouter();
    const [user, setUser] = useState<{ id: string; name: string; username?: string } | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkUser();

        // Listen to Auth events
        const unsubscribe = Hub.listen('auth', ({ payload }) => {
            switch (payload.event) {
                case 'signedIn':
                    checkUser();
                    break;
                case 'signedOut':
                    setUser(null);
                    break;
            }
        });

        return () => unsubscribe();
    }, []);

    const checkUser = () => {
        try {
            const currentUser = await getCurrentUser();
            setUser({
                id: currentUser.userId,
                name: currentUser.username,
            });
        } catch (_error) {
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const signOut = () => {
        localStorage.removeItem('jansathi_auth');
        localStorage.removeItem('jansathi_user');
        setUser(null);
        router.push('/auth/signin');
    };

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
        isAuthenticated: !!user
    };
}

export const getToken = async () => {
    try {
        const session = await fetchAuthSession();
        return session.tokens?.idToken?.toString() || session.tokens?.accessToken?.toString() || null;
    } catch {
        return null;
    }
};
