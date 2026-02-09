'use client';

import React, { useState } from 'react';
import {
    Mail,
    ShieldCheck,
    CheckCircle,
    Bell,
    Languages,
    Users,
    FileText,
    MapPin,
    X,
    Plus,
    Save
} from 'lucide-react';

const ProfilePage = () => {
    // 1. State Management
    const [profile, setProfile] = useState({
        firstName: 'Demo',
        lastName: 'User',
        email: 'demo@jansathi.ai',
        location: 'Lucknow, UP',
        language: 'Hindi (हिन्दी)',
        notifications: 'SMS & Voice Prompt'
    });

    const [familyMembers, setFamilyMembers] = useState([
        { relation: "Spouse", name: "Suman Devi", age: "32", status: "Covered", initials: "SD" },
        { relation: "Child", name: "Rahul Kumar", age: "08", status: "Covered", initials: "RK" },
        { relation: "Parent", name: "Ram Swaroop", age: "65", status: "Covered", initials: "RS" },
    ]);

    const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
    const [isFamilyModalOpen, setIsFamilyModalOpen] = useState(false);

    // Form states
    const [editForm, setEditForm] = useState({ ...profile });
    const [familyForm, setFamilyForm] = useState({ relation: 'Child', name: '', age: '' });

    // Handlers
    const handleProfileSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setProfile(editForm);
        setIsProfileModalOpen(false);
    };

    const handleFamilySubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const initials = familyForm.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        setFamilyMembers(prev => [...prev, { ...familyForm, status: 'Covered', initials }]);
        setFamilyForm({ relation: 'Child', name: '', age: '' });
        setIsFamilyModalOpen(false);
    };

    return (
        <div className="h-full max-w-5xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500 pb-12">
            {/* Profile Header */}
            <div className="glass-panel p-8 rounded-[40px] mb-6 bg-gradient-to-br from-blue-600/10 to-transparent relative overflow-hidden transition-colors">
                <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>

                <div className="flex flex-col md:flex-row items-center gap-8 relative z-10">
                    <div className="relative group">
                        <div className="w-36 h-36 rounded-[2.5rem] bg-slate-900 border border-white/10 p-1.5 flex items-center justify-center transition-all duration-500 shadow-premium group-hover:shadow-premium-hover group-hover:-translate-y-1">
                            <div className="w-full h-full flex items-center justify-center bg-blue-600/10 rounded-[2rem] text-5xl font-black text-blue-500 shadow-inner">
                                {profile.firstName?.[0]}{profile.lastName?.[0]}
                            </div>
                        </div>
                        <div className="absolute -bottom-2 -right-2 w-12 h-12 bg-emerald-500 rounded-2xl border-4 border-slate-950 flex items-center justify-center shadow-2xl transition-all duration-500 group-hover:scale-110">
                            <ShieldCheck className="w-6 h-6 text-white" />
                        </div>
                    </div>

                    <div className="text-center md:text-left flex-1">
                        <div className="flex flex-col md:flex-row md:items-center gap-4 mb-3">
                            <h2 className="text-4xl font-black text-white transition-colors tracking-tight">{profile.firstName} {profile.lastName}</h2>
                            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 shadow-sm self-center md:self-auto">
                                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                                <span className="text-[10px] font-black text-emerald-400 uppercase tracking-[0.2em]">Verified Beneficiary</span>
                            </div>
                        </div>
                        <p className="text-slate-400 font-bold flex items-center justify-center md:justify-start gap-2 mb-6 transition-colors">
                            <Mail className="w-4 h-4 text-blue-500" />
                            {profile.email}
                        </p>

                        <div className="flex flex-wrap justify-center md:justify-start gap-4">
                            <div className="px-4 py-2 bg-white/5 rounded-2xl border border-white/5 flex items-center gap-2 transition-colors">
                                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                                <span className="text-xs font-bold text-slate-300 uppercase tracking-tighter">e-KYC Complete</span>
                            </div>
                            <div className="px-4 py-2 bg-white/5 rounded-2xl border border-white/5 flex items-center gap-2 text-slate-400 transition-colors">
                                <MapPin className="w-4 h-4" />
                                <span className="text-xs font-semibold">{profile.location}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Top Stats - Benefit Focused */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                {[
                    { label: "Total Benefits Received", value: "₹14,500", detail: "Last paid: Jan 12", color: "text-blue-400" },
                    { label: "Active Applications", value: "02", detail: "PM-Kisan, Ration Card", color: "text-amber-400" },
                    { label: "Next Disbursement", value: "Oct 15", detail: "Estimated date", color: "text-emerald-400" },
                ].map((stat, idx) => (
                    <div key={idx} className="glass-panel p-8 rounded-[2.5rem] border border-white/5 relative group shadow-premium hover:shadow-premium-hover transition-all duration-500">
                        <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">{stat.label}</p>
                        <p className={`text-5xl font-black ${stat.color} mb-2 tracking-tighter`}>{stat.value}</p>
                        <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest italic">{stat.detail}</p>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Linked Documents - The "Digital Locker" */}
                <div className="lg:col-span-2 space-y-8">
                    {/* Linked Documents - The "Digital Locker" */}
                    <div className="glass-panel p-8 rounded-[2.5rem] shadow-premium">
                        <div className="flex justify-between items-center mb-8">
                            <h3 className="text-xl font-black text-white flex items-center gap-3 transition-colors">
                                <div className="w-10 h-10 rounded-xl bg-blue-600/10 flex items-center justify-center">
                                    <FileText className="w-6 h-6 text-blue-500" />
                                </div>
                                Linked Official IDs
                            </h3>
                            <button
                                onClick={() => alert("Redirecting to Official Document Linking portal...")}
                                className="text-[10px] font-black text-blue-500 uppercase tracking-widest hover:underline decoration-2 underline-offset-4"
                            >
                                Manage Links
                            </button>
                        </div>

                        <div className="grid gap-4">
                            {[
                                { name: "Aadhaar Card", id: "XXXX-XXXX-8829", status: "Verified", icon: <ShieldCheck className="text-emerald-500" /> },
                                { name: "Ration Card (PHH)", id: "NFSA-UP-002931-XX", status: "Active", icon: <CheckCircle className="text-blue-400" /> },
                                { name: "PAN Card", id: "XXXXX1234F", status: "Verified", icon: <ShieldCheck className="text-emerald-500" /> }
                            ].map((doc, idx) => (
                                <div key={idx} className="flex items-center justify-between p-5 bg-slate-900 border border-white/5 rounded-2xl hover:bg-white/[0.08] transition-all duration-300 shadow-sm hover:shadow-md group/doc">
                                    <div className="flex items-center gap-5">
                                        <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center shadow-inner group-hover/doc:scale-110 transition-transform">
                                            <FileText className="w-6 h-6 text-slate-500" />
                                        </div>
                                        <div>
                                            <p className="font-black text-white transition-colors tracking-tight">{doc.name}</p>
                                            <p className="text-xs font-black font-mono text-slate-500 uppercase">{doc.id}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 shadow-inner">
                                        <div className="w-4 h-4">
                                            {doc.icon}
                                        </div>
                                        <span className="text-[10px] font-black uppercase tracking-widest text-slate-300">{doc.status}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Family Unit Section - Repositioned Here */}
                    <div className="glass-panel p-8 rounded-[2.5rem] bg-gradient-to-br from-purple-600/5 to-transparent shadow-premium transition-colors">
                        <div className="flex justify-between items-center mb-8">
                            <h3 className="text-xl font-black text-white flex items-center gap-3 transition-colors">
                                <div className="w-10 h-10 rounded-xl bg-purple-600/10 flex items-center justify-center">
                                    <Users className="w-6 h-6 text-purple-400" />
                                </div>
                                Family Unit Members
                            </h3>
                            <button
                                onClick={() => setIsFamilyModalOpen(true)}
                                className="text-[10px] font-black text-purple-400 uppercase tracking-widest hover:underline decoration-2 underline-offset-4"
                            >
                                + Add Member
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {familyMembers.map((member, i) => (
                                <div key={i} className="p-7 bg-slate-900/40 rounded-[2.5rem] border border-white/5 flex flex-col gap-5 shadow-sm hover:shadow-premium transition-all duration-500 group/member hover:border-purple-500/20">
                                    {/* Line 1: Relation & Status */}
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <div className="w-1.5 h-1.5 rounded-full bg-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.5)]"></div>
                                            <p className="text-[10px] font-black text-purple-400 uppercase tracking-[0.2em]">{member.relation}</p>
                                        </div>
                                        <div className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 shadow-sm">
                                            <span className="text-[9px] font-black text-emerald-500 uppercase tracking-widest">Covered</span>
                                        </div>
                                    </div>

                                    {/* Line 2: Avatar & Name */}
                                    <div className="flex items-center gap-5">
                                        <div className="w-14 h-14 shrink-0 rounded-2xl bg-purple-500/10 flex items-center justify-center border border-purple-500/20 text-purple-400 font-black text-sm shadow-inner group-hover/member:scale-105 transition-transform">
                                            {member.initials}
                                        </div>
                                        <p className="text-xl font-black text-white transition-colors tracking-tight leading-snug">{member.name}</p>
                                    </div>

                                    {/* Line 3: Age */}
                                    <div className="flex items-center gap-3 pl-1">
                                        <div className="h-px w-8 bg-white/5"></div>
                                        <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.2em] italic">{member.age} Years Old</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Sidebar - Personal Info & Preferences moved here */}
                <div className="space-y-6">
                    <div className="glass-panel p-8 rounded-[2.5rem] shadow-premium">
                        <h3 className="text-xl font-black text-white mb-8 transition-colors">General Settings</h3>
                        <div className="space-y-8">
                            <div className="flex items-center gap-5">
                                <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center border border-white/10">
                                    <Languages className="w-6 h-6 text-blue-400" />
                                </div>
                                <div>
                                    <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-1">Language</p>
                                    <p className="text-sm font-black text-slate-100">{profile.language}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-5">
                                <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center border border-white/10">
                                    <Bell className="w-6 h-6 text-purple-400" />
                                </div>
                                <div>
                                    <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-1">Notifications</p>
                                    <p className="text-sm font-black text-slate-100">{profile.notifications}</p>
                                </div>
                            </div>

                            <div className="pt-4">
                                <button
                                    onClick={() => {
                                        setEditForm({ ...profile });
                                        setIsProfileModalOpen(true);
                                    }}
                                    className="w-full py-5 bg-blue-600 hover:bg-blue-700 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] transition-all text-white shadow-xl shadow-blue-600/20 active:scale-95 flex items-center justify-center gap-3"
                                >
                                    <Save className="w-4 h-4" />
                                    Edit Profile Details
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="p-6 glass-panel rounded-[40px] text-center transition-colors">
                        <p className="text-[10px] text-slate-500 font-black leading-relaxed transition-colors uppercase tracking-widest">
                            Data protected by <br />
                            <span className="text-blue-500 hover:underline cursor-pointer">Digital India Policy</span>
                        </p>
                    </div>
                </div>
            </div>

            {/* --- MODALS --- */}

            {/* Edit Profile Modal */}
            {isProfileModalOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-300">
                    <div className="glass-panel w-full max-w-lg p-8 rounded-[40px] bg-slate-900 border border-white/10 shadow-2xl relative animate-in zoom-in-95 duration-300">
                        <button
                            onClick={() => setIsProfileModalOpen(false)}
                            className="absolute top-6 right-6 p-2 rounded-xl hover:bg-white/5 text-slate-400 hover:text-white transition-all"
                        >
                            <X className="w-6 h-6" />
                        </button>

                        <h3 className="text-2xl font-black text-white mb-8 tracking-tight">Edit Profile Details</h3>

                        <form onSubmit={handleProfileSubmit} className="space-y-6">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">First Name</label>
                                    <input
                                        type="text"
                                        value={editForm.firstName}
                                        onChange={(e) => setEditForm(prev => ({ ...prev, firstName: e.target.value }))}
                                        className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3.5 text-white font-bold focus:border-blue-500 outline-none transition-all"
                                        required
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Last Name</label>
                                    <input
                                        type="text"
                                        value={editForm.lastName}
                                        onChange={(e) => setEditForm(prev => ({ ...prev, lastName: e.target.value }))}
                                        className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3.5 text-white font-bold focus:border-blue-500 outline-none transition-all"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Email Address</label>
                                <input
                                    type="email"
                                    value={editForm.email}
                                    onChange={(e) => setEditForm(prev => ({ ...prev, email: e.target.value }))}
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3.5 text-white font-bold focus:border-blue-500 outline-none transition-all"
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Location</label>
                                <input
                                    type="text"
                                    value={editForm.location}
                                    onChange={(e) => setEditForm(prev => ({ ...prev, location: e.target.value }))}
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3.5 text-white font-bold focus:border-blue-500 outline-none transition-all"
                                    required
                                />
                            </div>

                            <div className="flex gap-4 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setIsProfileModalOpen(false)}
                                    className="flex-1 py-4 bg-white/5 rounded-2xl text-xs font-black text-slate-400 uppercase tracking-widest hover:text-white transition-all"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-xl shadow-blue-500/20 active:scale-95 transition-all flex items-center justify-center gap-2"
                                >
                                    <Save className="w-4 h-4" />
                                    Save Changes
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Add Family Member Modal */}
            {isFamilyModalOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-300">
                    <div className="glass-panel w-full max-w-lg p-8 rounded-[40px] bg-slate-900 border border-white/10 shadow-2xl relative animate-in zoom-in-95 duration-300">
                        <button
                            onClick={() => setIsFamilyModalOpen(false)}
                            className="absolute top-6 right-6 p-2 rounded-xl hover:bg-white/5 text-slate-400 hover:text-white transition-all"
                        >
                            <X className="w-6 h-6" />
                        </button>

                        <h3 className="text-2xl font-black text-white mb-8 tracking-tight">Add Family Member</h3>

                        <form onSubmit={handleFamilySubmit} className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Full Name</label>
                                <input
                                    type="text"
                                    value={familyForm.name}
                                    onChange={(e) => setFamilyForm(prev => ({ ...prev, name: e.target.value }))}
                                    placeholder="e.g. Suman Devi"
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3.5 text-white font-bold focus:border-purple-500 outline-none transition-all placeholder:text-slate-700"
                                    required
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Relation</label>
                                    <select
                                        value={familyForm.relation}
                                        onChange={(e) => setFamilyForm(prev => ({ ...prev, relation: e.target.value }))}
                                        className="w-full bg-slate-800 border border-white/10 rounded-2xl px-5 py-3.5 text-white font-bold focus:border-purple-500 outline-none transition-all appearance-none cursor-pointer"
                                    >
                                        <option value="Spouse">Spouse</option>
                                        <option value="Child">Child</option>
                                        <option value="Parent">Parent</option>
                                        <option value="Sibling">Sibling</option>
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Age</label>
                                    <input
                                        type="number"
                                        value={familyForm.age}
                                        onChange={(e) => setFamilyForm(prev => ({ ...prev, age: e.target.value }))}
                                        placeholder="25"
                                        className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3.5 text-white font-bold focus:border-purple-500 outline-none transition-all placeholder:text-slate-700"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="flex gap-4 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setIsFamilyModalOpen(false)}
                                    className="flex-1 py-4 bg-white/5 rounded-2xl text-xs font-black text-slate-400 uppercase tracking-widest hover:text-white transition-all"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 py-4 bg-purple-600 hover:bg-purple-700 text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-xl shadow-purple-500/20 active:scale-95 transition-all flex items-center justify-center gap-2"
                                >
                                    <Plus className="w-4 h-4" />
                                    Add Member
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ProfilePage;


