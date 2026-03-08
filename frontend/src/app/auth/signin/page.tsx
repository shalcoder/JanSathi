'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft, Lock, Mail, KeyRound } from 'lucide-react';

export default function SignIn() {
    const router = useRouter();
    const [activeTab, setActiveTab] = useState<'signin' | 'signup'>('signin');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (activeTab === 'signup' && password !== confirmPassword) {
                setError('Passwords do not match');
                setLoading(false);
                return;
            }

            // For demo purposes, allow any email/password
            // In production, this would call your backend API
            if (email && password) {
                // Store a simple auth token
                localStorage.setItem('jansathi_auth', 'true');
                localStorage.setItem('jansathi_user', email);
                
                // Redirect to dashboard
                router.push('/dashboard');
            } else {
                setError('Please fill in all fields');
            }
        } catch (err) {
            setError('Authentication failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Ambience */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/10 via-background to-background"></div>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md bg-card border border-border/50 rounded-3xl shadow-2xl overflow-hidden relative z-10"
            >
                <div className="p-8">
                    <Link href="/" className="inline-flex items-center gap-2 text-sm text-secondary-foreground hover:text-foreground mb-8 transition-colors">
                        <ArrowLeft className="w-4 h-4" /> Back to Home
                    </Link>

                    <div className="mb-6 text-center">
                        <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mx-auto mb-4">
                            <Lock className="w-6 h-6 text-primary" />
                        </div>
                        <h1 className="text-2xl font-bold text-foreground">Welcome to JanSathi</h1>
                        <p className="text-secondary-foreground">Sign in with your Bharat Cloud ID</p>
                    </div>

                    {/* Tabs */}
                    <div className="flex border-b border-border/50 mb-6">
                        <button
                            onClick={() => setActiveTab('signin')}
                            className={`flex-1 pb-3 text-sm font-medium transition-colors ${
                                activeTab === 'signin'
                                    ? 'text-primary border-b-2 border-primary'
                                    : 'text-secondary-foreground hover:text-foreground'
                            }`}
                        >
                            Sign In
                        </button>
                        <button
                            onClick={() => setActiveTab('signup')}
                            className={`flex-1 pb-3 text-sm font-medium transition-colors ${
                                activeTab === 'signup'
                                    ? 'text-primary border-b-2 border-primary'
                                    : 'text-secondary-foreground hover:text-foreground'
                            }`}
                        >
                            Create Account
                        </button>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && (
                            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500 text-sm">
                                {error}
                            </div>
                        )}

                        <div>
                            <label htmlFor="email" className="block text-xs font-semibold text-secondary-foreground uppercase tracking-wider mb-2">
                                Email
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-foreground" />
                                <input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full pl-11 pr-4 py-3 bg-background/50 border border-border/50 rounded-xl text-foreground placeholder:text-secondary-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                                    placeholder="your.email@example.com"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-xs font-semibold text-secondary-foreground uppercase tracking-wider mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-foreground" />
                                <input
                                    id="password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full pl-11 pr-4 py-3 bg-background/50 border border-border/50 rounded-xl text-foreground placeholder:text-secondary-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        {activeTab === 'signup' && (
                            <div>
                                <label htmlFor="confirmPassword" className="block text-xs font-semibold text-secondary-foreground uppercase tracking-wider mb-2">
                                    Confirm Password
                                </label>
                                <div className="relative">
                                    <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-foreground" />
                                    <input
                                        id="confirmPassword"
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        className="w-full pl-11 pr-4 py-3 bg-background/50 border border-border/50 rounded-xl text-foreground placeholder:text-secondary-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                                        placeholder="••••••••"
                                        required
                                    />
                                </div>
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 bg-primary hover:bg-primary/90 text-white font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Please wait...' : activeTab === 'signin' ? 'Sign in' : 'Create Account'}
                        </button>
                    </form>

                    {activeTab === 'signin' && (
                        <div className="mt-4 text-center">
                            <Link href="/auth/forgot-password" className="text-sm text-primary hover:underline">
                                Forgot your password?
                            </Link>
                        </div>
                    )}
                </div>

                <div className="bg-secondary/30 p-4 text-center">
                    <p className="text-xs text-secondary-foreground opacity-60">
                        &copy; 2026 JanSathi Protocol. All Rights Reserved.
                    </p>
                </div>
            </motion.div>
        </div>
    );
}
