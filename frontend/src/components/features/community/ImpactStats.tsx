'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Users, Heart, Award, MapPin } from 'lucide-react';

const IMPACT_METRICS = [
    { label: "Community Support", value: "12,450+", sub: "Verified Queries", icon: Users, color: "text-blue-500" },
    { label: "Village Coverage", value: "142", sub: "Active Districts", icon: MapPin, color: "text-emerald-500" },
    { label: "Benefits Tracked", value: "₹2.4 Cr", sub: "Potential Aid", icon: TrendingUp, color: "text-orange-500" },
    { label: "Public Health", value: "5.2k", sub: "Ayushman Links", icon: Heart, color: "text-rose-500" },
];

export default function ImpactStats() {
    return (
        <div className="p-8 space-y-8 bg-card rounded-3xl border border-border/50 shadow-xl overflow-hidden relative">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl -mr-10 -mt-10"></div>

            <div className="space-y-2">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 rounded-full border border-primary/20">
                    <Award className="w-3 h-3 text-primary" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-primary">Community Impact</span>
                </div>
                <h3 className="text-2xl font-bold tracking-tight text-foreground">Village Collective Pulse</h3>
                <p className="text-xs text-secondary-foreground opacity-50 font-medium">Real-time public system impact tracker for JanSathi.</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
                {IMPACT_METRICS.map((item, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="p-5 rounded-2xl bg-secondary/30 border border-border/50 space-y-4 hover:border-primary/20 transition-all group/item"
                    >
                        <item.icon className={`w-6 h-6 ${item.color} group-hover/item:scale-110 transition-transform`} />
                        <div>
                            <p className="text-xl font-black text-foreground">{item.value}</p>
                            <p className="text-[10px] font-bold uppercase tracking-wider text-secondary-foreground opacity-40">{item.label}</p>
                            <p className="text-[9px] font-medium text-secondary-foreground opacity-30 mt-1 italic">{item.sub}</p>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Live Impact Feed — Unique Feature */}
            <div className="bg-background/50 rounded-2xl border border-border/30 p-4 relative overflow-hidden h-24">
                <p className="text-[9px] font-black uppercase tracking-[0.2em] text-primary mb-3">Live Community Impact</p>
                <div className="space-y-3 animate-pulse-slow">
                    <div className="flex items-center gap-3">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                        <p className="text-[10px] text-foreground font-medium italic opacity-80">Farmer in Raichur secured ₹6,000 via PM-Kisan Audit.</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
                        <p className="text-[10px] text-foreground font-medium italic opacity-80">Village 'A' secured 15 Ayushman cards today.</p>
                    </div>
                </div>
                <div className="absolute inset-x-0 bottom-0 h-8 bg-gradient-to-t from-background to-transparent pointer-events-none"></div>
            </div>

            <div className="pt-4 border-t border-border/10">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-[10px] font-bold uppercase tracking-widest text-primary">Security Node</p>
                        <p className="text-xs font-bold text-foreground">Sovereign Encryption Active</p>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                        <div className="h-2 w-20 bg-secondary rounded-full overflow-hidden">
                            <div className="h-full w-full bg-emerald-500"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
