'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle, Trash2, Mic } from 'lucide-react';
import { useSearchParams, useRouter } from 'next/navigation';
import AudioPlayer from './AudioPlayer';
import { sendQuery } from '@/services/api';

// --- Typewriter Component ---
const Typewriter = ({ text, onComplete }: { text: string; onComplete?: () => void }) => {
    const [displayedText, setDisplayedText] = useState('');
    const index = useRef(0);

    useEffect(() => {
        index.current = 0;
        setDisplayedText('');

        const intervalId = setInterval(() => {
            // Increment index by chunk size (e.g., 3 chars)
            index.current += 3;

            // Slice safely
            const currentText = text.slice(0, index.current);
            setDisplayedText(currentText);

            if (index.current >= text.length) {
                clearInterval(intervalId);
                if (onComplete) onComplete();
            }
        }, 10);

        return () => clearInterval(intervalId);
    }, [text]);

    return <div className="leading-relaxed whitespace-pre-wrap">{displayedText}</div>;
};

// --- Types ---
type Message = {
    id: string;
    role: 'user' | 'assistant';
    text: string;
    audio?: string;
    context?: string[];
    timestamp: string;
    isTyping?: boolean; // New flag for animation
};

type ChatSession = {
    id: string;
    title: string;
    messages: Message[];
    timestamp: string;
};

const SUGGESTIONS = [
    "How to apply for income certificate?",
    "Am I eligible for government scholarships?",
    "Free health schemes for senior citizens"
];

const SESSIONS_KEY = 'jansathi_chat_sessions';

export default function ChatInterface() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const sessionId = searchParams.get('id');

    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isMounted, setIsMounted] = useState(false);
    const [isListening, setIsListening] = useState(false); // For simplified voice state
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const recognitionRef = useRef<any>(null);

    // --- Voice Logic (Integrated) ---
    useEffect(() => {
        if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
            const SpeechRecognition = (window as any).webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false;
            recognitionRef.current.interimResults = false;
            recognitionRef.current.lang = 'en-US'; // Default, update dynamically if needed

            recognitionRef.current.onstart = () => setIsListening(true);
            recognitionRef.current.onend = () => setIsListening(false);
            recognitionRef.current.onresult = (event: any) => {
                const transcript = event.results[0][0].transcript;
                setInputText(transcript);
                handleSend(transcript);
            };
        }
    }, []);

    const toggleVoice = () => {
        if (isListening) {
            recognitionRef.current?.stop();
        } else {
            recognitionRef.current?.start();
        }
    };

    // --- Session Management ---
    useEffect(() => {
        setIsMounted(true);
        if (sessionId) {
            loadSession(sessionId);
        } else {
            setMessages([]);
        }
    }, [sessionId]);

    const loadSession = (id: string) => {
        try {
            const stored = localStorage.getItem(SESSIONS_KEY);
            if (stored) {
                const sessions = JSON.parse(stored);
                if (sessions[id]) {
                    // When loading history, ensure typing is off
                    const history = sessions[id].messages.map((m: Message) => ({ ...m, isTyping: false }));
                    setMessages(history);
                    return;
                }
            }
            router.push('/chat');
        } catch (e) {
            console.error(e);
        }
    };

    const saveSession = (msgs: Message[], id: string) => {
        try {
            const stored = localStorage.getItem(SESSIONS_KEY);
            let sessions = stored ? JSON.parse(stored) : {};
            const title = msgs.length > 0 ? msgs[0].text.substring(0, 30) + (msgs[0].text.length > 30 ? '...' : '') : 'New Chat';

            // Don't save transient typing state
            const cleanMsgs = msgs.map(({ isTyping, ...rest }) => rest);

            sessions[id] = {
                id,
                title,
                messages: cleanMsgs,
                timestamp: new Date().toISOString()
            };
            localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
            window.dispatchEvent(new Event('chat-storage-update'));
        } catch (e) { }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]); // Scroll on new messages or loading state

    const clearChat = () => {
        if (confirm("Delete this chat?")) {
            setMessages([]);
            if (sessionId) {
                try {
                    const stored = localStorage.getItem(SESSIONS_KEY);
                    if (stored) {
                        const sessions = JSON.parse(stored);
                        delete sessions[sessionId];
                        localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
                        window.dispatchEvent(new Event('chat-storage-update'));
                    }
                } catch (e) { }
                router.push('/chat');
            }
        }
    };

    const handleSend = async (text: string) => {
        if (!text.trim()) return;

        let currentSessionId = sessionId;
        if (!currentSessionId) {
            currentSessionId = Date.now().toString();
            router.push(`/chat?id=${currentSessionId}`);
        }

        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            text: text,
            timestamp: new Date().toISOString()
        };

        const newMessages = [...messages, userMsg];
        setMessages(newMessages);
        if (currentSessionId) saveSession(newMessages, currentSessionId);

        setIsLoading(true);
        setInputText('');

        try {
            const response = await sendQuery({ text_query: text, language: 'hi' });

            const aiMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                text: response.answer.text,
                audio: response.answer.audio,
                context: response.context,
                timestamp: new Date().toISOString(),
                isTyping: true // Start animation
            };

            const finalMessages = [...newMessages, aiMsg];
            setMessages(finalMessages);
            if (currentSessionId) saveSession(finalMessages, currentSessionId);

        } catch (error) {
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                text: 'Sorry, I am having trouble connecting to the server.',
                timestamp: new Date().toISOString(),
                isTyping: false
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    if (!isMounted) return null;

    return (
        <div className="flex flex-col h-[calc(100vh-0px)] w-full relative bg-slate-50 dark:bg-slate-950">

            {/* --- Messages Area (Scrollable) --- */}
            <div className="flex-1 overflow-y-auto pb-32 scroll-smooth"> {/* pb-32 ensures space for fixed footer */}

                {messages.length > 0 && (
                    <div className="fixed top-4 right-4 z-20">
                        <button
                            onClick={clearChat}
                            className="p-2 text-slate-400 hover:text-red-500 bg-white/50 hover:bg-white rounded-full transition-colors shadow-sm"
                            title="Delete Chat"
                        >
                            <Trash2 className="w-5 h-5" />
                        </button>
                    </div>
                )}

                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center min-h-full p-8 text-center animate-in fade-in duration-500">
                        <div className="space-y-6 max-w-3xl">
                            <h2 className="text-4xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-teal-500 leading-tight">
                                How can we help you today?
                            </h2>
                            <p className="text-xl text-slate-500 dark:text-slate-400">
                                Ask about schemes, certificates, or eligibility.
                            </p>
                        </div>

                        <div className="grid gap-4 w-full max-w-lg mt-12">
                            {SUGGESTIONS.map((s) => (
                                <button
                                    key={s}
                                    onClick={() => handleSend(s)}
                                    className="p-4 text-left bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl hover:border-blue-500 hover:shadow-lg hover:scale-[1.02] transition-all text-slate-700 dark:text-slate-300 group"
                                >
                                    <span className="text-lg group-hover:text-blue-600 dark:group-hover:text-blue-400 font-medium transition-colors">"{s}"</span>
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="max-w-4xl mx-auto w-full p-4 space-y-6 pt-8">
                        {messages.map((msg) => (
                            <div
                                key={msg.id}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`
                                        max-w-[90%] md:max-w-[80%] p-5 rounded-3xl shadow-sm text-base leading-relaxed
                                        ${msg.role === 'user'
                                            ? 'bg-blue-600 text-white rounded-br-sm'
                                            : 'bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 rounded-bl-sm border border-slate-200 dark:border-slate-800'}
                                    `}
                                >
                                    {msg.role === 'assistant' && msg.isTyping ? (
                                        <Typewriter
                                            text={msg.text}
                                            onComplete={() => {
                                                // Disable typing once done (optional, prevents re-typing on re-render)
                                            }}
                                        />
                                    ) : (
                                        <div className="whitespace-pre-wrap">{msg.text}</div>
                                    )}

                                    {msg.role === 'assistant' && msg.audio && (
                                        <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
                                            <AudioPlayer src={msg.audio} />
                                        </div>
                                    )}
                                    <div className="text-[10px] opacity-60 mt-2 text-right">
                                        {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </div>
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-white dark:bg-slate-900 p-5 rounded-3xl rounded-bl-sm border border-slate-200 dark:border-slate-800 shadow-sm">
                                    <div className="flex space-x-2">
                                        <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                        <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                        <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce"></div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* --- Input Area (Fixed Bottom) --- */}
            <div className="absolute bottom-0 left-0 right-0 p-4 bg-white/90 dark:bg-slate-950/90 backdrop-blur-lg border-t border-slate-200 dark:border-slate-800 z-30">
                <div className="max-w-4xl mx-auto w-full flex gap-3 items-end">

                    {/* Voice Button (Integrated) */}
                    <button
                        onClick={toggleVoice}
                        className={`p-3 rounded-full transition-all duration-300 ${isListening
                            ? 'bg-red-500 text-white animate-pulse shadow-lg'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
                            }`}
                        title="Interact with Voice"
                    >
                        <Mic className={`w-6 h-6 ${isListening ? 'animate-bounce' : ''}`} />
                    </button>

                    <div className="flex-1 bg-slate-100 dark:bg-slate-900 rounded-2xl flex items-center p-2 border border-transparent focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 dark:focus-within:ring-blue-900 transition-all">
                        <input
                            type="text"
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend(inputText)}
                            placeholder="Type a message..."
                            disabled={isLoading}
                            className="flex-1 bg-transparent border-none px-4 py-2 focus:ring-0 outline-none text-slate-800 dark:text-slate-100 placeholder:text-slate-400"
                        />
                        <button
                            onClick={() => handleSend(inputText)}
                            disabled={!inputText.trim() || isLoading}
                            className="p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-md"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </div>
                <div className="text-center text-xs text-slate-400 mt-2">
                    JanSathi AI can make mistakes. Check important info.
                </div>
            </div>
        </div>
    );
}
