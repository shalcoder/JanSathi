'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export function useAuth() {
    const router = useRouter();
    const [user, setUser] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is authenticated (demo mode - checks localStorage)
        const storedUser = localStorage.getItem('jansathi_user');

        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
            } catch (error) {
                console.error('Failed to parse user data:', error);
                localStorage.removeItem('jansathi_user');
            }
        }

        setLoading(false);
    }, []);

    const signOut = () => {
        localStorage.removeItem('jansathi_user');
        setUser(null);
        router.push('/sign-in');
    };

    const requireAuth = () => {
        if (!loading && !user) {
            router.push('/sign-in');
        }
    };

    return { user, loading, signOut, requireAuth, isAuthenticated: !!user };
}
