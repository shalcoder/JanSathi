'use client';

import React from 'react';
import { ArrowRight, Mic, ShieldCheck, Languages, MessageSquare, Globe, Cpu, Bot, Zap } from "lucide-react";
import Link from 'next/link';
import BackendStatus from "@/components/BackendStatus";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white overflow-x-hidden selection:bg-blue-500/30 font-sans">

      {/* Dynamic Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-0 w-[800px] h-[800px] bg-blue-600/10 rounded-full blur-[120px] -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute bottom-0 right-0 w-[800px] h-[800px] bg-purple-600/10 rounded-full blur-[120px] translate-x-1/2 translate-y-1/2"></div>
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-[0.03]"></div>
      </div>

      {/* Navbar */}
      <nav className="relative z-50 flex items-center justify-between px-4 sm:px-6 md:px-12 py-4 sm:py-6 max-w-7xl mx-auto backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <span className="font-black text-xl">JS</span>
          </div>
          <span className="text-xl sm:text-2xl font-black tracking-tighter">JanSathi</span>
        </div>
        <div className="flex items-center gap-3 sm:gap-4 md:gap-8">
          <a href="#features" className="hidden md:inline text-sm font-bold text-slate-400 hover:text-blue-400 transition-colors">Features</a>
          <a href="#how-it-works" className="hidden md:inline text-sm font-bold text-slate-400 hover:text-blue-400 transition-colors">How it works</a>
          <Link href="/sign-in" className="px-3 sm:px-4 md:px-6 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-white transition-all text-xs sm:text-sm font-bold">
            Sign In
          </Link>
          <Link href="/sign-up" className="px-3 sm:px-4 md:px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-full text-white transition-all text-xs sm:text-sm font-bold shadow-lg shadow-blue-600/20">
            Sign Up
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-32 px-6 md:px-12 max-w-7xl mx-auto flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-black uppercase tracking-widest mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <Zap className="w-3 h-3 fill-current" />
          AI for Bharat Hackathon 2026
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-8xl font-black tracking-tighter mb-6 sm:mb-8 leading-[0.95] animate-in fade-in slide-in-from-bottom-8 duration-1000">
          Government Services, <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-teal-400 to-purple-500">Simplified by AI.</span>
        </h1>

        <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-slate-400 max-w-3xl mb-8 sm:mb-12 leading-relaxed animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200 px-4">
          JanSathi is your voice-first AI assistant for government schemes,
          mandi prices, and document analysis. Designed to bridge the digital gap in rural India.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 items-center animate-in fade-in slide-in-from-bottom-16 duration-1000 delay-300">
          <Link
            href="/dashboard"
            className="group px-10 py-5 bg-blue-600 hover:bg-blue-700 text-white rounded-[2.5rem] font-black text-xl shadow-2xl shadow-blue-600/40 transition-all flex items-center gap-3 hover:scale-105 active:scale-95"
          >
            Start Talking <ArrowRight className="group-hover:translate-x-1 transition-transform" />
          </Link>
          <a
            href="#features"
            className="px-10 py-5 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-[2.5rem] font-black text-xl transition-all"
          >
            Explore Features
          </a>
        </div>
      </section>

      {/* Feature Grid */}
      <section id="features" className="relative z-10 py-16 sm:py-24 md:py-32 px-4 sm:px-6 md:px-12 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 md:gap-8">
          <FeatureCard
            icon={<Mic className="w-8 h-8 text-blue-400" />}
            title="Voice First"
            description="Speak in Hindi, Tamil, or Kannada. Our AI understands and talks back in your native tongue."
          />
          <FeatureCard
            icon={<Languages className="w-8 h-8 text-teal-400" />}
            title="Multi-lingual"
            description="Automatic translation for government documents and scheme descriptions into regional languages."
          />
          <FeatureCard
            icon={<Bot className="w-8 h-8 text-purple-400" />}
            title="Drishti Vision"
            description="Upload any government notice or form. JanSathi analyzes it instantly and tells you the next steps."
          />
        </div>
      </section>

      {/* Tech Stack / Telemetry Style Section */}
      <section id="how-it-works" className="relative z-10 py-16 sm:py-24 md:py-32 px-4 sm:px-6 md:px-12 max-w-7xl mx-auto">
        <div className="glass-panel p-6 sm:p-8 md:p-12 rounded-2xl sm:rounded-[2.5rem] md:rounded-[3rem] border border-white/10 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/5 blur-[80px] rounded-full"></div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 sm:gap-12 lg:gap-16 items-center">
            <div className="space-y-6 sm:space-y-8">
              <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-black tracking-tighter">Powered by Enterprise Grade AWS Infrastructure.</h2>
              <div className="space-y-4">
                <TechItem icon={<Cpu />} name="Bedrock (Claude 3)" detail="Reasoning & Intelligence" />
                <TechItem icon={<Globe />} name="AWS Polly" detail="Natural Neural Voice Synthesis" />
                <TechItem icon={<ShieldCheck />} name="AWS Transcribe" detail="High Accuracy Speech-to-Text" />
                <TechItem icon={<Bot />} name="Kendra" detail="Smart Search & RAG" />
              </div>
            </div>
            <div className="relative">
              <div className="aspect-square rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center p-8">
                <div className="relative w-full h-full border border-blue-500/20 rounded-full animate-[spin_20s_linear_infinite] flex items-center justify-center">
                  <div className="absolute top-0 w-12 h-12 bg-blue-500 rounded-full blur-xl translate-y-[-50%]"></div>
                  <div className="w-3/4 h-3/4 border border-teal-500/20 rounded-full flex items-center justify-center">
                    <div className="w-1/2 h-1/2 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full shadow-[0_0_50px_rgba(37,99,235,0.4)] flex items-center justify-center">
                      <span className="font-bold text-3xl">AI</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-12 sm:py-16 md:py-20 px-4 sm:px-6 md:px-12 border-t border-white/5 text-center">
        <p className="text-slate-500 font-bold mb-4 uppercase tracking-[0.2em] text-xs font-mono">JanSathi Professional v2.0</p>
        <p className="text-slate-400 max-w-md mx-auto mb-8">
          Empowering every citizen with the power of artificial intelligence.
        </p>
        <div className="flex justify-center gap-8 text-slate-600 font-black">
          <a href="#" className="hover:text-blue-500">About</a>
          <a href="#" className="hover:text-blue-500">Privacy</a>
          <a href="#" className="hover:text-blue-500">Terms</a>
        </div>
      </footer>

      <BackendStatus />
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="group p-10 rounded-[2.5rem] bg-white/5 border border-white/10 hover:bg-white/[0.07] hover:border-blue-500/30 transition-all duration-500">
      <div className="mb-8 inline-block p-5 bg-white/5 rounded-2xl shadow-inner group-hover:scale-110 transition-transform duration-500">
        {icon}
      </div>
      <h3 className="text-2xl font-black mb-4 tracking-tighter">{title}</h3>
      <p className="text-slate-400 leading-relaxed font-medium">
        {description}
      </p>
    </div>
  );
}

function TechItem({ icon, name, detail }: { icon: React.ReactNode, name: string, detail: string }) {
  return (
    <div className="flex items-center gap-4 p-4 rounded-2xl hover:bg-white/5 transition-colors group">
      <div className="p-3 bg-white/5 rounded-xl group-hover:text-blue-400 transition-colors">
        {icon}
      </div>
      <div>
        <p className="font-black text-lg leading-none mb-1">{name}</p>
        <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">{detail}</p>
      </div>
    </div>
  );
}
