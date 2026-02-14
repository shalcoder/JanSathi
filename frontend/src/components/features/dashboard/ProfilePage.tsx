'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
    Save,
    Fingerprint,
    ArrowUpRight,
    Activity
} from 'lucide-react';

const ProfilePage = () => {
    const [profile, setProfile] = useState({
        firstName: 'Rajesh',
        lastName: 'Kumar',
        email: 'rajesh.k@jansathi.in',
        location: 'Varanasi, Uttar Pradesh',
        language: 'Hindi',
        notifications: 'SMS & Voice'
    });

    const [familyMembers, setFamilyMembers] = useState([
        { relation: "Spouse", name: "Suman Devi", age: "32", status: "Covered", initials: "SD" },
        { relation: "Child", name: "Rahul Kumar", age: "08", status: "Covered", initials: "RK" },
        { relation: "Parent", name: "Ram Swaroop", age: "65", status: "Covered", initials: "RS" },
    ]);

    const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
    const [isFamilyModalOpen, setIsFamilyModalOpen] = useState(false);
    const [editForm, setEditForm] = useState({ ...profile });
    const [familyForm, setFamilyForm] = useState({ relation: 'Child', name: '', age: '' });

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
        <div className="h-full max-w-6xl mx-auto pb-20 relative px-4 sm:px-0">

            {/* Profile Header */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-10"
            >
                <div className="bg-card p-8 sm:p-10 rounded-2xl border border-border/50 shadow-sm relative overflow-hidden">
                    <div className="flex flex-col md:flex-row items-center gap-8 md:gap-12 relative z-10">
                        <div className="relative">
                            <div className="w-32 h-32 sm:w-40 sm:h-40 rounded-2xl bg-primary/10 p-1 flex items-center justify-center border-2 border-primary/20">
                                <div className="w-full h-full flex items-center justify-center bg-primary rounded-xl text-4xl sm:text-5xl font-bold text-white">
                                    {profile.firstName?.[0]}{profile.lastName?.[0]}
                                </div>
                            </div>
                            <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-emerald-500 rounded-lg border-2 border-white dark:border-slate-900 flex items-center justify-center shadow-lg">
                                <Fingerprint className="w-5 h-5 text-white" />
                            </div>
                        </div>

                        <div className="text-center md:text-left flex-1">
                            <div className="flex flex-col md:flex-row md:items-center gap-4 mb-4">
                                <h2 className="text-3xl sm:text-4xl font-bold text-foreground tracking-tight">{profile.firstName} {profile.lastName}</h2>
                                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-50 border border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-500/20">
                                    <ShieldCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                                    <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-widest">Verified Beneficiary</span>
                                </div>
                            </div>
                            <p className="text-base text-secondary-foreground font-medium flex items-center justify-center md:justify-start gap-2 mb-6 opacity-70">
                                <Mail className="w-4 h-4 text-primary" />
                                {profile.email}
                            </p>

                            <div className="flex flex-wrap justify-center md:justify-start gap-4">
                                <div className="px-4 py-2 bg-secondary/50 border border-border rounded-xl flex items-center gap-2">
                                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                                    <span className="text-[10px] font-bold text-foreground opacity-60 uppercase tracking-widest">KYC Completed</span>
                                </div>
                                <div className="px-4 py-2 bg-secondary/50 border border-border rounded-xl flex items-center gap-2">
                                    <MapPin className="w-4 h-4 text-primary opacity-60" />
                                    <span className="text-[10px] font-bold text-foreground opacity-60 uppercase tracking-widest">{profile.location}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </motion.div>

            {/* Stats Overview - More robust grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
                {[
                    { label: "Total Benefits Received", value: "₹21,500", detail: "Paid on Feb 04", color: "text-primary", icon: Activity },
                    { label: "Active Applications", value: "03", detail: "In Progress", color: "text-blue-600", icon: FileText },
                    { label: "Verification Score", value: "98%", detail: "Excellent", color: "text-emerald-600", icon: ShieldCheck },
                ].map((stat, idx) => (
                    <motion.div
                        key={idx}
                        className="p-8 bg-card border border-border/50 rounded-2xl shadow-sm group transition-shadow hover:shadow-md"
                    >
                        <p className="text-[11px] font-bold text-secondary-foreground uppercase tracking-wider mb-3 opacity-50">{stat.label}</p>
                        <p className={`text-5xl font-bold ${stat.color} tracking-tight mb-2`}>{stat.value}</p>
                        <p className="text-[10px] text-secondary-foreground font-bold uppercase tracking-widest opacity-40">{stat.detail}</p>
                    </motion.div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Linked Documents & Family */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="bg-card p-8 rounded-2xl border border-border shadow-sm">
                        <div className="flex justify-between items-center mb-8">
                            <h3 className="text-xl font-bold text-foreground flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                                    <FileText className="w-5 h-5 text-primary" />
                                </div>
                                Linked Documents
                            </h3>
                            <button className="text-[10px] font-bold text-primary uppercase tracking-widest hover:underline">
                                Sync Portal
                            </button>
                        </div>

                        <div className="grid gap-4">
                            {[
                                { name: "Aadhaar Card", id: "XXXX-XXXX-8829", status: "Active", icon: <Fingerprint className="text-emerald-500" /> },
                                { name: "Ration Card", id: "NFSA-UP-002931-XX", status: "Verified", icon: <CheckCircle className="text-primary" /> },
                                { name: "PAN Card", id: "XXXXX1234F", status: "Connected", icon: <ShieldCheck className="text-blue-500" /> }
                            ].map((doc, idx) => (
                                <div
                                    key={idx}
                                    className="flex items-center justify-between p-5 bg-secondary/20 border border-border/50 rounded-xl transition-colors hover:bg-secondary/30"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className="w-12 h-12 rounded-lg bg-background border border-border/30 flex items-center justify-center">
                                            <FileText className="w-6 h-6 text-foreground/40" />
                                        </div>
                                        <div>
                                            <p className="text-base font-bold text-foreground leading-none mb-1">{doc.name}</p>
                                            <p className="text-[10px] font-medium text-secondary-foreground opacity-50 uppercase tracking-widest">{doc.id}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2 px-3 py-1 bg-background border border-border/50 rounded-lg shadow-sm">
                                        <div className="w-4 h-4">{doc.icon}</div>
                                        <span className="text-[9px] font-bold uppercase tracking-widest text-foreground opacity-60">{doc.status}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Family Registry */}
                    <div className="bg-card p-8 rounded-2xl border border-border shadow-sm">
                        <div className="flex justify-between items-center mb-8">
                            <h3 className="text-xl font-bold text-foreground flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center">
                                    <Users className="w-5 h-5 text-blue-600" />
                                </div>
                                Family Registry
                            </h3>
                            <button
                                onClick={() => setIsFamilyModalOpen(true)}
                                className="px-5 py-2 bg-blue-600 text-white rounded-lg text-xs font-bold uppercase tracking-widest shadow-sm hover:bg-blue-700 transition-colors flex items-center gap-2"
                            >
                                <Plus className="w-4 h-4" />
                                Add Member
                            </button>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                            {familyMembers.map((member, i) => (
                                <div
                                    key={i}
                                    className="relative p-6 bg-card border border-border rounded-xl flex flex-col gap-4 shadow-sm group hover:border-primary/30 transition-all"
                                >
                                    <div className="flex justify-between items-start">
                                        <span className="text-[10px] font-bold text-blue-500 uppercase tracking-widest bg-blue-500/10 px-2 py-1 rounded-md">{member.relation}</span>
                                        <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20">
                                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                                            <span className="text-[9px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Active</span>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-4 mt-2">
                                        <div className="w-12 h-12 rounded-full bg-secondary flex items-center justify-center text-foreground font-bold text-lg border border-border">
                                            {member.initials}
                                        </div>
                                        <div>
                                            <p className="text-lg font-bold text-foreground leading-tight">{member.name}</p>
                                            <p className="text-[10px] text-secondary-foreground font-bold uppercase tracking-widest opacity-50 mt-1">Age: {member.age}</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Sidebar - Settings Summary */}
                <div className="space-y-6">
                    <div className="bg-card p-8 rounded-2xl border border-border shadow-sm">
                        <h3 className="text-base font-bold text-foreground mb-6 uppercase tracking-widest opacity-50">Preferences</h3>
                        <div className="space-y-6">
                            {[
                                { label: "Main Language", val: profile.language, icon: Languages, color: "text-primary" },
                                { label: "Notifications", val: profile.notifications, icon: Bell, color: "text-blue-600" },
                            ].map((item, i) => (
                                <div key={i} className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-secondary flex items-center justify-center border border-border">
                                        <item.icon className={`w-6 h-6 ${item.color}`} />
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-secondary-foreground uppercase font-bold tracking-widest mb-0.5 opacity-50">{item.label}</p>
                                        <p className="text-sm font-bold text-foreground">{item.val}</p>
                                    </div>
                                </div>
                            ))}

                            <div className="pt-4">
                                <button
                                    onClick={() => { setEditForm({ ...profile }); setIsProfileModalOpen(true); }}
                                    className="w-full py-4 bg-foreground dark:bg-slate-100 text-white dark:text-slate-900 rounded-xl text-xs font-bold uppercase tracking-widest shadow-sm hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
                                >
                                    <Save className="w-4 h-4" />
                                    Update Profile
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="p-6 bg-secondary/20 border border-border rounded-2xl text-center">
                        <ShieldCheck className="w-8 h-8 text-primary mx-auto mb-3 opacity-30" />
                        <p className="text-[9px] text-secondary-foreground font-bold uppercase tracking-widest opacity-40">
                            Securely Managed <br />
                            by JanSathi AI
                        </p>
                    </div>
                </div>
            </div>

            {/* Modals */}
            <AnimatePresence>
                {(isProfileModalOpen || isFamilyModalOpen) && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
                            onClick={() => { setIsProfileModalOpen(false); setIsFamilyModalOpen(false); }}
                        />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-card w-full max-w-lg p-8 sm:p-10 rounded-2xl border border-border/50 shadow-2xl relative z-10"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <button
                                onClick={() => { setIsProfileModalOpen(false); setIsFamilyModalOpen(false); }}
                                className="absolute top-6 right-6 p-2 text-secondary-foreground hover:text-foreground transition-colors"
                            >
                                <X className="w-6 h-6" />
                            </button>

                            <h3 className="text-2xl font-bold text-foreground mb-8 tracking-tight">
                                {isProfileModalOpen ? 'Update Profile' : 'Add Family Member'}
                            </h3>

                            {isProfileModalOpen ? (
                                <form onSubmit={handleProfileSubmit} className="space-y-5">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-1">
                                            <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">First Name</label>
                                            <input type="text" value={editForm.firstName} onChange={(e) => setEditForm(prev => ({ ...prev, firstName: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-primary" required />
                                        </div>
                                        <div className="space-y-1">
                                            <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">Last Name</label>
                                            <input type="text" value={editForm.lastName} onChange={(e) => setEditForm(prev => ({ ...prev, lastName: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-primary" required />
                                        </div>
                                    </div>
                                    <div className="space-y-1">
                                        <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">Email Address</label>
                                        <input type="email" value={editForm.email} onChange={(e) => setEditForm(prev => ({ ...prev, email: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-primary" required />
                                    </div>
                                    <div className="space-y-1">
                                        <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">Region / Location</label>
                                        <input type="text" value={editForm.location} onChange={(e) => setEditForm(prev => ({ ...prev, location: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-primary" required />
                                    </div>
                                    <button type="submit" className="w-full py-4 mt-4 bg-primary text-white rounded-xl text-xs font-bold uppercase tracking-widest shadow-sm hover:opacity-90 transition-opacity">
                                        Save Changes
                                    </button>
                                </form>
                            ) : (
                                <form onSubmit={handleFamilySubmit} className="space-y-5">
                                    <div className="space-y-1">
                                        <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">Full Name</label>
                                        <input type="text" value={familyForm.name} onChange={(e) => setFamilyForm(prev => ({ ...prev, name: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-blue-600" required />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-1">
                                            <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">Relation</label>
                                            <select value={familyForm.relation} onChange={(e) => setFamilyForm(prev => ({ ...prev, relation: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-blue-600 appearance-none">
                                                <option value="Spouse">Spouse</option><option value="Child">Child</option><option value="Parent">Parent</option><option value="Sibling">Sibling</option>
                                            </select>
                                        </div>
                                        <div className="space-y-1">
                                            <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">Age</label>
                                            <input type="number" value={familyForm.age} onChange={(e) => setFamilyForm(prev => ({ ...prev, age: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-blue-600" required />
                                        </div>
                                    </div>
                                    <button type="submit" className="w-full py-4 mt-4 bg-blue-600 text-white rounded-xl text-xs font-bold uppercase tracking-widest shadow-sm hover:bg-blue-700 transition-colors">
                                        Add Family Member
                                    </button>
                                </form>
                            )}
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default ProfilePage;
