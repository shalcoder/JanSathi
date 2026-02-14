'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';

interface VoiceInputProps {
    onTranscript: (text: string) => void;
    isProcessing: boolean;
    compact?: boolean;
}

export default function VoiceInput({ onTranscript, isProcessing, compact = false }: VoiceInputProps) {
    const [isListening, setIsListening] = useState(false);
    const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);
    const [error, setError] = useState<string | null>(null);

    const onTranscriptRef = React.useRef(onTranscript);

    useEffect(() => {
        onTranscriptRef.current = onTranscript;
    }, [onTranscript]);

    useEffect(() => {
        if (typeof window !== 'undefined') {
            const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
            if (SpeechRecognitionAPI) {
                const recognitionInstance = new SpeechRecognitionAPI();
                recognitionInstance.continuous = false;
                recognitionInstance.interimResults = false;
                recognitionInstance.lang = 'hi-IN'; // Defaulting to Hindi/India mixed

                recognitionInstance.onresult = (event: SpeechRecognitionEvent) => {
                    const transcript = event.results[0][0].transcript;
                    console.log('Transcript:', transcript);
                    onTranscriptRef.current(transcript);
                    setIsListening(false);
                };

                recognitionInstance.onerror = (event: SpeechRecognitionErrorEvent) => {
                    if (event.error === 'no-speech') {
                        console.warn('Voice input: No speech detected.');
                        setIsListening(false);
                        return; // Don't show error for timeout
                    }
                    console.error('Speech recognition error', event.error);
                    setError('Error: ' + event.error);
                    setIsListening(false);
                };

                recognitionInstance.onend = () => {
                    setIsListening(false);
                };

                setRecognition(recognitionInstance);

                return () => {
                    recognitionInstance.abort();
                };
            } else {
                setError('Voice input not supported in this browser.');
            }
        }
    }, []);

    const toggleListening = useCallback(() => {
        if (!recognition) return;

        if (isListening) {
            recognition.stop();
        } else {
            setError(null);
            try {
                recognition.start();
                setIsListening(true);
            } catch (e) {
                console.error("Failed to start recognition", e);
            }
        }
    }, [isListening, recognition]);

    if (error && !recognition && !compact) {
        return <div className="text-red-500 text-xs">{error}</div>
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
        <div className="flex flex-col items-center gap-2">
            <button
                onClick={toggleListening}
                disabled={isProcessing || !recognition}
                className={`
          relative flex items-center justify-center w-16 h-16 rounded-full transition-all duration-300
          ${isListening
                        ? 'bg-red-500 shadow-[0_0_20px_rgba(239,68,68,0.5)] scale-110'
                        : 'bg-primary hover:bg-blue-700 shadow-lg'}
          ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
                aria-label={isListening ? "Stop listening" : "Start listening"}
            >
                {isProcessing ? (
                    <Loader2 className="w-8 h-8 text-white animate-spin" />
                ) : isListening ? (
                    <MicOff className="w-8 h-8 text-white" />
                ) : (
                    <Mic className="w-8 h-8 text-white" />
                )}

                {/* Pulsing Ring Effect */}
                {isListening && (
                    <span className="absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75 animate-ping"></span>
                )}
            </button>

            <div className="h-6 flex items-center justify-center gap-1">
                {isListening ? (
                    <>
                        <div className="w-1 h-3 bg-red-400 rounded-full animate-[bounce_1s_infinite_100ms]"></div>
                        <div className="w-1 h-5 bg-red-500 rounded-full animate-[bounce_1s_infinite_200ms]"></div>
                        <div className="w-1 h-4 bg-red-400 rounded-full animate-[bounce_1s_infinite_300ms]"></div>
                        <div className="w-1 h-6 bg-red-500 rounded-full animate-[bounce_1s_infinite_150ms]"></div>
                        <div className="w-1 h-3 bg-red-400 rounded-full animate-[bounce_1s_infinite_250ms]"></div>
                    </>
                ) : (
                    <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
                        {error ? error : 'Tap to Speak'}
                    </p>
                )}
            </div>
        </div>
    );
}

// Type definitions for Web Speech API
declare global {
    interface Window {
        SpeechRecognition: any;
        webkitSpeechRecognition: any;
    }

    // Basic type placeholders to satisfy TS
    interface SpeechRecognition {
        continuous: boolean;
        interimResults: boolean;
        lang: string;
        start(): void;
        stop(): void;
        onresult: (event: SpeechRecognitionEvent) => void;
        onerror: (event: SpeechRecognitionErrorEvent) => void;
        onend: () => void;
    }

    interface SpeechRecognitionEvent {
        results: {
            [index: number]: {
                [index: number]: {
                    transcript: string;
                };
            };
        };
    }

    interface SpeechRecognitionErrorEvent {
        error: string;
    }
}
