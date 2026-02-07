'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, History as HistoryIcon, Languages, Camera, Image as ImageIcon, X, Trash2 } from 'lucide-react';
import VoiceInput from './VoiceInput';
import AudioPlayer from './AudioPlayer';
import { sendQuery, getHistory, analyzeImage } from '@/services/api';
import SchemeCard from './SchemeCard';
import { useSettings } from '@/hooks/useSettings';

// --- Typewriter Component ---
const Typewriter = ({ text, onComplete }: { text: string; onComplete?: () => void }) => {
    const [displayedText, setDisplayedText] = useState('');
    const index = useRef(0);
    const onCompleteRef = useRef(onComplete);

    // Keep the callback ref updated
    useEffect(() => {
        onCompleteRef.current = onComplete;
    }, [onComplete]);

    useEffect(() => {
        index.current = 0;
        setDisplayedText('');

        const intervalId = setInterval(() => {
            index.current += 2; // Speed up slightly
            if (index.current > text.length) index.current = text.length;

            setDisplayedText(text.slice(0, index.current));

            if (index.current >= text.length) {
                clearInterval(intervalId);
                if (onCompleteRef.current) onCompleteRef.current();
            }
        }, 10); // Faster Interval

        return () => clearInterval(intervalId);
    }, [text]); // Only re-run if TEXT changes, not onComplete

    return <div className="leading-relaxed whitespace-pre-wrap">{displayedText}</div>;
};

type Message = {
    id: string;
    role: 'user' | 'assistant';
    text: string;
    timestamp: Date;
    language?: string;
    userId?: string;
    audio?: string;
    context?: string[];
    isTyping?: boolean;
    structured_sources?: {
        title: string;
        text: string;
        link: string;
        benefit: string;
        logo: string;
    }[];
};

const LANGUAGES = [
    { code: 'hi', name: 'हिन्दी' },
    { code: 'en', name: 'English' },
    { code: 'kn', name: 'ಕನ್ನಡ' },
    { code: 'ta', name: 'தமிழ்' }
];

const SESSIONS_KEY = 'jansathi_chat_sessions';

export default function ChatInterface() {
    // Use a fallback user object instead of Clerk
    const user = { id: 'demo_user', firstName: 'JanSathi User' };

    // Global Settings
    const { settings, updateSettings } = useSettings();

    const [messages, setMessages] = useState<Message[]>([]);
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Local state for language is now synced with global settings
    const [language, setLanguage] = useState(settings.language);

    // Sync local language when settings change
    useEffect(() => {
        setLanguage(settings.language);
    }, [settings.language]);

    const [showHistory, setShowHistory] = useState(false);
    const scrollContainerRef = useRef<HTMLDivElement>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);

    const scrollToBottom = () => {
        if (scrollContainerRef.current) {
            const { scrollHeight, clientHeight } = scrollContainerRef.current;
            scrollContainerRef.current.scrollTo({
                top: scrollHeight - clientHeight,
                behavior: 'smooth'
            });
        }
    };

    // Initialize Sessions
    useEffect(() => {
        const handleLoadSession = (e: any) => {
            const sid = e.detail;
            loadSession(sid);
        };
        window.addEventListener('load-chat-session', handleLoadSession);

        // Initial load (check if we were in a session)
        const lastSession = sessionStorage.getItem('current_jansathi_session');
        if (lastSession) {
            loadSession(lastSession);
        } else {
            resetToWelcome();
        }

        return () => window.removeEventListener('load-chat-session', handleLoadSession);
    }, []);

    const resetToWelcome = () => {
        setCurrentSessionId(null);
        setMessages([{
            id: 'welcome',
            role: 'assistant',
            text: 'Namaste! I am JanSathi. Ask me anything about government schemes or services.',
            timestamp: new Date()
        }]);
    };

    const loadSession = (id: string) => {
        try {
            const stored = localStorage.getItem(SESSIONS_KEY);
            if (stored) {
                const sessions = JSON.parse(stored);
                if (sessions[id]) {
                    const restored = sessions[id].messages.map((m: any) => ({
                        ...m,
                        timestamp: new Date(m.timestamp),
                        isTyping: false // Don't animate old messages
                    }));
                    setMessages(restored);
                    setCurrentSessionId(id);
                    sessionStorage.setItem('current_jansathi_session', id);
                    return;
                }
            }
        } catch (e) {
            console.error("Failed to load session:", id, e);
        }
        resetToWelcome();
    };

    const saveSession = (msgs: Message[], id: string) => {
        try {
            const stored = localStorage.getItem(SESSIONS_KEY);
            let sessions = stored ? JSON.parse(stored) : {};

            // Clean messages for storage (remove typing state)
            const cleanMsgs = msgs.map(({ isTyping, ...rest }) => ({
                ...rest,
                timestamp: rest.timestamp.toISOString()
            }));

            const title = msgs.find(m => m.role === 'user')?.text.substring(0, 30) || 'New Conversation';

            sessions[id] = {
                id,
                title: title + (title.length >= 30 ? '...' : ''),
                messages: cleanMsgs,
                timestamp: new Date().toISOString()
            };

            localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
            window.dispatchEvent(new Event('chat-storage-update'));
        } catch (e) {
            console.error("Failed to save session:", e);
        }
    };

    useEffect(() => {
        if (currentSessionId && messages.length > 0) {
            saveSession(messages, currentSessionId);
        }

        if (messages.length > 1 || (messages.length === 1 && messages[0].id !== 'welcome')) {
            scrollToBottom();
        }
    }, [messages, currentSessionId]);

    const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setSelectedImage(file);
            setImagePreview(URL.createObjectURL(file));
        }
    };

    const clearImage = () => {
        setSelectedImage(null);
        setImagePreview(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const handleDeleteChat = () => {
        if (confirm("Are you sure you want to delete this conversation?")) {
            if (currentSessionId) {
                const stored = localStorage.getItem(SESSIONS_KEY);
                if (stored) {
                    const sessions = JSON.parse(stored);
                    delete sessions[currentSessionId];
                    localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
                    window.dispatchEvent(new Event('chat-storage-update'));
                }
            }
            sessionStorage.removeItem('current_jansathi_session');
            resetToWelcome();
        }
    };

    const handleSend = async (text: string = inputText) => {
        if ((!text.trim() && !selectedImage) || isLoading) return;

        let sid = currentSessionId;
        if (!sid) {
            sid = Date.now().toString();
            setCurrentSessionId(sid);
            sessionStorage.setItem('current_jansathi_session', sid);
        }

        setIsLoading(true);
        const newMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            text: text || (selectedImage ? 'Analyzed this document' : ''),
            timestamp: new Date(),
            language: language
        };

        const updatedMessages = [...messages.filter(m => m.id !== 'welcome'), newMessage];
        setMessages(updatedMessages);
        setInputText('');

        try {
            let data;
            if (selectedImage) {
                data = await analyzeImage(selectedImage, language);
                clearImage();

                const visionMsg: Message = {
                    id: Date.now().toString() + '_ai',
                    role: 'assistant',
                    text: data.analysis.text,
                    audio: data.analysis.audio,
                    timestamp: new Date(),
                    language: data.meta.language,
                    isTyping: true
                };
                setMessages(prev => [...prev, visionMsg]);
            } else {
                data = await sendQuery({
                    text_query: text,
                    language: language,
                    userId: user?.id
                });

                const aiMessage: Message = {
                    id: Date.now().toString() + '_ai',
                    role: 'assistant',
                    text: data.answer.text,
                    audio: data.answer.audio,
                    timestamp: new Date(),
                    language: data.meta?.language,
                    structured_sources: data.structured_sources,
                    isTyping: true
                };
                setMessages(prev => [...prev, aiMessage]);
            }
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                text: "Maaf kijiye, I faced a connection issue. Please try again.",
                timestamp: new Date(),
                isTyping: false
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full w-full relative bg-transparent">
            {/* Header Controls Removed for Full Screen Mode */}

            {/* Messages Area */}
            <div
                ref={scrollContainerRef}
                className="flex-1 overflow-y-auto p-4 space-y-4 bg-transparent [&::-webkit-scrollbar]:hidden scrollbar-none"
                style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
            >
                {messages.length === 0 || (messages.length === 1 && messages[0].id === 'welcome') ? (
                    <div className="flex flex-col items-center justify-center h-full text-center p-8 opacity-80 animate-in fade-in duration-700">
                        <div className="w-24 h-24 bg-blue-500/10 rounded-3xl flex items-center justify-center mb-6 border border-blue-500/20 shadow-2xl rotate-3">
                            <BotIcon className="w-12 h-12 text-blue-500" />
                        </div>
                        <h3 className="text-2xl font-black text-white mb-2 tracking-tighter">
                            Namaste! How can I help you today?
                        </h3>
                        <p className="text-slate-400 max-w-md mb-12 font-medium">
                            Ask me about government schemes, farming prices, or health benefits in your language.
                        </p>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
                            {[
                                "PM Kisan Samman Nidhi details",
                                "Ayushman Bharat eligibility",
                                "Apply for Ration Card",
                                "Mandi prices for Wheat"
                            ].map((q, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => {
                                        setInputText(q);
                                        handleSend(q);
                                    }}
                                    suppressHydrationWarning
                                    className="px-5 py-4 bg-white/5 border border-white/10 rounded-2xl text-left text-sm text-slate-300 hover:bg-blue-600 hover:text-white hover:border-blue-500 hover:shadow-xl hover:shadow-blue-600/20 transition-all flex items-center justify-between group"
                                >
                                    <span className="font-bold">{q}</span>
                                    <span className="opacity-0 group-hover:opacity-100 transition-opacity">→</span>
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <>
                        {messages.map((msg) => (
                            <div
                                key={msg.id}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2`}
                            >
                                <div
                                    className={`
                                        max-w-[85%] sm:max-w-[75%] p-5 rounded-[1.5rem] shadow-sm text-sm md:text-base transition-all duration-200
                                        ${msg.role === 'user'
                                            ? 'bg-blue-600 text-white rounded-br-none shadow-blue-600/20'
                                            : 'bg-white/95 dark:bg-slate-900/95 text-slate-800 dark:text-slate-100 rounded-bl-none border border-white/10 backdrop-blur-md'}
                                    `}
                                >
                                    {msg.role === 'assistant' && msg.isTyping ? (
                                        <Typewriter
                                            text={msg.text}
                                            onComplete={() => {
                                                // Mark message as done typing locally to switch to static render
                                                setMessages(prev => prev.map(m =>
                                                    m.id === msg.id ? { ...m, isTyping: false } : m
                                                ));
                                            }}
                                        />
                                    ) : (
                                        <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                                    )}

                                    {msg.role === 'assistant' && msg.structured_sources && msg.structured_sources.length > 0 && (
                                        <div className="mt-6 grid grid-cols-1 gap-4 w-full">
                                            {msg.structured_sources.map((source, idx) => (
                                                <SchemeCard
                                                    key={idx}
                                                    title={source.title || "Government Scheme"}
                                                    description={source.text}
                                                    link={source.link}
                                                    benefit={source.benefit || "View Details"}
                                                    logo={source.logo}
                                                />
                                            ))}
                                        </div>
                                    )}

                                    {msg.audio && (
                                        <div className="mt-4 pt-4 border-t border-slate-100 dark:border-white/5">
                                            <AudioPlayer src={msg.audio} />
                                        </div>
                                    )}

                                    <span className={`text-[10px] font-bold block mt-3 text-right ${msg.role === 'user' ? 'text-blue-100/60' : 'text-slate-500'}`}>
                                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-white/10 backdrop-blur-md p-4 rounded-2xl rounded-bl-none border border-white/10 shadow-sm flex items-center gap-3">
                                    <div className="flex space-x-1">
                                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                                    </div>
                                    <span className="text-[10px] text-blue-400 font-black uppercase tracking-widest animate-pulse">
                                        AWS Bedrock Analyzing...
                                    </span>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white/10 dark:bg-black/40 backdrop-blur-xl border-t border-white/5 z-20">

                {/* Image Preview Banner */}
                {imagePreview && (
                    <div className="mb-4 p-3 bg-blue-500/10 rounded-2xl flex items-center justify-between animate-in slide-in-from-bottom-4 backdrop-blur-md border border-blue-500/20">
                        <div className="flex items-center gap-4">
                            <div className="relative h-14 w-14 group">
                                <img src={imagePreview} alt="Selected" className="h-full w-full object-cover rounded-xl border border-white/20" />
                                <div className="absolute inset-0 bg-blue-500/20 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
                            </div>
                            <div>
                                <p className="text-xs font-black text-blue-400 uppercase tracking-widest">Document Selected</p>
                                <p className="text-sm text-slate-300 font-bold truncate max-w-[200px]">{selectedImage?.name}</p>
                            </div>
                        </div>
                        <button onClick={clearImage} className="p-2 bg-white/5 hover:bg-red-500/20 text-slate-400 hover:text-red-400 rounded-xl transition-all">
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                )}

                {/* Text Input Row */}
                <div className="flex gap-3 items-center bg-white/5 p-2 rounded-[2rem] border border-white/10 shadow-2xl shadow-black/20 focus-within:border-blue-500/50 transition-all">
                    <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        ref={fileInputRef}
                        onChange={handleImageSelect}
                    />

                    <button
                        onClick={() => fileInputRef.current?.click()}
                        suppressHydrationWarning
                        className={`p-4 rounded-[1.5rem] transition-all ${selectedImage ? 'bg-blue-600 text-white' : 'hover:bg-white/10 text-slate-400 hover:text-white'}`}
                        title="Analyze Document/Image"
                        disabled={isLoading}
                    >
                        <Camera className="w-6 h-6" />
                    </button>

                    <VoiceInput onTranscript={handleSend} isProcessing={isLoading} compact={true} />

                    <input
                        suppressHydrationWarning
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend(inputText)}
                        placeholder={selectedImage ? "Press Send to analyze this image..." : (language === 'hi' ? 'अपना प्रश्न पूछें...' : 'Ask JanSathi...')}
                        className="flex-1 p-3 bg-transparent text-white placeholder:text-slate-500 focus:outline-none font-medium"
                        disabled={isLoading}
                    />
                    <button
                        onClick={() => handleSend(inputText)}
                        disabled={isLoading || (!inputText.trim() && !selectedImage)}
                        className="p-4 bg-blue-600 hover:bg-blue-700 text-white rounded-[1.5rem] shadow-xl shadow-blue-600/20 disabled:opacity-50 disabled:shadow-none transition-all active:scale-95 group"
                    >
                        <Send className="w-6 h-6 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                    </button>
                </div>
                <p className="text-[10px] text-center text-slate-500 font-bold uppercase tracking-widest mt-4">JanSathi Professional AI • v2.0</p>
            </div>
        </div>
    );
}

function BotIcon({ className }: { className?: string }) {
    return (
        <svg viewBox="0 0 24 24" fill="none" className={className} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 8V4H8" />
            <rect width="16" height="12" x="4" y="8" rx="2" />
            <path d="M2 14h2" />
            <path d="M20 14h2" />
            <path d="M15 13v2" />
            <path d="M9 13v2" />
        </svg>
    )
}
