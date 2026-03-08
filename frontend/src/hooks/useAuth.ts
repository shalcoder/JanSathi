'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export function useAuth() {
    const router = useRouter();
    const [user, setUser] = useState<{ id: string; name: string; username?: string } | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkUser();
    }, []);

    const checkUser = () => {
        try {
            const authToken = localStorage.getItem('jansathi_auth');
            const userEmail = localStorage.getItem('jansathi_user');
            
            if (authToken === 'true' && userEmail) {
                setUser({
                    id: userEmail,
                    name: userEmail.split('@')[0],
                    username: userEmail
                });
            } else {
                setUser(null);
            }
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
