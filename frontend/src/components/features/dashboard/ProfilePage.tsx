'use client';

import React from 'react';
import { User, Mail, Shield, Bell, MapPin, Calendar, Award } from 'lucide-react';
import { useSettings } from '@/hooks/useSettings';

const ProfilePage = () => {
    const { settings } = useSettings();
    // Demo user (no authentication required)
    const user = {
        firstName: 'Demo',
        lastName: 'User',
        imageUrl: '',
        primaryEmailAddress: { toString: () => 'demo@jansathi.ai' }
    };

    const languageMap: Record<string, string> = {
        'hi': 'Hindi (हिन्दी)',
        'en': 'English',
        'kn': 'Kannada (ಕನ್ನಡ)',
        'ta': 'Tamil (தமிழ்)'
    };

    return (
        <div className="min-h-full max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500 font-sans">
            {/* Profile Header */}
            <div className="glass-panel p-8 rounded-[40px] border border-white/10 mb-6 bg-gradient-to-br from-blue-600/10 to-purple-600/10 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>

                <div className="flex flex-col md:flex-row items-center gap-8 relative z-10">
                    <div className="relative">
                        <div className="w-32 h-32 rounded-[2rem] bg-gradient-to-br from-blue-500 to-indigo-600 p-1 shadow-2xl shadow-blue-500/20">
                            {user.imageUrl ? (
                                <img src={user.imageUrl} className="w-full h-full object-cover rounded-[1.8rem]" alt="Profile" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center bg-slate-900 rounded-[1.8rem] text-4xl font-bold text-white">
                                    {user.firstName?.[0]}{user.lastName?.[0]}
                                </div>
                            )}
                        </div>
                        <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-emerald-500 rounded-2xl border-4 border-slate-950 flex items-center justify-center">
                            <Shield className="w-5 h-5 text-white" />
                        </div>
                    </div>

                    <div className="text-center md:text-left flex-1">
                        <div className="flex flex-col md:flex-row md:items-center gap-3 mb-2">
                            <h2 className="text-3xl font-black text-white">{user.firstName} {user.lastName}</h2>
                            <span className="px-3 py-1 rounded-full bg-blue-500/20 border border-blue-500/30 text-[10px] font-bold text-blue-400 uppercase tracking-widest self-center md:self-auto">Citizen Elite</span>
                        </div>
                        <p className="text-slate-400 font-medium flex items-center justify-center md:justify-start gap-2 mb-4">
                            <Mail className="w-4 h-4" />
                            {user.primaryEmailAddress?.toString() || 'demo@jansathi.ai'}
                        </p>

                        <div className="flex flex-wrap justify-center md:justify-start gap-4">
                            <div className="px-4 py-2 bg-white/5 rounded-2xl border border-white/5 flex items-center gap-2">
                                <Award className="w-4 h-4 text-amber-400" />
                                <span className="text-xs font-semibold text-slate-300">Level 4 Contributor</span>
                            </div>
                            <div className="px-4 py-2 bg-white/5 rounded-2xl border border-white/5 flex items-center gap-2">
                                <Shield className="w-4 h-4 text-emerald-400" />
                                <span className="text-xs font-semibold text-slate-300">Verified Citizen</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                {[
                    { label: "Active Schemes", value: "3", color: "text-blue-500", bg: "bg-blue-500/10" },
                    { label: "Queries This Month", value: "124", color: "text-purple-500", bg: "bg-purple-500/10" },
                    { label: "Documents Scanned", value: "12", color: "text-emerald-500", bg: "bg-emerald-500/10" },
                ].map((stat, idx) => (
                    <div key={idx} className="glass-panel p-6 rounded-3xl border border-white/5">
                        <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">{stat.label}</p>
                        <p className={`text-3xl font-black ${stat.color}`}>{stat.value}</p>
                    </div>
                ))}
            </div>

            {/* Details Card */}
            <div className="glass-panel p-8 rounded-[40px] border border-white/10">
                <h3 className="text-xl font-bold text-white mb-6">Personal Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-6">
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center">
                                <MapPin className="w-5 h-5 text-slate-400" />
                            </div>
                            <div>
                                <p className="text-[10px] text-slate-500 uppercase font-bold">Location</p>
                                <p className="text-sm text-slate-200">Lucknow, Uttar Pradesh</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center">
                                <Calendar className="w-5 h-5 text-slate-400" />
                            </div>
                            <div>
                                <p className="text-[10px] text-slate-500 uppercase font-bold">Member Since</p>
                                <p className="text-sm text-slate-200">September 2023</p>
                            </div>
                        </div>
                    </div>
                    <div className="space-y-6">
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center">
                                <Bell className="w-5 h-5 text-slate-400" />
                            </div>
                            <div>
                                <p className="text-[10px] text-slate-500 uppercase font-bold">Preferred Language</p>
                                <p className="text-sm text-slate-200">{languageMap[settings.language] || 'Hindi (हिन्दी)'}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;
