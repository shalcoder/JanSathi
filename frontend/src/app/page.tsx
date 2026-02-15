'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Mic, ShieldCheck, Languages, Bot, Globe, Cpu, Server, Database, ChevronRight, Activity, Zap, Users, AlertTriangle, CheckCircle2, Cloud, Radio, Lock } from "lucide-react";
import BackendStatus from "@/components/BackendStatus";
import ImpactStats from "@/components/features/community/ImpactStats";
import { SignedIn, SignedOut, UserButton, SignOutButton } from "@clerk/nextjs";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background text-foreground overflow-x-hidden font-[family-name:var(--font-outfit)] selection:bg-primary/30 relative">

      {/* 1. Global Ambient Background */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
        <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-primary/20 opacity-20 blur-[100px] animate-pulse-slow"></div>
        <div className="absolute right-0 bottom-0 -z-10 h-[400px] w-[400px] rounded-full bg-accent/20 opacity-20 blur-[120px] animate-float-slow"></div>
      </div>

      {/* 2. Professional Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-4 sm:px-6 py-4 backdrop-blur-xl bg-background/70 border-b border-white/10 dark:border-white/5 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3 group cursor-pointer">
            <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center shadow-lg shadow-orange-500/20 group-hover:shadow-orange-500/40 transition-all duration-300">
              <span className="font-bold text-xl text-white">JS</span>
              <div className="absolute inset-0 rounded-xl bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </div>
            <span className="text-xl font-bold tracking-tight text-foreground">JanSathi</span>
          </div>

          <div className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-8">
              {['Mission', 'Features', 'How it Works', 'Architecture', 'Roadmap'].map((item) => (
                <a key={item} href={`#${item.toLowerCase().replace(/\s+/g, '-')}`} className="text-sm font-medium text-secondary-foreground hover:text-primary transition-colors hover:bg-secondary/50 px-3 py-1.5 rounded-lg">
                  {item}
                </a>
              ))}
            </div>

            <SignedOut>
              <Link
                href="/sign-in"
                className="px-6 py-2.5 bg-foreground text-background dark:bg-white dark:text-black rounded-lg font-bold text-sm shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-2"
              >
                Sign In
                <ArrowRight className="w-4 h-4" />
              </Link>
            </SignedOut>

            <SignedIn>
              <div className="flex items-center gap-4">
                <Link
                  href="/dashboard"
                  className="px-6 py-2.5 bg-primary text-white rounded-lg font-bold text-sm shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300"
                >
                  Dashboard
                </Link>
                <UserButton afterSignOutUrl="/" />
              </div>
            </SignedIn>
          </div>
        </div>
      </nav>

      {/* 3. Hero Section */}
      <section className="relative z-10 pt-32 pb-20 px-6 max-w-6xl mx-auto flex flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary/50 backdrop-blur-md border border-border/50 text-primary text-[11px] font-bold uppercase tracking-widest mb-8 hover:bg-secondary/80 transition-colors cursor-default"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
          </span>
          Sovereign Bharat Cloud • Version 2.5
        </motion.div>

        <motion.p
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.05 }}
          className="text-lg md:text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-orange-600 to-orange-400 mb-4 tracking-wider uppercase"
        >
          Jai Hind, JanSathi!
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="text-5xl sm:text-7xl lg:text-8xl font-bold tracking-tighter mb-8 leading-[1.1] text-foreground"
        >
          Empowering <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-orange-500 via-red-500 to-purple-600 animate-gradient-x">
            Bharat.
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="text-lg md:text-xl text-secondary-foreground/80 max-w-2xl mb-12 leading-relaxed font-medium"
        >
          A "Voice-First" AI Assistant that bridges the gap. Ask in your native language and instant access to government schemes. <span className="text-foreground font-semibold">Transforming complex portals into simple conversations.</span>
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="flex flex-col sm:flex-row gap-4 items-center w-full justify-center"
        >
          <SignedOut>
            <Link
              href="/sign-in"
              className="group relative w-full sm:w-auto px-8 py-4 bg-primary text-white rounded-2xl font-bold text-lg shadow-lg shadow-orange-500/25 hover:shadow-orange-500/40 hover:-translate-y-1 transition-all duration-300 overflow-hidden"
            >
              <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
              <span className="relative flex items-center justify-center gap-2">
                Start Chat
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>
          </SignedOut>

          <SignedIn>
            <Link
              href="/dashboard"
              className="group relative w-full sm:w-auto px-8 py-4 bg-primary text-white rounded-2xl font-bold text-lg shadow-lg shadow-orange-500/25 hover:shadow-orange-500/40 hover:-translate-y-1 transition-all duration-300 overflow-hidden"
            >
              <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
              <span className="relative flex items-center justify-center gap-2">
                Go to Dashboard
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>
          </SignedIn>

          <a
            href="#mission"
            className="w-full sm:w-auto px-8 py-4 bg-card border border-border/50 text-foreground rounded-2xl font-bold text-lg hover:bg-secondary/50 hover:border-primary/20 transition-all duration-300 flex items-center justify-center gap-2 group"
          >
            <Zap className="w-5 h-5 text-secondary-foreground group-hover:text-primary transition-colors" />
            See How
          </a>
        </motion.div>
      </section>

      {/* 4. The Problem (Mission) Section */}
      <section id="mission" className="relative z-10 py-24 px-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
          <div>
            <div className="inline-flex items-center gap-2 mb-6">
              <div className="h-px w-8 bg-red-500"></div>
              <p className="text-[11px] font-bold text-red-500 uppercase tracking-[0.3em]">The Challenge</p>
            </div>
            <h2 className="text-4xl lg:text-5xl font-bold tracking-tight text-foreground leading-tight mb-8">
              Why JanSathi? <br />
              <span className="text-secondary-foreground opacity-60">The Digital Divide.</span>
            </h2>
            <p className="text-lg text-secondary-foreground leading-relaxed mb-8">
              Communities in India, especially rural farmers and non-English speakers, struggle to access critical government schemes.
            </p>

            <div className="space-y-6">
              <ProblemItem
                icon={<Languages className="w-5 h-5 text-red-500" />}
                title="Language Barriers"
                desc="Most information is in English, excluding 90% of the population."
              />
              <ProblemItem
                icon={<AlertTriangle className="w-5 h-5 text-orange-500" />}
                title="Complex Portals"
                desc="Sites like PM-KISAN are hard to navigate for digital novices."
              />
              <ProblemItem
                icon={<Activity className="w-5 h-5 text-yellow-500" />}
                title="Low Digital Literacy"
                desc="Typing is difficult for many; voice is the natural interface."
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <StatCard number="800M+" label="Internet Users" desc="Mostly mobile-first" />
            <StatCard number="100M+" label="Farmers" desc="Eligible for PM-KISAN" />
            <StatCard number="22+" label="Languages" desc="Spoken across India" />
            <StatCard number="99%" label="Coverage" desc="Target for Schemes" />
          </div>
        </div>

        {/* Impact Visualizer — Advanced Feature */}
        <div className="mt-24 max-w-4xl mx-auto">
          <ImpactStats />
        </div>
      </section>

      {/* 5. Process / How it Works */}
      <section id="how-it-works" className="relative z-10 py-24 px-6 max-w-7xl mx-auto bg-secondary/20 rounded-[3rem] my-10">
        <div className="text-center mb-16">
          <p className="text-[11px] font-bold text-primary uppercase tracking-[0.3em] mb-4">Simple Workflow</p>
          <h2 className="text-4xl font-bold text-foreground">From Voice to Value in Seconds</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {/* Connecting Line */}
          <div className="hidden md:block absolute top-12 left-[16%] right-[16%] h-0.5 bg-gradient-to-r from-primary/0 via-primary/30 to-primary/0 border-t border-dashed border-primary/50 z-0"></div>

          <ProcessStep
            number="01"
            title="Speak Naturally"
            desc="Ask questions in Hindi, Tamil, or Kannada using your microphone."
            icon={<Mic className="w-6 h-6 text-white" />}
            color="bg-orange-500"
          />
          <ProcessStep
            number="02"
            title="AI Understands"
            desc="Our 'Sanskrit Logic Core' interprets your intent and searches government databases."
            icon={<Cpu className="w-6 h-6 text-white" />}
            color="bg-blue-600"
          />
          <ProcessStep
            number="03"
            title="Instant Help"
            desc="Get actionable answers, scheme links, and status updates immediately."
            icon={<CheckCircle2 className="w-6 h-6 text-white" />}
            color="bg-emerald-500"
          />
        </div>
      </section>

      {/* 6. Features Grid */}
      <section id="features" className="relative z-10 py-24 px-6 max-w-7xl mx-auto">
        <div className="flex flex-col items-start mb-16">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="flex items-center gap-2 mb-4"
          >
            <div className="h-px w-8 bg-primary"></div>
            <p className="text-[11px] font-bold text-primary uppercase tracking-[0.3em]">Core Capabilities</p>
          </motion.div>
          <h2 className="text-4xl lg:text-5xl font-bold tracking-tight text-foreground leading-tight">
            Comprehensive <span className="text-primary">Intelligence</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[minmax(180px,auto)]">
          <FeatureCard
            icon={<Mic className="w-8 h-8 text-white" />}
            title="Linguistic Neural Mesh"
            subtitle="Matrubhasha Core"
            description="Real-time voice synthesis in 22+ regional dialects using advanced transformer models."
            className="md:col-span-2 bg-gradient-to-br from-orange-500 to-red-600 text-white border-none shadow-orange-500/20"
            iconBg="bg-white/20"
            textColor="text-white"
            subTextColor="text-orange-100"
          />
          <FeatureCard
            icon={<Languages className="w-8 h-8 text-blue-500" />}
            title="Semantic Interpreter"
            subtitle="Sarkari Gyan"
            description="Deep understanding of 5000+ policy documents with query resolution."
            className="bg-card hover:border-blue-500/20"
            delay={0.1}
          />
          <FeatureCard
            icon={<Bot className="w-8 h-8 text-emerald-500" />}
            title="Drishti Vision V2"
            subtitle="Kagaz-Se-Data"
            description="State-of-the-art OCR pipeline for instant Aadhaar & Ration Card digitisation."
            className="bg-card hover:border-emerald-500/20"
            delay={0.2}
          />
          <FeatureCard
            icon={<ShieldCheck className="w-8 h-8 text-indigo-500" />}
            title="Zero-Knowledge Security"
            subtitle="Surakshit Protocol"
            description="End-to-end encryption ensures your personal data never leaves the secure Bharat cloud infrastructure."
            className="md:col-span-2 bg-card hover:border-indigo-500/20"
            delay={0.3}
          />
        </div>
      </section>

      {/* 7. Architecture Section */}
      <section id="architecture" className="relative z-10 py-24 px-6 max-w-7xl mx-auto">
        <div className="bg-card p-8 lg:p-16 rounded-[2.5rem] border border-border/50 relative overflow-hidden shadow-2xl">
          {/* Decorative Grid Background */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808008_1px,transparent_1px),linear-gradient(to_bottom,#80808008_1px,transparent_1px)] bg-[size:32px_32px] mask-gradient"></div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center relative z-10">
            <div className="space-y-10">
              <div>
                <div className="inline-flex items-center gap-3 px-4 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 mb-6">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-emerald-600 dark:text-emerald-400">System Status: Active</span>
                </div>
                <h2 className="text-3xl sm:text-5xl font-bold tracking-tight leading-tight mb-6 text-foreground">
                  AWS Cloud <br />
                  <span className="text-primary">Architecture.</span>
                </h2>
                <p className="text-secondary-foreground font-medium text-base leading-relaxed max-w-md opacity-80 mb-6">
                  Scalable, secure, and built for a billion users. Leveraging the full power of the AWS ecosystem.
                </p>

                <ul className="space-y-3">
                  <ArchListItem text="Frontend: Next.js (React) on Vercel/Amplify" />
                  <ArchListItem text="API Layer: Python Flask on AWS Lambda / EC2" />
                  <ArchListItem text="Voice: AWS Transcribe & AWS Polly Neural Engine" />
                  <ArchListItem text="Knowledge: AWS Kendra (Gov Index)" />
                  <ArchListItem text="Reasoning: Amazon Bedrock (Claude / Titan)" />
                </ul>
              </div>
            </div>

            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-primary to-purple-600 rounded-[2rem] blur opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
              <div className="aspect-video bg-background/50 backdrop-blur-xl rounded-[2rem] border border-white/10 flex items-center justify-center relative overflow-hidden shadow-2xl p-8">
                {/* Simple Schematic */}
                <div className="flex flex-col items-center justify-center gap-4 w-full h-full">
                  <div className="flex justify-between w-full opacity-60">
                    <div className="p-2 border border-border rounded bg-card/50 text-[10px] font-mono">APP</div>
                    <div className="p-2 border border-border rounded bg-card/50 text-[10px] font-mono">API</div>
                    <div className="p-2 border border-border rounded bg-card/50 text-[10px] font-mono">AI</div>
                  </div>
                  <div className="w-full h-px bg-gradient-to-r from-transparent via-primary to-transparent animate-pulse"></div>
                  <div className="w-20 h-20 rounded-full bg-primary/20 flex items-center justify-center animate-pulse-slow">
                    <Cloud className="w-10 h-10 text-primary" />
                  </div>
                  <p className="text-xs font-mono text-secondary-foreground">AWS REGION: AP-SOUTH-1</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 8. Roadmap Section */}
      <section id="roadmap" className="relative z-10 py-24 px-6 max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-[11px] font-bold text-primary uppercase tracking-[0.3em] mb-4">The Future</p>
          <h2 className="text-4xl font-bold text-foreground">Project Roadmap</h2>
        </div>

        <div className="space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border before:to-transparent">
          <RoadmapItem
            phase="Phase 1"
            title="Production Baseline"
            desc="Clean Architecture + Voice Q&A for Central Schemes. (Completed)"
            align="left"
          />
          <RoadmapItem
            phase="Phase 2"
            title="Visual Intelligence"
            desc="Drishti Multimodal analysis for scanning physical notices. (Completed)"
            align="right"
          />
          <RoadmapItem
            phase="Phase 3"
            title="Public Impact v3.0"
            desc="Hybrid Knowledge Graph + Mandi Market Integration. (Current)"
            align="left"
          />
          <RoadmapItem
            phase="Phase 4"
            title="Sovereign Agent"
            desc="'Fill for Me' - Autonomous form assistant via voice. (Future)"
            align="right"
          />
        </div>
      </section>

      {/* 9. Footer - Expanded */}
      <footer className="relative z-10 py-20 px-6 border-t border-border/50 bg-background/50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12">
          <div className="col-span-1 md:col-span-1">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center text-white font-bold text-lg shadow-lg">JS</div>
              <span className="font-bold text-xl tracking-tight text-foreground">JanSathi</span>
            </div>
            <p className="text-sm text-secondary-foreground leading-relaxed opacity-70">
              Empowering the last mile with Intelligence. Bringing government schemes to every doorstep in Bharat.
            </p>
          </div>

          <div>
            <h4 className="font-bold text-foreground mb-6">Product</h4>
            <ul className="space-y-4 text-sm text-secondary-foreground opacity-80">
              <li><a href="#features" className="hover:text-primary transition-colors">Features</a></li>
              <li><a href="#architecture" className="hover:text-primary transition-colors">Architecture</a></li>
              <li><a href="#roadmap" className="hover:text-primary transition-colors">Roadmap</a></li>
              <li><Link href="/dashboard" className="hover:text-primary transition-colors">Try Demo</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-foreground mb-6">Resources</h4>
            <ul className="space-y-4 text-sm text-secondary-foreground opacity-80">
              <li><Link href="/docs" className="hover:text-primary transition-colors">Documentation</Link></li>
              <li><Link href="/privacy" className="hover:text-primary transition-colors">Privacy Policy</Link></li>
              <li><Link href="/terms" className="hover:text-primary transition-colors">Terms of Service</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-foreground mb-6">Contact</h4>
            <ul className="space-y-4 text-sm text-secondary-foreground opacity-80">
              <li className="flex items-center gap-2"><Globe className="w-4 h-4" /> India Regional Node</li>
              <li className="flex items-center gap-2"><Lock className="w-4 h-4" /> Secure & Encrypted</li>
              <li className="mt-4">
                <span className="inline-block px-3 py-1 bg-emerald-500/10 text-emerald-600 rounded-full text-xs font-bold uppercase tracking-wider">System Online</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="max-w-7xl mx-auto mt-20 pt-8 border-t border-border flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-xs text-secondary-foreground/40 font-bold uppercase tracking-widest">
            © 2026 JanSathi Protocol. All rights reserved.
          </p>
          <div className="flex gap-6">
            {/* Social icons placeholders */}
          </div>
        </div>
      </footer>

      <BackendStatus />
    </main >
  );
}

// Sub-components for cleaner code

function ProblemItem({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) {
  return (
    <div className="flex gap-4">
      <div className="shrink-0 w-10 h-10 rounded-full bg-secondary flex items-center justify-center">
        {icon}
      </div>
      <div>
        <h3 className="font-bold text-foreground text-lg">{title}</h3>
        <p className="text-secondary-foreground text-sm leading-relaxed opacity-70">{desc}</p>
      </div>
    </div>
  );
}

function StatCard({ number, label, desc }: { number: string, label: string, desc: string }) {
  return (
    <div className="p-6 rounded-2xl bg-card border border-border/50 shadow-sm text-center transform hover:-translate-y-1 transition-transform">
      <p className="text-3xl lg:text-4xl font-bold text-primary mb-2">{number}</p>
      <p className="font-bold text-foreground text-sm uppercase tracking-wide">{label}</p>
      <p className="text-xs text-secondary-foreground opacity-50 mt-1">{desc}</p>
    </div>
  );
}

function ProcessStep({ number, title, desc, icon, color }: any) {
  return (
    <div className="relative z-10 flex flex-col items-center text-center group">
      <div className={`w-16 h-16 rounded-2xl ${color} flex items-center justify-center text-white shadow-lg mb-6 transform group-hover:scale-110 transition-transform duration-300`}>
        {icon}
      </div>
      <span className="absolute -top-4 -right-4 text-[4rem] font-bold text-foreground/5 opacity-0 group-hover:opacity-100 transition-opacity select-none -z-10">{number}</span>
      <h3 className="text-xl font-bold text-foreground mb-3">{title}</h3>
      <p className="text-secondary-foreground text-sm leading-relaxed max-w-xs mx-auto opacity-70">{desc}</p>
    </div>
  );
}

function ArchListItem({ text }: { text: string }) {
  return (
    <li className="flex items-start gap-3">
      <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary shrink-0"></div>
      <p className="text-sm font-medium text-foreground/80 leading-relaxed">{text}</p>
    </li>
  );
}

function RoadmapItem({ phase, title, desc, align }: any) {
  return (
    <div className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active`}>
      <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-background bg-card shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
        <div className="w-2.5 h-2.5 bg-primary rounded-full"></div>
      </div>
      <div className={`w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-6 rounded-2xl bg-card border border-border/50 shadow-sm hover:border-primary/30 transition-all ${align === 'left' ? 'mr-auto' : 'ml-auto'}`}>
        <div className="flex items-center justify-between mb-2">
          <span className="inline-block px-2 py-1 rounded-md bg-secondary text-[10px] font-bold text-secondary-foreground uppercase tracking-widest">{phase}</span>
        </div>
        <h3 className="font-bold text-lg text-foreground mb-2">{title}</h3>
        <p className="text-sm text-secondary-foreground opacity-70">{desc}</p>
      </div>
    </div>
  );
}

function FeatureCard({
  icon, title, subtitle, description, className = '', iconBg = 'bg-secondary', textColor = 'text-foreground', subTextColor = 'text-primary', delay = 0
}: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay }}
      className={`p-8 rounded-3xl border border-border/50 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between group ${className}`}
    >
      <div>
        <div className={`mb-6 w-14 h-14 rounded-2xl ${iconBg} flex items-center justify-center transition-transform duration-300 group-hover:scale-110 shadow-sm`}>
          {icon}
        </div>
        <div>
          {subtitle && (
            <p className={`text-[10px] font-bold ${subTextColor} uppercase tracking-[0.2em] mb-3 opacity-80`}>
              {subtitle}
            </p>
          )}
          <h3 className={`text-2xl font-bold mb-3 tracking-tight ${textColor}`}>{title}</h3>
          <p className={`text-sm font-medium leading-relaxed opacity-70 ${textColor === 'text-white' ? 'text-white' : 'text-secondary-foreground'}`}>
            {description}
          </p>
        </div>
      </div>
      <div className={`mt-8 flex items-center gap-2 text-xs font-bold uppercase tracking-wider ${textColor} opacity-0 group-hover:opacity-100 transition-opacity transform translate-y-2 group-hover:translate-y-0`}>
        Learn more <ChevronRight className="w-4 h-4" />
      </div>
    </motion.div>
  );
}

function TechItem({ icon, name, detail, delay }: { icon: React.ReactNode, name: string, detail: string, delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ delay }}
      className="flex items-center gap-4 p-4 rounded-2xl bg-background/50 border border-border/50 shadow-sm hover:border-primary/30 transition-colors"
    >
      <div className="p-2.5 rounded-xl bg-primary/10 text-primary">
        {icon}
      </div>
      <div>
        <p className="font-bold text-base leading-none mb-1.5 text-foreground">{name}</p>
        <p className="text-[9px] text-secondary-foreground font-bold uppercase tracking-widest opacity-60">{detail}</p>
      </div>
    </motion.div>
  );
}
