'use client';

import React from 'react';
import { useSignIn, useSignUp } from "@clerk/nextjs";
import { Mail, Lock, LogIn } from "lucide-react";
import { useRouter } from "next/navigation";

// Brand Icons
const GoogleIcon = () => (
    <svg viewBox="0 0 24 24" className="w-5 h-5" aria-hidden="true">
        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
    </svg>
);

const MicrosoftIcon = () => (
    <svg viewBox="0 0 23 23" className="w-5 h-5" aria-hidden="true">
        <path fill="#f35325" d="M1 1h10v10H1z" />
        <path fill="#81bc06" d="M12 1h10v10H12z" />
        <path fill="#05a6f0" d="M1 12h10v10H1z" />
        <path fill="#ffba08" d="M12 12h10v10H12z" />
    </svg>
);

interface CustomAuthProps {
    mode?: "signIn" | "signUp";
}

export default function CustomAuth({ mode = "signUp" }: CustomAuthProps) {
    const { signIn, isLoaded: isSignInLoaded } = useSignIn();
    const { signUp, isLoaded: isSignUpLoaded } = useSignUp();
    const router = useRouter();

    const handleOAuth = async (strategy: "oauth_google" | "oauth_microsoft") => {
        if (mode === "signIn") {
            if (!isSignInLoaded) return;
            await signIn.authenticateWithRedirect({
                strategy,
                redirectUrl: "/sso-callback",
                redirectUrlComplete: "/dashboard",
            });
        } else {
            if (!isSignUpLoaded) return;
            await signUp.authenticateWithRedirect({
                strategy,
                redirectUrl: "/sso-callback",
                redirectUrlComplete: "/dashboard",
            });
        }
    };

    const handleEmailClick = () => {
        // Redirect to a dedicated email entry page or toggle state
        // For simplicity, we can route to the specific Clerk page for email
        router.push(mode === "signIn" ? "/sign-in/email" : "/sign-up/email");
    };

    // For now, simple toggles or specific routes for email/sso could be implemented
    // But aligning with the image request:

    return (
        <div className="w-full max-w-sm mx-auto flex flex-col gap-3">
            {/* Header */}
            <div className="text-center mb-6">
                <h1 className="text-2xl font-bold text-foreground">
                    {mode === "signUp" ? "Create an account" : "Welcome back"}
                </h1>
                <p className="text-sm text-muted-foreground mt-1">
                    {mode === "signUp" ? "Enter your email to sign up for this app" : "Access your dashboard"}
                </p>
            </div>

            {/* Social Buttons */}
            <button
                onClick={() => handleOAuth("oauth_google")}
                className="flex items-center justify-center gap-3 w-full bg-[#2F2F2F] hover:bg-[#3F3F3F] text-white py-2.5 rounded-lg border border-[#404040] transition-all font-medium text-sm"
            >
                <GoogleIcon />
                <span>{mode === "signUp" ? "Sign up with Google" : "Continue with Google"}</span>
            </button>

            <button
                onClick={() => handleOAuth("oauth_microsoft")}
                className="flex items-center justify-center gap-3 w-full bg-[#2F2F2F] hover:bg-[#3F3F3F] text-white py-2.5 rounded-lg border border-[#404040] transition-all font-medium text-sm"
            >
                <MicrosoftIcon />
                <span>{mode === "signUp" ? "Sign up with Microsoft" : "Continue with Microsoft"}</span>
            </button>

            {/* Split Row: Email & SSO */}
            <div className="grid grid-cols-2 gap-3">
                <button
                    onClick={handleEmailClick}
                    className="flex items-center justify-center gap-2 bg-[#2F2F2F] hover:bg-[#3F3F3F] text-white py-2.5 rounded-lg border border-[#404040] transition-all font-medium text-sm"
                >
                    <Mail className="w-4 h-4" />
                    <span>Email</span>
                </button>

                <button
                    onClick={() => router.push(mode === "signIn" ? "/sign-in/sso" : "/sign-up/sso")}
                    className="flex items-center justify-center gap-2 bg-[#2F2F2F] hover:bg-[#3F3F3F] text-white py-2.5 rounded-lg border border-[#404040] transition-all font-medium text-sm"
                >
                    <Lock className="w-4 h-4" />
                    <span>SSO</span>
                </button>
            </div>

            {/* Divider / Spacer */}
            <div className="h-4"></div>

            {/* Footer Action */}
            <button
                onClick={() => router.push(mode === "signUp" ? "/sign-in" : "/sign-up")}
                className="flex items-center justify-center gap-2 w-full bg-transparent hover:bg-[#2F2F2F] text-muted-foreground hover:text-white py-2.5 rounded-lg border border-transparent hover:border-[#404040] transition-all font-bold text-sm uppercase tracking-wide"
            >
                {mode === "signUp" ? (
                    <>
                        <span>Log In</span>
                    </>
                ) : (
                    <>
                        <span>Create Account</span>
                    </>
                )}
            </button>

            {/* Terms */}
            <p className="text-[10px] text-center text-muted-foreground mt-4 px-4">
                By clicking continue, you agree to our <a href="#" className="underline hover:text-white">Terms of Service</a> and <a href="#" className="underline hover:text-white">Privacy Policy</a>.
            </p>
        </div>
    );
}
