'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Mic, Languages, Bot, Globe, Cpu, Database, ChevronRight, Activity, Zap, Users, AlertTriangle, CheckCircle2, Radio, Lock, FileText, Shield } from "lucide-react";
import BackendStatus from "@/components/BackendStatus";
import ImpactStats from "@/components/features/community/ImpactStats";
import { SignedIn, SignedOut, UserButton } from "@clerk/nextjs";

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
          A <strong className="text-foreground">Telecom-Native Agentic Infrastructure</strong>. Speak in your language via a simple phone call, and our <span className="text-primary font-bold">10-Layer Agentic Pipeline</span> instantly connects you to schemes, market prices, and public services.
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
              <div className="h-px w-8 bg-primary"></div>
              <p className="text-[11px] font-bold text-primary uppercase tracking-[0.3em]">Our Mission</p>
            </div>
            <h2 className="text-4xl lg:text-5xl font-bold tracking-tight text-foreground leading-tight mb-8">
              Empowering the last mile <br />
              <span className="text-secondary-foreground opacity-60">with Intelligence.</span>
            </h2>
            <p className="text-xl text-secondary-foreground leading-relaxed mb-8 font-medium">
              Bringing government schemes to every doorstep in Bharat.
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
                desc="Navigating apps is difficult. A simple phone call is universally accessible."
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
            title="Toll-Free Voice Call"
            desc="Dial the number and speak naturally in local languages. No apps, no internet needed."
            icon={<Mic className="w-6 h-6 text-white" />}
            color="bg-orange-500"
          />
          <ProcessStep
            number="02"
            title="9-Agent Triage Engine"
            desc="Our ecosystem of 9 specialized AI agents instantly processes intent, verifies documents, and matches schemes."
            icon={<Cpu className="w-6 h-6 text-white" />}
            color="bg-blue-600"
          />
          <ProcessStep
            number="03"
            title="Automated Delivery"
            desc="Receive precise voice answers instantly, followed by SMS receipts, or a seamless transfer to a human expert."
            icon={<CheckCircle2 className="w-6 h-6 text-white" />}
            color="bg-emerald-500"
          />
        </div>
      </section>

      {/* 6. Features Grid */}
      <section id="features" className="relative z-10 py-24 px-6 max-w-7xl mx-auto">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-primary/10 blur-[120px] rounded-full pointer-events-none -z-10"></div>
        <div className="flex flex-col items-start mb-16 relative">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="flex items-center gap-2 mb-4"
          >
             <div className="h-px w-12 bg-gradient-to-r from-transparent via-primary to-transparent"></div>
            <p className="text-[12px] font-black text-primary uppercase tracking-[0.4em]">Core Capabilities</p>
          </motion.div>
          <h2 className="text-4xl lg:text-5xl font-black tracking-tight text-foreground leading-tight">
            The 9-Agent <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-orange-400">Ecosystem</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 auto-rows-max">
          <FeatureCard
            icon={<Radio className="w-6 h-6 text-white" />}
            title="A1: Telecom IVR"
            description="Entry point. Handles calls, intent, consent, and audio."
            className="bg-gradient-to-br from-orange-500 via-red-500 to-rose-600 text-white shadow-lg"
            iconBg="bg-white/20 backdrop-blur-md"
            textColor="text-white"
            compact={true}
          />
          <FeatureCard
            icon={<Database className="w-6 h-6 text-blue-500" />}
            title="A2: Scheme Matcher"
            description="Cross-references profile constraints against vectors."
            className="bg-card/40 backdrop-blur-xl border border-blue-500/20"
            compact={true}
            delay={0.1}
          />
          <FeatureCard
            icon={<Bot className="w-6 h-6 text-emerald-500" />}
            title="A3: Market Agent"
            description="Real-time API integration for Mandi prices."
            className="bg-card/40 backdrop-blur-xl border border-emerald-500/20"
            compact={true}
            delay={0.2}
          />
          <FeatureCard
            icon={<Globe className="w-6 h-6 text-cyan-500" />}
            title="A4: Weather Agent"
            description="Local weather alerts for agricultural planning."
            className="bg-card/40 backdrop-blur-xl border border-cyan-500/20"
            compact={true}
            delay={0.3}
          />
          <FeatureCard
            icon={<FileText className="w-6 h-6 text-amber-500" />}
            title="A5: Document Verifier"
            description="OCR and validation for uploaded scheme docs."
            className="bg-card/40 backdrop-blur-xl border border-amber-500/20"
            compact={true}
            delay={0.1}
          />
          <FeatureCard
            icon={<Activity className="w-6 h-6 text-purple-500" />}
            title="A6: Eligibility Engine"
            description="Deterministic rule engine for scheme passes."
            className="bg-card/40 backdrop-blur-xl border border-purple-500/20"
            compact={true}
            delay={0.2}
          />
          <FeatureCard
            icon={<Shield className="w-6 h-6 text-teal-500" />}
            title="A7: Security Auditor"
            description="Enforces DPDP compliance and action hashing."
            className="bg-card/40 backdrop-blur-xl border border-teal-500/20"
            compact={true}
            delay={0.3}
          />
           <FeatureCard
            icon={<Zap className="w-6 h-6 text-yellow-500" />}
            title="A8: Output Generator"
            description="Constructs customized SMS and PDF receipts."
            className="bg-card/40 backdrop-blur-xl border border-yellow-500/20"
            compact={true}
            delay={0.4}
          />
          <FeatureCard
            icon={<Users className="w-6 h-6 text-indigo-500" />}
            title="A9: HITL Escalator"
            description="Deterministic fallback transfer to human operators."
            className="col-span-1 sm:col-span-2 lg:col-span-4 bg-card/60 backdrop-blur-xl border border-indigo-500/30"
            iconBg="bg-indigo-500/10"
            compact={false}
            delay={0.5}
          />
        </div>
      </section>

      {/* 7. Architecture Section */}
      <section id="architecture" className="relative z-10 py-24 px-6 max-w-7xl mx-auto">
        <div className="bg-card/60 backdrop-blur-2xl p-8 lg:p-16 rounded-[3rem] border border-border/60 relative overflow-hidden shadow-2xl">
          {/* Decorative Grid Background */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:40px_40px] mask-gradient-radial"></div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center relative z-10">
            <div className="space-y-10">
              <div>
                <motion.div 
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  className="inline-flex items-center gap-3 px-5 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 mb-8 shadow-inner shadow-emerald-500/10"
                >
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                  </span>
                  <span className="text-xs font-black uppercase tracking-[0.2em] text-emerald-600 dark:text-emerald-400">System Status: Active</span>
                </motion.div>
                <h2 className="text-4xl sm:text-6xl font-black tracking-tighter leading-[1.1] mb-6 text-foreground">
                  10-Layer <br />
                  <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 animate-gradient-x inline-block pb-2">
                    Agentic Pipeline.
                  </span>
                </h2>
                <p className="text-secondary-foreground font-medium text-lg leading-relaxed max-w-md opacity-90 mb-8">
                  Scalable, secure, and built for a billion users. Our backend implements a rigorous 10-tier automation architecture.
                </p>

                <ul className="space-y-4">
                  <ArchListItem text="L1 & L2: AWS Connect IVR & PII Masking Engine" color="from-orange-500" />
                  <ArchListItem text="L3: Hybrid Intelligence (Claude 3.5 Sonnet + Deterministic Rules)" color="from-blue-500" />
                  <ArchListItem text="L4 & L5: Real-time Decision Engine & Action Routing" color="from-indigo-500" />
                  <ArchListItem text="L6 & L7: AWS SNS Notification & Execution Handlers" color="from-emerald-500" />
                  <ArchListItem text="L8 & L9: Security Guardrails & CloudWatch Observability" color="from-purple-500" />
                </ul>
              </div>
            </div>

            <div className="relative w-full flex justify-center lg:justify-end perspective-[2000px]">
              <div className="absolute inset-0 bg-gradient-to-tr from-blue-600/20 via-purple-600/20 to-emerald-500/20 rounded-[3rem] blur-3xl opacity-50 group-hover:opacity-100 transition duration-1000"></div>
              
              <div className="w-full max-w-lg py-12 px-6 sm:px-10 bg-slate-950/80 backdrop-blur-3xl rounded-[2.5rem] border border-white/10 flex items-center justify-center relative shadow-[0_0_50px_rgba(0,0,0,0.3)] transform-gpu transition-transform duration-700 hover:rotate-y-[-4deg] hover:rotate-x-[2deg]">
                
                <div className="relative w-full flex flex-col items-stretch justify-center gap-3">
                  {[
                    { name: "L1: Telecom Integration", style: "border-orange-500/40 bg-orange-500/10 text-orange-400 group-hover/layer:bg-orange-500/20" },
                    { name: "L2: Sync & Ingestion", style: "border-amber-500/40 bg-amber-500/10 text-amber-400 group-hover/layer:bg-amber-500/20" },
                    { name: "L3: Hybrid Intelligence", style: "border-blue-500/40 bg-blue-500/10 text-blue-400 group-hover/layer:bg-blue-500/20" },
                    { name: "L4: Decision Engine", style: "border-cyan-500/40 bg-cyan-500/10 text-cyan-400 group-hover/layer:bg-cyan-500/20" },
                    { name: "L5: Verification Engine", style: "border-indigo-500/40 bg-indigo-500/10 text-indigo-400 group-hover/layer:bg-indigo-500/20" },
                    { name: "L6: Action Execution", style: "border-emerald-500/40 bg-emerald-500/10 text-emerald-400 group-hover/layer:bg-emerald-500/20" },
                    { name: "L7: Notification (SNS)", style: "border-green-500/40 bg-green-500/10 text-green-400 group-hover/layer:bg-green-500/20" },
                    { name: "L8: Security Guardrails", style: "border-rose-500/40 bg-rose-500/10 text-rose-400 group-hover/layer:bg-rose-500/20" },
                    { name: "L9: Observability", style: "border-purple-500/40 bg-purple-500/10 text-purple-400 group-hover/layer:bg-purple-500/20" },
                    { name: "L10: Analytics Vault", style: "border-slate-400/40 bg-slate-400/10 text-slate-300 group-hover/layer:bg-slate-400/20" },
                  ].map((layer, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: 40 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: idx * 0.08, type: 'spring' }}
                      whileHover={{ scale: 1.02, x: -10 }}
                      viewport={{ once: true, margin: "-50px" }}
                      className={`w-full h-12 sm:h-14 rounded-xl border ${layer.style} flex items-center shadow-lg transition-all duration-300 cursor-crosshair relative overflow-hidden group/layer z-10`}
                    >
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-white/80 opacity-0 group-hover/layer:opacity-100 transition-opacity"></div>
                      <span className="font-mono text-xs sm:text-sm font-bold tracking-widest pl-6 md:pl-8 drop-shadow-md">
                         {layer.name}
                      </span>
                    </motion.div>
                  ))}
                  
                  {/* Subtle connecting line behind */}
                  <div className="absolute left-8 md:left-10 top-6 bottom-6 w-[2px] bg-gradient-to-b from-transparent via-white/10 to-transparent z-0"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 8. Roadmap Section */}
      <section id="roadmap" className="relative z-10 py-32 px-6 max-w-5xl mx-auto">
        <div className="text-center mb-24">
          <div className="inline-flex items-center justify-center gap-2 mb-6">
             <div className="h-px w-8 bg-gradient-to-r from-transparent to-primary"></div>
             <p className="text-[12px] font-black text-primary uppercase tracking-[0.4em]">The Future</p>
             <div className="h-px w-8 bg-gradient-to-l from-transparent to-primary"></div>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-foreground">Project Roadmap</h2>
        </div>

        <div className="space-y-12 relative before:absolute before:inset-0 before:ml-6 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-1 before:bg-gradient-to-b before:from-primary/50 before:via-orange-500/30 before:to-transparent before:rounded-full">
          <RoadmapItem
            phase="Phase 1"
            title="Telecom Infrastructure Baseline"
            desc="Amazon Connect IVR + LangChain Supervisor Pipeline"
            status="Completed"
            align="left"
          />
          <RoadmapItem
            phase="Phase 2"
            title="Scheme Reasoner & Profile DB"
            desc="Clerk Auth, Rich User Profile, RAG Matching Engine"
            status="Completed"
            align="right"
          />
          <RoadmapItem
            phase="Phase 3"
            title="Data Synchronisation Layer"
            desc="Profile sync from Dashboard to IVR AWS session lookup"
            status="Completed"
            align="left"
          />
          <RoadmapItem
            phase="Phase 4"
            title="10-Layer Event Bus & Tracing"
            desc="AWS architecture scaling with DynamoDB & CloudWatch JSON Logs"
            status="Completed"
            align="right"
          />
          <RoadmapItem
            phase="Phase 5"
            title="Offline Gram-Panchayat Mesh"
            desc="Decentralized sync points via LoRaWAN for zero-internet validation"
            status="Upcoming"
            align="left"
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
              <li>
                <Link href="/contact" className="hover:text-primary transition-colors flex items-center gap-2">Contact Us</Link>
              </li>
              <li>
                <Link href="/region" className="hover:text-primary transition-colors flex items-center gap-2"><Globe className="w-4 h-4" /> India Regional Node</Link>
              </li>
              <li>
                <Link href="/security" className="hover:text-primary transition-colors flex items-center gap-2"><Lock className="w-4 h-4" /> Secure & Encrypted</Link>
              </li>
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
            <a href="https://github.com/shalcoder/JanSathi" target="_blank" rel="noopener noreferrer" className="text-secondary-foreground/40 hover:text-foreground transition-colors">
              <span className="sr-only">GitHub</span>
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
              </svg>
            </a>
            <a href="#" className="text-secondary-foreground/40 hover:text-foreground transition-colors">
              <span className="sr-only">Twitter</span>
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
              </svg>
            </a>
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

interface ProcessStepProps {
  number: string;
  title: string;
  desc: string;
  icon: React.ReactNode;
  color: string;
}

function ProcessStep({ number, title, desc, icon, color }: ProcessStepProps) {
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

function ArchListItem({ text, color = 'from-primary' }: { text: string, color?: string }) {
  return (
    <li className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/5 transition-colors border border-transparent hover:border-white/5">
      <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${color} to-transparent opacity-80 flex items-center justify-center shrink-0 shadow-inner`}>
        <CheckCircle2 className="w-5 h-5 text-white" />
      </div>
      <p className="text-base font-bold text-foreground/90 tracking-tight">{text}</p>
    </li>
  );
}

interface RoadmapItemProps {
  phase: string;
  title: string;
  desc: string;
  status: 'Completed' | 'Upcoming';
  align: 'left' | 'right';
}

function RoadmapItem({ phase, title, desc, status, align }: RoadmapItemProps) {
  const isCompleted = status === 'Completed';
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group`}
    >
      <div className={`flex items-center justify-center w-12 h-12 rounded-full border-4 border-background shadow-xl shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 transition-colors duration-500 ${isCompleted ? 'bg-primary' : 'bg-secondary'}`}>
        {isCompleted ? <CheckCircle2 className="w-5 h-5 text-white" /> : <div className="w-3 h-3 bg-secondary-foreground rounded-full"></div>}
      </div>
      <div className={`w-[calc(100%-4rem)] md:w-[calc(50%-3rem)] p-8 rounded-[2rem] bg-card/60 backdrop-blur-xl border border-border/60 shadow-lg hover:shadow-xl hover:border-primary/50 transition-all duration-300 ${align === 'left' ? 'mr-auto' : 'ml-auto'}`}>
        <div className="flex items-center justify-between mb-4">
          <span className="inline-block px-3 py-1.5 rounded-lg bg-primary/10 text-[11px] font-black text-primary uppercase tracking-[0.2em]">{phase}</span>
          <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded border ${isCompleted ? 'text-emerald-500 border-emerald-500/20 bg-emerald-500/10' : 'text-orange-500 border-orange-500/20 bg-orange-500/10'}`}>
            {status}
          </span>
        </div>
        <h3 className="font-bold text-xl md:text-2xl text-foreground mb-3 tracking-tight">{title}</h3>
        <p className="text-base text-secondary-foreground opacity-80 leading-relaxed font-medium">{desc}</p>
      </div>
    </motion.div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  subtitle?: string;
  description: string;
  className?: string;
  iconBg?: string;
  textColor?: string;
  subTextColor?: string;
  delay?: number;
  compact?: boolean;
}

function FeatureCard({
  icon, title, subtitle, description, className = '', iconBg = 'bg-secondary border border-border/50', textColor = 'text-foreground', subTextColor = 'text-primary', delay = 0, compact = false
}: FeatureCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ delay, type: 'spring', stiffness: 100, damping: 20 }}
      className={`p-6 md:p-8 rounded-[2rem] shadow-xl hover:-translate-y-2 transition-all duration-300 flex flex-col justify-between group relative overflow-hidden ${className}`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      <div className="relative z-10">
        <div className={`mb-6 w-12 h-12 rounded-xl ${iconBg} flex items-center justify-center transition-transform duration-500 group-hover:scale-110 shadow-inner group-hover:rotate-3`}>
          {icon}
        </div>
        <div>
          {subtitle && (
            <p className={`text-[10px] font-black ${subTextColor} uppercase tracking-[0.3em] mb-2 opacity-90 drop-shadow-sm`}>
              {subtitle}
            </p>
          )}
          <h3 className={`${compact ? 'text-xl' : 'text-3xl'} font-black mb-3 tracking-tighter ${textColor}`}>{title}</h3>
          <p className={`text-sm font-medium leading-relaxed opacity-80 ${textColor === 'text-white' ? 'text-white' : 'text-secondary-foreground'}`}>
            {description}
          </p>
        </div>
      </div>
      <div className={`mt-10 flex items-center gap-2 text-sm font-bold uppercase tracking-wider ${textColor} opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-4 group-hover:translate-y-0 relative z-10`}>
        Learn more <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
      </div>
    </motion.div>
  );
}

