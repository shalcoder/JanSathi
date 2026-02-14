'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Camera, X, Sparkles, Bot, ArrowUpRight, CheckCircle2, Shield, Activity } from 'lucide-react';
import VoiceInput from './VoiceInput';
import AudioPlayer from './AudioPlayer';
<<<<<<< HEAD
import { sendQuery, getHistory, analyzeImage } from '@/services/api';
=======
import { sendQuery, analyzeImage, QueryResponse } from '@/services/api';
>>>>>>> poornachandran
import SchemeCard from './SchemeCard';
import { useSettings } from '@/hooks/useSettings';
import DocumentScorecard from './DocumentScorecard';
import { Languages, Globe } from 'lucide-react';

const Typewriter = ({ text, onComplete }: { text: string; onComplete?: () => void }) => {
    const [displayedText, setDisplayedText] = useState('');
    const index = useRef(0);
    const onCompleteRef = useRef(onComplete);

    useEffect(() => { onCompleteRef.current = onComplete; }, [onComplete]);

    useEffect(() => {
        index.current = 0;
        setDisplayedText('');
        const intervalId = setInterval(() => {
            index.current += 3;
            if (index.current > text.length) index.current = text.length;
            setDisplayedText(text.slice(0, index.current));
            if (index.current >= text.length) {
                clearInterval(intervalId);
                if (onCompleteRef.current) onCompleteRef.current();
            }
        }, 12);
        return () => clearInterval(intervalId);
    }, [text]);

    return <div className="leading-relaxed whitespace-pre-wrap">{displayedText}</div>;
};

type Message = {
    id: string;
    role: 'user' | 'assistant';
    text: string;
    timestamp: Date;
    language?: string;
    audio?: string;
    isTyping?: boolean;
    structured_sources?: any[];
};

const SUGGESTIONS = [
    { title: "PM Awas Yojana", desc: "Sarkari Makan (Housing)", style: "bento-1x1" },
    { title: "E-Shram Registry", desc: "Majdoor Labh (Worker Benefits)", style: "bento-1x1" },
    { title: "PM-Kisan Status", desc: "Kheti Sahayata (Farmer Aid)", style: "bento-1x1" },
    { title: "Ration Card", desc: "Khadya Suraksha (Food Security)", style: "bento-1x1" }
];

const SESSIONS_KEY = 'jansathi_chat_sessions';

export default function ChatInterface() {
<<<<<<< HEAD
    // Demo user (no authentication required)
    const user = { id: 'demo_user', firstName: 'JanSathi User' };

    // Global Settings
    const { settings, updateSettings } = useSettings();

=======
    const { settings } = useSettings();
>>>>>>> poornachandran
    const [messages, setMessages] = useState<Message[]>([]);
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [language, setLanguage] = useState(settings.language);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [selectedImage, setSelectedImage] = useState<File | null>(null);

    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => { setLanguage(settings.language); }, [settings.language]);

    useEffect(() => {
        const lastSession = sessionStorage.getItem('current_jansathi_session');
        if (lastSession) loadSession(lastSession);
        else resetToWelcome();
    }, []);

    const resetToWelcome = () => {
        setCurrentSessionId(null);
        setMessages([]);
    };

    const loadSession = (id: string) => {
        const stored = localStorage.getItem(SESSIONS_KEY);
        if (stored) {
            const sessions = JSON.parse(stored);
            if (sessions[id]) {
                setMessages(sessions[id].messages.map((m: any) => ({ ...m, timestamp: new Date(m.timestamp), isTyping: false })));
                setCurrentSessionId(id);
                sessionStorage.setItem('current_jansathi_session', id);
            }
        }
    };

    const handleSend = async (text: string = inputText) => {
        if ((!text.trim() && !selectedImage) || isLoading) return;

        let sid = currentSessionId || Date.now().toString();
        if (!currentSessionId) {
            setCurrentSessionId(sid);
            sessionStorage.setItem('current_jansathi_session', sid);
        }

        setIsLoading(true);
        const newMessage: Message = { id: Date.now().toString(), role: 'user', text: text || 'Document Analysis', timestamp: new Date() };
        setMessages(prev => [...prev, newMessage]);
        setInputText('');

        try {
            if (selectedImage) {
                const data = await analyzeImage(selectedImage, language);
                setSelectedImage(null); setImagePreview(null);
                setMessages(prev => [...prev, { id: 'ai_' + Date.now(), role: 'assistant', text: data.analysis.text, audio: data.analysis.audio, timestamp: new Date(), isTyping: true }]);
            } else {
                const data: QueryResponse = await sendQuery({ text_query: text, language });
                setMessages(prev => [...prev, {
                    id: 'ai_' + Date.now(),
                    role: 'assistant',
                    text: data.answer.text,
                    audio: data.answer.audio,
                    structured_sources: data.structured_sources,
                    timestamp: new Date(),
                    isTyping: true
                }]);
            }
        } catch (e) {
            setMessages(prev => [...prev, { id: 'err_' + Date.now(), role: 'assistant', text: "Connection slow. Trying again...", timestamp: new Date() }]);
        } finally { setIsLoading(false); }
    };

    const DIALECTS = [
        { code: 'hi', name: 'Hindi (Standard)' },
        { code: 'hi-rural', name: 'Hindi (Gramin)' },
        { code: 'kn', name: 'Kannada' },
        { code: 'ta', name: 'Tamil' },
        { code: 'te', name: 'Telugu' },
        { code: 'ml', name: 'Malayalam' },
        { code: 'gu', name: 'Gujarati' },
        { code: 'mr', name: 'Marathi' },
        { code: 'pa', name: 'Punjabi' }
    ];

    return (
<<<<<<< HEAD
        <div className="flex flex-col h-full w-full glass-panel rounded-2xl sm:rounded-3xl overflow-hidden shadow-2xl relative border border-white/10 bg-black/20 backdrop-blur-xl transition-all duration-500">

            {/* Header Controls */}
            <div className="flex justify-between items-center p-3 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 z-10">
                <div className="flex items-center gap-2">
                    <button
                        onClick={handleDeleteChat}
                        className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                        title="Delete this chat"
                    >
                        <Trash2 className="w-4 h-4" />
                    </button>
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded-md">Live Consultation</span>
=======
        <div className="flex flex-col h-full w-full relative bg-transparent">
            {/* Vishwa Dialect Tuner — Elite Feature */}
            <div className="absolute top-4 left-4 z-50 flex items-center gap-2 p-1.5 bg-background/50 backdrop-blur-xl border border-border/50 rounded-2xl shadow-lg">
                <div className="p-2 rounded-xl bg-primary/10">
                    <Globe className="w-4 h-4 text-primary" />
>>>>>>> poornachandran
                </div>
                <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="bg-transparent text-[10px] font-black uppercase tracking-widest text-foreground outline-none px-2 pr-6 appearance-none cursor-pointer"
                >
                    {DIALECTS.map(d => (
                        <option key={d.code} value={d.code} className="bg-card text-foreground">{d.name}</option>
                    ))}
                </select>
                <div className="pr-1 opacity-40">
                    <Languages className="w-3 h-3" />
                </div>
            </div>

            {/* Background elements */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -mr-20 -mt-20"></div>

            {/* Messages Area */}
<<<<<<< HEAD
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-transparent scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
                {messages.length === 0 || (messages.length === 1 && messages[0].id === 'welcome') ? (
                    <div className="flex flex-col items-center justify-center h-full text-center p-4 sm:p-8 opacity-80 animate-in fade-in duration-700">
                        <div className="w-20 h-20 sm:w-24 sm:h-24 bg-blue-500/10 rounded-2xl sm:rounded-3xl flex items-center justify-center mb-4 sm:mb-6 border border-blue-500/20 shadow-2xl rotate-3">
                            <BotIcon className="w-10 h-10 sm:w-12 sm:h-12 text-blue-500" />
                        </div>
                        <h3 className="text-xl sm:text-2xl font-black text-white mb-2 tracking-tighter">
                            Namaste! How can I help you today?
                        </h3>
                        <p className="text-sm sm:text-base text-slate-400 max-w-md mb-8 sm:mb-12 font-medium px-4">
                            Ask me about government schemes, farming prices, or health benefits in your language.
                        </p>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg px-4">
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
                                    className="px-4 sm:px-5 py-3 sm:py-4 bg-white/5 border border-white/10 rounded-xl sm:rounded-2xl text-left text-xs sm:text-sm text-slate-300 hover:bg-blue-600 hover:text-white hover:border-blue-500 hover:shadow-xl hover:shadow-blue-600/20 transition-all flex items-center justify-between group"
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
                                        max-w-[95%] sm:max-w-[85%] md:max-w-[75%] p-3 sm:p-4 md:p-5 rounded-xl sm:rounded-[1.5rem] shadow-sm text-sm md:text-base transition-all duration-200
                                        ${msg.role === 'user'
                                            ? 'bg-blue-600 text-white rounded-br-none shadow-blue-600/20'
                                            : 'bg-white/95 dark:bg-slate-900/95 text-slate-800 dark:text-slate-100 rounded-bl-none border border-white/10 backdrop-blur-md'}
                                    `}
                                >
                                    {msg.role === 'assistant' && msg.isTyping ? (
                                        <Typewriter text={msg.text} onComplete={() => {
                                            // Handle completion if needed
                                        }} />
                                    ) : (
                                        <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                                    )}

                                    {msg.role === 'assistant' && msg.structured_sources && msg.structured_sources.length > 0 && (
                                        <div className="mt-6 flex flex-col gap-6 w-full">
                                            <div className="flex items-center gap-2 p-3 bg-blue-500/10 rounded-2xl border border-blue-500/20">
                                                <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center animate-pulse">
                                                    <BotIcon className="w-4 h-4 text-white" />
                                                </div>
                                                <div className="flex-1">
                                                    <p className="text-[10px] font-black text-blue-400 uppercase tracking-widest leading-none mb-1">Fill For Me (Phase 4 Beta)</p>
                                                    <p className="text-xs text-slate-400 font-medium">I can help you apply for these schemes using voice!</p>
                                                </div>
                                                <button
                                                    onClick={() => alert("JanSathi Form Assistant is initializing... (Finalizing AWS Integration for Phase 4)")}
                                                    className="px-4 py-2 bg-blue-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:scale-105 active:scale-95 transition-all shadow-lg shadow-blue-600/20"
                                                >
                                                    Start Agent
                                                </button>
                                            </div>

                                            <div className="grid grid-cols-1 gap-3 sm:gap-4 w-full">
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
                                        </div>
                                    )}
=======
            <div ref={scrollContainerRef} className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-6 scroll-smooth scrollbar-none pb-8 sm:pb-12">

                <AnimatePresence mode="wait">
                    {messages.length === 0 ? (
                        <motion.div
                            key="welcome"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="flex flex-col items-center justify-center min-h-[60vh] text-center max-w-5xl mx-auto py-10"
                        >
                            <div className="space-y-6 w-full px-4">
                                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800 text-emerald-600 text-[10px] font-bold uppercase tracking-widest">
                                    <CheckCircle2 className="w-3.5 h-3.5" />
                                    Verified Assistant
                                </div>

                                <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-foreground">
                                    Hello! <br />
                                    How can <span className="text-primary">JanSathi</span> help?
                                </h1>
>>>>>>> poornachandran

                                <p className="text-base text-secondary-foreground max-w-lg mx-auto font-medium opacity-60 leading-relaxed">
                                    Ask me anything about government schemes, documents, or your benefits.
                                </p>

                                {/* Suggestions - More breathing room */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-12 max-w-4xl mx-auto px-2 pb-10">
                                    {SUGGESTIONS.map((s, i) => (
                                        <button
                                            key={i}
                                            onClick={() => handleSend(s.title)}
                                            className="bg-card border border-border/50 p-5 text-left rounded-xl hover:border-primary/30 transition-colors shadow-sm flex flex-col justify-center"
                                        >
                                            <p className="text-sm font-bold text-foreground mb-1">{s.title}</p>
                                            <p className="text-[10px] font-bold text-secondary-foreground opacity-40 uppercase tracking-wider">{s.desc}</p>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    ) : (
                        <div className="max-w-4xl mx-auto w-full space-y-6 px-2">
                            {messages.map((msg) => (
                                <motion.div
                                    key={msg.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div className={`
                                         p-5 sm:p-7 rounded-2xl relative shadow-sm
                                         ${msg.role === 'user'
                                            ? 'max-w-[85%] sm:max-w-[70%] bg-primary text-white'
                                            : 'w-full sm:max-w-[90%] bg-card border border-border/50 text-foreground'}
                                     `}>
                                        {msg.role === 'assistant' && msg.isTyping ? (
                                            <div className="font-bold text-base leading-relaxed">
                                                <Typewriter text={msg.text} onComplete={() => setMessages(prev => prev.map(m => m.id === msg.id ? { ...m, isTyping: false } : m))} />
                                            </div>
                                        ) : (
                                            <div className="space-y-4">
                                                <p className="whitespace-pre-wrap leading-relaxed font-bold text-base tracking-normal">{msg.text}</p>

                                                {msg.structured_sources && msg.structured_sources.length > 0 && (
                                                    <div className="grid grid-cols-1 gap-4 pt-4">
                                                        {selectedImage && msg.role === 'assistant' && (
                                                            <DocumentScorecard
                                                                docType="Verified Government ID"
                                                                scores={{ accuracy: 94, integrity: 100, eligibility: 88 }}
                                                                vulnerabilities={["Blur detected in bottom corner", "Ensure all margins are visible"]}
                                                            />
                                                        )}
                                                        {msg.structured_sources.map((s, sIdx) => (
                                                            <div key={sIdx} className="space-y-4">
                                                                <SchemeCard
                                                                    title={s.title}
                                                                    description={s.text}
                                                                    link={s.link}
                                                                    benefit={s.benefit}
                                                                    logo={s.logo}
                                                                    related={s.graph_recommendations}
                                                                />
                                                                {/* Agentic Form Draft — Extraordinary Feature */}
                                                                {msg.text.includes("Form") && (
                                                                    <motion.div
                                                                        initial={{ opacity: 0, scale: 0.98 }}
                                                                        animate={{ opacity: 1, scale: 1 }}
                                                                        className="p-6 bg-primary/5 border-2 border-dashed border-primary/20 rounded-3xl space-y-4"
                                                                    >
                                                                        <div className="flex items-center justify-between">
                                                                            <h5 className="text-[10px] font-black uppercase tracking-[0.2em] text-primary">Sovereign Form Draft</h5>
                                                                            <div className="px-2 py-0.5 bg-primary/20 rounded text-[8px] font-bold text-primary">AUTO-FILLED</div>
                                                                        </div>
                                                                        <div className="space-y-2 opacity-60">
                                                                            <div className="h-4 bg-primary/10 rounded w-3/4"></div>
                                                                            <div className="h-4 bg-primary/10 rounded w-1/2"></div>
                                                                        </div>
                                                                        <button className="w-full py-3 bg-primary text-white text-xs font-bold rounded-2xl shadow-lg hover:shadow-primary/20 transition-all">
                                                                            Verify and Apply in 1-Click
                                                                        </button>
                                                                    </motion.div>
                                                                )}
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        {msg.audio && <div className="mt-6 pt-6 border-t border-border/10"><AudioPlayer src={msg.audio} /></div>}

                                        <div className={`text-[9px] font-bold uppercase tracking-wider mt-4 opacity-30 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                                            {msg.role === 'user' ? 'Sent' : 'Verified Information'}
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                            {isLoading && (
                                <div className="flex justify-start">
                                    <div className="flex items-center gap-3 p-3 px-5 bg-secondary/30 rounded-full border border-border">
                                        <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse"></div>
                                        <span className="text-[10px] text-foreground font-bold uppercase tracking-wider">JanSathi is thinking...</span>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </AnimatePresence>
            </div>

            {/* Input Area */}
<<<<<<< HEAD
            <div className="p-3 sm:p-4 bg-white/10 dark:bg-black/40 backdrop-blur-xl border-t border-white/5 z-20">

                {/* Image Preview Banner */}
                {imagePreview && (
                    <div className="mb-3 sm:mb-4 p-3 bg-blue-500/10 rounded-xl sm:rounded-2xl flex items-center justify-between animate-in slide-in-from-bottom-4 backdrop-blur-md border border-blue-500/20">
                        <div className="flex items-center gap-3 sm:gap-4 overflow-hidden">
                            <div className="relative h-12 w-12 sm:h-14 sm:w-14 group flex-shrink-0">
                                <img src={imagePreview} alt="Selected" className="h-full w-full object-cover rounded-lg sm:rounded-xl border border-white/20" />
                                <div className="absolute inset-0 bg-blue-500/20 rounded-lg sm:rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
                            </div>
                            <div className="min-w-0 flex-1">
                                <p className="text-xs font-black text-blue-400 uppercase tracking-widest">Document Selected</p>
                                <p className="text-xs sm:text-sm text-slate-300 font-bold truncate">{selectedImage?.name}</p>
                            </div>
                        </div>
                        <button onClick={clearImage} className="p-2 bg-white/5 hover:bg-red-500/20 text-slate-400 hover:text-red-400 rounded-lg sm:rounded-xl transition-all flex-shrink-0 ml-2">
                            <X className="w-4 h-4 sm:w-5 sm:h-5" />
                        </button>
=======
            <div className="shrink-0 p-4 sm:p-6 bg-background/80 backdrop-blur-md border-t border-border/50">
                <div className="max-w-4xl mx-auto w-full">

                    <AnimatePresence>
                        {imagePreview && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: 20 }}
                                className="mb-4 p-4 bg-card rounded-2xl flex items-center justify-between border border-primary/30 shadow-lg"
                            >
                                <div className="flex items-center gap-4">
                                    <img src={imagePreview} className="h-16 w-16 object-cover rounded-xl border border-border shadow-sm" alt="Upload" />
                                    <div>
                                        <p className="text-[10px] font-bold text-primary uppercase tracking-widest mb-0.5">Image Selected</p>
                                        <p className="text-sm font-bold truncate max-w-[200px] text-foreground">{selectedImage?.name}</p>
                                    </div>
                                </div>
                                <button onClick={() => { setSelectedImage(null); setImagePreview(null); }} className="p-3 bg-secondary/50 hover:text-red-600 rounded-xl transition-colors">
                                    <X className="w-6 h-6" />
                                </button>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <div className="flex items-end gap-3 p-2 bg-secondary/30 border border-border/50 rounded-[2rem] shadow-sm relative transition-all focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary/50">
                        <div
                            className="p-1.5 rounded-2xl bg-card flex-1 flex items-center gap-2 border border-border shadow-lg focus-within:border-primary transition-colors"
                        >
                            <input type="file" accept="image/*" className="hidden" ref={fileInputRef} onChange={(e) => { if (e.target.files?.[0]) { setSelectedImage(e.target.files[0]); setImagePreview(URL.createObjectURL(e.target.files[0])); } }} />

                            <button onClick={() => fileInputRef.current?.click()} className={`p-3 rounded-xl transition-all ${selectedImage ? 'bg-primary text-white' : 'hover:bg-secondary text-secondary-foreground'}`}>
                                <Camera className="w-5 h-5" />
                            </button>

                            <VoiceInput onTranscript={handleSend} isProcessing={isLoading} compact={true} />

                            <input
                                type="text"
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                placeholder={selectedImage ? "Click send to analyze photo..." : "Ask your question here..."}
                                className="flex-1 bg-transparent px-3 text-[15px] font-bold text-foreground placeholder:opacity-30 focus:outline-none"
                                disabled={isLoading}
                            />

                            <button
                                onClick={() => handleSend()}
                                disabled={isLoading || (!inputText.trim() && !selectedImage)}
                                className="p-3.5 bg-primary text-white rounded-xl shadow-md disabled:opacity-20 active:scale-95 transition-all"
                            >
                                <Send className="w-5 h-5" />
                            </button>
                        </div>
>>>>>>> poornachandran
                    </div>

<<<<<<< HEAD
                {/* Voice Input Centered */}
                <div className="mb-4 sm:mb-6 flex justify-center">
                    <VoiceInput onTranscript={handleSend} isProcessing={isLoading} />
                </div>

                {/* Text Input Row */}
                <div className="flex gap-2 sm:gap-3 items-center bg-white/5 p-1.5 sm:p-2 rounded-2xl sm:rounded-[2rem] border border-white/10 shadow-2xl shadow-black/20 focus-within:border-blue-500/50 transition-all">
                    <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        ref={fileInputRef}
                        onChange={handleImageSelect}
                    />

                    <button
                        onClick={() => fileInputRef.current?.click()}
                        className={`p-3 sm:p-4 rounded-xl sm:rounded-[1.5rem] transition-all ${selectedImage ? 'bg-blue-600 text-white' : 'hover:bg-white/10 text-slate-400 hover:text-white'}`}
                        title="Analyze Document/Image"
                        disabled={isLoading}
                    >
                        <Camera className="w-5 h-5 sm:w-6 sm:h-6" />
                    </button>

                    <input
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend(inputText)}
                        placeholder={selectedImage ? "Press Send to analyze this image..." : (language === 'hi' ? 'अपना प्रश्न पूछें...' : 'Ask JanSathi...')}
                        className="flex-1 p-2 sm:p-3 bg-transparent text-white placeholder:text-slate-500 focus:outline-none font-medium text-sm sm:text-base"
                        disabled={isLoading}
                    />
                    <button
                        onClick={() => handleSend(inputText)}
                        disabled={isLoading || (!inputText.trim() && !selectedImage)}
                        className="p-3 sm:p-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl sm:rounded-[1.5rem] shadow-xl shadow-blue-600/20 disabled:opacity-50 disabled:shadow-none transition-all active:scale-95 group"
                    >
                        <Send className="w-5 h-5 sm:w-6 sm:h-6 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                    </button>
                </div>
                <p className="text-[10px] text-center text-slate-500 font-bold uppercase tracking-widest mt-3 sm:mt-4">JanSathi Professional AI • v2.0</p>
=======
                    <div className="flex justify-center items-center gap-3 mt-4 opacity-30">
                        <div className="h-px w-8 bg-foreground"></div>
                        <p className="text-[9px] font-bold uppercase tracking-widest text-foreground">Verified Information • Secure Helper</p>
                        <div className="h-px w-8 bg-foreground"></div>
                    </div>
                </div>
>>>>>>> poornachandran
            </div>
        </div>
    );
}
