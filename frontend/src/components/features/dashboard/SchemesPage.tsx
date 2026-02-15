import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, ArrowRight, Landmark, Sprout, Building2, GraduationCap, HeartPulse } from 'lucide-react';

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
        const fetchSchemes = async () => {
            try {
                const response = await fetch('/api/schemes');
                const data = await response.json();
                if (data.schemes) {
                    setSchemes(data.schemes);
                    setFilteredSchemes(data.schemes);
                }
            } catch (error) {
                console.error("Failed to fetch schemes:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchSchemes();
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
                            className="group relative bg-card hover:bg-secondary/10 border border-border/50 hover:border-primary/30 rounded-2xl p-6 transition-all cursor-pointer shadow-sm hover:shadow-md"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-wider">
                                    Official
                                </span>
                                <button className="text-secondary-foreground/40 hover:text-primary transition-colors">
                                    <ArrowRight className="w-5 h-5 -rotate-45 group-hover:rotate-0 transition-transform" />
                                </button>
                            </div>

                            <h3 className="text-xl font-black text-foreground mb-1">{scheme.title}</h3>
                            <p className="text-sm font-medium text-secondary-foreground mb-4">{scheme.ministry}</p>

                            <div className="flex items-center justify-between mt-auto pt-4 border-t border-border/40">
                                <div>
                                    <p className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider">Benefit</p>
                                    <p className="font-bold text-foreground truncate max-w-[150px]">{scheme.benefit}</p>
                                </div>
                                <button className="px-4 py-2 bg-foreground text-background rounded-lg text-[10px] font-bold uppercase tracking-widest hover:opacity-90 transition-opacity">
                                    View Details
                                </button>
                            </div>
                        </motion.div>
                    ))
                )}
            </div>
        </div>
    );
}
