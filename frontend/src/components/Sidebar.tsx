'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Home, MessageSquare, Menu, PlusCircle, MessageCircle } from 'lucide-react';
import { useState, useEffect } from 'react';

type ChatSession = {
    id: string;
    title: string;
    lastMessage: string;
    timestamp: string;
};

export default function Sidebar() {
    const pathname = usePathname();
    const router = useRouter();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [sessions, setSessions] = useState<ChatSession[]>([]);

    const isActive = (path: string) => pathname === path;

    // Function to load sessions from localStorage
    const loadSessions = () => {
        try {
            const stored = localStorage.getItem('jansathi_chat_sessions');
            if (stored) {
                const parsed = JSON.parse(stored);
                // Sort by newest first (descending timestamp)
                const sorted = Object.values(parsed).sort((a: any, b: any) =>
                    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
                ) as ChatSession[];
                setSessions(sorted);
            } else {
                setSessions([]);
            }
        } catch (e) {
            console.error("Failed to load sessions", e);
        }
    };

    useEffect(() => {
        loadSessions();

        // Listen for custom event 'chat-storage-update' to refresh list
        const handleStorageUpdate = () => loadSessions();
        window.addEventListener('chat-storage-update', handleStorageUpdate);

        return () => {
            window.removeEventListener('chat-storage-update', handleStorageUpdate);
        };
    }, []);

    const handleNewChat = () => {
        router.push('/chat');
        setIsMobileMenuOpen(false);
    };

    return (
        <>
            {/* Mobile Menu Button */}
            <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="md:hidden fixed top-4 left-4 z-50 p-2 bg-white dark:bg-slate-900 rounded-lg shadow-md border border-slate-200 dark:border-slate-800"
            >
                <Menu className="w-6 h-6 text-slate-700 dark:text-slate-200" />
            </button>

            {/* Sidebar Container */}
            <aside
                className={`
          fixed inset-y-0 left-0 z-40 w-64 bg-white dark:bg-slate-950 border-r border-slate-200 dark:border-slate-800 transform transition-transform duration-300 ease-in-out
          ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0 md:static md:h-screen
        `}
            >
                <div className="h-full flex flex-col">
                    {/* Logo Area */}
                    <div className="p-6 border-b border-slate-200 dark:border-slate-800">
                        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-teal-500">
                            JanSathi
                        </h1>
                    </div>

                    {/* Navigation Links */}
                    <nav className="p-4 space-y-2">
                        <Link
                            href="/"
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${isActive('/')
                                    ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400 font-medium'
                                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                                }`}
                        >
                            <Home className="w-5 h-5" />
                            <span>Home</span>
                        </Link>

                        <button
                            onClick={handleNewChat}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors text-left ${isActive('/chat') && !window.location.search
                                    ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400 font-medium'
                                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                                }`}
                        >
                            <PlusCircle className="w-5 h-5" />
                            <span>New Chat</span>
                        </button>
                    </nav>

                    {/* History List */}
                    <div className="flex-1 overflow-y-auto px-4 pb-4">
                        {sessions.length > 0 && (
                            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 px-2 mt-2">
                                Recent Chats
                            </div>
                        )}

                        <div className="space-y-1">
                            {sessions.length === 0 ? (
                                <p className="text-xs text-slate-400 px-6 italic mt-4 text-center">No history yet.</p>
                            ) : (
                                sessions.map((session) => (
                                    <Link
                                        key={session.id}
                                        href={`/chat?id=${session.id}`}
                                        className={`block p-2 rounded-lg text-sm truncate transition-colors ${isActive('/chat') && window.location.search.includes(session.id)
                                                ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300'
                                                : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                                            }`}
                                    >
                                        <div className="flex items-center gap-2 max-w-full">
                                            <MessageCircle className="w-3 h-3 text-slate-400 flex-shrink-0" />
                                            <span className="truncate">{session.title}</span>
                                        </div>
                                    </Link>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Footer Area */}
                    <div className="p-4 border-t border-slate-200 dark:border-slate-800">
                        <div className="text-xs text-slate-400 text-center">
                            © 2026 JanSathi
                        </div>
                    </div>
                </div>
            </aside>

            {/* Overlay for Mobile */}
            {isMobileMenuOpen && (
                <div
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="fixed inset-0 z-30 bg-black/20 backdrop-blur-sm md:hidden"
                />
            )}
        </>
    );
}
