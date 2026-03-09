'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface VoiceInputProps {
    onTranscript: (text: string) => void;
    isProcessing: boolean;
    compact?: boolean;
    language?: string;
}

interface BrowserSpeechRecognitionAlternative {
    transcript: string;
    confidence: number;
}

interface BrowserSpeechRecognitionResult {
    isFinal: boolean;
    length: number;
    [index: number]: BrowserSpeechRecognitionAlternative;
}

interface BrowserSpeechRecognitionEvent {
    results: {
        length: number;
        [index: number]: BrowserSpeechRecognitionResult;
    };
}

interface BrowserSpeechRecognitionErrorEvent {
    error: string;
}

interface BrowserSpeechRecognition {
    continuous: boolean;
    interimResults: boolean;
    lang: string;
    start(): void;
    stop(): void;
    abort(): void;
    onresult: (event: BrowserSpeechRecognitionEvent) => void;
    onerror: (event: BrowserSpeechRecognitionErrorEvent) => void;
    onend: () => void;
}

const localeMap: Record<string, string> = {
    en: 'en-IN',
    hi: 'hi-IN',
    ta: 'ta-IN',
    te: 'te-IN',
    kn: 'kn-IN',
    ml: 'ml-IN',
    mr: 'mr-IN',
    bn: 'bn-IN',
    gu: 'gu-IN',
    pa: 'pa-IN',
    or: 'or-IN',
    as: 'as-IN',
};

const WAVEFORM_BARS = 12;

export default function VoiceInput({ onTranscript, isProcessing, compact = false, language = 'hi' }: VoiceInputProps) {
    const [isListening, setIsListening] = useState(false);
    const [recognition, setRecognition] = useState<BrowserSpeechRecognition | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [interimText, setInterimText] = useState('');

    const onTranscriptRef = React.useRef(onTranscript);

    useEffect(() => {
        onTranscriptRef.current = onTranscript;
    }, [onTranscript]);

    useEffect(() => {
        if (typeof window !== 'undefined') {
            const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognitionAPI) {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                const recognitionInstance = new (SpeechRecognitionAPI as any)();
                recognitionInstance.continuous = false;
                recognitionInstance.interimResults = true;
                recognitionInstance.lang = localeMap[language] || 'hi-IN';

                recognitionInstance.onresult = (event: BrowserSpeechRecognitionEvent) => {
                    const result = event.results[event.results.length - 1];
                    const transcript = result[0].transcript;
                    if (result.isFinal) {
                        setInterimText('');
                        onTranscriptRef.current(transcript);
                        setIsListening(false);
                    } else {
                        setInterimText(transcript);
                    }
                };

                recognitionInstance.onerror = (event: BrowserSpeechRecognitionErrorEvent) => {
                    if (event.error === 'no-speech') {
                        setIsListening(false);
                        setInterimText('');
                        return;
                    }
                    setError('Error: ' + event.error);
                    setIsListening(false);
                    setInterimText('');
                };

                recognitionInstance.onend = () => {
                    setIsListening(false);
                    setInterimText('');
                };

                setTimeout(() => setRecognition(recognitionInstance), 0);
                return () => { recognitionInstance.abort(); };
            } else {
                setTimeout(() => setError('Voice input not supported in this browser.'), 0);
            }
        }
    }, [language]);

    const toggleListening = useCallback(() => {
        if (!recognition) return;
        if (isListening) {
            recognition.stop();
        } else {
            setError(null);
            setInterimText('');
            try {
                recognition.start();
                setIsListening(true);
            } catch (e) {
                console.error("Failed to start recognition", e);
            }
        }
    }, [isListening, recognition]);

    if (error && !recognition && !compact) {
        return <div className="text-red-500 text-xs">{error}</div>;
    }

    if (compact) {
        return (
            <button
                onClick={toggleListening}
                disabled={isProcessing || !recognition}
                className={`
                    p-4 rounded-[1.5rem] transition-all relative overflow-hidden
                    ${isListening
                        ? 'bg-red-500 text-white shadow-[0_0_15px_rgba(239,68,68,0.5)]'
                        : 'hover:bg-white/10 text-slate-400 hover:text-white'}
                    ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
                `}
                title={error || (isListening ? "Stop listening" : "Start voice input")}
            >
                {isProcessing ? (
                    <Loader2 className="w-6 h-6 animate-spin" />
                ) : isListening ? (
                    <MicOff className="w-6 h-6 animate-pulse" />
                ) : (
                    <Mic className="w-6 h-6" />
                )}
                {isListening && (
                    <span className="absolute inset-0 bg-white/20 animate-pulse rounded-[1.5rem]"></span>
                )}
            </button>
        );
    }

    return (
        <div className="flex flex-col items-center gap-3">
            {/* Main mic button */}
            <div className="relative">
                <button
                    onClick={toggleListening}
                    disabled={isProcessing || !recognition}
                    className={`
                        relative flex items-center justify-center w-20 h-20 rounded-full transition-all duration-300
                        ${isListening
                            ? 'bg-red-500 shadow-[0_0_30px_rgba(239,68,68,0.6)] scale-110'
                            : 'bg-primary hover:bg-blue-700 shadow-lg hover:shadow-xl hover:scale-105'}
                        ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                    `}
                    aria-label={isListening ? "Stop listening" : "Start listening"}
                >
                    {isProcessing ? (
                        <Loader2 className="w-9 h-9 text-white animate-spin" />
                    ) : isListening ? (
                        <MicOff className="w-9 h-9 text-white" />
                    ) : (
                        <Mic className="w-9 h-9 text-white" />
                    )}
                    {/* Pulsing ring when listening */}
                    {isListening && (
                        <>
                            <span className="absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-40 animate-ping" />
                            <span className="absolute inline-flex h-[130%] w-[130%] rounded-full bg-red-400 opacity-20 animate-ping [animation-delay:300ms]" />
                        </>
                    )}
                </button>
            </div>

            {/* Waveform bars */}
            <div className="h-8 flex items-center justify-center gap-[3px]">
                <AnimatePresence mode="wait">
                    {isListening ? (
                        <motion.div
                            key="waveform"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex items-center gap-[3px]"
                        >
                            {Array.from({ length: WAVEFORM_BARS }).map((_, i) => (
                                <motion.div
                                    key={i}
                                    className="w-1 bg-red-500 rounded-full"
                                    animate={{ height: ['4px', `${8 + Math.random() * 20}px`, '4px'] }}
                                    transition={{
                                        duration: 0.5 + Math.random() * 0.3,
                                        repeat: Infinity,
                                        delay: i * 0.05,
                                        ease: 'easeInOut',
                                    }}
                                />
                            ))}
                        </motion.div>
                    ) : (
                        <motion.p
                            key="label"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="text-sm font-medium text-slate-600 dark:text-slate-300"
                        >
                            {isProcessing ? 'Processing…' : error ? error : 'Tap to Speak'}
                        </motion.p>
                    )}
                </AnimatePresence>
            </div>

            {/* Interim transcript preview */}
            <AnimatePresence>
                {interimText && (
                    <motion.div
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 4 }}
                        className="max-w-[260px] text-center px-3 py-2 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-foreground/80 font-medium italic"
                    >
                        &ldquo;{interimText}&rdquo;
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

// Type definitions for Web Speech API
declare global {
    interface Window {
        SpeechRecognition?: {
            new (): BrowserSpeechRecognition;
        };
        webkitSpeechRecognition?: {
            new (): BrowserSpeechRecognition;
        };
    }
}
