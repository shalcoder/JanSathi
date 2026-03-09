'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Camera, X, Sparkles, Shield, ExternalLink,    Search,
    Globe,
    ShieldCheck,
    Activity,
    CheckCircle2,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import VoiceInput from './VoiceInput';
import AudioPlayer from './AudioPlayer';
import BenefitReceipt from './BenefitReceipt';
import SlotCollectionProgress from './SlotCollectionProgress';
import ApplicationSuccessModal from './ApplicationSuccessModal';
import { LifeEventWorkflow, type LifeEventData } from './LifeEventWorkflow';
import TelemetryPanel from './TelemetryPanel';
import SchemeCard from './SchemeCard';
import { useSession } from '@/hooks/useSession';
import DocumentScorecard from './DocumentScorecard';
import ExplainabilityCard from './ExplainabilityCard';
import MultiAgentThoughtProcess from './MultiAgentThoughtProcess';
import { useAuth } from '@/hooks/useAuth';
import { useI18n, type Language } from '@/context/i18n';
import { SUPPORTED_LANGUAGES } from '@/lib/languages';
import {
    sendUnifiedQuery,
    analyzeImage,
    applyForBenefit,
    getUserProfile,
    type UnifiedQueryResponse,
    type BenefitReceipt as BenefitReceiptType,
    type Thought,
    type Citation,
} from '@/services/api';
import { enqueue, registerOnlineFlush, type QueuedAction } from '@/services/offlineQueue';

// ─── Constants ────────────────────────────────────────────────────────────────

// ─── Typewriter ───────────────────────────────────────────────────────────────

const Typewriter = ({ text = '', onComplete }: { text: string; onComplete?: () => void }) => {
    const [displayedText, setDisplayedText] = useState('');
    const index = useRef(0);
    const onCompleteRef = useRef(onComplete);

    useEffect(() => { onCompleteRef.current = onComplete; }, [onComplete]);

    useEffect(() => {
        index.current = 0;
        const safeText = text || '';
        const intervalId = setInterval(() => {
            index.current += 3;
            if (index.current > safeText.length) index.current = safeText.length;
            setDisplayedText(safeText.slice(0, index.current));
            if (index.current >= safeText.length) {
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
    lifeEvent?: LifeEventData;
    benefitReceipt?: BenefitReceiptType;
    confidence?: number;
    turnId?: string;
    debugInfo?: UnifiedQueryResponse['debug'];
    citations?: Citation[];
    applyStatus?: 'idle' | 'applying' | 'applied' | 'queued';
    // Slot-filling fields from agentic pipeline
    slots?: Record<string, string | number | boolean>;
    slotsComplete?: boolean;
    schemeName?: string;
};

const SUGGESTIONS = [
    { title: "PM Awas Yojana", desc: "Housing assistance eligibility", style: "bento-1x1" },
    { title: "E-Shram Registry", desc: "Unorganized worker benefits", style: "bento-1x1" },
    { title: "PM-Kisan Status", desc: "Installment and status check", style: "bento-1x1" },
    { title: "Ration Card", desc: "Application and renewal support", style: "bento-1x1" }
];

const SESSIONS_KEY = 'jansathi_chat_sessions';

// ─── Citations & Thoughts ─────────────────────────────────────────────────────

const CitationsList = ({ citations }: { citations: Citation[] }) => {
    if (!citations?.length) return null;
    return (
        <div className="mt-4 pt-4 border-t border-border/10">
            <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-3 flex items-center gap-2">
                <ExternalLink className="w-3 h-3 text-primary" />
                Verified Citations
            </h4>
            <div className="flex flex-wrap gap-2">
                {citations.map((c, idx) => (
                    <a
                        key={idx}
                        href={c.sources[0]}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-secondary/50 border border-border/50 text-[11px] font-bold text-foreground hover:bg-secondary transition-colors"
                        title={c.text}
                    >
                        Source {idx + 1}
                        <ExternalLink className="w-2.5 h-2.5 opacity-50" />
                    </a>
                ))}
            </div>
        </div>
    );
};

const ThoughtPanel = ({ thoughts }: { thoughts: Thought[] }) => {
    const [isOpen, setIsOpen] = useState(false);
    if (!thoughts?.length) return null;

    return (
        <div className="mt-4">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent/5 border border-accent/20 text-[10px] font-black uppercase tracking-widest text-accent hover:bg-accent/10 transition-colors"
            >
                <Sparkles className="w-3 h-3" />
                {isOpen ? 'Hide Process Details' : 'View Process Details'}
            </button>
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                    >
                        <div className="mt-3 p-4 rounded-xl bg-accent/[0.03] border border-accent/10 space-y-3">
                            {thoughts.map((t, idx) => (
                                <div key={idx} className="flex gap-3 text-[11px] leading-relaxed">
                                    <div className="mt-1 shrink-0">
                                        {t.type === 'rationale' && <Sparkles className="w-3 h-3 text-amber-500" />}
                                        {t.type === 'tool_call' && <CheckCircle2 className="w-3 h-3 text-primary" />}
                                        {t.type === 'observation' && <Shield className="w-3 h-3 text-emerald-500" />}
                                    </div>
                                    <div className="space-y-1">
                                        <div className="font-black uppercase tracking-widest text-[9px] opacity-40">
                                            {t.type.replace('_', ' ')}
                                        </div>
                                        <div className="text-foreground/80 font-medium italic">
                                            {t.type === 'tool_call' ? `Executing: ${t.tool}` : t.text}
                                        </div>
                                        {t.input && (
                                            <div className="px-2 py-1 rounded bg-background/50 border border-border/20 font-mono text-[9px] break-all opacity-60">
                                                {t.input}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

const TaskWorkflow = ({ active }: { active: boolean }) => {
    const [step, setStep] = useState(0);
    const steps = [
        { label: 'Intent Classification', icon: Search },
        { label: 'Kendra Retrieval', icon: Globe },
        { label: 'Rules Evaluation', icon: ShieldCheck },
        { label: 'Risk Assessment', icon: Activity },
        { label: 'Synthesis', icon: Sparkles }
    ];

    useEffect(() => {
        if (!active) return;
        const interval = setInterval(() => {
            setStep(s => (s < steps.length - 1 ? s + 1 : s));
        }, 1500);
        return () => clearInterval(interval);
    }, [active, steps.length]);

    if (!active) return null;

    return (
        <div className="mt-4 p-4 rounded-2xl bg-zinc-900/60 dark:bg-zinc-800/60 border border-zinc-700/50 space-y-4">
            <div className="flex items-center justify-between">
                <span className="text-[10px] font-black uppercase tracking-widest text-zinc-400">Processing Status</span>
                <span className="text-[10px] font-mono text-zinc-500">{Math.round(((step + 1) / steps.length) * 100)}%</span>
            </div>
            <div className="flex gap-1">
                {steps.map((s, idx) => (
                    <div
                        key={idx}
                        className={`h-1.5 flex-1 rounded-full transition-all duration-500 ${idx <= step ? 'bg-primary' : 'bg-zinc-700'}`}
                    />
                ))}
            </div>
            <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-zinc-700/80 flex items-center justify-center animate-pulse">
                    {React.createElement(steps[step].icon, { className: "w-4 h-4 text-primary" })}
                </div>
                <div>
                    <div className="text-sm font-bold text-zinc-200">{steps[step].label}</div>
                    <div className="text-[11px] text-zinc-400">Analyzing your request...</div>
                </div>
            </div>
        </div>
    );
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function ChatInterface() {
    const { user } = useAuth();
    const { language, setLanguage } = useI18n();
    const { sessionId, token, resetSession } = useSession();
    const [messages, setMessages] = useState<Message[]>([]);
    const [localSessionId, setLocalSessionId] = useState<string | null>(null);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isThinking, setIsThinking] = useState(false);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [userProfile, setUserProfile] = useState<Record<string, unknown> | null>(null);
    const [appModal, setAppModal] = useState<{
        caseId: string;
        schemeName?: string;
        smsSent?: boolean;
    } | null>(null);

    // Fetch user profile once token is available so it can be passed as context to every query
    useEffect(() => {
        if (!token) return;
        getUserProfile(token).then(res => {
            if (res?.data) setUserProfile(res.data as Record<string, unknown>);
        }).catch(() => {/* non-fatal */});
    }, [token]);

    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Sync from settings if needed, but context is primary
    // useEffect(() => { setLanguage(settings.language); }, [settings.language]);

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

    const hasStaleToolParamError = (thoughts?: Thought[]) => {
        if (!thoughts?.length) return false;
        return thoughts.some(
            (t) => t.type === 'observation' && (t.text || '').includes('Invalid parameters for retrieve_knowledge')
        );
    };

    // ── Main send handler ──────────────────────────────────────────────────────

    const handleSend = async (text: string = inputText) => {
        if ((!text.trim() && !selectedImage) || isLoading) return;

        const activeSid = localSessionId || sessionId || Date.now().toString();
        
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

        try {
            if (selectedImage) {
                // Image analysis (legacy endpoint kept)
                const data = await analyzeImage(selectedImage, language);
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
                let response = await sendUnifiedQuery(
                    {
                        session_id: activeSid,
                        channel: 'web',
                        input: { text },
                        metadata: {
                            lang: language,
                            user_id: user?.id || 'anonymous',
                            ...(userProfile ? { user_profile: userProfile } : {}),
                        }
                    },
                    token ?? undefined,
                    activeSid
                );

                // Auto-heal old/sticky Bedrock session traces by retrying once on a fresh session.
                if (hasStaleToolParamError(response.debug?.thoughts)) {
                    const freshSid = `local-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
                    setLocalSessionId(freshSid);
                    sessionStorage.setItem('current_jansathi_session', freshSid);
                    resetSession();

                    response = await sendUnifiedQuery(
                        {
                            session_id: freshSid,
                            channel: 'web',
                            input: { text },
                            metadata: {
                                lang: language,
                                user_id: user?.id || 'anonymous',
                                ...(userProfile ? { user_profile: userProfile } : {}),
                            }
                        },
                        token ?? undefined,
                        freshSid
                    );
                }

                const aiMsg: Message = {
                    id: 'ai_' + Date.now(),
                    role: 'assistant',
                    text: response.response_text,
                    audioUrl: response.audio_url,
                    lifeEvent: (response as any).life_event ?? undefined,
                    benefitReceipt: response.benefit_receipt,
                    confidence: response.confidence,
                    turnId: response.turn_id,
                    debugInfo: response.debug,
                    citations: response.citations,
                    timestamp: new Date(),
                    isTyping: true,
                    applyStatus: 'idle',
                    // Slot-filling fields
                    slots: response.slots && Object.keys(response.slots).length > 0 ? response.slots : undefined,
                    slotsComplete: response.slots_complete,
                    schemeName: response.scheme_hint || undefined,
                };
                setMessages(prev => {
                    const next = [...prev, aiMsg];
                    persistSession(activeSid, next);
                    return next;
                });
            }
        } catch (err) {
            console.error("Agentic query failed:", err);
            const _offlineReplies: Record<string, string> = {
                hi: '🙏 अभी सरकारी सर्वर से जुड़ने में समस्या है।\n\n'
                  + '📋 आधिकारिक जानकारी के लिए:\n'
                  + '• सभी योजनाएं: myscheme.gov.in\n'
                  + '• PM किसान: pmkisan.gov.in\n'
                  + '• आयुष्मान भारत: pmjay.gov.in\n'
                  + '• PM आवास: pmaymis.gov.in\n\n'
                  + 'कृपया कुछ देर बाद पुनः प्रयास करें।',
                ta: '🙏 இப்போது சேவையகத்துடன் இணைப்பில் சிக்கல்.\n📋 https://myscheme.gov.in இல் தகவல் காணலாம்.\nசிறிது நேரம் கழித்து முயற்சிக்கவும்.',
                te: '🙏 ప్రస్తుతం సర్వర్‌కు కనెక్ట్ సమస్య.\n📋 https://myscheme.gov.in లో సమాచారం చూడవచ్చు.\nమళ్లీ ప్రయత్నించండి.',
                kn: '🙏 ಈಗ ಸರ್ವರ್‌ಗೆ ಸಂಪರ್ಕ ಸಮಸ್ಯೆ.\n📋 https://myscheme.gov.in ನಲ್ಲಿ ಮಾಹಿತಿ ಲಭ್ಯ.\nಸ್ವಲ್ಪ ಸಮಯದ ನಂತರ ಪ್ರಯತ್ನಿಸಿ.',
                mr: '🙏 आत्ता सर्व्हरशी कनेक्ट होण्यात समस्या.\n📋 https://myscheme.gov.in वर माहिती मिळवा.\nकृपया थोड्या वेळाने पुन्हा प्रयत्न करा.',
                bn: '🙏 এখন সার্ভারের সাথে সংযোগ সমস্যা।\n📋 https://myscheme.gov.in-এ তথ্য পাওয়া যাবে।\nকিছুক্ষণ পরে আবার চেষ্টা করুন।',
                en: '🙏 Having trouble connecting to the government server right now.\n\n'
                  + '📋 Find official scheme information at:\n'
                  + '• All Schemes: myscheme.gov.in\n'
                  + '• PM-KISAN: pmkisan.gov.in\n'
                  + '• Ayushman Bharat: pmjay.gov.in\n\n'
                  + 'Please try again in a moment.',
            };
            const errMsg: Message = {
                id: 'err_' + Date.now(),
                role: 'assistant',
                text: _offlineReplies[language] ?? _offlineReplies['en'],
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
            const result = await applyForBenefit(
                { session_id: sessionId, turn_id: msg.turnId },
                token ?? undefined
            );
            setMessages(prev =>
                prev.map(m => m.id === msg.id ? { ...m, applyStatus: 'applied' as const } : m)
            );
            // Show success modal
            setAppModal({
                caseId: result.case_id || `CASE-${Date.now().toString(36).toUpperCase()}`,
                schemeName: msg.schemeName,
                smsSent: true,
            });
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

            {/* Native Language Toggle */}
            <div className="absolute top-4 left-4 sm:left-6 lg:left-8 z-50">
                <div className="relative">
                    <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value as Language)}
                        title="Select language"
                        aria-label="Select language"
                        className="appearance-none bg-background/60 backdrop-blur-xl border border-border/50 text-foreground text-xs font-bold rounded-xl px-4 py-2 pr-8 outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-sm hover:bg-secondary/40 transition-colors"
                    >
                        {SUPPORTED_LANGUAGES.map((lang) => (
                            <option key={lang.code} value={lang.code}>
                                {lang.native}
                            </option>
                        ))}
                    </select>
                </div>
            </div>



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
                                    Trusted Assistant
                                </div>
                                <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
                                    JanSathi Copilot <br />
                                    <span className="text-primary">Professional Benefit Guidance</span>
                                </h1>
                                <p className="text-sm text-secondary-foreground max-w-lg mx-auto font-medium leading-relaxed">
                                    Ask about government schemes, application status, or upload documents for review.
                                </p>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-8 max-w-4xl mx-auto px-2 pb-4">
                                    {SUGGESTIONS.map((s, i) => (
                                        <button
                                            key={i}
                                            onClick={() => handleSend(s.title)}
                                            className="bg-card border border-border/60 p-4 text-left rounded-2xl hover:border-primary/40 transition-all shadow-sm hover:shadow-md flex flex-col justify-center group relative overflow-hidden"
                                        >
                                            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-60 transition-opacity"></div>
                                            <div className="relative z-10">
                                                <p className="text-sm font-semibold text-foreground mb-1 group-hover:text-primary transition-colors">{s.title}</p>
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
                                                    <span className="text-[9px] font-bold uppercase tracking-wider text-muted-foreground">Session Active</span>
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
                                                            : <><Sparkles className="w-3 h-3" /> AI Assisted</>
                                                        }
                                                    </div>
                                                )}

                                                {/* Message text */}
                                                <div className="max-w-none text-foreground leading-relaxed font-medium text-sm sm:text-base">
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
                                                            ul: ({ children }) => <div className="space-y-1 mb-4">{children}</div>,
                                                            li: ({ children }) => (
                                                                <div className="flex items-start gap-2 text-sm">
                                                                    <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary/40 shrink-0" />
                                                                    <span>{children}</span>
                                                                </div>
                                                            ),
                                                            strong: ({ children }) => (
                                                                <strong className="font-black text-foreground underline decoration-primary/20 decoration-2 underline-offset-2">
                                                                    {children}
                                                                </strong>
                                                            ),
                                                        }}
                                                    >
                                                        {msg.text || (msg.isTyping ? "" : "Generating response...")}
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

                                                {/* ── Life Event Workflow ────────────────────────── */}
                                                {msg.lifeEvent?.detected && (
                                                    <LifeEventWorkflow data={msg.lifeEvent} />
                                                )}

                                                {/* ── NEW: Benefit Receipt ─────────────────────── */}
                                                {msg.benefitReceipt && (
                                                    <BenefitReceipt
                                                        receipt={msg.benefitReceipt}
                                                        confidence={msg.confidence}
                                                        schemeName={msg.schemeName}
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

                                                {/* ── Slot Collection Progress ─────────────────── */}
                                                {msg.slots && !msg.benefitReceipt && (
                                                    <SlotCollectionProgress
                                                        slots={msg.slots}
                                                        slotsComplete={msg.slotsComplete ?? false}
                                                        schemeName={msg.schemeName}
                                                    />
                                                )}

                                                {/* Helper suggestion for thinking state — only render inside assistant cards */}
                                                {msg.role === 'assistant' && isLoading && isThinking && !messages.some(m => m.isTyping && m.role === 'assistant') && (
                                                    <div className="max-w-[85%] sm:max-w-md">
                                                        <div className="flex gap-3">
                                                            <div className="w-8 h-8 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0">
                                                                <Activity className="w-4 h-4 text-primary animate-pulse" />
                                                            </div>
                                                            <div className="space-y-3 flex-1">
                                                                <div className="bg-secondary/30 rounded-2xl p-4 border border-border/50 animate-pulse">
                                                                    <div className="h-4 bg-foreground/10 rounded w-3/4 mb-2"></div>
                                                                    <div className="h-4 bg-foreground/10 rounded w-1/2"></div>
                                                                </div>
                                                                <TaskWorkflow active={isLoading} />
                                                            </div>
                                                        </div>
                                                    </div>
                                                )}

                                                {/* Apply status badge */}
                                                {(msg.applyStatus === 'applied' || msg.applyStatus === 'queued') && (
                                                    <div className={`mt-2 text-xs font-semibold flex items-center gap-1.5 ${msg.applyStatus === 'applied' ? 'text-emerald-400' : 'text-amber-400'}`}>
                                                        {msg.applyStatus === 'applied'
                                                            ? <>Application submitted successfully</>
                                                            : <>Request queued and will submit when online</>
                                                        }
                                                    </div>
                                                )}

                                                {/* Audio player — unified audio_url or legacy audio */}
                                                {(msg.audioUrl || msg.audio) && (
                                                    <div className="mt-6 pt-6 border-t border-border/10">
                                                        <AudioPlayer src={(msg.audioUrl || msg.audio)!} />
                                                    </div>
                                                )}

                                                {/* ── Bedrock Trace: Citations & Thoughts ─────── */}
                                                {msg.citations && (
                                                    <CitationsList citations={msg.citations} />
                                                )}
                                                {msg.debugInfo?.thoughts && (
                                                    <ThoughtPanel thoughts={msg.debugInfo.thoughts} />
                                                )}

                                                {/* ── NEW: Telemetry Panel ─────────────────────── */}
                                                {msg.role === 'assistant' && (msg.debugInfo || msg.confidence !== undefined) && (
                                                    <TelemetryPanel debug={msg.debugInfo} confidence={msg.confidence} />
                                                )}
                                            </div>
                                        )}

                                        <div className={`text-[8px] font-black uppercase tracking-[0.2em] mt-4 flex items-center gap-2 ${msg.role === 'user' ? 'justify-end text-white/60' : 'justify-start text-muted-foreground'}`}>
                                            <div className={`w-1 h-1 rounded-full ${msg.role === 'user' ? 'bg-white/40' : 'bg-success'}`} />
                                            {msg.role === 'user' ? 'Secure Input' : 'Verified Response'}
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
                                        <span className="text-[10px] text-foreground font-bold uppercase tracking-wider">Generating response...</span>
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
                                    aria-label="Remove selected image"
                                    title="Remove selected image"
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
                                title="Upload image"
                                aria-label="Upload image"
                                onChange={(e) => {
                                    if (e.target.files?.[0]) {
                                        setSelectedImage(e.target.files[0]);
                                        setImagePreview(URL.createObjectURL(e.target.files[0]));
                                    }
                                }}
                            />
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                aria-label="Upload image"
                                title="Upload image"
                                className={`p-3 rounded-2xl transition-all ${selectedImage ? 'bg-primary text-white shadow-[0_0_15px_rgba(234,88,12,0.4)]' : 'hover:bg-secondary/80 text-secondary-foreground hover:text-foreground'}`}
                            >
                                <Camera className="w-5 h-5" />
                            </button>

                            <VoiceInput onTranscript={handleSend} isProcessing={isLoading} compact={true} language={language} />

                            <input
                                type="text"
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                placeholder={selectedImage ? "Click Send to analyze the document..." : "Ask about eligibility, status, or documentation..."}
                                className="flex-1 bg-transparent px-3 py-2 text-[15px] font-bold text-foreground placeholder:opacity-30 focus:outline-none w-full"
                                disabled={isLoading}
                            />

                            <button
                                onClick={() => handleSend()}
                                disabled={isLoading || (!inputText.trim() && !selectedImage)}
                                aria-label="Send message"
                                title="Send message"
                                className="p-3.5 bg-primary text-white rounded-2xl shadow-[0_4px_15px_rgba(234,88,12,0.3)] disabled:opacity-30 active:scale-95 transition-all hover:bg-primary/90 hover:shadow-[0_4px_25px_rgba(234,88,12,0.4)]"
                            >
                                <Send className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    <div className="flex justify-center items-center gap-3 mt-4 opacity-60">
                        <div className="h-px w-8 bg-foreground" />
                        <p className="text-[9px] font-bold uppercase tracking-widest text-foreground">Verified Information • Privacy First</p>
                        <div className="h-px w-8 bg-foreground" />
                    </div>
                </div>
            </div>

            {/* Application Success Modal */}
            {appModal && (
                <ApplicationSuccessModal
                    caseId={appModal.caseId}
                    schemeName={appModal.schemeName}
                    smsSent={appModal.smsSent}
                    onClose={() => setAppModal(null)}
                />
            )}
        </div>
    );
}
