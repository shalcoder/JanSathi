'use client';

import React, { useState, useEffect } from 'react';
import { ShoppingBag, TrendingUp, TrendingDown, MapPin, Search, Calendar, RefreshCw } from 'lucide-react';
import { getMarketRates } from '@/services/api';

const MarketPrices = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [prices, setPrices] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchRates = async () => {
        setIsLoading(true);
        try {
            const data = await getMarketRates();
            // If API fails/returns empty, we use our fallback defaults for demo
            setPrices(data.length > 0 ? data : [
                { crop: "Wheat (Gehun)", market: "Lucknow", price: "2450", unit: "quintal", change: "+12", trend: "up" },
                { crop: "Rice (Chawal)", market: "Patna", price: "3100", unit: "quintal", change: "-5", trend: "down" },
                { crop: "Potato (Aloo)", market: "Agra", price: "1200", unit: "quintal", change: "+45", trend: "up" },
                { crop: "Onion (Pyaz)", market: "Nasik", price: "2800", unit: "quintal", change: "+110", trend: "up" },
                { crop: "Tomato (Tamatar)", market: "Bangalore", price: "1500", unit: "quintal", change: "-200", trend: "down" },
                { crop: "Mustard (Sarson)", market: "Jaipur", price: "5600", unit: "quintal", change: "+15", trend: "up" },
            ]);
        } catch (e) {
            console.error("Fetch error", e);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchRates();
    }, []);

    const filteredPrices = prices.filter(p =>
        p.crop.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.market.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="min-h-full flex flex-col gap-4 sm:gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500 font-sans">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
                <div>
                    <h2 className="text-3xl font-black text-white mb-2">Mandi (Market) Rates</h2>
                    <p className="text-slate-400 font-medium">Live agricultural commodity prices from across India.</p>
                </div>
                <div className="flex gap-2 w-full md:w-auto">
                    <button
                        onClick={fetchRates}
                        className="p-3 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all text-slate-400"
                        title="Refresh Rates"
                    >
                        <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
                    </button>
                    <div className="relative flex-1 md:w-64">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input
                            type="text"
                            placeholder="Search crop or market..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-white"
                        />
                    </div>
                </div>
            </div>

            {isLoading && prices.length === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center py-20 bg-white/5 rounded-[3rem] border border-dashed border-white/10">
                    <RefreshCw className="w-12 h-12 text-blue-500 animate-spin mb-4" />
                    <p className="text-slate-500 font-bold uppercase tracking-widest text-xs">Connecting to mandis...</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredPrices.map((p, idx) => (
                        <div key={idx} className="glass-panel p-6 rounded-[2rem] border border-white/5 hover:border-blue-500/30 transition-all group">
                            <div className="flex justify-between items-start mb-4">
                                <div className="p-3 bg-white/5 rounded-2xl group-hover:bg-blue-500/10 transition-colors">
                                    <ShoppingBag className="w-6 h-6 text-blue-400" />
                                </div>
                                <div className={`flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold uppercase ${p.trend === 'up' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
                                    {p.trend === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                    {p.change} today
                                </div>
                            </div>

                            <h3 className="text-xl font-bold text-white mb-1">{p.crop}</h3>
                            <div className="flex items-center gap-2 text-slate-500 text-sm mb-6">
                                <MapPin className="w-3 h-3" />
                                {p.market} Mandi
                            </div>

                            <div className="flex items-end justify-between">
                                <div>
                                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Current Rate</p>
                                    <p className="text-2xl font-black text-white">₹{p.price}<span className="text-xs text-slate-500 font-bold ml-1">/{p.unit}</span></p>
                                </div>
                                <button className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all">
                                    History
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="p-8 glass-panel rounded-[3rem] border border-blue-500/10 bg-gradient-to-br from-blue-600/5 to-transparent relative overflow-hidden flex-1">
                    <div className="relative z-10 flex flex-col md:flex-row items-center gap-6">
                        <div className="w-16 h-16 rounded-3xl bg-blue-500 flex items-center justify-center shadow-2xl shadow-blue-500/40">
                            <Calendar className="w-8 h-8 text-white" />
                        </div>
                        <div className="flex-1 text-center md:text-left">
                            <h3 className="text-xl font-bold text-white mb-2">Market Prediction AI</h3>
                            <p className="text-slate-400 text-sm leading-relaxed">
                                Based on current weather patterns, Wheat prices are expected to rise. Consider selling in 2 weeks.
                            </p>
                        </div>
                    </div>
                </div>

                <div className="p-8 glass-panel rounded-[3rem] border border-emerald-500/10 bg-gradient-to-br from-emerald-600/5 to-transparent relative overflow-hidden flex-1">
                    <div className="relative z-10">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold text-white">Recommended Inputs</h3>
                            <span className="text-[10px] font-black text-emerald-500 uppercase tracking-widest px-3 py-1 bg-emerald-500/10 rounded-full">Best Deals</span>
                        </div>
                        <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-none">
                            {[
                                { name: "Organic Urea", price: "450", disc: "10% OFF" },
                                { name: "Basmati Seeds", price: "2100", disc: "Trending" },
                                { name: "Hand Tiller", price: "3400", disc: "Subsidy" }
                            ].map((item, i) => (
                                <div key={i} className="min-w-[160px] p-4 bg-white/5 rounded-2xl border border-white/5 text-center flex flex-col items-center">
                                    <p className="text-xs font-bold text-white mb-1">{item.name}</p>
                                    <p className="text-lg font-black text-emerald-400">₹{item.price}</p>
                                    <p className="text-[8px] font-black text-slate-500 uppercase mt-2 mb-4">{item.disc}</p>
                                    <button className="w-full py-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-500 text-[10px] font-bold rounded-lg transition-all">
                                        Contact Dealer
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MarketPrices;
