'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft, UserPlus, Loader2 } from 'lucide-react';

export default function SignUp() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: ''
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        // Simulate Signup API call
        setTimeout(() => {
            localStorage.setItem('jansathi_auth_token', 'demo-token-signup');
            // Set user profile data too in simulation
            localStorage.setItem('jansathi_user_name', formData.name);
            router.push('/dashboard');
        }, 1500);
    };

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-6 relative overflow-hidden">

            {/* Background Ambience */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-orange-500/10 via-background to-background"></div>
            </div>

            <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="w-full max-w-md bg-card border border-border/50 rounded-3xl shadow-2xl overflow-hidden relative z-10"
            >
                <div className="p-8">
                    <Link href="/" className="inline-flex items-center gap-2 text-sm text-secondary-foreground hover:text-foreground mb-8 transition-colors">
                        <ArrowLeft className="w-4 h-4" /> Back to Home
                    </Link>

                    <div className="mb-8">
                        <div className="w-12 h-12 bg-orange-500/10 rounded-xl flex items-center justify-center mb-4">
                            <UserPlus className="w-6 h-6 text-orange-500" />
                        </div>
                        <h1 className="text-2xl font-bold text-foreground">Create Account</h1>
                        <p className="text-secondary-foreground">Join JanSathi to unlock full access.</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-xs font-bold uppercase tracking-widest text-secondary-foreground mb-2">Full Name</label>
                            <input
                                type="text"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                className="w-full px-4 py-3 bg-secondary/30 border border-border/50 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-foreground"
                                placeholder="e.g. Rahul Kumar"
                                required
                            />
                        </div>
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

                        <div className="pt-4">
                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full py-3.5 bg-primary text-white font-bold rounded-xl hover:opacity-90 transition-opacity flex items-center justify-center gap-2 shadow-lg shadow-orange-500/25"
                            >
                                {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Create Account"}
                            </button>
                        </div>
                    </form>
                </div>

                <div className="bg-secondary/30 p-4 text-center">
                    <p className="text-sm text-secondary-foreground">Already have an account? <Link href="/auth/signin" className="text-primary font-bold hover:underline">Sign In</Link></p>
                </div>
            </motion.div>
        </div>
    );
}
