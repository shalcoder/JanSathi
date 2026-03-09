'use client';

import React, { useState, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Mail, KeyRound, Eye, EyeOff, Phone, MessageSquare, CheckCircle2, Loader2 } from 'lucide-react';
import { signIn, confirmSignIn } from 'aws-amplify/auth';

type AuthTab = 'email' | 'phone';
type OTPStep = 'phone' | 'otp';

export default function SignIn() {
    const router = useRouter();

    // ── Tab state ──
    const [tab, setTab] = useState<AuthTab>('phone');

    // ── Email/Password state ──
    const [email, setEmail]       = useState('');
    const [password, setPassword] = useState('');
    const [showPwd, setShowPwd]   = useState(false);

    // ── Phone/OTP state ──
    const [phone, setPhone]           = useState('');
    const [otpStep, setOtpStep]       = useState<OTPStep>('phone');
    const [otp, setOtp]               = useState<string[]>(Array(6).fill(''));
    const otpRefs                      = useRef<(HTMLInputElement | null)[]>([]);
    const [smsSent, setSmsSent]       = useState(false);

    // ── Shared ──
    const [loading, setLoading]   = useState(false);
    const [error, setError]       = useState('');

    // ─────────────────────────────────────────────────────────────────────────
    // Email / Password sign-in
    // ─────────────────────────────────────────────────────────────────────────

    const handleEmailSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const { isSignedIn, nextStep } = await signIn({ username: email.trim(), password });
            if (nextStep.signInStep === 'CONFIRM_SIGN_UP') {
                router.push(`/auth/confirm?email=${encodeURIComponent(email)}`);
                return;
            }
            if (nextStep.signInStep === 'RESET_PASSWORD') {
                router.push('/auth/reset-password');
                return;
            }
            if (isSignedIn) await redirectAfterLogin();
        } catch (err: unknown) {
            const e = err as { name?: string; message?: string };
            if (e.name === 'UserNotFoundException' || e.name === 'NotAuthorizedException') {
                setError('Incorrect email or password.');
            } else if (e.name === 'UserNotConfirmedException') {
                router.push(`/auth/confirm?email=${encodeURIComponent(email)}`);
            } else {
                setError(e.message || 'Sign in failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    // ─────────────────────────────────────────────────────────────────────────
    // Phone / OTP sign-in
    // ─────────────────────────────────────────────────────────────────────────

    // Normalise phone to E.164 format (+91XXXXXXXXXX)
    const normalizePhone = (raw: string) => {
        const digits = raw.replace(/\D/g, '');
        if (digits.startsWith('91') && digits.length === 12) return `+${digits}`;
        if (digits.length === 10) return `+91${digits}`;
        return `+${digits}`;
    };

    const handleSendOTP = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!phone.replace(/\D/g, '').match(/^\d{10,12}$/)) {
            setError('Please enter a valid 10-digit mobile number.');
            return;
        }
        setError('');
        setLoading(true);
        try {
            const normalized = normalizePhone(phone);
            // Cognito Custom Auth flow — OTP delivered as Cognito challenge
            await signIn({
                username: normalized,
                options: { authFlowType: 'CUSTOM_WITHOUT_SRP' },
            });
            setSmsSent(true);
            setOtpStep('otp');
            setTimeout(() => otpRefs.current[0]?.focus(), 100);
        } catch (err: unknown) {
            const e = err as { name?: string; message?: string };
            // If user doesn't exist in Cognito, still show OTP step (graceful)
            if (e.name === 'UserNotFoundException') {
                setError('Mobile number not registered. Please sign up first.');
            } else if (e.name === 'NotAuthorizedException') {
                // Might still go to challenge — attempt to proceed
                setSmsSent(true);
                setOtpStep('otp');
                setTimeout(() => otpRefs.current[0]?.focus(), 100);
            } else {
                setError(e.message || 'Unable to send OTP. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleOTPChange = (idx: number, val: string) => {
        const digit = val.replace(/\D/g, '').slice(-1);
        const next = [...otp];
        next[idx] = digit;
        setOtp(next);
        if (digit && idx < 5) otpRefs.current[idx + 1]?.focus();
        // Auto-submit when all 6 digits filled
        if (next.every(d => d) && next.join('').length === 6) {
            handleVerifyOTP(next.join(''));
        }
    };

    const handleOTPKeyDown = (idx: number, e: React.KeyboardEvent) => {
        if (e.key === 'Backspace' && !otp[idx] && idx > 0) {
            otpRefs.current[idx - 1]?.focus();
        }
    };

    const handleVerifyOTP = async (code?: string) => {
        const otpCode = code || otp.join('');
        if (otpCode.length < 6) { setError('Enter the complete 6-digit OTP.'); return; }
        setError('');
        setLoading(true);
        try {
            const { isSignedIn } = await confirmSignIn({ challengeResponse: otpCode });
            if (isSignedIn) await redirectAfterLogin();
        } catch (err: unknown) {
            const e = err as { name?: string; message?: string };
            if (e.name === 'CodeMismatchException') {
                setError('Incorrect OTP. Please try again.');
            } else if (e.name === 'ExpiredCodeException') {
                setError('OTP expired. Please request a new one.');
                setOtpStep('phone');
                setOtp(Array(6).fill(''));
            } else {
                setError(e.message || 'OTP verification failed.');
            }
        } finally {
            setLoading(false);
        }
    };

    // ─────────────────────────────────────────────────────────────────────────
    // Redirect after successful login
    // ─────────────────────────────────────────────────────────────────────────

    const redirectAfterLogin = async () => {
        try {
            const { getToken }    = await import('@/hooks/useAuth');
            const { buildClient } = await import('@/services/api');
            const tok    = await getToken();
            const client = buildClient(tok || undefined);
            const res    = await client.get('/v1/profile');
            const data   = res.data?.data;
            if (data && data.profile_complete === false) {
                router.push('/onboarding');
            } else {
                router.push('/dashboard');
            }
        } catch {
            router.push('/dashboard');
        }
    };

    // ─────────────────────────────────────────────────────────────────────────
    // Render
    // ─────────────────────────────────────────────────────────────────────────

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-6 relative overflow-hidden">
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/10 via-background to-background" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md bg-card/80 backdrop-blur-2xl border border-border/50 rounded-3xl shadow-2xl overflow-hidden relative z-10"
            >
                <div className="p-8">
                    <Link href="/" className="inline-flex items-center gap-2 text-sm text-secondary-foreground hover:text-foreground mb-8 transition-colors">
                        <ArrowLeft className="w-4 h-4" /> Back to Home
                    </Link>

                    <div className="mb-6 text-center">
                        <div className="mx-auto w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-orange-500/20 mb-4">JS</div>
                        <h1 className="text-3xl font-bold tracking-tight text-foreground mb-2">Welcome Back</h1>
                        <p className="text-sm text-secondary-foreground font-medium opacity-70">Sign in to your JanSathi account</p>
                    </div>

                    {/* Tab switcher */}
                    <div className="flex rounded-xl border border-border/50 overflow-hidden mb-6 bg-background/30">
                        <button
                            type="button"
                            onClick={() => { setTab('phone'); setError(''); }}
                            className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-semibold transition-all ${tab === 'phone' ? 'bg-primary text-white shadow-sm' : 'text-secondary-foreground hover:text-foreground'}`}
                        >
                            <Phone className="w-4 h-4" /> Mobile OTP
                        </button>
                        <button
                            type="button"
                            onClick={() => { setTab('email'); setError(''); }}
                            className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-sm font-semibold transition-all ${tab === 'email' ? 'bg-primary text-white shadow-sm' : 'text-secondary-foreground hover:text-foreground'}`}
                        >
                            <Mail className="w-4 h-4" /> Email
                        </button>
                    </div>

                    {/* Error banner */}
                    <AnimatePresence>
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500 text-sm font-medium"
                            >
                                {error}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <AnimatePresence mode="wait">
                        {/* ── Phone / OTP Tab ── */}
                        {tab === 'phone' && (
                            <motion.div key="phone-tab" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }}>
                                {otpStep === 'phone' ? (
                                    <form onSubmit={handleSendOTP} className="space-y-4">
                                        <div>
                                            <label className="block text-xs font-semibold text-secondary-foreground uppercase tracking-wider mb-2">
                                                Mobile Number
                                            </label>
                                            <div className="relative">
                                                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-foreground/50" />
                                                <span className="absolute left-10 top-1/2 -translate-y-1/2 text-sm text-secondary-foreground/60 font-medium">+91</span>
                                                <input
                                                    type="tel"
                                                    value={phone}
                                                    onChange={(e) => setPhone(e.target.value)}
                                                    className="w-full pl-20 pr-4 py-3 bg-input border border-border rounded-xl text-foreground placeholder:text-secondary-foreground/40 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                                                    placeholder="98765 43210"
                                                    autoComplete="tel"
                                                    maxLength={14}
                                                    required
                                                />
                                            </div>
                                        </div>
                                        <button
                                            type="submit"
                                            disabled={loading}
                                            className="w-full py-3 bg-primary text-white rounded-xl font-bold text-sm uppercase tracking-wider shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2"
                                        >
                                            {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Sending OTP…</> : <><MessageSquare className="w-4 h-4" /> Send OTP</>}
                                        </button>
                                    </form>
                                ) : (
                                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
                                        {/* SMS sent confirmation */}
                                        {smsSent && (
                                            <div className="flex items-center gap-3 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
                                                <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                                                <p className="text-sm text-emerald-600 font-medium">
                                                    OTP sent to +91 {phone.replace(/\D/g, '').slice(-10).replace(/(\d{5})(\d{5})/, '$1 $2')}
                                                </p>
                                            </div>
                                        )}

                                        <div>
                                            <label className="block text-xs font-semibold text-secondary-foreground uppercase tracking-wider mb-4 text-center">
                                                Enter 6-digit OTP
                                            </label>
                                            <div className="flex gap-2 justify-center">
                                                {otp.map((digit, idx) => (
                                                    <input
                                                        key={idx}
                                                        ref={el => { otpRefs.current[idx] = el; }}
                                                        type="text"
                                                        inputMode="numeric"
                                                        pattern="[0-9]*"
                                                        maxLength={1}
                                                        value={digit}
                                                        onChange={(e) => handleOTPChange(idx, e.target.value)}
                                                        onKeyDown={(e) => handleOTPKeyDown(idx, e)}
                                                        className="w-12 h-14 text-center text-xl font-bold bg-input border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                                                        aria-label={`OTP digit ${idx + 1}`}
                                                    />
                                                ))}
                                            </div>
                                        </div>

                                        <button
                                            type="button"
                                            onClick={() => handleVerifyOTP()}
                                            disabled={loading || otp.join('').length < 6}
                                            className="w-full py-3 bg-primary text-white rounded-xl font-bold text-sm uppercase tracking-wider shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2"
                                        >
                                            {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Verifying…</> : 'Verify OTP'}
                                        </button>

                                        <button
                                            type="button"
                                            onClick={() => { setOtpStep('phone'); setOtp(Array(6).fill('')); setError(''); setSmsSent(false); }}
                                            className="w-full text-center text-sm text-secondary-foreground hover:text-foreground transition-colors"
                                        >
                                            ← Change mobile number / Resend OTP
                                        </button>
                                    </motion.div>
                                )}
                            </motion.div>
                        )}

                        {/* ── Email / Password Tab ── */}
                        {tab === 'email' && (
                            <motion.form key="email-tab" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} onSubmit={handleEmailSubmit} className="space-y-4">
                                <div>
                                    <label htmlFor="email" className="block text-xs font-semibold text-secondary-foreground uppercase tracking-wider mb-2">
                                        Email
                                    </label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-foreground/50" />
                                        <input
                                            id="email"
                                            type="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            className="w-full pl-11 pr-4 py-3 bg-input border border-border rounded-xl text-foreground placeholder:text-secondary-foreground/40 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                                            placeholder="your.email@example.com"
                                            autoComplete="email"
                                            required
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label htmlFor="password" className="block text-xs font-semibold text-secondary-foreground uppercase tracking-wider mb-2">
                                        Password
                                    </label>
                                    <div className="relative">
                                        <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-foreground/50" />
                                        <input
                                            id="password"
                                            type={showPwd ? 'text' : 'password'}
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            className="w-full pl-11 pr-11 py-3 bg-input border border-border rounded-xl text-foreground placeholder:text-secondary-foreground/40 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                                            placeholder="••••••••"
                                            autoComplete="current-password"
                                            required
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPwd(v => !v)}
                                            aria-label={showPwd ? 'Hide password' : 'Show password'}
                                            className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-foreground/50 hover:text-foreground"
                                        >
                                            {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                        </button>
                                    </div>
                                </div>

                                <div className="flex justify-end">
                                    <Link href="/auth/forgot-password" className="text-sm text-primary hover:underline font-medium">
                                        Forgot password?
                                    </Link>
                                </div>

                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full py-3 bg-primary text-white rounded-xl font-bold text-sm uppercase tracking-wider shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {loading ? 'Signing in…' : 'Sign In'}
                                </button>
                            </motion.form>
                        )}
                    </AnimatePresence>

                    <p className="text-center text-sm text-secondary-foreground mt-5">
                        Don&apos;t have an account?{' '}
                        <Link href="/auth/signup" className="text-primary font-semibold hover:underline">
                            Create one
                        </Link>
                    </p>
                </div>

                <div className="bg-secondary/10 p-4 text-center border-t border-border/50">
                    <p className="text-[10px] text-secondary-foreground opacity-60 font-bold uppercase tracking-widest">
                        Powered by AWS Cognito — End-to-end encrypted
                    </p>
                </div>
            </motion.div>
        </div>
    );
}
