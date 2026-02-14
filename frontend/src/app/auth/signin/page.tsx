'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft, Lock, Loader2, CheckCircle2 } from 'lucide-react';

export default function SignIn() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });

    const handleDemoLogin = async () => {
        setIsLoading(true);
        setFormData({ email: 'judge@jansathi.in', password: 'demo-password' });

        // Simulate API call
        setTimeout(() => {
            localStorage.setItem('jansathi_auth_token', 'demo-token-123');
            router.push('/dashboard');
        }, 1500);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        // Demo credentials check
        if (formData.email === 'judge@jansathi.in' && formData.password === 'demo123') {
            setTimeout(() => {
                localStorage.setItem('jansathi_auth_token', 'demo-token-123');
                router.push('/dashboard');
            }, 1500);
        } else {
            setTimeout(() => {
                setIsLoading(false);
                setError('Invalid credentials. Try using the Demo Login.');
            }, 1000);
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

                    <div className="mb-8 text-center">
                        <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mx-auto mb-4">
                            <Lock className="w-6 h-6 text-primary" />
                        </div>
                        <h1 className="text-2xl font-bold text-foreground">Welcome Back</h1>
                        <p className="text-secondary-foreground">Sign in to access your JanSathi dashboard</p>
                    </div>

                    {error && (
                        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-500 text-sm font-medium flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-red-500"></div>
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-xs font-bold uppercase tracking-widest text-secondary-foreground mb-2">Email Address</label>
                            <input
                                type="email"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                className="w-full px-4 py-3 bg-secondary/30 border border-border/50 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-foreground"
                                placeholder="name@example.com"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-bold uppercase tracking-widest text-secondary-foreground mb-2">Password</label>
                            <input
                                type="password"
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                className="w-full px-4 py-3 bg-secondary/30 border border-border/50 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-foreground"
                                placeholder="••••••••"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-3.5 bg-foreground text-background font-bold rounded-xl hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
                        >
                            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Sign In"}
                        </button>
                    </form>

                    <div className="mt-6 pt-6 border-t border-border">
                        <button
                            onClick={handleDemoLogin}
                            disabled={isLoading}
                            className="w-full py-3 bg-primary/10 text-primary font-bold rounded-xl hover:bg-primary/20 transition-colors flex items-center justify-center gap-2 group"
                        >
                            <CheckCircle2 className="w-5 h-5 group-hover:scale-110 transition-transform" />
                            Use Judge Demo Login
                        </button>
                        <p className="text-center text-xs text-secondary-foreground mt-2 opacity-60">Credentials: judge@jansathi.in / demo123</p>
                    </div>
                </div>

                <div className="bg-secondary/30 p-4 text-center">
                    <p className="text-sm text-secondary-foreground">Don't have an account? <Link href="/auth/signup" className="text-primary font-bold hover:underline">Sign Up</Link></p>
                </div>
            </motion.div>
        </div>
    );
}
