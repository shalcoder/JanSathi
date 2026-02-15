'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Book, Shield, Mic, FileText, Zap, Key, Server, Users } from 'lucide-react';
import Link from 'next/link';

export default function Documentation() {
    return (
        <main className="min-h-screen bg-background text-foreground pb-20 relative overflow-hidden">
            {/* Ambient Background */}
            <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808008_1px,transparent_1px),linear-gradient(to_bottom,#80808008_1px,transparent_1px)] bg-[size:24px_24px]"></div>
                <div className="absolute right-0 top-0 -z-10 m-auto h-[500px] w-[500px] rounded-full bg-primary/5 blur-[100px]"></div>
            </div>

            <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4 backdrop-blur-md border-b border-border/50">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold shadow-lg">JS</div>
                        <span className="font-bold text-lg">JanSathi Docs</span>
                    </div>
                    <Link href="/" className="text-sm font-bold text-secondary-foreground hover:text-primary transition-colors">
                        Back to Home
                    </Link>
                </div>
            </nav>

            <div className="pt-32 px-6 max-w-7xl mx-auto relative z-10">

                {/* Hero */}
                <div className="mb-20">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="max-w-3xl"
                    >
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 text-[10px] font-bold uppercase tracking-widest mb-6 border border-blue-100 dark:border-blue-800">
                            v2.5.0 Release
                        </div>
                        <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6 leading-tight">
                            Platform <span className="text-primary">Documentation</span>
                        </h1>
                        <p className="text-xl text-secondary-foreground leading-relaxed max-w-2xl">
                            Everything you need to verify, integrate, and understand the JanSathi Sovereign Cloud architecture.
                        </p>
                    </motion.div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">

                    {/* Navigation Sidebar (Sticky) */}
                    <div className="hidden lg:block space-y-8 sticky top-32 h-fit">
                        <div>
                            <h3 className="font-bold text-foreground mb-4 px-2">Getting Started</h3>
                            <ul className="space-y-1">
                                <NavItem href="#auth" label="Authentication & Demo" active />
                                <NavItem href="#voice" label="Voice Capabilities" />
                                <NavItem href="#docs" label="Document Analysis" />
                            </ul>
                        </div>
                        <div>
                            <h3 className="font-bold text-foreground mb-4 px-2">Architecture</h3>
                            <ul className="space-y-1">
                                <NavItem href="#stack" label="Tech Stack" />
                                <NavItem href="#security" label="Privacy & Security" />
                                <NavItem href="#api" label="API Reference" />
                            </ul>
                        </div>
                    </div>

                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-16">

                        {/* Authentication */}
                        <section id="auth" className="scroll-mt-32">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/20 text-orange-600"><Key className="w-6 h-6" /></div>
                                <h2 className="text-3xl font-bold text-foreground">Authentication</h2>
                            </div>
                            <div className="prose dark:prose-invert max-w-none text-secondary-foreground">
                                <p className="mb-4">
                                    JanSathi v2.5 introduces a robust authentication flow designed for both security and ease of evaluation.
                                </p>
                                <div className="bg-card border border-border/50 rounded-2xl p-6 mb-6">
                                    <h3 className="text-lg font-bold text-foreground mb-2">Hackathon Judge Access</h3>
                                    <p className="text-sm mb-4">
                                        We have implemented a specific <strong>Demo Login</strong> flow to bypass registration:
                                    </p>
                                    <ol className="list-decimal pl-5 space-y-2 text-sm font-medium">
                                        <li>Navigate to the <strong>Sign In</strong> page.</li>
                                        <li>Click the yellow <strong>{'"Use Judge Demo Login"'}</strong> button.</li>
                                        <li>System auto-fills credentials: <code>judge@jansathi.in</code></li>
                                        <li>Instant access to the Dashboard with pre-populated dummy data.</li>
                                    </ol>
                                </div>
                            </div>
                        </section>

                        {/* Voice */}
                        <section id="voice" className="scroll-mt-32">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900/20 text-purple-600"><Mic className="w-6 h-6" /></div>
                                <h2 className="text-3xl font-bold text-foreground">Voice Capabilities</h2>
                            </div>
                            <p className="text-secondary-foreground mb-6 leading-relaxed">
                                Our {'"Matrubhasha Core"'} engine enables seamless voice interaction in Indian languages. It uses the Web Speech API for low-latency input and processes intent locally before querying the knowledge base.
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <FeatureCard title="Hindi (Hi-IN)" desc="Native speech recognition with dialect support." />
                                <FeatureCard title="English (En-IN)" desc="Optimized for Indian accents and terminology." />
                                <FeatureCard title="Kannada (Kn-IN)" desc="Beta support for Karnataka region schemes." />
                            </div>
                        </section>

                        {/* Documents */}
                        <section id="docs" className="scroll-mt-32">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/20 text-blue-600"><FileText className="w-6 h-6" /></div>
                                <h2 className="text-3xl font-bold text-foreground">Drishti Document Analysis</h2>
                            </div>
                            <p className="text-secondary-foreground mb-6 leading-relaxed">
                                The Drishti engine allows users to upload photos of physical documents (Ration Cards, Aadhaar) to automatically extract details and find eligible schemes.
                            </p>
                            <div className="p-4 bg-secondary/30 rounded-xl border border-border/50 text-sm font-mono text-foreground">
                                Supported Formats: .JPG, .PNG, .PDF (Max 5MB)
                            </div>
                        </section>

                        {/* Tech Stack */}
                        <section id="stack" className="scroll-mt-32">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2 rounded-lg bg-emerald-100 dark:bg-emerald-900/20 text-emerald-600"><Server className="w-6 h-6" /></div>
                                <h2 className="text-3xl font-bold text-foreground">Tech Stack</h2>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                                <StackItem label="Frontend" val="Next.js 15 (App Router)" />
                                <StackItem label="Styling" val="Tailwind CSS + Framer Motion" />
                                <StackItem label="Backend" val="Python Flask (REST API)" />
                                <StackItem label="Database" val="SQLite / AWS DynamoDB" />
                                <StackItem label="AI Model" val="Gemini / AWS Bedrock" />
                                <StackItem label="Auth" val="Custom JWT / Clerk (Ready)" />
                            </div>
                        </section>

                    </div>
                </div>

                <div className="mt-20 py-10 border-t border-border/50 text-center">
                    <p className="text-xs font-bold text-secondary-foreground uppercase tracking-widest opacity-40">
                        © 2026 JanSathi Protocol • Documentation
                    </p>
                </div>
            </div>
        </main>
    );
}

function NavItem({ href, label, active }: { href: string, label: string, active?: boolean }) {
    return (
        <li>
            <a
                href={href}
                className={`block px-4 py-2 rounded-lg text-sm font-bold transition-colors ${active ? 'bg-primary/10 text-primary' : 'text-secondary-foreground hover:text-foreground hover:bg-secondary/50'}`}
            >
                {label}
            </a>
        </li>
    );
}

function FeatureCard({ title, desc }: { title: string, desc: string }) {
    return (
        <div className="p-5 rounded-2xl bg-card border border-border/50 shadow-sm">
            <h4 className="font-bold text-foreground mb-1">{title}</h4>
            <p className="text-xs text-secondary-foreground opacity-70">{desc}</p>
        </div>
    );
}

function StackItem({ label, val }: { label: string, val: string }) {
    return (
        <div className="p-4 rounded-xl bg-secondary/20 border border-border/50">
            <p className="text-[10px] font-bold text-secondary-foreground uppercase tracking-widest opacity-50 mb-1">{label}</p>
            <p className="font-bold text-sm text-foreground">{val}</p>
        </div>
    );
}
