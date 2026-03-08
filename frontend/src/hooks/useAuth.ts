'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getCurrentUser, signOut as amplifySignOut } from 'aws-amplify/auth';
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

    const checkUser = async () => {
        try {
            const currentUser = await getCurrentUser();
            setUser({
                id: currentUser.userId,
                name: currentUser.username,
                // Email/attributes require fetchUserAttributes() normally, but keeping simple for now
            });
        } catch (_error) {
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const signOut = async () => {
        await amplifySignOut();
        router.push('/auth/signin');
    };

    const requireAuth = () => {
        if (!loading && !user) {
            router.push('/auth/signin');
        }
    };

    return {
        user,
        loading,
        signOut,
        requireAuth,
        isAuthenticated: !!user
    };
}
