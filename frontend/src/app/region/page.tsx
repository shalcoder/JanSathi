import React from 'react';
import Link from 'next/link';
import { ArrowLeft, Globe, Zap, CheckCircle2 } from 'lucide-react';

export default function RegionPage() {
  return (
    <div className="min-h-screen bg-background text-foreground font-[family-name:var(--font-outfit)] relative overflow-hidden transition-colors duration-500">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none z-0"></div>
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-orange-500/5 rounded-full blur-[120px] pointer-events-none z-0"></div>
      <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-[120px] pointer-events-none z-0"></div>

      <div className="max-w-4xl mx-auto px-6 py-20 relative z-10 flex flex-col items-center text-center mt-8">
        <div className="w-20 h-20 bg-orange-500/10 border border-orange-500/20 rounded-3xl flex items-center justify-center mb-8 shadow-2xl shadow-orange-500/20">
          <Globe className="w-10 h-10 text-orange-500" />
        </div>
        
        <h1 className="text-4xl md:text-6xl font-black mb-6 tracking-tight">India Regional Node</h1>
        <p className="text-xl text-secondary-foreground leading-relaxed mb-12 max-w-2xl bg-secondary/30 py-2 px-6 rounded-full border border-border/50 flex items-center gap-3">
          <Zap className="w-5 h-5 text-amber-500" /> Currently running from ap-south-1 (Mumbai)
        </p>

        <div className="w-full max-w-2xl p-8 bg-card/60 backdrop-blur-xl border border-border/50 rounded-3xl shadow-xl text-left hover:border-orange-500/30 transition-colors">
           <h3 className="font-bold text-xl mb-6 text-foreground">Global Tracing Metrics</h3>
           <ul className="space-y-4">
              <li className="flex items-center gap-4 bg-secondary/40 p-4 rounded-2xl border border-border/30">
                 <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                 <div>
                    <h4 className="font-bold text-foreground">IVR Latency</h4>
                    <p className="text-sm text-secondary-foreground">TTS/STT optimized &lt; 800ms for Hindi, Tamil, Kannada.</p>
                 </div>
              </li>
              <li className="flex items-center gap-4 bg-secondary/40 p-4 rounded-2xl border border-border/30">
                 <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                 <div>
                    <h4 className="font-bold text-foreground">Multi-Agent State</h4>
                    <p className="text-sm text-secondary-foreground">AWS Step Functions executing 9-agent DAG in ~1.2s avg.</p>
                 </div>
              </li>
           </ul>
        </div>

        <Link href="/" className="inline-flex items-center gap-2 mt-16 px-8 py-4 bg-secondary border border-border/50 hover:bg-secondary/80 text-foreground rounded-2xl font-bold transition-all hover:-translate-y-1 shadow-lg">
          <ArrowLeft className="w-5 h-5" /> Return to Home
        </Link>
      </div>
    </div>
  );
}
