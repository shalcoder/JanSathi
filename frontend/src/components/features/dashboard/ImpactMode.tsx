'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Phone, CheckCircle, AlertTriangle, MapPin, TrendingUp, Users, Zap } from 'lucide-react';

interface Stat {
  icon: React.ElementType;
  label: string;
  value: number;
  suffix?: string;
  color: string;
  glowColor: string;
}

const STATS: Stat[] = [
  { icon: Phone, label: 'Calls Processed', value: 47, color: 'text-blue-400', glowColor: 'rgba(96,165,250,0.15)' },
  { icon: CheckCircle, label: 'Eligible Citizens', value: 32, color: 'text-emerald-400', glowColor: 'rgba(52,211,153,0.15)' },
  { icon: AlertTriangle, label: 'HITL Escalated', value: 5, color: 'text-amber-400', glowColor: 'rgba(251,191,36,0.15)' },
  { icon: MapPin, label: 'Office Trips Saved', value: 18, color: 'text-purple-400', glowColor: 'rgba(167,139,250,0.15)' },
  { icon: TrendingUp, label: 'KM Travel Avoided', value: 82, suffix: ' km', color: 'text-rose-400', glowColor: 'rgba(251,113,133,0.15)' },
  { icon: Users, label: 'Families Reached', value: 29, color: 'text-cyan-400', glowColor: 'rgba(34,211,238,0.15)' },
];

function useCountUp(target: number, duration = 1400) {
  const [val, setVal] = useState(0);
  const startedAt = useRef<number | null>(null);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    startedAt.current = null;
    const step = (ts: number) => {
      if (!startedAt.current) startedAt.current = ts;
      const progress = Math.min((ts - startedAt.current) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setVal(Math.round(target * eased));
      if (progress < 1) rafRef.current = requestAnimationFrame(step);
    };
    rafRef.current = requestAnimationFrame(step);
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  }, [target, duration]);

  return val;
}

function StatCard({ stat, delay }: { stat: Stat; delay: number }) {
  const count = useCountUp(stat.value);
  const Icon = stat.icon;
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="relative bg-card/60 backdrop-blur-xl border border-border/50 rounded-2xl p-5 overflow-hidden group hover:scale-[1.02] transition-transform"
      style={{ boxShadow: `0 8px 30px ${stat.glowColor}` }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-3">
          <div className="p-2.5 rounded-xl bg-card border border-border/50" style={{ boxShadow: `0 0 15px ${stat.glowColor}` }}>
            <Icon className={`w-5 h-5 ${stat.color}`} />
          </div>
          <div className={`text-[10px] font-bold uppercase tracking-widest ${stat.color} opacity-60`}>LIVE</div>
        </div>
        <div className={`text-4xl font-black ${stat.color} font-mono`}>
          {count}{stat.suffix ?? ''}
        </div>
        <p className="text-xs font-bold text-secondary-foreground/70 uppercase tracking-wider mt-1">{stat.label}</p>
      </div>
    </motion.div>
  );
}

export default function ImpactMode() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2.5 rounded-xl bg-primary/10 border border-primary/20">
          <Zap className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-black text-foreground tracking-tight">Impact Dashboard</h2>
          <p className="text-xs text-secondary-foreground font-medium">Real-time civic impact since deployment • Seeded session data</p>
        </div>
        <div className="ml-auto flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">Live</span>
        </div>
      </div>

      {/* Stat Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {STATS.map((stat, i) => (
          <StatCard key={stat.label} stat={stat} delay={i * 0.08} />
        ))}
      </div>

      {/* Impact Narrative */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="p-5 rounded-2xl bg-primary/5 border border-primary/20 flex gap-4 items-start"
      >
        <div className="p-2.5 rounded-xl bg-primary/15 border border-primary/25 shrink-0">
          <MapPin className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 className="font-bold text-foreground mb-1">82 km of Rural Travel Eliminated</h3>
          <p className="text-sm text-secondary-foreground leading-relaxed">
            JanSathi&apos;s voice-first approach replaced physical trips to district offices. 18 families stayed home —
            saving ₹4,100 in transport costs and over 36 hours of productive farming time.
          </p>
        </div>
      </motion.div>
    </div>
  );
}
