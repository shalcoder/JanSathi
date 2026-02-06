'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, History as HistoryIcon, Languages, Camera, Image as ImageIcon, X } from 'lucide-react';
import VoiceInput from './VoiceInput';
import AudioPlayer from './AudioPlayer';
import { useUser } from '@clerk/nextjs';
import { sendQuery, getHistory, analyzeImage } from '@/services/api';

import SchemeCard from './SchemeCard';

type Message = {
    id: string;
    role: 'user' | 'assistant';
    text: string;
    timestamp: Date;
    language?: string;
    userId?: string;
    audio?: string;
    context?: string[];
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

export default function ChatInterface() {
    const clerk = useUser();
    // Safety fallback for demo mode without valid Clerk keys
    const user = clerk?.user ?? { id: 'demo_user', firstName: 'JanSathi User' };
    const isLoaded = clerk?.isLoaded ?? true;
    const [messages, setMessages] = useState<Message[]>([]);

    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [language, setLanguage] = useState('hi');
    const [showHistory, setShowHistory] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        // Load messages from session storage
        const saved = sessionStorage.getItem('jansathi_chat');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                const restored = parsed.map((m: any) => ({
                    ...m,
                    timestamp: new Date(m.timestamp)
                }));
                setMessages(restored);
            } catch (e) {
                console.error("Failed to load session:", e);
                setMessages([{
                    id: 'welcome',
                    role: 'assistant',
                    text: 'Namaste! I am JanSathi. Ask me anything about government schemes or services.',
                    timestamp: new Date()
                }]);
            }
        } else {
            setMessages([{
                id: 'welcome',
                role: 'assistant',
                text: 'Namaste! I am JanSathi. Ask me anything about government schemes or services.',
                timestamp: new Date()
            }]);
        }
    }, []);

    useEffect(() => {
        if (messages.length > 0) {
            sessionStorage.setItem('jansathi_chat', JSON.stringify(messages));
        }

        // Only auto-scroll if there are real messages (not just the welcome message)
        if (messages.length > 1 || (messages.length === 1 && messages[0].id !== 'welcome')) {
            scrollToBottom();
        }
    }, [messages]);

    // Load History
    useEffect(() => {
        const loadHistory = async () => {
            const history = await getHistory(20);
            if (history && history.length > 0) {
                const formattedHistory: Message[] = history.map((item: any) => ({
                    id: item.id.toString(),
                    role: 'assistant' as 'assistant', // Explicit cast to satisfy literal type
                    text: item.answer,
                    timestamp: new Date(item.timestamp),
                    language: item.language,
                })).reverse();
                // Merge with user queries if needed, for now just show answers as blocks
                setMessages(prev => [...prev, ...formattedHistory]);
            }
        };
        // Only load if we want to show it or at start
        // loadHistory(); 
    }, []);

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

    const handleSend = async (text: string = inputText) => {
        if ((!text.trim() && !selectedImage) || isLoading) return;

        setIsLoading(true);
        const newMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            text: text || (selectedImage ? 'Analyzed this document' : ''),
            timestamp: new Date(),
            language: language // Track language for this message
        };

        // Optimistically add user message
        setMessages(prev => [...prev, newMessage]);
        setInputText('');

        try {
            let data;
            if (selectedImage) {
                // Handle Image Analysis
                data = await analyzeImage(selectedImage, language);
                clearImage();

                // Construct Vision Response
                const visionMsg: Message = {
                    id: Date.now().toString() + '_ai',
                    role: 'assistant',
                    text: data.analysis.text,
                    audio: data.analysis.audio,
                    timestamp: new Date(),
                    language: data.meta.language
                };
                setMessages(prev => [...prev, visionMsg]);

            } else {
                // Handle Text/Voice Query (Existing Logic)
                data = await sendQuery({
                    text_query: text,
                    language: language,
                    // @ts-ignore - adding metadata for backend
                    userId: user?.id
                });

                const aiMessage: Message = {
                    id: Date.now().toString() + '_ai',
                    role: 'assistant',
                    text: data.answer.text,
                    audio: data.answer.audio,
                    timestamp: new Date(),
                    language: data.meta?.language,
                    structured_sources: data.structured_sources
                };
                setMessages(prev => [...prev, aiMessage]);
            }
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                text: "Maaf kijiye, I faced a connection issue. Please try again.",
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full w-full glass-panel rounded-3xl overflow-hidden shadow-2xl relative border border-white/10 bg-black/20 backdrop-blur-xl transition-all duration-500">

            {/* Header Controls */}
            <div className="flex justify-between items-center p-3 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 z-10">
                <div className="flex items-center gap-2">
                    <HistoryIcon
                        className={`w-5 h-5 cursor-pointer ${showHistory ? 'text-blue-600' : 'text-slate-400'}`}
                        onClick={() => setShowHistory(!showHistory)}
                    />
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Live Chat</span>
                </div>

                <div className="flex items-center gap-2">
                    <Languages className="w-4 h-4 text-slate-400" />
                    <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="text-xs bg-slate-100 dark:bg-slate-800 border-none rounded-lg px-2 py-1 outline-none ring-1 ring-slate-200 dark:ring-slate-700 focus:ring-blue-500"
                    >
                        {LANGUAGES.map(lang => (
                            <option key={lang.code} value={lang.code}>{lang.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-transparent scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
                {messages.length === 0 || (messages.length === 1 && messages[0].id === 'welcome') ? (
                    <div className="flex flex-col items-center justify-center h-full text-center p-8 opacity-80">
                        <div className="w-24 h-24 bg-blue-50 dark:bg-slate-800 rounded-full flex items-center justify-center mb-6 animate-pulse">
                            <img src="/logo.svg" alt="JanSathi" className="w-12 h-12" onError={(e) => (e.target as HTMLImageElement).src = 'https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg'} />
                        </div>
                        <h3 className="text-xl font-bold text-slate-700 dark:text-slate-200 mb-2">
                            Namaste! How can I help you today?
                        </h3>
                        <p className="text-slate-500 max-w-md mb-8">
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
                                    className="px-4 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-left text-sm text-slate-700 dark:text-slate-300 hover:border-blue-500 hover:shadow-md transition-all flex items-center justify-between group"
                                >
                                    {q}
                                    <span className="opacity-0 group-hover:opacity-100 text-blue-500 transition-opacity">→</span>
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <>
                        {messages.map((msg) => (
                            <div
                                key={msg.id}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`
                                        max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl shadow-sm text-sm md:text-base transition-all duration-200
                                        ${msg.role === 'user'
                                            ? 'bg-blue-600 text-white rounded-br-none shadow-blue-200 dark:shadow-none'
                                            : 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 rounded-bl-none border border-slate-200 dark:border-slate-700'}
                                    `}
                                >
                                    <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>

                                    {msg.role === 'assistant' && msg.structured_sources && msg.structured_sources.length > 0 && (
                                        <div className="mt-4 grid grid-cols-1 gap-3 w-full">
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

                                    {/* Audio Player */}
                                    {msg.audio && <AudioPlayer src={msg.audio} />}

                                    {msg.role === 'assistant' && msg.text && (
                                        <div className="mt-2 flex items-center gap-2 opacity-50">
                                            <span className="text-[10px]">AI Voice Output</span>
                                        </div>
                                    )}

                                    <span className={`text-[10px] block mt-2 text-right ${msg.role === 'user' ? 'text-blue-100' : 'text-slate-400'}`}>
                                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-white dark:bg-slate-800 p-4 rounded-2xl rounded-bl-none border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-2">
                                    <div className="flex space-x-1">
                                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                                    </div>
                                    <span className="text-xs text-slate-400 font-medium animate-pulse ml-2">
                                        Processing with AWS Bedrock...
                                    </span>
                                </div>
                            </div>
                        )}
                    </>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white/10 dark:bg-black/20 backdrop-blur-md border-t border-white/10 z-20">

                {/* Image Preview Banner */}
                {imagePreview && (
                    <div className="mb-2 p-2 bg-slate-100/90 dark:bg-slate-900/90 rounded-lg flex items-center justify-between animate-in slide-in-from-bottom-2 backdrop-blur-md border border-white/10">
                        <div className="flex items-center gap-3">
                            <img src={imagePreview} alt="Selected" className="h-12 w-12 object-cover rounded-md border border-slate-300" />
                            <span className="text-xs text-slate-500 dark:text-slate-300 font-medium truncate max-w-[150px]">
                                {selectedImage?.name}
                            </span>
                        </div>
                        <button onClick={clearImage} className="p-1 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-full">
                            <X className="w-4 h-4 text-slate-500" />
                        </button>
                    </div>
                )}

                {/* Voice Input Centered */}
                <div className="mb-4 flex justify-center">
                    <VoiceInput onTranscript={handleSend} isProcessing={isLoading} />
                </div>

                {/* Text Input Row */}
                <div className="flex gap-2 items-center bg-white/5 dark:bg-black/40 p-1.5 rounded-2xl border border-white/10 shadow-lg backdrop-blur-sm">
                    <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        ref={fileInputRef}
                        onChange={handleImageSelect}
                    />

                    <button
                        onClick={() => fileInputRef.current?.click()}
                        className={`p-3 rounded-xl hover:bg-white/10 text-slate-400 hover:text-blue-400 transition-colors ${selectedImage ? 'text-blue-400 bg-blue-500/10' : ''}`}
                        title="Analyze Document/Image"
                        disabled={isLoading}
                    >
                        <Camera className="w-5 h-5" />
                    </button>

                    <input
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend(inputText)}
                        placeholder={selectedImage ? "Press Send to analyze this image..." : (language === 'hi' ? 'अपना प्रश्न पूछें...' : 'Type your question...')}
                        className="flex-1 p-2 bg-transparent text-slate-800 dark:text-slate-100 placeholder:text-slate-500 focus:outline-none"
                        disabled={isLoading}
                    />
                    <button
                        onClick={() => handleSend(inputText)}
                        disabled={isLoading || (!inputText.trim() && !selectedImage)}
                        className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-lg shadow-blue-500/30 disabled:opacity-50 disabled:shadow-none transition-all active:scale-95"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
