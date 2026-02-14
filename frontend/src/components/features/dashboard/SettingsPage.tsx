'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Globe, Volume2, Shield, Trash2, Save, Languages, Bell, Database } from 'lucide-react';
import { useSettings } from '@/hooks/useSettings';

const SettingsPage = () => {
    const { settings, updateSettings } = useSettings();

    const handleSave = () => {
        alert("Settings saved successfully!");
    };

    return (
<<<<<<< HEAD
        <div className="min-h-full max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h2 className="text-3xl font-black text-white mb-8">App Settings</h2>
=======
        <div className="h-full max-w-5xl mx-auto pb-20 relative px-4 sm:px-0">
>>>>>>> poornachandran

            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-10"
            >
                <div className="flex items-center gap-2 mb-2">
                    <span className="text-[10px] font-bold text-secondary-foreground uppercase tracking-widest opacity-40">System Settings</span>
                </div>
                <h2 className="text-4xl font-bold text-foreground tracking-tight">
                    Settings
                </h2>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Language Settings */}
                <div className="p-8 rounded-2xl bg-card border border-border/50 shadow-sm">
                    <h3 className="text-lg font-bold text-foreground mb-8 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                            <Languages className="w-5 h-5 text-primary" />
                        </div>
                        Language
                    </h3>

                    <div className="space-y-8">
                        <div className="space-y-2">
                            <label className="text-[11px] font-bold text-secondary-foreground uppercase tracking-wider ml-1 opacity-50">Select Main Language</label>
                            <select
                                value={settings.language}
                                onChange={(e) => updateSettings({ language: e.target.value })}
                                className="w-full h-14 bg-secondary/30 border border-border/50 rounded-xl px-5 text-foreground font-bold outline-none focus:border-primary appearance-none cursor-pointer"
                            >
                                <option value="hi">Hindi (हिन्दी)</option>
                                <option value="en">English</option>
                                <option value="kn">Kannada (ಕನ್ನಡ)</option>
                                <option value="ta">Tamil (தமிழ்)</option>
                            </select>
                        </div>

                        <div className="flex items-center justify-between p-5 rounded-xl bg-secondary/20 border border-border/50">
                            <div>
                                <p className="text-sm font-bold text-foreground">Auto-translation</p>
                                <p className="text-[10px] text-secondary-foreground font-bold uppercase tracking-widest opacity-40">Translate as you type</p>
                            </div>
                            <button
                                onClick={() => updateSettings({ autoTranslate: !settings.autoTranslate })}
                                className={`w-14 h-8 rounded-full transition-all relative p-1 ${settings.autoTranslate ? 'bg-primary' : 'bg-slate-300 dark:bg-slate-700'}`}
                            >
                                <motion.div
                                    animate={{ x: settings.autoTranslate ? 24 : 0 }}
                                    className="w-6 h-6 bg-white rounded-full shadow-sm"
                                />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Voice & Alerts */}
                <div className="p-8 rounded-2xl bg-card border border-border/50 shadow-sm">
                    <h3 className="text-lg font-bold text-foreground mb-8 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center">
                            <Volume2 className="w-5 h-5 text-blue-600" />
                        </div>
                        Voice & Alerts
                    </h3>

                    <div className="space-y-6">
                        <div className="flex items-center justify-between p-5 rounded-xl bg-secondary/20 border border-border/50">
                            <div>
                                <p className="text-sm font-bold text-foreground">Voice Responses</p>
                                <p className="text-[10px] text-secondary-foreground font-bold uppercase tracking-widest opacity-40">JanSathi will speak to you</p>
                            </div>
                            <button
                                onClick={() => updateSettings({ voiceEnabled: !settings.voiceEnabled })}
                                className={`w-14 h-8 rounded-full transition-all relative p-1 ${settings.voiceEnabled ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-700'}`}
                            >
                                <motion.div
                                    animate={{ x: settings.voiceEnabled ? 24 : 0 }}
                                    className="w-6 h-6 bg-white rounded-full shadow-sm"
                                />
                            </button>
                        </div>

                        <div className="flex items-center justify-between p-5 rounded-xl bg-secondary/20 border border-border/50">
                            <div>
                                <p className="text-sm font-bold text-foreground">Push Notifications</p>
                                <p className="text-[10px] text-secondary-foreground font-bold uppercase tracking-widest opacity-40">Get updates on schemes</p>
                            </div>
                            <button
                                onClick={async () => {
                                    if (!settings.notifications) {
                                        // Request Permission
                                        if (!("Notification" in window)) {
                                            alert("This browser does not support notifications.");
                                            return;
                                        }

                                        if (Notification.permission === "granted") {
                                            updateSettings({ notifications: true });
                                            new Notification("JanSathi Notifications Enabled", {
                                                body: "You will now receive updates about government schemes.",
                                                icon: "/icons/icon-192.png" // Assuming this exists
                                            });
                                        } else if (Notification.permission !== "denied") {
                                            const permission = await Notification.requestPermission();
                                            if (permission === "granted") {
                                                updateSettings({ notifications: true });
                                                new Notification("JanSathi Notifications Enabled", {
                                                    body: "You will now receive updates about government schemes.",
                                                    icon: "/icons/icon-192.png"
                                                });
                                            }
                                        } else {
                                            alert("Notifications are disabled in browser settings. Please enable them manually.");
                                        }
                                    } else {
                                        updateSettings({ notifications: false });
                                    }
                                }}
                                className={`w-14 h-8 rounded-full transition-all relative p-1 ${settings.notifications ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-700'}`}
                            >
                                <motion.div
                                    animate={{ x: settings.notifications ? 24 : 0 }}
                                    className="w-6 h-6 bg-white rounded-full shadow-sm"
                                />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Privacy & Security */}
                <div className="md:col-span-2 p-8 rounded-2xl bg-card border border-red-100 dark:border-red-900/20 shadow-sm">
                    <h3 className="text-lg font-bold text-foreground mb-8 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-red-50 dark:bg-red-900/20 flex items-center justify-center">
                            <Shield className="w-5 h-5 text-red-600" />
                        </div>
                        Privacy & Security
                    </h3>

                    <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                        <div className="flex-1 text-center md:text-left">
                            <p className="text-base font-bold text-foreground mb-1">Delete All Chat History</p>
                            <p className="text-xs font-medium text-secondary-foreground opacity-60 leading-relaxed">
                                This will permanently remove all your messages and document history from this device.
                            </p>
                        </div>

                        <button
                            onClick={() => {
                                if (confirm('Delete all history? This cannot be undone.')) {
                                    localStorage.removeItem('jansathi_chat_sessions');
                                    sessionStorage.removeItem('current_jansathi_session');
                                    window.location.reload();
                                }
                            }}
                            className="px-8 py-3 bg-red-50 hover:bg-red-600 text-red-600 hover:text-white border border-red-200/50 dark:border-red-900/40 rounded-xl text-xs font-bold uppercase tracking-widest transition-all flex items-center gap-2 whitespace-nowrap"
                        >
                            <Trash2 className="w-5 h-5" />
                            Clear History
                        </button>
                    </div>
                </div>
            </div>

            {/* Sticky Save Button - Improved Spacing */}
            <div className="mt-16 flex justify-center pb-8 border-t border-border/50 pt-12">
                <button
                    onClick={handleSave}
                    className="w-full sm:w-auto px-12 py-5 bg-foreground dark:bg-slate-100 text-white dark:text-slate-900 rounded-xl font-bold text-sm uppercase tracking-widest shadow-xl flex items-center justify-center gap-4 hover:opacity-90 transition-opacity"
                >
                    <Save className="w-5 h-5" />
                    Save All Changes
                </button>
            </div>

            <div className="mt-8 text-center">
                <p className="text-[10px] font-bold text-secondary-foreground uppercase tracking-widest opacity-30 px-6 py-2 rounded-full border border-border inline-block">
                    JanSathi v2.5.0 • BharatAI Core
                </p>
            </div>
        </div>
    );
};

export default SettingsPage;
