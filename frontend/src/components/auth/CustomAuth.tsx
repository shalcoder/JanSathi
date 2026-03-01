'use client';

import React from 'react';
import { useSignIn, useSignUp } from "@clerk/nextjs";
import { Mail, Lock, LogIn, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Link from 'next/link';

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
        <motion.div 
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="w-full max-w-sm mx-auto flex flex-col gap-4 p-8 rounded-[2rem] bg-card/80 backdrop-blur-2xl border border-border/50 shadow-2xl relative overflow-hidden"
        >
            {/* Decorative Gradient Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 via-transparent to-primary/5 pointer-events-none -z-10"></div>
            
            {/* Header */}
            <div className="text-center mb-4 relative z-10">
                <div className="mx-auto w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-orange-500/20 mb-4">JS</div>
                <h1 className="text-3xl font-bold tracking-tight text-foreground mb-2">
                    {mode === "signUp" ? "Create an account" : "Welcome back"}
                </h1>
                <p className="text-sm text-secondary-foreground font-medium">
                    {mode === "signUp" ? "Enter your email to sign up for this app" : "Access your Agentic dashboard"}
                </p>
            </div>

            {/* Social Buttons */}
            <div className="space-y-3 relative z-10">
            <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleOAuth("oauth_google")}
                className="flex items-center justify-center gap-3 w-full bg-secondary hover:bg-secondary/80 text-foreground py-3 rounded-xl border border-border/50 transition-all font-bold text-sm shadow-sm"
            >
                <GoogleIcon />
                <span>{mode === "signUp" ? "Sign up with Google" : "Continue with Google"}</span>
            </motion.button>

            <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleOAuth("oauth_microsoft")}
                className="flex items-center justify-center gap-3 w-full bg-secondary hover:bg-secondary/80 text-foreground py-3 rounded-xl border border-border/50 transition-all font-bold text-sm shadow-sm"
            >
                <MicrosoftIcon />
                <span>{mode === "signUp" ? "Sign up with Microsoft" : "Continue with Microsoft"}</span>
            </motion.button>

            {/* Split Row: Email & SSO */}
            <div className="grid grid-cols-2 gap-3 mt-2">
                <motion.button
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={handleEmailClick}
                    className="flex items-center justify-center gap-2 bg-secondary hover:bg-secondary/80 text-foreground py-3 rounded-xl border border-border/50 transition-all font-bold text-sm"
                >
                    <Mail className="w-4 h-4 text-secondary-foreground" />
                    <span>Email</span>
                </motion.button>

                <motion.button
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => router.push(mode === "signIn" ? "/sign-in/sso" : "/sign-up/sso")}
                    className="flex items-center justify-center gap-2 bg-secondary hover:bg-secondary/80 text-foreground py-3 rounded-xl border border-border/50 transition-all font-bold text-sm"
                >
                    <Lock className="w-4 h-4 text-secondary-foreground" />
                    <span>SSO</span>
                </motion.button>
            </div>
            </div>

            {/* Divider / Spacer */}
            <div className="h-4"></div>

            {/* Footer Action */}
            <button
                onClick={() => router.push(mode === "signUp" ? "/sign-in" : "/sign-up")}
                className="flex items-center justify-center gap-2 w-full bg-transparent hover:bg-secondary/50 text-secondary-foreground hover:text-foreground py-3 rounded-xl border border-transparent hover:border-border/50 transition-all font-bold text-sm tracking-wide group"
            >
                {mode === "signUp" ? (
                    <>
                        <span>Log in instead</span>
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </>
                ) : (
                    <>
                        <span>Create Account</span>
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </>
                )}
            </button>

            {/* Terms */}
            <p className="text-[11px] text-center text-gray-500 mt-4 px-4 font-medium">
                By clicking continue, you agree to our <Link href="/terms" className="underline hover:text-white transition-colors">Terms of Service</Link> and <Link href="/privacy" className="underline hover:text-white transition-colors">Privacy Policy</Link>.
            </p>
        </motion.div>
    );
}
