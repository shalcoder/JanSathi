import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, ArrowRight, Landmark, Sprout, Building2, GraduationCap, HeartPulse } from 'lucide-react';
import { getSchemes } from '@/services/api';

interface Scheme {
    id: string;
    title: string;
    benefit: string;
    ministry: string;
    category: string;
    keywords: string[];
}

export default function SchemesPage() {
    const [schemes, setSchemes] = useState<Scheme[]>([]);
    const [filteredSchemes, setFilteredSchemes] = useState<Scheme[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [activeCategory, setActiveCategory] = useState('all');

    const categories = [
        { id: 'all', label: 'All', icon: Landmark },
        { id: 'agriculture', label: 'Agriculture', icon: Sprout },
        { id: 'housing', label: 'Housing', icon: Building2 },
        { id: 'education', label: 'Education', icon: GraduationCap },
        { id: 'health', label: 'Health', icon: HeartPulse },
    ];

    useEffect(() => {
        const fetchSchemesData = async () => {
            setLoading(true);
            try {
                const data = await getSchemes() as { schemes?: Scheme[] };
                if (data?.schemes && Array.isArray(data.schemes) && data.schemes.length > 0) {
                    setSchemes(data.schemes);
                    setFilteredSchemes(data.schemes);
                } else {
                    // Fallback to demo data if backend is empty
                    const demoSchemes: Scheme[] = [
                        { id: '1', title: 'PM Kisan Samman Nidhi', benefit: '₹6,000/year', ministry: 'Ministry of Agriculture', category: 'agriculture', keywords: ['farmers', 'direct transfer'] },
                        { id: '2', title: 'Ayushman Bharat', benefit: '₹5 Lakh Cover', ministry: 'Ministry of Health', category: 'health', keywords: ['health', 'insurance'] },
                        { id: '3', title: 'PM Awas Yojana', benefit: 'Housing Subsidy', ministry: 'Ministry of Housing', category: 'housing', keywords: ['home', 'urban', 'rural'] },
                        { id: '4', title: 'Atal Pension Yojana', benefit: 'Monthly Pension', ministry: 'PFRDA', category: 'general', keywords: ['pension', 'old age'] },
                    ];
                    setSchemes(demoSchemes);
                    setFilteredSchemes(demoSchemes);
                }
            } catch (error) {
                console.error("Failed to fetch schemes:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchSchemesData();
    }, []);

    useEffect(() => {
        let filtered = schemes;

        if (activeCategory !== 'all') {
            filtered = filtered.filter(s => s.category === activeCategory);
        }

        if (searchQuery) {
            const lowQuery = searchQuery.toLowerCase();
            filtered = filtered.filter(s =>
                s.title.toLowerCase().includes(lowQuery) ||
                s.ministry.toLowerCase().includes(lowQuery) ||
                (s.keywords && s.keywords.some(k => k.toLowerCase().includes(lowQuery)))
            );
        }

        setFilteredSchemes(filtered);
    }, [searchQuery, activeCategory, schemes]);

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
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
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
                {categories.map((cat) => (
                    <button
                        key={cat.id}
                        onClick={() => setActiveCategory(cat.id)}
                        className={`
              flex items-center gap-2 px-6 py-3 rounded-full border whitespace-nowrap transition-all
              ${activeCategory === cat.id ? 'bg-foreground text-background border-foreground' : 'bg-card border-border hover:border-primary/50 text-secondary-foreground hover:text-foreground'}
            `}
                    >
                        <cat.icon className="w-4 h-4" />
                        <span className="font-bold text-sm">{cat.label}</span>
                    </button>
                ))}
            </div>

            {/* Schemes Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-20">
                {loading ? (
                    <div className="col-span-full flex justify-center py-20">
                        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
                    </div>
                ) : filteredSchemes.length === 0 ? (
                    <div className="col-span-full text-center py-20 bg-secondary/10 rounded-3xl border border-dashed border-border text-secondary-foreground">
                        No schemes found matching your criteria.
                    </div>
                ) : (
                    filteredSchemes.map((scheme, i) => (
                        <motion.div
                            key={scheme.id}
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: i * 0.05 }}
                            className="group relative bg-card hover:bg-secondary/5 border border-border/50 hover:border-primary/30 rounded-3xl p-6 sm:p-8 transition-all shadow-sm hover:shadow-xl flex flex-col"
                        >
                            <div className="flex justify-between items-start mb-6">
                                <span className="px-4 py-1.5 rounded-full bg-orange-500/10 text-orange-600 text-[10px] font-black uppercase tracking-[0.2em] border border-orange-500/20">
                                    ELIGIBLE
                                </span>
                                <div className="text-secondary-foreground/20 group-hover:text-primary transition-colors">
                                    <ArrowRight className="w-6 h-6 -rotate-45 group-hover:rotate-0 transition-transform duration-300" />
                                </div>
                            </div>

                            <div className="mb-6 flex-1">
                                <h3 className="text-2xl font-black text-foreground mb-2 group-hover:text-primary transition-colors">{scheme.title}</h3>
                                <p className="text-sm font-bold text-secondary-foreground/60">{scheme.ministry}</p>
                            </div>

                            <div className="flex flex-wrap gap-2 mb-8">
                                {scheme.keywords?.slice(0, 2).map((k, ki) => (
                                    <span key={ki} className="px-3 py-1 bg-secondary border border-border/50 rounded-lg text-[10px] font-bold text-secondary-foreground uppercase tracking-wider">
                                        {k}
                                    </span>
                                ))}
                            </div>

                            <div className="flex items-center justify-between pt-6 border-t border-border/30">
                                <div>
                                    <p className="text-[10px] font-black text-secondary-foreground/40 uppercase tracking-[0.2em] mb-1">BENEFIT</p>
                                    <p className="text-lg font-black text-foreground tracking-tight">{scheme.benefit}</p>
                                </div>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        alert(`Opening application for ${scheme.title}`);
                                    }}
                                    className="px-6 py-3.5 bg-foreground text-background rounded-xl text-xs font-black uppercase tracking-[0.1em] hover:scale-105 active:scale-95 transition-all shadow-lg"
                                >
                                    APPLY NOW
                                </button>
                            </div>
                        </motion.div>
                    ))
                )}
            </div>
        </div>
    );
}
