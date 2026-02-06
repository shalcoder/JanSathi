import React from 'react';
import { MessageSquarePlus, LayoutDashboard, FileText, Settings, User } from 'lucide-react';

interface SidebarProps {
    activePage: string;
    onPageChange: (page: string) => void;
    onNewChat?: () => void;
}

const Sidebar = ({ activePage, onPageChange, onNewChat }: SidebarProps) => {
    const navItems = [
        { id: 'dashboard', icon: LayoutDashboard, label: "Dashboard" },
        { id: 'documents', icon: FileText, label: "Documents" },
        { id: 'profile', icon: User, label: "Profile" },
        { id: 'settings', icon: Settings, label: "Settings" },
    ];

    return (
        <div className="h-full w-full flex flex-col justify-between py-6 px-4 bg-slate-900/95 lg:bg-transparent backdrop-blur-2xl lg:backdrop-blur-none border-r border-white/10 relative z-20 transition-all duration-300">

            {/* Logo Area */}
            <div className="flex items-center gap-3 mb-10 pl-2">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
                    <span className="text-white font-bold text-xl">JS</span>
                </div>
                <div className="hidden lg:block">
                    <h1 className="font-bold text-lg text-slate-800 dark:text-white leading-tight">JanSathi</h1>
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Enterprise AI</p>
                </div>
            </div>

            {/* Navigation */}
            <div className="flex-1 flex flex-col gap-2">
                <button
                    onClick={() => {
                        onPageChange('dashboard');
                        if (onNewChat) onNewChat();
                    }}
                    className="flex items-center gap-3 px-4 py-3 rounded-xl bg-blue-600 text-white shadow-lg shadow-blue-500/20 hover:bg-blue-700 hover:shadow-blue-500/40 transition-all group mb-6"
                >
                    <MessageSquarePlus className="w-5 h-5" />
                    <span className="hidden lg:block font-medium">New Chat</span>
                </button>

                <nav className="space-y-1">
                    {navItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => onPageChange(item.id)}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === item.id
                                ? 'bg-blue-600/10 text-blue-600 dark:text-blue-400 border border-blue-500/20 shadow-sm'
                                : 'text-slate-500 dark:text-slate-400 hover:bg-white/5 hover:text-slate-900 dark:hover:text-slate-200'
                                }`}
                        >
                            <item.icon className={`w-5 h-5 ${activePage === item.id ? 'text-blue-600 dark:text-blue-400' : ''}`} />
                            <span className="hidden lg:block font-medium text-sm">{item.label}</span>
                        </button>
                    ))}
                </nav>
            </div>

            {/* User Profile (Mini) */}
            <div className="mt-auto pt-6 border-t border-white/10">
                <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500 flex items-center justify-center text-xs text-white font-bold shadow-sm">
                        DU
                    </div>
                    <div className="hidden lg:block overflow-hidden">
                        <p className="text-sm font-semibold text-slate-700 dark:text-slate-200 truncate">Demo User</p>
                        <p className="text-[10px] text-slate-400 truncate">demo@jansathi.ai</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
