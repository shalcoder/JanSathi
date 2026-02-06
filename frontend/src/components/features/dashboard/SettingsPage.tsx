'use client';

import React, { useState } from 'react';
import { Settings, Globe, Moon, Volume2, Shield, Bell, Trash2, Save } from 'lucide-react';

const SettingsPage = () => {
    const [voiceEnabled, setVoiceEnabled] = useState(true);
    const [notifications, setNotifications] = useState(true);
    const [autoTranslate, setAutoTranslate] = useState(true);

    return (
        <div className="h-full max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h2 className="text-3xl font-black text-white mb-8">App Settings</h2>

            <div className="space-y-6">
                {/* Interface Settings */}
                <div className="glass-panel p-8 rounded-[40px] border border-white/10">
                    <h3 className="text-lg font-bold text-slate-200 mb-6 flex items-center gap-2">
                        <Globe className="w-5 h-5 text-blue-400" />
                        Interface & Language
                    </h3>

                    <div className="space-y-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-semibold text-slate-300">Default Query Language</p>
                                <p className="text-xs text-slate-500">Preferred language for AI responses.</p>
                            </div>
                            <select className="bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50">
                                <option value="hi">Hindi (हिन्दी)</option>
                                <option value="en">English</option>
                                <option value="kn">Kannada (ಕನ್ನಡ)</option>
                                <option value="ta">Tamil (தமிழ்)</option>
                            </select>
                        </div>

                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-semibold text-slate-300">Auto-translate Voice</p>
                                <p className="text-xs text-slate-500">Automatically translate speech to preferred language.</p>
                            </div>
                            <button
                                onClick={() => setAutoTranslate(!autoTranslate)}
                                className={`w-12 h-6 rounded-full transition-all relative ${autoTranslate ? 'bg-blue-600' : 'bg-slate-700'}`}
                            >
                                <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${autoTranslate ? 'left-7' : 'left-1'}`}></div>
                            </button>
                        </div>
                    </div>
                </div>

                {/* AI & Accessibility */}
                <div className="glass-panel p-8 rounded-[40px] border border-white/10">
                    <h3 className="text-lg font-bold text-slate-200 mb-6 flex items-center gap-2">
                        <Volume2 className="w-5 h-5 text-purple-400" />
                        AI & Accessibility
                    </h3>

                    <div className="space-y-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-semibold text-slate-300">Voice Synthesis (TTS)</p>
                                <p className="text-xs text-slate-500">Read AI responses aloud automatically.</p>
                            </div>
                            <button
                                onClick={() => setVoiceEnabled(!voiceEnabled)}
                                className={`w-12 h-6 rounded-full transition-all relative ${voiceEnabled ? 'bg-blue-600' : 'bg-slate-700'}`}
                            >
                                <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${voiceEnabled ? 'left-7' : 'left-1'}`}></div>
                            </button>
                        </div>

                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-semibold text-slate-300">Push Notifications</p>
                                <p className="text-xs text-slate-500">Alerts for new government schemes.</p>
                            </div>
                            <button
                                onClick={() => setNotifications(!notifications)}
                                className={`w-12 h-6 rounded-full transition-all relative ${notifications ? 'bg-blue-600' : 'bg-slate-700'}`}
                            >
                                <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${notifications ? 'left-7' : 'left-1'}`}></div>
                            </button>
                        </div>
                    </div>
                </div>

                {/* Data & Privacy */}
                <div className="glass-panel p-8 rounded-[40px] border border-white/10 border-red-500/10">
                    <h3 className="text-lg font-bold text-slate-200 mb-6 flex items-center gap-2">
                        <Shield className="w-5 h-5 text-red-400" />
                        Data & Privacy
                    </h3>

                    <div className="space-y-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-semibold text-slate-300">Clear Chat History</p>
                                <p className="text-xs text-slate-500">Permanently delete all conversation records.</p>
                            </div>
                            <button
                                onClick={() => {
                                    if (confirm('Are you sure you want to clear all history?')) {
                                        sessionStorage.removeItem('jansathi_chat');
                                        window.location.reload();
                                    }
                                }}
                                className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20 rounded-xl text-xs font-bold transition-all"
                            >
                                <Trash2 className="w-4 h-4 mr-2 inline" />
                                Clear Data
                            </button>
                        </div>
                    </div>
                </div>

                <div className="flex justify-end pt-4">
                    <button className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-[2rem] font-bold shadow-xl shadow-blue-500/20 flex items-center gap-2 transition-all active:scale-95">
                        <Save className="w-5 h-5" />
                        Save All Changes
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;
