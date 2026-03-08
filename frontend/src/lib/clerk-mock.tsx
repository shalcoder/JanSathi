import React from 'react';

export const useAuth = () => ({ 
    isLoaded: true, 
    isSignedIn: true, 
    sessionId: 'demo-session', 
    getToken: async () => 'mock-token' 
});

export const useUser = () => ({ 
    isLoaded: true, 
    isSignedIn: true, 
    user: { 
        id: 'demo-user', 
        fullName: 'Demo User', 
        primaryEmailAddress: { emailAddress: 'demo@jansathi.in' } 
    } 
});

export const UserButton = () => <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">D</div>;
export const SignedIn = ({ children }: { children: React.ReactNode }) => <>{children}</>;
export const SignedOut = ({ children }: { children: React.ReactNode }) => null;
export const SignIn = () => <div className="p-4 text-center">Demo Mode - Auth Bypassed</div>;
export const SignUp = () => <div className="p-4 text-center">Demo Mode - Auth Bypassed</div>;
export const SignInButton = ({ children }: { children: React.ReactNode }) => <button>{children || 'Sign In'}</button>;
export const SignOutButton = ({ children }: { children: React.ReactNode }) => <button>{children || 'Sign Out'}</button>;
export const ClerkProvider = ({ children }: { children: React.ReactNode }) => <>{children}</>;
export const AuthenticateWithRedirectCallback = () => <div className="p-4 text-center">Redirecting...</div>;
