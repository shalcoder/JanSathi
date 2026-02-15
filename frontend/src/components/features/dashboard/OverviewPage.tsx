import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Users, Clock, CheckCircle, ArrowRight } from 'lucide-react';

export default function OverviewPage({ onNavigate }: { onNavigate: (page: string) => void }) {
    const stats = [
        { label: "Active Applications", value: "3", icon: Clock, color: "text-blue-500", bg: "bg-blue-500/10" },
        { label: "Schemes Eligible", value: "12", icon: CheckCircle, color: "text-emerald-500", bg: "bg-emerald-500/10" },
        { label: "Community Posts", value: "28", icon: Users, color: "text-purple-500", bg: "bg-purple-500/10" },
        { label: "Completion Rate", value: "85%", icon: TrendingUp, color: "text-amber-500", bg: "bg-amber-500/10" },
    ];

    return (
        <div className="space-y-8 p-6 lg:p-10 max-w-7xl mx-auto">
            {/* Welcome Section */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-black tracking-tight text-foreground">Dashboard</h1>
                    <p className="text-secondary-foreground font-medium mt-1">Welcome back, here&apos;s what&apos;s happening today.</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={async () => {
                            if (confirm("This will populate the production database with schemes and forum data. Proceed?")) {
                                try {
                                    const res = await fetch('/api/admin/seed', { method: 'POST' });
                                    const data = await res.json();
                                    alert(data.message || "Database seeded!");
                                    window.location.reload();
                                } catch (e) {
                                    alert("Seeding failed. Check console.");
                                }
                            }
                        }}
                        className="px-6 py-3 bg-secondary/50 hover:bg-secondary text-foreground rounded-xl font-bold transition-all border border-border flex items-center gap-2"
                    >
                        <span>Sync Database</span>
                    </button>
                    <button
                        onClick={() => onNavigate('assistant')}
                        className="px-6 py-3 bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl font-bold transition-all shadow-lg active:scale-95 flex items-center gap-2"
                    >
                        <span>Ask Assistant</span>
                        <ArrowRight className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {stats.map((stat, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-6 rounded-2xl bg-card border border-border/50 hover:border-border transition-colors group"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div className={`p-3 rounded-xl ${stat.bg} ${stat.color} transition-transform group-hover:scale-110`}>
                                <stat.icon className="w-6 h-6" />
                            </div>
                            <span className="text-xs font-bold uppercase tracking-wider text-secondary-foreground opacity-50">This Week</span>
                        </div>
                        <h3 className="text-3xl font-black text-foreground mb-1">{stat.value}</h3>
                        <p className="text-sm font-semibold text-secondary-foreground">{stat.label}</p>
                    </motion.div>
                ))}
            </div>

            {/* Recent Activity & Recommendations */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Applications */}
                <div className="lg:col-span-2 space-y-6">
                    <h2 className="text-xl font-bold flex items-center gap-2">
                        <Clock className="w-5 h-5 text-primary" />
                        Recent Applications
                    </h2>
                    <div className="bg-card border border-border/50 rounded-2xl overflow-hidden">
                        {[1, 2, 3].map((item, i) => (
                            <div key={i} className="p-4 border-b border-border/50 last:border-none hover:bg-secondary/20 transition-colors flex items-center justify-between group cursor-pointer">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center font-bold text-secondary-foreground">
                                        PM
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-foreground">PM Kisan Samman Nidhi</h4>
                                        <p className="text-xs text-secondary-foreground opacity-80">Application #{2024000 + item} • Pending Review</p>
                                    </div>
                                </div>
                                <span className="px-3 py-1 rounded-full bg-amber-500/10 text-amber-500 text-xs font-bold uppercase tracking-wider">
                                    Processing
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Recommended Schemes */}
                <div className="space-y-6">
                    <h2 className="text-xl font-bold flex items-center gap-2">
                        <CheckCircle className="w-5 h-5 text-emerald-500" />
                        For You
                    </h2>
                    <div className="bg-card border border-border/50 rounded-2xl p-6 relative overflow-hidden group hover:border-primary/50 transition-colors cursor-pointer" onClick={() => onNavigate('schemes')}>
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <TrendingUp className="w-24 h-24" />
                        </div>
                        <span className="px-2 py-1 rounded-md bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-widest mb-3 inline-block">
                            High Match
                        </span>
                        <h3 className="text-lg font-bold mb-2">Ayushman Bharat</h3>
                        <p className="text-sm text-secondary-foreground mb-4 opacity-80">Based on your profile, you are eligible for ₹5L health coverage.</p>
                        <button className="text-sm font-bold text-primary flex items-center gap-2 hover:gap-3 transition-all">
                            View Details <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
