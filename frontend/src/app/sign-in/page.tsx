'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Mail, Lock, Chrome, ArrowRight, Loader2, Shield } from 'lucide-react';

export default function SignInPage() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleEmailSignIn = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        // Demo authentication - replace with real auth provider
        setTimeout(() => {
            if (email && password) {
                localStorage.setItem('jansathi_user', JSON.stringify({
                    email,
                    name: email.split('@')[0],
                    signedIn: true,
                    timestamp: new Date().toISOString()
                }));
                router.push('/dashboard');
            } else {
                setError('Please enter valid credentials');
                setIsLoading(false);
            }
        }, 1000);
    };

    const handleGoogleSignIn = () => {
        setIsLoading(true);
        // Demo - Replace with actual Google OAuth
        setTimeout(() => {
            localStorage.setItem('jansathi_user', JSON.stringify({
                email: 'demo@gmail.com',
                name: 'Google User',
                signedIn: true,
                provider: 'google',
                timestamp: new Date().toISOString()
            }));
            router.push('/dashboard');
        }, 1000);
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[120px] -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[120px] translate-x-1/2 translate-y-1/2"></div>

            {/* Sign In Card */}
            <div className="relative z-10 w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center gap-2 mb-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                            <span className="font-black text-xl text-white">JS</span>
                        </div>
                        <span className="text-3xl font-black tracking-tighter text-white">JanSathi</span>
                    </div>
                    <p className="text-slate-400 text-sm">Sign in to access your government assistant</p>
                </div>

                {/* Main Card */}
                <div className="glass-panel p-8 rounded-3xl border border-white/10 backdrop-blur-xl bg-black/20 shadow-2xl">
                    <h1 className="text-2xl font-black text-white mb-6">Welcome Back</h1>

                    {error && (
                        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    {/* Google Sign In */}
                    <button
                        onClick={handleGoogleSignIn}
                        disabled={isLoading}
                        className="w-full flex items-center justify-center gap-3 px-6 py-3 bg-white hover:bg-gray-100 text-gray-900 rounded-xl font-bold transition-all shadow-lg disabled:opacity-50 mb-6"
                    >
                        <Chrome className="w-5 h-5" />
                        Continue with Google
                    </button>

                    {/* Divider */}
                    <div className="relative mb-6">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-white/10"></div>
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-slate-950 px-2 text-slate-500 font-bold">Or continue with email</span>
                        </div>
                    </div>

                    {/* Email Sign In Form */}
                    <form onSubmit={handleEmailSignIn} className="space-y-4">
                        <div>
                            <label className="block text-sm font-bold text-slate-300 mb-2">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="you@example.com"
                                    className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/10 transition-all"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-300 mb-2">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/10 transition-all"
                                    required
                                />
                            </div>
                        </div>

                        <div className="flex items-center justify-between">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="checkbox" className="w-4 h-4 rounded border-white/10 bg-white/5 text-blue-600 focus:ring-blue-500 focus:ring-offset-slate-950" />
                                <span className="text-sm text-slate-400">Remember me</span>
                            </label>
                            <Link href="/forgot-password" className="text-sm text-blue-400 hover:text-blue-300 font-semibold">
                                Forgot password?
                            </Link>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-all shadow-xl shadow-blue-600/20 disabled:opacity-50 group"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Signing In...
                                </>
                            ) : (
                                <>
                                    Sign In
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    {/* Sign Up Link */}
                    <div className="mt-6 text-center">
                        <p className="text-slate-400 text-sm">
                            Don't have an account?{' '}
                            <Link href="/sign-up" className="text-blue-400 hover:text-blue-300 font-bold">
                                Sign up for free
                            </Link>
                        </p>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-6 text-center">
                    <div className="flex items-center justify-center gap-2 text-slate-500 text-xs">
                        <Shield className="w-3 h-3" />
                        <span>Secured by industry-standard encryption</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
