'use client';

import { useRouter } from 'next/navigation';
import { useUser, useAuth as useClerkAuth } from '@clerk/nextjs';

export function useAuth() {
    const router = useRouter();
    const { user, isLoaded: isUserLoaded } = useUser();
    const { signOut: clerkSignOut, isLoaded: isAuthLoaded } = useClerkAuth();

    const loading = !isUserLoaded || !isAuthLoaded;

    const signOut = async () => {
        await clerkSignOut();
        router.push('/sign-in');
    };

    const requireAuth = () => {
        if (!loading && !user) {
            router.push('/sign-in');
        }
    };

    return {
        user: user ? {
            email: user.primaryEmailAddress?.emailAddress,
            name: user.fullName || user.username || user.firstName,
            imageUrl: user.imageUrl,
            id: user.id
        } : null,
        loading,
        signOut,
        requireAuth,
        isAuthenticated: !!user
    };
}
