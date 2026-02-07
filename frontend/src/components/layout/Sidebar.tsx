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
    Home,
    ShoppingBag
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
        { id: 'market', label: 'Market Rates', icon: ShoppingBag },
        { id: 'profile', label: 'Profile', icon: User },
        { id: 'settings', label: 'Settings', icon: Settings },
    ];

    return (
        <div className="h-full w-full flex flex-col justify-between py-6 px-4 bg-slate-900/95 lg:bg-transparent backdrop-blur-2xl lg:backdrop-blur-none border-r border-white/10 relative z-20">

            <div className="space-y-8 overflow-y-auto scrollbar-none">
                {/* Brand */}
                <div className="px-2 flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
                        <span className="font-black text-xs">JS</span>
                    </div>
                    <div>
                        <h1 className="font-black text-xl tracking-tighter text-white">JanSathi</h1>
                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Enterprise AI</p>
                    </div>
                </div>

                {/* New Chat Button */}
                <button
                    onClick={onNewChat}
                    className="w-full flex items-center justify-center gap-2 py-3.5 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-bold transition-all shadow-lg shadow-blue-600/20 active:scale-95 group"
                >
                    <PlusCircle className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
                    <span>New Consultation</span>
                </button>

                {/* Main Nav */}
                <nav className="space-y-1">
                    <p className="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Platform</p>
                    {navItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => onPageChange(item.id)}
                            className={`
                                w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group
                                ${activePage === item.id
                                    ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                                    : 'text-slate-400 hover:bg-white/5 hover:text-white border border-transparent'}
                            `}
                        >
                            <item.icon className={`w-5 h-5 ${activePage === item.id ? 'text-blue-400' : 'group-hover:text-white'}`} />
                            <span className="font-bold text-sm">{item.label}</span>
                            {activePage === item.id && <ChevronRight className="w-4 h-4 ml-auto opacity-50" />}
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
                                        // Logic to switch to dashboard and load this session
                                        onPageChange('dashboard');
                                        window.dispatchEvent(new CustomEvent('load-chat-session', { detail: session.id }));
                                    }}
                                    className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-slate-400 hover:bg-white/5 hover:text-white transition-all text-left group"
                                >
                                    <MessageCircle className="w-4 h-4 flex-shrink-0 opacity-40 group-hover:opacity-100" />
                                    <span className="truncate text-xs font-medium">{session.title}</span>
                                </button>
                            ))
                        )}
                    </div>
                </div>
            </div>

            {/* WhatsApp Support (Phase 3 Integration) */}
            <div className="mb-4">
                <a
                    href="https://wa.me/911234567890?text=I%20need%20help%20with%20JanSathi"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full flex items-center gap-3 px-4 py-3 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-500 rounded-xl transition-all group"
                >
                    <div className="w-5 h-5 flex items-center justify-center bg-emerald-500 rounded-full">
                        <MessageCircle className="w-3 h-3 text-white" />
                    </div>
                    <span className="font-bold text-sm">WhatsApp Helper</span>
                    <span className="ml-auto text-[8px] font-black uppercase tracking-widest bg-emerald-500 text-white px-1.5 py-0.5 rounded-full">Beta</span>
                </a>
            </div>

            {/* Footer */}
            <div className="pt-6 border-t border-white/5">
                <button
                    onClick={() => {
                        localStorage.removeItem('jansathi_user');
                        localStorage.removeItem('jansathi_chat_sessions');
                        window.location.href = '/sign-in';
                    }}
                    className="w-full flex items-center gap-3 px-4 py-3 text-slate-500 hover:text-red-400 hover:bg-red-500/5 rounded-xl transition-all group"
                >
                    <LogOut className="w-5 h-5" />
                    <span className="font-bold text-sm">Sign Out</span>
                </button>
            </div>
        </div>
    );
}
