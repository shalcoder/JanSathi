'use client';

import React, { useState, useEffect } from 'react';
import {
    LayoutDashboard,
    FileText,
    User,
    Settings,
    PlusCircle,
    LogOut,
    MessageCircle,
    ChevronRight,
    Home
} from 'lucide-react';
import Link from 'next/link';

type SidebarProps = {
    activePage: string;
    onPageChange: (page: string) => void;
    onNewChat?: () => void;
};

type ChatSession = {
    id: string;
    title: string;
    timestamp: string;
};

export default function Sidebar({ activePage, onPageChange, onNewChat }: SidebarProps) {
    const [sessions, setSessions] = useState<ChatSession[]>([]);

    const loadSessions = () => {
        try {
            const stored = localStorage.getItem('jansathi_chat_sessions');
            if (stored) {
                const parsed = JSON.parse(stored);
                const sorted = Object.values(parsed).sort((a: any, b: any) =>
                    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
                ) as ChatSession[];
                setSessions(sorted);
            }
        } catch (e) {
            console.error("Failed to load sessions", e);
        }
    };

    useEffect(() => {
        loadSessions();
        const handleUpdate = () => loadSessions();
        window.addEventListener('chat-storage-update', handleUpdate);
        return () => window.removeEventListener('chat-storage-update', handleUpdate);
    }, []);

    const navItems = [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'documents', label: 'Documents', icon: FileText },

        { id: 'profile', label: 'Profile', icon: User },
        { id: 'settings', label: 'Settings', icon: Settings },
    ];

    return (
        <div className="h-full w-full flex flex-col justify-between py-6 px-4 bg-slate-900 lg:bg-transparent backdrop-blur-2xl lg:backdrop-blur-none border-r border-white/5 relative z-20 transition-all duration-500">

            <div
                className="space-y-8 overflow-y-auto scrollbar-none [&::-webkit-scrollbar]:hidden"
                style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
            >
                {/* Brand */}
                <div className="px-2 flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-xl shadow-blue-600/30">
                        <span className="font-black text-sm text-white">JS</span>
                    </div>
                    <div>
                        <h1 className="font-black text-2xl tracking-tighter text-white transition-colors leading-none">JanSathi</h1>
                        <p className="text-[10px] text-slate-400 font-black uppercase tracking-[0.2em] mt-1">Enterprise AI</p>
                    </div>
                </div>

                {/* New Chat Button */}
                <button
                    onClick={onNewChat}
                    suppressHydrationWarning
                    className="w-full flex items-center justify-center gap-3 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-black text-sm transition-all shadow-xl shadow-blue-600/30 active:scale-95 group relative overflow-hidden"
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-[shimmer_2s_infinite]"></div>
                    <PlusCircle className="w-5 h-5 group-hover:rotate-90 transition-transform duration-500 relative z-10" />
                    <span className="relative z-10">New Consultation</span>
                </button>

                {/* Main Nav */}
                <nav className="space-y-1">
                    <p className="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Platform</p>
                    {navItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => onPageChange(item.id)}
                            suppressHydrationWarning
                            className={`
                                w-full flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-300 group
                                ${activePage === item.id
                                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20 border border-blue-500'
                                    : 'text-slate-400 hover:bg-white/5 hover:text-white border border-transparent'}
                            `}
                        >
                            <item.icon className={`w-5 h-5 ${activePage === item.id ? 'text-white' : 'group-hover:text-white transition-colors'}`} />
                            <span className="font-black text-sm tracking-tight">{item.label}</span>
                            {activePage === item.id && <ChevronRight className="w-4 h-4 ml-auto opacity-70" />}
                        </button>
                    ))}

                    <Link
                        href="/"
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-slate-400 hover:bg-white/5 hover:text-white"
                    >
                        <Home className="w-5 h-5" />
                        <span className="font-bold text-sm">Landing Page</span>
                    </Link>
                </nav>

                {/* Recent Consultations (Poornachandran's Addition) */}
                <div className="space-y-1">
                    <p className="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Recent Conversations</p>
                    <div className="space-y-1 max-h-48 overflow-y-auto scrollbar-none px-1">
                        {sessions.length === 0 ? (
                            <div className="px-4 py-3 rounded-xl bg-white/5 border border-dashed border-white/10 text-center">
                                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">No history yet</p>
                            </div>
                        ) : (
                            sessions.map((session) => (
                                <button
                                    key={session.id}
                                    onClick={() => {
                                        onPageChange('dashboard');
                                        window.dispatchEvent(new CustomEvent('load-chat-session', { detail: session.id }));
                                    }}
                                    suppressHydrationWarning
                                    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:bg-white/5 hover:text-white transition-all text-left group"
                                >
                                    <MessageCircle className="w-4 h-4 flex-shrink-0 text-slate-400 group-hover:text-blue-400 transition-colors" />
                                    <span className="truncate text-xs font-bold">{session.title}</span>
                                </button>
                            ))
                        )}
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="pt-6 border-t border-white/5">
                <button
                    suppressHydrationWarning
                    className="w-full flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-red-500 transition-all group font-black text-sm"
                >
                    <LogOut className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                    <span>Sign Out</span>
                </button>
            </div>
        </div>
    );
}
