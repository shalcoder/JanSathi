'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    PlusCircle,
    LayoutDashboard,
    FileText,
    User,
    Settings,
    CheckCircle,
    Users,
    HelpCircle,
    Shield,
    Sparkles,
    ChevronRight,
    Home,
    LogOut,
} from 'lucide-react';
import Link from 'next/link';
import { useUser, UserButton, SignedIn, SignedOut, SignInButton, SignOutButton } from '@clerk/nextjs';

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

    useEffect(() => {
        const loadSessions = () => {
            try {
                const stored = localStorage.getItem(SESSIONS_KEY);
                if (stored) {
                    const parsed = JSON.parse(stored);
                    const sorted = (Object.values(parsed) as ChatSession[]).sort((a, b) =>
                        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
                    );
                    setSessions(sorted);
                }
            } catch (e) {
                console.error("Failed to load sessions", e);
            }
        };

        loadSessions();
        const handleUpdate = () => loadSessions();
        window.addEventListener('chat-storage-update', handleUpdate);
        return () => window.removeEventListener('chat-storage-update', handleUpdate);
    }, []);

    const navGroups = [
        {
            title: "General",
            items: [
                { id: 'overview', label: 'Overview', icon: LayoutDashboard, color: 'text-indigo-500' },
                { id: 'assistant', label: 'AI Assistant', icon: Sparkles, color: 'text-primary' },
            ]
        },
        {
            title: "Services",
            items: [
                { id: 'schemes', label: 'Schemes', icon: Shield, color: 'text-emerald-500' },
                { id: 'applications', label: 'Applications', icon: CheckCircle, color: 'text-amber-500' },
                { id: 'documents', label: 'Documents', icon: FileText, color: 'text-blue-500' },
            ]
        },
        {
            title: "Community",
            items: [
                { id: 'community', label: 'Local Forum', icon: Users, color: 'text-purple-500' },
            ]
        },
        {
            title: "Account",
            items: [
                { id: 'profile', label: 'Profile', icon: User, color: 'text-slate-500' },
                { id: 'settings', label: 'Settings', icon: Settings, color: 'text-slate-500' },
                { id: 'help', label: 'Help & Support', icon: HelpCircle, color: 'text-rose-500' },
            ]
        }
    ];

    return (
        <div className="h-full w-full flex flex-col justify-between py-6 px-4 bg-background lg:bg-transparent border-r border-border/60 relative z-20 transition-all duration-500">

            <div className="space-y-6 overflow-y-auto scrollbar-none pb-8 h-full">
                {/* Brand Logo */}
                <div className="px-2 flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center shadow-md shadow-primary/20">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="font-bold text-xl tracking-tight text-foreground leading-none">JanSathi</h1>
                        <p className="text-[10px] text-secondary-foreground font-bold uppercase tracking-wider opacity-50 mt-1">Bharat AI Helper</p>
                    </div>
                </div>

                {/* New Chat Button */}
                <button
                    onClick={onNewChat}
                    className="w-full flex items-center justify-center gap-2 py-3 bg-primary text-white rounded-xl font-bold text-xs uppercase tracking-widest transition-all hover:bg-primary/90 active:scale-95 shadow-md shadow-primary/20 hover:shadow-lg"
                >
                    <PlusCircle className="w-4 h-4" />
                    <span>New Chat</span>
                </button>

                {/* Main Navigation */}
                <nav className="space-y-6">
                    {navGroups.map((group, groupIndex) => (
                        <div key={groupIndex}>
                            <p className="px-4 text-[10px] font-bold text-secondary-foreground uppercase tracking-wider mb-2 opacity-40">{group.title}</p>
                            <div className="space-y-1">
                                {group.items.map((item) => (
                                    <button
                                        key={item.id}
                                        onClick={() => onPageChange(item.id)}
                                        className={`
                                            w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all group relative font-medium
                                            ${activePage === item.id
                                                ? 'bg-primary/10 text-primary border border-primary/20 shadow-sm'
                                                : 'text-secondary-foreground hover:bg-secondary/40 hover:text-foreground border border-transparent'}
                                        `}
                                    >
                                        <item.icon className={`w-4 h-4 ${activePage === item.id ? item.color : 'opacity-50 group-hover:opacity-100 group-hover:text-foreground transition-opacity'}`} />
                                        <span className="text-sm tracking-tight">{item.label}</span>
                                        {activePage === item.id && (
                                            <motion.div
                                                layoutId="active-pill"
                                                className="ml-auto w-1.5 h-1.5 rounded-full bg-primary"
                                            />
                                        )}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ))}

                    <div className="pt-2">
                        <Link
                            href="/"
                            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl transition-colors text-secondary-foreground hover:bg-secondary/40 hover:text-foreground opacity-70 hover:opacity-100"
                        >
                            <Home className="w-4 h-4" />
                            <span className="text-sm font-medium tracking-tight">Go to Home</span>
                        </Link>
                    </div>
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

            {/* Profile Footer - Compact */}
            <div className="pt-4 border-t border-border/50 mt-auto">
                <SignedIn>
                    <div className="space-y-2">
                        <div className="p-3 rounded-lg bg-secondary/20 border border-border/50 flex items-center gap-3 group cursor-pointer hover:bg-secondary/40 transition-colors">
                            <div className="shrink-0">
                                <UserButton
                                    afterSignOutUrl="/"
                                    appearance={{
                                        elements: {
                                            avatarBox: "w-8 h-8 border border-slate-200 dark:border-slate-700"
                                        }
                                    }}
                                />
                            </div>
                            <div className="flex-1 min-w-0">
                                <UserProfileName />
                            </div>
                        </div>

                        <SignOutButton>
                            <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all text-secondary-foreground hover:bg-red-500/10 hover:text-red-500 font-bold group border border-transparent hover:border-red-500/20 text-xs">
                                <LogOut className="w-4 h-4 opacity-40 group-hover:opacity-100 group-hover:text-red-500 transition-colors" />
                                <span>Sign Out</span>
                            </button>
                        </SignOutButton>
                    </div>
                </SignedIn>

                <SignedOut>
                    <SignInButton mode="modal">
                        <button className="w-full flex items-center justify-center gap-2 py-2 bg-primary text-white rounded-lg font-bold text-xs uppercase tracking-widest transition-opacity hover:opacity-90 shadow-sm">
                            <User className="w-3 h-3" />
                            <span>Sign In</span>
                        </button>
                    </SignInButton>
                </SignedOut>

                <div className="text-center mt-4 opacity-20 hover:opacity-100 transition-opacity">
                    <p className="text-[9px] font-bold text-secondary-foreground uppercase tracking-widest">
                        v2.5.0
                    </p>
                </div>
            </div>
        </div>
    );
}

function UserProfileName() {
    const { user } = useUser();
    return (
        <>
            <p className="text-sm font-bold text-foreground truncate tracking-tight">
                {user?.fullName || user?.username || "JanSathi Citizen"}
            </p>
            <p className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest flex items-center gap-2 mt-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                Verified
            </p>
        </>
    );
}
