import React from 'react';
import Link from 'next/link';
import { ArrowLeft, Mail, MessageSquare } from 'lucide-react';

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-background text-foreground font-[family-name:var(--font-outfit)] relative overflow-hidden transition-colors duration-500">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none z-0"></div>
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px] pointer-events-none z-0"></div>
      <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-[120px] pointer-events-none z-0"></div>

      <div className="max-w-4xl mx-auto px-6 py-20 relative z-10 flex flex-col items-center text-center mt-8">
        <div className="w-20 h-20 bg-blue-500/10 border border-blue-500/20 rounded-3xl flex items-center justify-center mb-8 shadow-2xl shadow-blue-500/20">
          <Mail className="w-10 h-10 text-blue-500" />
        </div>
        
        <h1 className="text-4xl md:text-6xl font-black mb-6 tracking-tight">Contact Us</h1>
        <p className="text-xl text-secondary-foreground leading-relaxed mb-12 max-w-2xl bg-secondary/30 py-2 px-6 rounded-full border border-border/50">
          Get in touch with the JanSathi Core Team
        </p>

        <div className="w-full max-w-2xl p-8 bg-card/60 backdrop-blur-xl border border-border/50 rounded-3xl shadow-xl text-left hover:border-blue-500/30 transition-colors">
           <h3 className="font-bold text-xl mb-3 text-foreground flex items-center gap-3">
             <MessageSquare className="w-6 h-6 text-blue-500" />
             Hackathon Evaluation
           </h3>
           <p className="text-base text-secondary-foreground leading-relaxed mb-6">
             For technical support, SMS integration requests, or inquiries about deploying the multi-agent civic tech pipeline in your region, please reach out directly:
           </p>
           <a href="mailto:hello@jansathi.ai" className="inline-flex px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-all shadow-lg shadow-blue-500/20">
             hello@jansathi.ai
           </a>
        </div>

        <Link href="/" className="inline-flex items-center gap-2 mt-16 px-8 py-4 bg-secondary border border-border/50 hover:bg-secondary/80 text-foreground rounded-2xl font-bold transition-all hover:-translate-y-1 shadow-lg">
          <ArrowLeft className="w-5 h-5" /> Return to Home
        </Link>
      </div>
    </div>
  );
}
