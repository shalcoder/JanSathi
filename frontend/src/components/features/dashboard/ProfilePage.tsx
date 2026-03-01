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
    Activity,
    ArrowRight,
    User
} from 'lucide-react';
import { useUser, useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { buildClient } from '@/services/api';

const ProfilePage = () => {
    const router = useRouter();
    const { user, isLoaded } = useUser();
    const { getToken } = useAuth();
    
    // Track API state
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    const [profile, setProfile] = useState({
        firstName: '',
        lastName: '',
        full_name: '',
        phone: '',
        email: '',
        location: 'Update Location',
        language: 'Hindi',
        preferred_language: 'hi',
        notifications: 'SMS & Voice',
        kycStatus: 'Pending Verification',
        occupation: 'Farmer',
        category: 'General',
        annual_income: '',
        land_holding_acres: '',
        has_aadhaar: false,
        has_ration_card: false,
        has_bank_account: false,
        has_pm_kisan: false,
    });

    // 1. Fetch live profile on mount
    React.useEffect(() => {
        if (!isLoaded || !user) return;

        const loadProfile = async () => {
            try {
                const token = await getToken();
                const client = buildClient(token || undefined);
                const res = await client.get('/v1/profile');
                const data = res.data.data;
                
                if (data) {
                    // Split full name if present
                    const names = (data.full_name || '').split(' ');
                    const firstName = names[0] || user.firstName || 'Citizen';
                    const lastName = names.length > 1 ? names.slice(1).join(' ') : (user.lastName || '');
                    
                    const loc = data.village ? `${data.village}, ${data.district}` : (data.district || 'Update Location');
                    
                    // Helper functions for options
                    const langMap: Record<string, string> = { 'hi': 'Hindi', 'en': 'English', 'ta': 'Tamil', 'kn': 'Kannada' };
                    setProfile(prev => ({
                        ...prev,
                        firstName,
                        lastName,
                        full_name: data.full_name || '',
                        phone: data.phone || '',
                        email: user.primaryEmailAddress?.emailAddress || '',
                        location: loc,
                        language: langMap[data.preferred_language] || 'Hindi',
                        preferred_language: data.preferred_language || 'hi',
                        occupation: data.occupation || 'Farmer',
                        category: data.category || 'General',
                        annual_income: data.annual_income || '',
                        land_holding_acres: data.land_holding_acres || '',
                        has_aadhaar: data.has_aadhaar || false,
                        has_ration_card: data.has_ration_card || false,
                        has_bank_account: data.has_bank_account || false,
                        has_pm_kisan: data.has_pm_kisan || false,
                        kycStatus: data.has_aadhaar ? 'KYC Completed' : 'Pending Verification'
                    }));
                }
            } catch (err: unknown) {
                console.error("Failed to load profile", err);
                const error = err as { response?: { status?: number, data?: { detail?: string } } };
                if (error.response?.status === 404 || error.response?.status === 400 || (error.response && error.response.data && String(error.response.data.detail).includes('not found'))) {
                    // Profile doesn't exist, redirect to onboarding or show empty state
                    router.push('/onboarding');
                    setError("missing_profile"); // Special flag
                } else {
                    setError("Failed to load your profile data.");
                }
            } finally {
                setIsLoading(false);
            }
        };

        loadProfile();
    }, [isLoaded, user, getToken, router]);

    // 2. Save profile to backend
    const handleProfileSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setError(null);
        setSuccessMessage(null);
        
        try {
            const token = await getToken();
            const client = buildClient(token || undefined);
            
            // Reconstruct full name
            const full_name = `${editForm.firstName} ${editForm.lastName}`.trim();
            
            await client.put('/v1/profile', {
                full_name,
                phone: editForm.phone,
                preferred_language: editForm.preferred_language,
                occupation: editForm.occupation,
                category: editForm.category,
                annual_income: editForm.annual_income,
                land_holding_acres: editForm.land_holding_acres,
            });
            
            setProfile(editForm);
            setIsProfileModalOpen(false);
            setSuccessMessage("Profile updated successfully");
            
            // Clear success message after 3 seconds
            setTimeout(() => setSuccessMessage(null), 3000);
            
        } catch (err) {
            console.error("Failed to update profile", err);
            setError("Failed to update profile. Please try again.");
        } finally {
            setIsSaving(false);
        }
    };

    const [familyMembers, setFamilyMembers] = useState([
        { relation: "Spouse", name: "Suman Devi", age: "32", status: "Covered", initials: "SD" },
        { relation: "Child", name: "Rahul Kumar", age: "08", status: "Covered", initials: "RK" },
        { relation: "Parent", name: "Ram Swaroop", age: "65", status: "Covered", initials: "RS" },
    ]);

    const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
    const [isFamilyModalOpen, setIsFamilyModalOpen] = useState(false);
    const [editForm, setEditForm] = useState({ ...profile });
    // Sync editForm when profile changes (e.g. on load)
    React.useEffect(() => {
        setEditForm(profile);
    }, [profile]);

    const [familyForm, setFamilyForm] = useState({ relation: 'Child', name: '', age: '' });

    const handleFamilySubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const initials = familyForm.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        setFamilyMembers(prev => [...prev, { ...familyForm, status: 'Covered', initials }]);
        setFamilyForm({ relation: 'Child', name: '', age: '' });
        setIsFamilyModalOpen(false);
    };

    if (isLoading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full"></div>
            </div>
        );
    }

    if (error === "missing_profile") {
        return (
            <div className="h-full flex flex-col items-center justify-center text-center p-6">
                <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center mb-6 border border-primary/20">
                    <User className="w-12 h-12 text-primary" />
                </div>
                <h2 className="text-3xl font-black text-foreground mb-4">Complete Your Profile</h2>
                <p className="text-secondary-foreground max-w-md mb-8">
                    To access personalized government schemes, notifications, and the IVR features, please complete your onboarding profile.
                </p>
                <button 
                  onClick={() => router.push('/onboarding')}
                  className="px-8 py-4 bg-primary text-white rounded-xl font-bold flex items-center gap-2 hover:bg-orange-600 transition-all shadow-lg"
                >
                    Start Onboarding <ArrowRight className="w-5 h-5" />
                </button>
            </div>
        );
    }

    return (
        <div className="h-full max-w-6xl mx-auto pb-20 relative px-4 sm:px-0">
            {error && error !== "missing_profile" && (
                <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 text-sm font-medium">
                    {error}
                </div>
            )}
            {successMessage && (
                <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 text-sm font-medium flex items-center gap-2">
                    <CheckCircle className="w-5 h-5" />
                    {successMessage}
                </div>
            )}

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
                                <div className={`px-4 py-2 ${profile.kycStatus === 'KYC Completed' ? 'bg-emerald-50 border-emerald-100' : 'bg-amber-50 border-amber-100'} border rounded-xl flex items-center gap-2`}>
                                    {profile.kycStatus === 'KYC Completed' ? <CheckCircle className="w-4 h-4 text-emerald-500" /> : <Activity className="w-4 h-4 text-amber-500" />}
                                    <span className={`text-[10px] font-bold ${profile.kycStatus === 'KYC Completed' ? 'text-emerald-700' : 'text-amber-700'} uppercase tracking-widest`}>{profile.kycStatus}</span>
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
                        <h3 className="text-base font-bold text-foreground mb-6 uppercase tracking-widest opacity-50">Socioeconomic Profile</h3>
                        <div className="space-y-6">
                            {[
                                { label: "Main Language", val: profile.language, icon: Languages, color: "text-primary" },
                                { label: "Mobile Number", val: profile.phone || "Not Set", icon: Bell, color: "text-blue-600" },
                                { label: "Occupation", val: profile.occupation, icon: Activity, color: "text-emerald-500" },
                                { label: "Caste Category", val: profile.category, icon: Users, color: "text-amber-500" },
                                { label: "Registered Land", val: profile.land_holding_acres ? `${profile.land_holding_acres} Acres` : 'N/A', icon: MapPin, color: "text-purple-500" },
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

                    <div className="p-6 bg-card border border-border shadow-sm rounded-2xl text-center relative overflow-hidden group hover:border-primary/50 transition-colors">
                        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        <ShieldCheck className="w-10 h-10 text-primary mx-auto mb-4 opacity-50 group-hover:opacity-100 transition-opacity" />
                        <h4 className="text-sm font-black text-foreground mb-1 uppercase tracking-wider">Securely Managed</h4>
                        <p className="text-xs text-secondary-foreground font-medium opacity-70">
                            by JanSathi AI Security Core
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
                                        <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">Mobile Number (IVR/SMS)</label>
                                        <input type="tel" value={editForm.phone} onChange={(e) => setEditForm(prev => ({ ...prev, phone: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-primary" required />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-1">
                                            <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">Occupation</label>
                                            <select value={editForm.occupation} onChange={(e) => setEditForm(prev => ({ ...prev, occupation: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-primary appearance-none">
                                                <option value="Farmer">Farmer</option>
                                                <option value="Artisan">Artisan</option>
                                                <option value="Daily Wage Worker">Daily Wage Worker</option>
                                                <option value="Student">Student</option>
                                                <option value="Other">Other</option>
                                            </select>
                                        </div>
                                        <div className="space-y-1">
                                            <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">Category</label>
                                            <select value={editForm.category} onChange={(e) => setEditForm(prev => ({ ...prev, category: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-primary appearance-none">
                                                <option value="General">General</option>
                                                <option value="OBC">OBC</option>
                                                <option value="SC">SC</option>
                                                <option value="ST">ST</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-1">
                                            <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">Annual Income (₹)</label>
                                            <input type="number" value={editForm.annual_income} onChange={(e) => setEditForm(prev => ({ ...prev, annual_income: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-primary" />
                                        </div>
                                        <div className="space-y-1">
                                            <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">Land Acres (optional)</label>
                                            <input type="number" step="0.1" value={editForm.land_holding_acres} onChange={(e) => setEditForm(prev => ({ ...prev, land_holding_acres: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-primary" />
                                        </div>
                                    </div>
                                    <div className="space-y-1">
                                        <label className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-60">Preferred Language</label>
                                        <select value={editForm.preferred_language} onChange={(e) => setEditForm(prev => ({ ...prev, preferred_language: e.target.value }))} className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 text-foreground font-bold outline-none focus:border-primary appearance-none">
                                            <option value="hi">Hindi</option>
                                            <option value="en">English</option>
                                            <option value="ta">Tamil</option>
                                            <option value="kn">Kannada</option>
                                        </select>
                                    </div>
                                    <button type="submit" disabled={isSaving} className="w-full py-4 mt-4 bg-primary text-white rounded-xl text-xs font-bold uppercase tracking-widest shadow-sm flex items-center justify-center disabled:opacity-50">
                                        {isSaving ? 'Saving...' : 'Save Changes'}
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
