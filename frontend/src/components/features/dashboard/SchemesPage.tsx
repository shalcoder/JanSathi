import React from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, ArrowRight, Landmark, Sprout, Building2, GraduationCap, HeartPulse } from 'lucide-react';

export default function SchemesPage() {
    const categories = [
        { id: 'all', label: 'All', icon: Landmark },
        { id: 'agri', label: 'Agriculture', icon: Sprout },
        { id: 'infra', label: 'Housing', icon: Building2 },
        { id: 'edu', label: 'Education', icon: GraduationCap },
        { id: 'health', label: 'Health', icon: HeartPulse },
    ];

    const schemes = [
        { title: "PM Kisan Samman Nidhi", dept: "Ministry of Agriculture", amt: "₹6,000/year", tags: ["Farmers", "Direct Transfer"] },
        { title: "Ayushman Bharat", dept: "Ministry of Health", amt: "₹5 Lakh Cover", tags: ["Health", "Insurance"] },
        { title: "PM Awas Yojana", dept: "Ministry of Housing", amt: "Subsidized Loan", tags: ["Housing", "Urban/Rural"] },
        { title: "Atal Pension Yojana", dept: "PFRDA", amt: "Pension", tags: ["Old Age", "Social Security"] },
    ];

    return (
        <div className="space-y-8 p-6 lg:p-10 max-w-7xl mx-auto h-full flex flex-col">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-black tracking-tight text-foreground">Government Schemes</h1>
                    <p className="text-secondary-foreground font-medium mt-1">Browse and apply for verify schemes tailored for you.</p>
                </div>
            </div>

            {/* Search & Filter Bar */}
            <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-foreground/50" />
                    <input
                        type="text"
                        placeholder="Search schemes by name, department..."
                        className="w-full pl-12 pr-4 py-4 bg-card border border-border rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none font-medium transition-all"
                    />
                </div>
                <button className="px-6 py-4 bg-secondary/50 border border-border rounded-xl font-bold flex items-center gap-2 hover:bg-secondary transition-colors">
                    <Filter className="w-5 h-5" />
                    <span>Filters</span>
                </button>
            </div>

            {/* Categories */}
            <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-none">
                {categories.map((cat, i) => (
                    <button
                        key={cat.id}
                        className={`
              flex items-center gap-2 px-6 py-3 rounded-full border whitespace-nowrap transition-all
              ${i === 0 ? 'bg-foreground text-background border-foreground' : 'bg-card border-border hover:border-primary/50 text-secondary-foreground hover:text-foreground'}
            `}
                    >
                        <cat.icon className="w-4 h-4" />
                        <span className="font-bold text-sm">{cat.label}</span>
                    </button>
                ))}
            </div>

            {/* Schemes Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-20">
                {schemes.map((scheme, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.1 }}
                        className="group relative bg-card hover:bg-secondary/10 border border-border/50 hover:border-primary/30 rounded-2xl p-6 transition-all cursor-pointer shadow-sm hover:shadow-md"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-wider">
                                Eligible
                            </span>
                            <button className="text-secondary-foreground/40 hover:text-primary transition-colors">
                                <ArrowRight className="w-5 h-5 -rotate-45 group-hover:rotate-0 transition-transform" />
                            </button>
                        </div>

                        <h3 className="text-xl font-black text-foreground mb-1">{scheme.title}</h3>
                        <p className="text-sm font-medium text-secondary-foreground mb-4">{scheme.dept}</p>

                        <div className="flex flex-wrap gap-2 mb-6">
                            {scheme.tags.map(tag => (
                                <span key={tag} className="text-[10px] font-bold px-2 py-1 bg-secondary rounded text-secondary-foreground/70">
                                    {tag}
                                </span>
                            ))}
                        </div>

                        <div className="flex items-center justify-between mt-auto pt-4 border-t border-border/40">
                            <div>
                                <p className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider">Benefit</p>
                                <p className="font-bold text-foreground">{scheme.amt}</p>
                            </div>
                            <button className="px-4 py-2 bg-foreground text-background rounded-lg text-xs font-bold uppercase tracking-widest hover:opacity-90 transition-opacity">
                                Apply Now
                            </button>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
