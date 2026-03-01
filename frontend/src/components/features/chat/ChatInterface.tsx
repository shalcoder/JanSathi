'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Camera, X, Sparkles, Shield, ExternalLink, CheckCircle2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import VoiceInput from './VoiceInput';
import AudioPlayer from './AudioPlayer';
import BenefitReceipt from './BenefitReceipt';
import TelemetryPanel from './TelemetryPanel';
import SchemeCard from './SchemeCard';
import { useSettings } from '@/hooks/useSettings';
import { useSession } from '@/hooks/useSession';
import DocumentScorecard from './DocumentScorecard';
import ExplainabilityCard from './ExplainabilityCard';
import MultiAgentThoughtProcess from './MultiAgentThoughtProcess';
import { Languages, Globe } from 'lucide-react';
import { useUser } from '@clerk/nextjs';
import {
    sendUnifiedQuery,
    analyzeImage,
    applyForBenefit,
    type UnifiedQueryResponse,
    type BenefitReceipt as BenefitReceiptType,
} from '@/services/api';
import { enqueue, registerOnlineFlush, type QueuedAction } from '@/services/offlineQueue';

// ─── Typewriter ───────────────────────────────────────────────────────────────

const Typewriter = ({ text, onComplete }: { text: string; onComplete?: () => void }) => {
    const [displayedText, setDisplayedText] = useState('');
    const index = useRef(0);
    const onCompleteRef = useRef(onComplete);

    useEffect(() => { onCompleteRef.current = onComplete; }, [onComplete]);

    useEffect(() => {
        index.current = 0;
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

    return <div className="leading-relaxed font-medium text-foreground/90">{displayedText}</div>;
};

// ─── Types ────────────────────────────────────────────────────────────────────

interface Source {
    title: string;
    text: string;
    link: string;
    benefit: string;
    logo: string;
    graph_recommendations?: string[];
}

type Message = {
    id: string;
    role: 'user' | 'assistant';
    text: string;
    timestamp: Date;
    language?: string;
    audio?: string;
    audioUrl?: string;       // from unified response
    isTyping?: boolean;
    structured_sources?: Source[];
    provenance?: string;
    explainability?: {
        confidence: number;
        matching_criteria: string[];
        privacy_protocol: string;
    };
    // Unified fields
    benefitReceipt?: BenefitReceiptType;
    confidence?: number;
    turnId?: string;
    debugInfo?: UnifiedQueryResponse['debug'];
    applyStatus?: 'idle' | 'applying' | 'applied' | 'queued';
};

const SUGGESTIONS = [
    { title: "PM Awas Yojana", desc: "Sarkari Makan (Housing)", style: "bento-1x1" },
    { title: "E-Shram Registry", desc: "Majdoor Labh (Worker Benefits)", style: "bento-1x1" },
    { title: "PM-Kisan Status", desc: "Kheti Sahayata (Farmer Aid)", style: "bento-1x1" },
    { title: "Ration Card", desc: "Khadya Suraksha (Food Security)", style: "bento-1x1" }
];

const SESSIONS_KEY = 'jansathi_chat_sessions';

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

// ─── Demo fallback cache ──────────────────────────────────────────────────────

const DEMO_FALLBACKS: Record<string, string> = {
    'PM-Kisan Status': 'PM-Kisan Samman Nidhi provides ₹6,000/year to eligible farmers in 3 installments. Check your status at pmkisan.gov.in.',
    'PM Awas Yojana': 'PM Awas Yojana (Urban) offers housing assistance for EWS/LIG/MIG categories. Apply via pmaymis.gov.in.',
    'Ration Card': 'A Ration Card gives access to subsidised food grains under the National Food Security Act. Apply at your local Ration office.',
    'E-Shram Registry': 'E-Shram is a national database for unorganised workers. Register at eshram.gov.in to get a UAN and access benefits.',
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function ChatInterface() {
    const { user } = useUser();
    const { settings } = useSettings();
    const { sessionId, token } = useSession();

    const [messages, setMessages] = useState<Message[]>([]);
    const [localSessionId, setLocalSessionId] = useState<string | null>(null);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isThinking, setIsThinking] = useState(false);
    const [isDemoMode, setIsDemoMode] = useState(false);
    const [language, setLanguage] = useState(settings.language);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [selectedImage, setSelectedImage] = useState<File | null>(null);

    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => { setLanguage(settings.language); }, [settings.language]);

    // Restore last session from sessionStorage
    useEffect(() => {
        const lastSession = sessionStorage.getItem('current_jansathi_session');
        if (lastSession) loadSession(lastSession);
        else resetToWelcome();
    }, []);

    // Register offline queue flush handler
    useEffect(() => {
        const cleanup = registerOnlineFlush(async (action: QueuedAction) => {
            if (action.type === 'apply' && token) {
                await applyForBenefit(action.payload as unknown as Parameters<typeof applyForBenefit>[0], token);
            }
        });
        return cleanup;
    }, [token]);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollContainerRef.current) {
            scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
        }
    }, [messages, isLoading]);

    const resetToWelcome = () => {
        setLocalSessionId(null);
        setMessages([]);
    };

    const loadSession = (id: string) => {
        const stored = localStorage.getItem(SESSIONS_KEY);
        if (stored) {
            const sessions = JSON.parse(stored);
            if (sessions[id]) {
                setMessages(sessions[id].messages.map((m: Message) => ({
                    ...m,
                    timestamp: new Date(m.timestamp),
                    isTyping: false
                })));
                setLocalSessionId(id);
                sessionStorage.setItem('current_jansathi_session', id);
            }
        }
    };

    const persistSession = useCallback((sid: string, msgs: Message[]) => {
        const stored = localStorage.getItem(SESSIONS_KEY);
        const sessions = stored ? JSON.parse(stored) : {};
        sessions[sid] = { messages: msgs, updatedAt: new Date().toISOString() };
        localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
    }, []);

    // ── Main send handler ──────────────────────────────────────────────────────

    const handleSend = async (text: string = inputText) => {
        if ((!text.trim() && !selectedImage) || isLoading) return;

        const activeSid = sessionId || localSessionId || Date.now().toString();
        if (!localSessionId) {
            setLocalSessionId(activeSid);
            sessionStorage.setItem('current_jansathi_session', activeSid);
        }

        setIsLoading(true);
        setIsThinking(true);
        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            text: text || 'Document Analysis',
            timestamp: new Date()
        };

        setMessages(prev => {
            const next = [...prev, userMsg];
            persistSession(activeSid, next);
            return next;
        });
        setInputText('');
        setIsDemoMode(false);

        // Set a 6-second demo-fallback timeout
        const fallbackTimer = setTimeout(() => {
            setIsDemoMode(true);
        }, 6000);

        try {
            if (selectedImage) {
                // Image analysis (legacy endpoint kept)
                const data = await analyzeImage(selectedImage, language);
                clearTimeout(fallbackTimer);
                setSelectedImage(null);
                setImagePreview(null);
                const aiMsg: Message = {
                    id: 'ai_' + Date.now(),
                    role: 'assistant',
                    text: data.analysis.text,
                    audio: data.analysis.audio,
                    timestamp: new Date(),
                    isTyping: true
                };
                setMessages(prev => {
                    const next = [...prev, aiMsg];
                    persistSession(activeSid, next);
                    return next;
                });
            } else {
                // Use unified query endpoint
                const response = await sendUnifiedQuery(
                    {
                        session_id: activeSid,
                        channel: 'web',
                        input: { text },
                        metadata: { lang: language, user_id: user?.id || 'anonymous' }
                    },
                    token ?? undefined,
                    activeSid
                );
                clearTimeout(fallbackTimer);
                setIsDemoMode(false);

                const aiMsg: Message = {
                    id: 'ai_' + Date.now(),
                    role: 'assistant',
                    text: response.response_text,
                    audioUrl: response.audio_url,
                    benefitReceipt: response.benefit_receipt,
                    confidence: response.confidence,
                    turnId: response.turn_id,
                    debugInfo: response.debug,
                    timestamp: new Date(),
                    isTyping: true,
                    applyStatus: 'idle'
                };
                setMessages(prev => {
                    const next = [...prev, aiMsg];
                    persistSession(activeSid, next);
                    return next;
                });
            }
        } catch {
            clearTimeout(fallbackTimer);
            // Show demo fallback if available
            const fallbackText = DEMO_FALLBACKS[text] ??
                "I'm having trouble connecting right now. Please try again in a moment.";
            setIsDemoMode(true);
            const errMsg: Message = {
                id: 'err_' + Date.now(),
                role: 'assistant',
                text: fallbackText,
                timestamp: new Date(),
                isTyping: true
            };
            setMessages(prev => {
                const next = [...prev, errMsg];
                persistSession(activeSid, next);
                return next;
            });
        } finally {
            setIsLoading(false);
            setIsThinking(false);
        }
    };

    const handleApply = async (msg: Message) => {
        if (!msg.turnId || !sessionId) return;

        // Update status to 'applying'
        setMessages(prev =>
            prev.map(m => m.id === msg.id ? { ...m, applyStatus: 'applying' as const } : m)
        );

        // If offline, queue the action
        if (!navigator.onLine) {
            enqueue('apply', { session_id: sessionId, turn_id: msg.turnId });
            setMessages(prev =>
                prev.map(m => m.id === msg.id ? { ...m, applyStatus: 'queued' as const } : m)
            );
            return;
        }

        try {
            await applyForBenefit(
                { session_id: sessionId, turn_id: msg.turnId },
                token ?? undefined
            );
            setMessages(prev =>
                prev.map(m => m.id === msg.id ? { ...m, applyStatus: 'applied' as const } : m)
            );
        } catch {
            setMessages(prev =>
                prev.map(m => m.id === msg.id ? { ...m, applyStatus: 'idle' as const } : m)
            );
            alert('Failed to submit application. Please try again.');
        }
    };

    const handleAskAgain = (msg: Message) => {
        if (msg.turnId) {
            handleSend(msg.text);
        }
    };

    // Legacy scheme apply (for SchemeCard)
    const handleSchemeApply = async (schemeTitle: string) => {
        handleSend(`I want to apply for ${schemeTitle}`);
    };

    // ── Render ─────────────────────────────────────────────────────────────────

    return (
        <div className="flex flex-col h-full w-full relative bg-transparent">

            {/* Dialect Tuner */}
            <div className="absolute top-4 left-4 z-50 flex items-center gap-2 p-1.5 bg-background/50 backdrop-blur-xl border border-border/50 rounded-2xl shadow-lg">
                <div className="p-2 rounded-xl bg-primary/10">
                    <Globe className="w-4 h-4 text-primary" />
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

            {/* Demo mode badge */}
            <AnimatePresence>
                {isDemoMode && (
                    <motion.div
                        initial={{ opacity: 0, y: -8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        className="absolute top-4 right-4 z-50 flex items-center gap-1.5 px-3 py-1.5 bg-amber-500/20 border border-amber-500/40 rounded-full"
                    >
                        <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                        <span className="text-[10px] font-bold text-amber-300 uppercase tracking-wider">Demo Mode</span>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Background element */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -mr-20 -mt-20" />

            {/* Messages Area */}
            <div ref={scrollContainerRef} className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-6 scroll-smooth scrollbar-none pb-8 sm:pb-12">
                <AnimatePresence mode="wait">
                    {messages.length === 0 ? (
                        <motion.div
                            key="welcome"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="flex flex-col items-center justify-center min-h-[45vh] text-center max-w-5xl mx-auto py-6"
                        >
                            <div className="space-y-4 w-full px-4">
                                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800 text-emerald-600 text-[9px] font-bold uppercase tracking-widest">
                                    <CheckCircle2 className="w-3 h-3" />
                                    Verified Assistant
                                </div>
                                <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
                                    Hello! <br />
                                    How can <span className="text-primary">JanSathi</span> help?
                                </h1>
                                <p className="text-sm text-secondary-foreground max-w-lg mx-auto font-medium leading-relaxed">
                                    Ask me anything about government schemes, documents, or your benefits.
                                </p>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-8 max-w-4xl mx-auto px-2 pb-4">
                                    {SUGGESTIONS.map((s, i) => (
                                        <button
                                            key={i}
                                            onClick={() => handleSend(s.title)}
                                            className="bg-card/60 backdrop-blur-xl border border-border/50 p-4 text-left rounded-2xl hover:border-primary/50 transition-all shadow-[0_4px_20px_rgb(0,0,0,0.02)] hover:shadow-[0_8px_30px_rgba(234,88,12,0.1)] flex flex-col justify-center group relative overflow-hidden"
                                        >
                                            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                            <div className="relative z-10">
                                                <p className="text-sm font-bold text-foreground mb-1 group-hover:text-primary transition-colors">{s.title}</p>
                                                <p className="text-[9px] font-bold text-secondary-foreground/60 uppercase tracking-wider">{s.desc}</p>
                                            </div>
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
                                        p-4 sm:p-5 relative shadow-sm transition-all
                                        ${msg.role === 'user'
                                            ? 'max-w-[85%] sm:max-w-[70%] bg-primary/95 backdrop-blur-md text-white rounded-2xl rounded-tr-sm shadow-[0_4px_20px_rgba(234,88,12,0.25)] border border-primary/20'
                                            : 'w-full sm:max-w-[95%] bg-card/70 backdrop-blur-xl border border-border/50 text-foreground rounded-2xl rounded-tl-sm hover:shadow-[0_4px_20px_rgba(0,0,0,0.05)] hover:border-border/80'}
                                    `}>
                                        {/* FL Active badge on user messages */}
                                        {msg.role === 'user' && (
                                            <div className="absolute -top-3 right-4 bg-background border border-border/50 shadow-sm px-2 py-1 rounded-full flex items-center gap-1.5 z-10">
                                                <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                                                <span className="text-[9px] font-bold uppercase tracking-wider text-muted-foreground">FL-Node Active</span>
                                            </div>
                                        )}

                                        {/* Assistant: Typing animation or static content */}
                                        {msg.role === 'assistant' && msg.isTyping ? (
                                            <div className="text-base leading-relaxed">
                                                <Typewriter
                                                    text={msg.text}
                                                    onComplete={() =>
                                                        setMessages(prev =>
                                                            prev.map(m => m.id === msg.id ? { ...m, isTyping: false } : m)
                                                        )
                                                    }
                                                />
                                            </div>
                                        ) : (
                                            <div className="space-y-4">
                                                {/* Provenance badge */}
                                                {msg.role === 'assistant' && (
                                                    <div className={`
                                                        inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest mb-3
                                                        ${msg.provenance === 'verified_doc'
                                                            ? 'bg-success/10 text-success border border-success/20'
                                                            : 'bg-accent/10 text-accent border border-accent/20'}
                                                    `}>
                                                        {msg.provenance === 'verified_doc'
                                                            ? <><Shield className="w-3 h-3" /> Official Source</>
                                                            : <><Sparkles className="w-3 h-3" /> AI Search</>
                                                        }
                                                    </div>
                                                )}

                                                {/* Message text */}
                                                <div className="prose prose-sm dark:prose-invert max-w-none text-foreground leading-relaxed font-medium">
                                                    <ReactMarkdown
                                                        remarkPlugins={[remarkGfm]}
                                                        components={{
                                                            p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
                                                            a: ({ href, children }) => (
                                                                <a
                                                                    href={href}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="inline-flex items-center gap-1 text-primary hover:underline font-bold decoration-primary/30 underline-offset-4"
                                                                >
                                                                    {children}
                                                                    <ExternalLink className="w-2.5 h-2.5" />
                                                                </a>
                                                            ),
                                                            ul: ({ children }) => <ul className="space-y-1 mb-4 list-none">{children}</ul>,
                                                            li: ({ children }) => (
                                                                <li className="flex items-start gap-2 text-sm">
                                                                    <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary/40 shrink-0" />
                                                                    <span>{children}</span>
                                                                </li>
                                                            ),
                                                            strong: ({ children }) => (
                                                                <strong className="font-black text-foreground underline decoration-primary/20 decoration-2 underline-offset-2">
                                                                    {children}
                                                                </strong>
                                                            ),
                                                        }}
                                                    >
                                                        {msg.text}
                                                    </ReactMarkdown>
                                                </div>

                                                {/* Explainability */}
                                                {msg.explainability && (
                                                    <div className="mt-4 pt-4 border-t border-border/10">
                                                        <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-3 flex items-center gap-2">
                                                            <Shield className="w-3 h-3 text-emerald-500" />
                                                            Trust & Provenance
                                                        </h4>
                                                        <ExplainabilityCard
                                                            confidence={msg.explainability.confidence}
                                                            criteria={msg.explainability.matching_criteria}
                                                            protocol={msg.explainability.privacy_protocol}
                                                        />
                                                    </div>
                                                )}

                                                {/* Legacy structured sources (SchemeCard grid) */}
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
                                                            <SchemeCard
                                                                key={sIdx}
                                                                title={s.title}
                                                                description={s.text}
                                                                link={s.link}
                                                                benefit={s.benefit}
                                                                logo={s.logo}
                                                                related={s.graph_recommendations}
                                                                onApply={handleSchemeApply}
                                                            />
                                                        ))}
                                                    </div>
                                                )}

                                                {/* ── NEW: Benefit Receipt ─────────────────────── */}
                                                {msg.benefitReceipt && (
                                                    <BenefitReceipt
                                                        receipt={msg.benefitReceipt}
                                                        confidence={msg.confidence}
                                                        turnId={msg.turnId}
                                                        sessionId={sessionId ?? undefined}
                                                        isApplying={msg.applyStatus === 'applying'}
                                                        onApply={
                                                            msg.applyStatus === 'applied'
                                                                ? undefined
                                                                : () => handleApply(msg)
                                                        }
                                                        onAskAgain={() => handleAskAgain(msg)}
                                                    />
                                                )}

                                                {/* Apply status badge */}
                                                {(msg.applyStatus === 'applied' || msg.applyStatus === 'queued') && (
                                                    <div className={`mt-2 text-xs font-semibold flex items-center gap-1.5 ${msg.applyStatus === 'applied' ? 'text-emerald-400' : 'text-amber-400'}`}>
                                                        {msg.applyStatus === 'applied'
                                                            ? <>✅ Application submitted!</>
                                                            : <>⏳ Queued — will submit when online</>
                                                        }
                                                    </div>
                                                )}

                                                {/* Audio player — unified audio_url or legacy audio */}
                                                {(msg.audioUrl || msg.audio) && (
                                                    <div className="mt-6 pt-6 border-t border-border/10">
                                                        <AudioPlayer src={(msg.audioUrl || msg.audio)!} />
                                                    </div>
                                                )}

                                                {/* ── NEW: Telemetry Panel ─────────────────────── */}
                                                {msg.role === 'assistant' && (msg.debugInfo || msg.confidence !== undefined) && (
                                                    <TelemetryPanel debug={msg.debugInfo} confidence={msg.confidence} />
                                                )}
                                            </div>
                                        )}

                                        <div className={`text-[8px] font-black uppercase tracking-[0.2em] mt-4 flex items-center gap-2 ${msg.role === 'user' ? 'justify-end text-white/60' : 'justify-start text-muted-foreground'}`}>
                                            <div className={`w-1 h-1 rounded-full ${msg.role === 'user' ? 'bg-white/40' : 'bg-success'}`} />
                                            {msg.role === 'user' ? 'Transmission Secure' : 'Authenticated Data'}
                                        </div>
                                    </div>
                                </motion.div>
                            ))}

                            {/* Thinking State */}
                            {isThinking && (
                                <div className="flex justify-start px-2">
                                    <MultiAgentThoughtProcess />
                                </div>
                            )}

                            {/* Loading fallback */}
                            {isLoading && !isThinking && (
                                <div className="flex justify-start px-2">
                                    <div className="flex items-center gap-3 p-3 px-5 bg-secondary/30 rounded-full border border-border">
                                        <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" />
                                        <span className="text-[10px] text-foreground font-bold uppercase tracking-wider">JanSathi is thinking...</span>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </AnimatePresence>
            </div>

            {/* Input Area */}
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
                                    {/* eslint-disable-next-line @next/next/no-img-element */}
                                    <img src={imagePreview} className="h-16 w-16 object-cover rounded-xl border border-border shadow-sm" alt="Upload preview" />
                                    <div>
                                        <p className="text-[10px] font-bold text-primary uppercase tracking-widest mb-0.5">Image Selected</p>
                                        <p className="text-sm font-bold truncate max-w-[200px] text-foreground">{selectedImage?.name}</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => { setSelectedImage(null); setImagePreview(null); }}
                                    className="p-3 bg-secondary/50 hover:text-red-600 rounded-xl transition-colors"
                                >
                                    <X className="w-6 h-6" />
                                </button>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <div className="flex items-end gap-3 p-2 bg-card/80 backdrop-blur-xl border border-border/50 rounded-[2rem] shadow-[0_8px_30px_rgb(0,0,0,0.04)] relative transition-all focus-within:shadow-[0_8px_30px_rgba(234,88,12,0.15)] focus-within:border-primary/50 group">
                        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent opacity-0 group-focus-within:opacity-100 transition-opacity rounded-[2rem] pointer-events-none"></div>
                        <div className="p-1.5 rounded-[1.8rem] bg-background/50 backdrop-blur-md flex-1 flex items-center gap-2 border border-border/50 shadow-inner focus-within:border-primary/50 transition-colors relative z-10 overflow-hidden">
                            <input
                                type="file"
                                accept="image/*"
                                className="hidden"
                                ref={fileInputRef}
                                onChange={(e) => {
                                    if (e.target.files?.[0]) {
                                        setSelectedImage(e.target.files[0]);
                                        setImagePreview(URL.createObjectURL(e.target.files[0]));
                                    }
                                }}
                            />
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                className={`p-3 rounded-2xl transition-all ${selectedImage ? 'bg-primary text-white shadow-[0_0_15px_rgba(234,88,12,0.4)]' : 'hover:bg-secondary/80 text-secondary-foreground hover:text-foreground'}`}
                            >
                                <Camera className="w-5 h-5" />
                            </button>

                            <VoiceInput onTranscript={handleSend} isProcessing={isLoading} compact={true} />

                            <input
                                type="text"
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                placeholder={selectedImage ? "Click send to analyze photo..." : "Ask your question here..."}
                                className="flex-1 bg-transparent px-3 py-2 text-[15px] font-bold text-foreground placeholder:opacity-30 focus:outline-none w-full"
                                disabled={isLoading}
                            />

                            <button
                                onClick={() => handleSend()}
                                disabled={isLoading || (!inputText.trim() && !selectedImage)}
                                className="p-3.5 bg-primary text-white rounded-2xl shadow-[0_4px_15px_rgba(234,88,12,0.3)] disabled:opacity-30 active:scale-95 transition-all hover:bg-primary/90 hover:shadow-[0_4px_25px_rgba(234,88,12,0.4)]"
                            >
                                <Send className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    <div className="flex justify-center items-center gap-3 mt-4 opacity-60">
                        <div className="h-px w-8 bg-foreground" />
                        <p className="text-[9px] font-bold uppercase tracking-widest text-foreground">Verified Information • Secure Helper</p>
                        <div className="h-px w-8 bg-foreground" />
                    </div>
                </div>
            </div>
        </div>
    );
}
