'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Mail, Lock, User, Chrome, ArrowRight, Loader2, Shield, Check } from 'lucide-react';

export default function SignUpPage() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [acceptTerms, setAcceptTerms] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleEmailSignUp = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        // Validation
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            setIsLoading(false);
            return;
        }

        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters');
            setIsLoading(false);
            return;
        }

        if (!acceptTerms) {
            setError('Please accept the terms and conditions');
            setIsLoading(false);
            return;
        }

        // Demo authentication - replace with real auth provider
        setTimeout(() => {
            localStorage.setItem('jansathi_user', JSON.stringify({
                email: formData.email,
                name: formData.name,
                signedIn: true,
                timestamp: new Date().toISOString()
            }));
            router.push('/dashboard');
        }, 1000);
    };

    const handleGoogleSignUp = () => {
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

            {/* Sign Up Card */}
            <div className="relative z-10 w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center gap-2 mb-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                            <span className="font-black text-xl text-white">JS</span>
                        </div>
                        <span className="text-3xl font-black tracking-tighter text-white">JanSathi</span>
                    </div>
                    <p className="text-slate-400 text-sm">Create your account to get started</p>
                </div>

                {/* Main Card */}
                <div className="glass-panel p-8 rounded-3xl border border-white/10 backdrop-blur-xl bg-black/20 shadow-2xl">
                    <h1 className="text-2xl font-black text-white mb-6">Create Account</h1>

                    {error && (
                        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    {/* Google Sign Up */}
                    <button
                        onClick={handleGoogleSignUp}
                        disabled={isLoading}
                        className="w-full flex items-center justify-center gap-3 px-6 py-3 bg-white hover:bg-gray-100 text-gray-900 rounded-xl font-bold transition-all shadow-lg disabled:opacity-50 mb-6"
                    >
                        <Chrome className="w-5 h-5" />
                        Sign up with Google
                    </button>

                    {/* Divider */}
                    <div className="relative mb-6">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-white/10"></div>
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-slate-950 px-2 text-slate-500 font-bold">Or sign up with email</span>
                        </div>
                    </div>

                    {/* Email Sign Up Form */}
                    <form onSubmit={handleEmailSignUp} className="space-y-4">
                        <div>
                            <label className="block text-sm font-bold text-slate-300 mb-2">Full Name</label>
                            <div className="relative">
                                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    placeholder="Rajesh Kumar"
                                    className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/10 transition-all"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-300 mb-2">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
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
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    placeholder="••••••••"
                                    className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/10 transition-all"
                                    required
                                />
                            </div>
                            <p className="text-xs text-slate-500 mt-1">Must be at least 8 characters</p>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-300 mb-2">Confirm Password</label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                <input
                                    type="password"
                                    name="confirmPassword"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    placeholder="••••••••"
                                    className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/10 transition-all"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="flex items-start gap-3 cursor-pointer">
                                <div className="relative flex items-center">
                                    <input
                                        type="checkbox"
                                        checked={acceptTerms}
                                        onChange={(e) => setAcceptTerms(e.target.checked)}
                                        className="w-5 h-5 rounded border-white/10 bg-white/5 text-blue-600 focus:ring-blue-500 focus:ring-offset-slate-950"
                                    />
                                    {acceptTerms && (
                                        <Check className="absolute w-4 h-4 text-white pointer-events-none left-0.5 top-0.5" />
                                    )}
                                </div>
                                <span className="text-sm text-slate-400">
                                    I agree to the{' '}
                                    <Link href="/terms" className="text-blue-400 hover:text-blue-300 font-semibold">
                                        Terms of Service
                                    </Link>{' '}
                                    and{' '}
                                    <Link href="/privacy" className="text-blue-400 hover:text-blue-300 font-semibold">
                                        Privacy Policy
                                    </Link>
                                </span>
                            </label>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-all shadow-xl shadow-blue-600/20 disabled:opacity-50 group"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Creating Account...
                                </>
                            ) : (
                                <>
                                    Create Account
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    {/* Sign In Link */}
                    <div className="mt-6 text-center">
                        <p className="text-slate-400 text-sm">
                            Already have an account?{' '}
                            <Link href="/sign-in" className="text-blue-400 hover:text-blue-300 font-bold">
                                Sign in
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
