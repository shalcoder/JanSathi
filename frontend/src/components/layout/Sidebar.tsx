'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    LayoutDashboard,
    FileText,
    User,
    Settings,
    PlusCircle,
    Sparkles,
    ChevronRight,
    Home,
    LogOut,
    Shield
} from 'lucide-react';
import Link from 'next/link';

interface ChatSession {
    id: string;
    title: string;
    timestamp: string;
}

interface SidebarProps {
    activePage: string;
    onPageChange: (page: string) => void;
    onNewChat?: () => void;
}

const SESSIONS_KEY = 'jansathi_chat_sessions';

export default function Sidebar({ activePage, onPageChange, onNewChat }: SidebarProps) {
    const [sessions, setSessions] = useState<ChatSession[]>([]);

    const loadSessions = () => {
        try {
            const stored = localStorage.getItem(SESSIONS_KEY);
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
        { id: 'dashboard', label: 'Assistant', icon: LayoutDashboard, color: 'text-primary' },
        { id: 'documents', label: 'Documents', icon: FileText, color: 'text-blue-600' },
        { id: 'profile', label: 'Profile', icon: User, color: 'text-emerald-500' },
        { id: 'settings', label: 'Settings', icon: Settings, color: 'text-slate-500' },
    ];

    return (
        <div className="h-full w-full flex flex-col justify-between py-10 px-6 bg-background lg:bg-transparent border-r border-border/30 relative z-20 transition-all duration-500">

            <div className="space-y-10 overflow-y-auto scrollbar-none pb-8">
                {/* Brand Logo */}
                <div className="px-2 flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center shadow-sm">
                        <Sparkles className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="font-bold text-2xl tracking-tight text-foreground leading-none">JanSathi</h1>
                        <p className="text-[10px] text-secondary-foreground font-bold uppercase tracking-wider opacity-40 mt-1">Bharat AI Helper</p>
                    </div>
                </div>

                {/* New Chat Button */}
                <button
                    onClick={onNewChat}
                    className="w-full flex items-center justify-center gap-3 py-5 bg-primary text-white rounded-xl font-bold text-xs uppercase tracking-widest transition-opacity hover:opacity-90 active:scale-95 shadow-sm"
                >
                    <PlusCircle className="w-5 h-5" />
                    <span>New Chat</span>
                </button>

                {/* Main Navigation */}
                <nav className="space-y-2">
                    <p className="px-4 text-[10px] font-bold text-secondary-foreground uppercase tracking-wider mb-4 opacity-30">Menu</p>
                    {navItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => onPageChange(item.id)}
                            className={`
                                w-full flex items-center gap-4 px-4 py-4 rounded-xl transition-colors group relative
                                ${activePage === item.id
                                    ? 'bg-primary/10 text-primary border border-primary/20'
                                    : 'text-secondary-foreground hover:bg-secondary/50 hover:text-foreground border border-transparent'}
                            `}
                        >
                            <item.icon className={`w-5 h-5 ${activePage === item.id ? item.color : 'opacity-40'}`} />
                            <span className="text-[14px] font-bold tracking-tight">{item.label}</span>
                            {activePage === item.id && (
                                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary" />
                            )}
                        </button>
                    ))}

                    <Link
                        href="/"
                        className="w-full flex items-center gap-4 px-4 py-4 rounded-xl transition-colors text-secondary-foreground hover:bg-secondary/50 hover:text-foreground mt-6"
                    >
                        <Home className="w-5 h-5 opacity-40" />
                        <span className="text-[14px] font-bold tracking-tight">Go to Home</span>
                    </Link>
                </nav>

                {/* Recent Chats */}
                <div className="space-y-4 pt-6">
                    <div className="flex items-center justify-between px-4">
                        <p className="text-[10px] font-bold text-secondary-foreground uppercase tracking-wider opacity-30">Recent Chats</p>
                        <button className="text-[10px] font-bold text-primary hover:underline uppercase tracking-wider">Clear</button>
                    </div>
                    <div className="space-y-1 max-h-56 overflow-y-auto px-1 scrollbar-none">
                        {sessions.length === 0 ? (
                            <div className="px-4 py-8 rounded-xl bg-secondary/20 border border-border/50 text-center opacity-40">
                                <p className="text-[10px] text-secondary-foreground font-bold uppercase tracking-wider">No history yet</p>
                            </div>
                        ) : (
                            sessions.map((session) => (
                                <button
                                    key={session.id}
                                    onClick={() => {
                                        onPageChange('dashboard');
                                        window.dispatchEvent(new CustomEvent('load-chat-session', { detail: session.id }));
                                    }}
                                    className="w-full text-left px-4 py-3 rounded-lg hover:bg-secondary/50 transition-colors group flex items-center gap-3"
                                >
                                    <div className="w-1.5 h-1.5 rounded-full bg-border group-hover:bg-primary shrink-0" />
                                    <div className="min-w-0 flex-1">
                                        <p className="text-[13px] font-bold text-foreground truncate group-hover:text-primary transition-colors tracking-tight">{session.title}</p>
                                        <p className="text-[10px] text-secondary-foreground font-medium opacity-40 uppercase tracking-tighter mt-1">{new Date(session.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</p>
                                    </div>
                                </button>
                            ))
                        )}
                    </div>
                </div>
            </div>

<<<<<<< HEAD
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
=======
            {/* Profile Footer - Better Spacing */}
            <div className="pt-8 border-t border-border/50 mt-auto">
                <div
                    className="p-4 rounded-xl bg-secondary/20 border border-border/50 flex items-center gap-4 group cursor-pointer hover:bg-secondary/40 transition-colors"
                >
                    <div className="w-11 h-11 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center overflow-hidden shrink-0">
                        <span className="text-sm font-bold text-foreground/40 text-center">RK</span>
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-bold text-foreground truncate tracking-tight">Rajesh Kumar</p>
                        <p className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest flex items-center gap-2 mt-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            Verified
                        </p>
                    </div>
                </div>

                <p className="text-center text-[9px] font-bold text-secondary-foreground uppercase tracking-widest mt-6 opacity-20">
                    JanSathi v2.5.0
                </p>
>>>>>>> poornachandran
            </div>
        </div>
    );
}

// End of Sidebar Component
