'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Phone, PhoneOff, Mic, MicOff, Hash, Globe, Volume2, Clock,
  ChevronRight, AlertCircle, Wifi, Brain, Zap, CheckCircle
} from 'lucide-react';
import SMSSimulator, { SMSMessage } from './SMSSimulator';
import TelemetryPanel, { TelemetryData } from './TelemetryPanel';
import { buildClient } from '@/services/api';
import { useSession } from '@/hooks/useSession';
import { useAuth } from '@/hooks/useAuth';

// ── Types ──────────────────────────────────────────────────────────────────────

type CallState = 'idle' | 'ringing' | 'active' | 'ended';

interface TranscriptEntry {
  id: string;
  role: 'user' | 'system';
  text: string;
  timestamp: string;
}

interface EmulatorResponse {
  response_text?: string;
  response?: string;
  audio_url?: string | null;
  agents_activated?: string[];
  workflow_stage?: string;
  slots?: Record<string, unknown>;
  rule_trace?: Array<{ rule: string; pass: boolean; citation?: string }>;
  artifact_generated?: { type: string; url?: string };
  sms_payload?: { body: string };
  telemetry?: TelemetryData & { agents_count?: number };
  is_terminal?: boolean;
}

// ── Sub-components ─────────────────────────────────────────────────────────────

// Agent pipeline definitions (must match backend agents_activated names)
type AgentStatus = {
  id: string;
  name: string;
  label: string;
  status: 'idle' | 'processing' | 'done';
};

const AGENT_DEFS: Omit<AgentStatus, 'status'>[] = [
  { id: 'intent',      name: 'IntentClassifier',     label: 'Intent Classifier'     },
  { id: 'knowledge',   name: 'KnowledgeRetriever',   label: 'Knowledge Retriever'   },
  { id: 'eligibility', name: 'EligibilityValidator', label: 'Eligibility Validator' },
  { id: 'risk',        name: 'RiskAssessor',          label: 'Risk Assessor'         },
  { id: 'response',    name: 'ResponseGenerator',    label: 'Response Generator'    },
  { id: 'scheme',      name: 'SchemeAdvisor',         label: 'Scheme Advisor'        },
  { id: 'document',    name: 'DocumentOrchestrator', label: 'Document Orchestrator' },
  { id: 'notify',      name: 'NotificationAgent',    label: 'Notification Agent'    },
  { id: 'hitl',        name: 'HITLRouter',            label: 'HITL Router'           },
];

function AgentPipeline({ agents, isProcessing }: { agents: AgentStatus[]; isProcessing: boolean }) {
  return (
    <div className="bg-card/60 backdrop-blur-xl border border-border/50 rounded-2xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <Brain className="w-4 h-4 text-primary" />
        <span className="text-[11px] font-bold text-secondary-foreground uppercase tracking-widest">
          9-Agent Pipeline
        </span>
        {isProcessing && (
          <div className="ml-auto flex items-center gap-1">
            <motion.div animate={{ scale: [1, 1.4, 1] }} transition={{ repeat: Infinity, duration: 0.7 }}>
              <div className="w-1.5 h-1.5 rounded-full bg-primary" />
            </motion.div>
            <span className="text-[9px] font-bold text-primary">LIVE</span>
          </div>
        )}
      </div>
      <div className="space-y-1">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg transition-all duration-300 ${
              agent.status === 'processing'
                ? 'bg-zinc-800/60 border border-zinc-600/40'
                : agent.status === 'done'
                ? 'bg-emerald-500/10 border border-emerald-500/20'
                : 'border border-transparent'
            }`}
          >
            {agent.status === 'processing' ? (
              <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}>
                <Zap className="w-3 h-3 text-primary" />
              </motion.div>
            ) : agent.status === 'done' ? (
              <CheckCircle className="w-3 h-3 text-emerald-400" />
            ) : (
              <div className="w-3 h-3 rounded-full border border-white/15" />
            )}
            <span
              className={`text-[10px] font-semibold transition-colors ${
                agent.status === 'processing'
                  ? 'text-primary'
                  : agent.status === 'done'
                  ? 'text-emerald-400'
                  : 'text-white/35'
              }`}
            >
              {agent.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

const DTMF_KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#'];

function DTMFKeypad({ onKey }: { onKey: (k: string) => void }) {
  return (
    <div className="grid grid-cols-3 gap-2">
      {DTMF_KEYS.map((k) => (
        <button
          key={k}
          onClick={() => onKey(k)}
          className="h-12 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-bold text-lg transition-all active:scale-95 shadow-sm"
        >
          {k}
        </button>
      ))}
    </div>
  );
}

function CallTimer({ active }: { active: boolean }) {
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    if (!active) { setSeconds(0); return; }
    const id = setInterval(() => setSeconds(s => s + 1), 1000);
    return () => clearInterval(id);
  }, [active]);
  const fmt = (n: number) => String(n).padStart(2, '0');
  return (
    <span className="font-mono text-sm text-white/60 tabular-nums">
      {fmt(Math.floor(seconds / 60))}:{fmt(seconds % 60)}
    </span>
  );
}

// ── SpeechRecognition type shim ──────────────────────────────────────────────
interface SpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: SpeechRecognitionResultList;
}
interface SpeechRecognitionInstance extends EventTarget {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  maxAlternatives: number;
  start(): void;
  stop(): void;
  abort(): void;
  onstart: (() => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
  onresult: ((e: SpeechRecognitionEvent) => void) | null;
}
interface WindowWithSpeech {
  SpeechRecognition?: new () => SpeechRecognitionInstance;
  webkitSpeechRecognition?: new () => SpeechRecognitionInstance;
}

// ── Main Component ─────────────────────────────────────────────────────────────

const LANGUAGES = [
  { code: 'hi-IN', label: 'हिंदी',  greeting: 'नमस्ते! मैं जन साथी हूँ। आपकी कैसे मदद कर सकता हूँ?' },
  { code: 'en-IN', label: 'English', greeting: 'Hello! I am JanSathi. How can I help you today?' },
  { code: 'ta-IN', label: 'தமிழ்',  greeting: 'வணக்கம்! நான் ஜன்சாதி. உங்களுக்கு எவ்வாறு உதவலாம்?' },
  { code: 'te-IN', label: 'తెలుగు', greeting: 'నమస్కారం! నేను జన్‌సాథి. మీకు ఎలా సహాయం చేయగలను?' },
  { code: 'kn-IN', label: 'ಕನ್ನಡ',  greeting: 'ನಮಸ್ಕಾರ! ನಾನು ಜನ್‌ಸಾಥಿ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?' },
  { code: 'mr-IN', label: 'मराठी',  greeting: 'नमस्कार! मी जनसाथी आहे. मी आपली कशी मदद करू?' },
  { code: 'bn-IN', label: 'বাংলা',  greeting: 'নমস্কার! আমি জনসাথী। আপনাকে কীভাবে সাহায্য করতে পারি?' },
];

export default function PhoneEmulatorPage() {
  const { sessionId, token } = useSession();
  const { user, loading: isLoaded } = useAuth();

  const [callState, setCallState] = useState<CallState>('idle');
  const [lang, setLang] = useState('hi-IN');
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [smsMessages, setSmsMessages] = useState<SMSMessage[]>([]);
  const [telemetry, setTelemetry] = useState<TelemetryData>({});
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [interim, setInterim] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [activeAgents, setActiveAgents] = useState<AgentStatus[]>(
    AGENT_DEFS.map(a => ({ ...a, status: 'idle' }))
  );

  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const agentTimersRef = useRef<number[]>([]);
  const transcriptEndRef = useRef<HTMLDivElement>(null);
  const activeRef = useRef(false);

  // API client ---------------------------------------------------------------
  const client = buildClient(token ?? undefined, sessionId ?? undefined);

  // Scroll transcript -------------------------------------------------------
  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript, interim]);

  // Send to backend ----------------------------------------------------------
  const sendToBackend = useCallback(async (text: string) => {
    const sid = sessionId || `emulator-${Date.now()}`;
    const userProfile = {
      name: user?.name,
      state: 'up',
      occupation: 'farmer',
      income_bracket: 'low',
    };

    // Animate all 9 agents through the pipeline with stagger
    agentTimersRef.current.forEach(t => clearTimeout(t));
    agentTimersRef.current = [];
    AGENT_DEFS.forEach(({ id }, idx) => {
      const t = setTimeout(() => {
        setActiveAgents(prev => prev.map(a => a.id === id ? { ...a, status: 'processing' } : a));
      }, idx * 180) as unknown as number;
      agentTimersRef.current.push(t);
    });

    try {
      const res = await client.post<EmulatorResponse>('/v1/ivr/voice', {
        session_id: sid,
        text,
        language: lang.split('-')[0],
        channel: 'web-ivr',
        user_profile: userProfile,
      }, { timeout: 10000 });
      const data = res.data;
      const responseText = data.response_text || data.response || 'मैं समझा नहीं। कृपया दोबारा बोलें।';

      // Stop animation; show which agents were actually activated
      agentTimersRef.current.forEach(t => clearTimeout(t));
      agentTimersRef.current = [];
      const activated = data.agents_activated ?? [];
      setActiveAgents(AGENT_DEFS.map(a => ({
        ...a,
        status: activated.includes(a.name) ? 'done' : 'idle',
      })));
      // Auto-reset to idle after 3 s
      const resetT = setTimeout(() => {
        setActiveAgents(AGENT_DEFS.map(a => ({ ...a, status: 'idle' })));
      }, 3000) as unknown as number;
      agentTimersRef.current.push(resetT);

      // Update telemetry
      setTelemetry({
        intent: data.telemetry?.intent,
        confidence: data.telemetry?.confidence,
        slots: data.slots ?? data.telemetry?.slots,
        rule_trace: data.rule_trace ?? data.telemetry?.rule_trace,
        workflow_stage: data.workflow_stage ?? data.telemetry?.workflow_stage,
        risk_score: data.telemetry?.risk_score,
        latency_ms: data.telemetry?.latency_ms,
        tokens_used: data.telemetry?.tokens_used,
      });

      // Add system transcript
      addTranscript('system', responseText);

      // Speak via Polly audio_url (real multilingual TTS) or browser TTS fallback
      speakText(responseText, data.audio_url ?? undefined);

      // SMS / artifact
      if (data.artifact_generated || data.sms_payload) {
        const smsBody = data.sms_payload?.body
          || `आपका आवेदन संसाधित हो गया है। आर्टिफैक्ट प्रकार: ${data.artifact_generated?.type ?? 'receipt'}`;
        const newSMS: SMSMessage = {
          id: `sms-${Date.now()}`,
          body: smsBody,
          timestamp: new Date().toLocaleTimeString(),
          receiptUrl: data.artifact_generated?.url,
          artifactType: data.artifact_generated?.type as SMSMessage['artifactType'],
        };
        setSmsMessages(prev => [newSMS, ...prev]);
      }

      if (data.is_terminal) {
        setTimeout(() => endCall(), 2000);
      }
    } catch (e) {
      console.error('[PhoneEmulator] Backend error:', e);
      agentTimersRef.current.forEach(t => clearTimeout(t));
      agentTimersRef.current = [];
      setActiveAgents(AGENT_DEFS.map(a => ({ ...a, status: 'idle' })));
      const _ivrOffline: Record<string, string> = {
        'hi-IN': 'अभी सरकारी सर्वर से जुड़ने में समस्या है। कृपया myscheme.gov.in पर जाएं या बाद में प्रयास करें।',
        'en-IN': 'Having trouble connecting to the server. Please visit myscheme.gov.in or try again shortly.',
        'ta-IN': 'சேவையகத்துடன் இணைப்பில் சிக்கல். myscheme.gov.in பார்க்கவும்.',
        'te-IN': 'సర్వర్ కనెక్షన్ సమస్య. myscheme.gov.in చూడండి లేదా మళ్లీ ప్రయత్నించండి.',
        'kn-IN': 'ಸರ್ವರ್ ಸಂಪರ್ಕ ಸಮಸ್ಯೆ. myscheme.gov.in ನೋಡಿ ಅಥವಾ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.',
        'mr-IN': 'सर्व्हरशी संपर्कात समस्या. myscheme.gov.in पहा किंवा नंतर प्रयत्न करा.',
        'bn-IN': 'সার্ভার সংযোগ সমস্যা। myscheme.gov.in দেখুন বা পরে চেষ্টা করুন।',
      };
      const fallback = _ivrOffline[lang] ?? _ivrOffline['en-IN'];
      addTranscript('system', fallback);
      speakText(fallback);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, token, lang, user]);

  // TTS -----------------------------------------------------------------------
  // Uses Polly presigned audio URL when available (real multilingual speech).
  // Falls back to browser SpeechSynthesis when no URL is provided.
  const speakText = (text: string, audioUrl?: string) => {
    if (typeof window === 'undefined') return;
    // Stop currently playing audio / TTS
    if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; }
    synthRef.current?.cancel();

    const onDone = () => {
      setIsSpeaking(false);
      if (activeRef.current) startListening();
    };

    if (audioUrl) {
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      setIsSpeaking(true);
      audio.onended = () => { audioRef.current = null; onDone(); };
      audio.onerror = () => { audioRef.current = null; setIsSpeaking(false); browserTTS(text, onDone); };
      audio.play().catch(() => { audioRef.current = null; setIsSpeaking(false); browserTTS(text, onDone); });
      return;
    }
    browserTTS(text, onDone);
  };

  const browserTTS = (text: string, onDone: () => void) => {
    synthRef.current = window.speechSynthesis;
    synthRef.current.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang = lang;
    utt.rate = 0.9;
    utt.onstart = () => setIsSpeaking(true);
    utt.onend = onDone;
    synthRef.current.speak(utt);
  };

  // STT -----------------------------------------------------------------------
  const startListening = useCallback(() => {
    if (!activeRef.current) return;
    const win = window as WindowWithSpeech;
    const SR = win.SpeechRecognition || win.webkitSpeechRecognition;
    if (!SR) { setError('Speech recognition not supported in this browser.'); return; }

    const rec: SpeechRecognitionInstance = new SR();
    rec.lang = lang;
    rec.interimResults = true;
    rec.continuous = false;
    rec.maxAlternatives = 1;
    recognitionRef.current = rec;

    rec.onstart = () => setIsListening(true);
    rec.onend = () => { setIsListening(false); setInterim(''); };
    rec.onerror = () => { setIsListening(false); setInterim(''); };

    rec.onresult = (e: SpeechRecognitionEvent) => {
      let interim_ = '';
      let final_ = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const t = e.results[i][0].transcript;
        if (e.results[i].isFinal) final_ += t;
        else interim_ += t;
      }
      setInterim(interim_);
      if (final_.trim()) {
        setInterim('');
        addTranscript('user', final_.trim());
        sendToBackend(final_.trim());
      }
    };

    rec.start();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang, sendToBackend]);

  // DTMF key press -----------------------------------------------------------
  const handleDTMF = (key: string) => {
    recognitionRef.current?.abort();
    addTranscript('user', `[DTMF: ${key}]`);
    sendToBackend(`DTMF:${key}`);
  };

  // Transcript helper --------------------------------------------------------
  const addTranscript = (role: 'user' | 'system', text: string) => {
    setTranscript(prev => [...prev, {
      id: `${role}-${Date.now()}`,
      role,
      text,
      timestamp: new Date().toLocaleTimeString(),
    }]);
  };

  // Call start/end -----------------------------------------------------------
  const startCall = async () => {
    setCallState('ringing');
    setTranscript([]);
    setSmsMessages([]);
    setTelemetry({});
    setActiveAgents(AGENT_DEFS.map(a => ({ ...a, status: 'idle' })));
    await new Promise(r => setTimeout(r, 1200));
    setCallState('active');
    activeRef.current = true;
    const greeting =
      LANGUAGES.find(l => l.code === lang)?.greeting ??
      'नमस्ते! मैं जन साथी हूँ। आपकी कैसे मदद कर सकता हूँ?';
    addTranscript('system', greeting);
    speakText(greeting);
  };

  const endCall = () => {
    activeRef.current = false;
    recognitionRef.current?.abort();
    synthRef.current?.cancel();
    if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; }
    agentTimersRef.current.forEach(t => clearTimeout(t));
    agentTimersRef.current = [];
    setIsListening(false);
    setIsSpeaking(false);
    setInterim('');
    setCallState('ended');
  };

  const resetEmulator = () => {
    setCallState('idle');
    setTranscript([]);
    setSmsMessages([]);
    setTelemetry({});
    setActiveAgents(AGENT_DEFS.map(a => ({ ...a, status: 'idle' })));
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 p-6 lg:p-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-foreground">Web Phone Emulator</h1>
          <p className="text-sm text-secondary-foreground font-medium mt-1">Real-time speech-to-speech civic automation</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20">
          <Wifi className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">JanSathi IVR</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
        {/* ── LEFT: Phone Emulator ── */}
        <div className="bg-[#0f0f0f] rounded-3xl border border-white/10 shadow-[0_20px_60px_rgba(0,0,0,0.5)] overflow-hidden flex flex-col">

          {/* Status bar */}
          <div className="flex items-center justify-between px-6 py-3 border-b border-white/5">
            <div className="flex items-center gap-2">
              <div className={`w-2.5 h-2.5 rounded-full ${callState === 'active' ? 'bg-emerald-400 animate-pulse' : callState === 'ringing' ? 'bg-amber-400 animate-pulse' : 'bg-white/30'}`} />
              <span className="text-[11px] font-bold text-white/50 uppercase tracking-widest">
                {callState === 'idle' ? 'Ready' : callState === 'ringing' ? 'Connecting...' : callState === 'active' ? 'In Call' : 'Call Ended'}
              </span>
            </div>
            <div className="flex items-center gap-3">
              {callState === 'active' && <CallTimer active />}
              {isListening && (
                <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1 }} className="flex items-center gap-1.5">
                  <Mic className="w-3.5 h-3.5 text-red-400" />
                  <span className="text-[10px] text-red-400 font-bold">Listening</span>
                </motion.div>
              )}
              {isSpeaking && (
                <motion.div animate={{ opacity: [1, 0.5, 1] }} transition={{ repeat: Infinity, duration: 0.8 }} className="flex items-center gap-1.5">
                  <Volume2 className="w-3.5 h-3.5 text-blue-400" />
                  <span className="text-[10px] text-blue-400 font-bold">Speaking</span>
                </motion.div>
              )}
            </div>
          </div>

          {/* Transcript */}
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3 min-h-[280px] max-h-[360px]">
            <AnimatePresence initial={false}>
              {transcript.map((entry) => (
                <motion.div
                  key={entry.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${entry.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm font-medium ${
                    entry.role === 'user'
                      ? 'bg-primary/90 text-white rounded-tr-sm'
                      : 'bg-white/8 text-white/85 border border-white/10 rounded-tl-sm'
                  }`}>
                    <p className="leading-relaxed">{entry.text}</p>
                    <p className="text-[9px] mt-1 opacity-40 font-mono">{entry.timestamp}</p>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            {interim && (
              <div className="flex justify-end">
                <div className="max-w-[80%] px-4 py-2.5 rounded-2xl bg-primary/40 text-white/70 border border-primary/30 text-sm italic">
                  {interim}...
                </div>
              </div>
            )}
            {callState === 'idle' && (
              <div className="flex flex-col items-center justify-center h-40 gap-3 text-white/30">
                <Phone className="w-10 h-10" />
                <p className="text-sm font-medium">Select language and press Call to begin</p>
              </div>
            )}
            <div ref={transcriptEndRef} />
          </div>

          {/* Controls */}
          <div className="px-5 py-4 border-t border-white/5 space-y-4">
            {error && (
              <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-red-500/15 border border-red-500/25 text-red-400 text-xs font-medium">
                <AlertCircle className="w-4 h-4 shrink-0" /> {error}
              </div>
            )}

            {/* Language Selector */}
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-white/40" />
              <div className="flex gap-1.5">
                {LANGUAGES.map(l => (
                  <button
                    key={l.code}
                    onClick={() => setLang(l.code)}
                    disabled={callState === 'active'}
                    className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${lang === l.code ? 'bg-primary text-white' : 'bg-white/5 text-white/50 hover:bg-white/10'}`}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
            </div>

            {/* DTMF + Call Button Row */}
            <div className="grid grid-cols-[1fr_auto] gap-4 items-end">
              <DTMFKeypad onKey={handleDTMF} />
              <div className="flex flex-col gap-2">
                {callState === 'idle' || callState === 'ended' ? (
                  <button
                    onClick={callState === 'ended' ? resetEmulator : startCall}
                    className="w-16 h-16 rounded-full bg-emerald-500 hover:bg-emerald-400 text-white transition-all active:scale-95 flex items-center justify-center shadow-[0_0_25px_rgba(52,211,153,0.4)]"
                  >
                    {callState === 'ended' ? <ChevronRight className="w-7 h-7" /> : <Phone className="w-7 h-7" />}
                  </button>
                ) : callState === 'ringing' ? (
                  <div className="w-16 h-16 rounded-full bg-amber-500/30 border-2 border-amber-400 flex items-center justify-center">
                    <motion.div animate={{ scale: [1, 1.15, 1] }} transition={{ repeat: Infinity }}>
                      <Clock className="w-7 h-7 text-amber-400" />
                    </motion.div>
                  </div>
                ) : (
                  <button
                    onClick={endCall}
                    aria-label="End call"
                    title="End call"
                    className="w-16 h-16 rounded-full bg-red-500 hover:bg-red-400 text-white transition-all active:scale-95 flex items-center justify-center shadow-[0_0_25px_rgba(239,68,68,0.4)]"
                  >
                    <PhoneOff className="w-7 h-7" />
                  </button>
                )}
                <button
                  onClick={() => isListening ? recognitionRef.current?.abort() : startListening()}
                  disabled={callState !== 'active'}
                  aria-label={isListening ? 'Stop listening' : 'Start listening'}
                  title={isListening ? 'Stop listening' : 'Start listening'}
                  className={`w-16 h-10 rounded-full transition-all flex items-center justify-center text-white ${isListening ? 'bg-red-500/80 border border-red-400' : 'bg-white/5 border border-white/10'} disabled:opacity-30`}
                >
                  {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* ── RIGHT: Agent Pipeline + SMS + Telemetry ── */}
        <div className="space-y-4 flex flex-col">
          {/* 9-Agent Pipeline */}
          <AgentPipeline
            agents={activeAgents}
            isProcessing={activeAgents.some(a => a.status === 'processing')}
          />

          {/* SMS Simulator */}
          <div className="flex-1 bg-card/60 backdrop-blur-xl border border-border/50 rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="text-[11px] font-bold text-secondary-foreground uppercase tracking-widest">SMS Inbox</span>
            </div>
            {smsMessages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-32 text-secondary-foreground/40">
                <Hash className="w-8 h-8 mb-2" />
                <p className="text-xs font-medium">Artifacts appear here after workflow completion</p>
              </div>
            ) : (
              <SMSSimulator
                messages={smsMessages}
                onDismiss={(id) => setSmsMessages(prev => prev.filter(m => m.id !== id))}
              />
            )}
          </div>

          {/* Telemetry Panel */}
          <TelemetryPanel data={telemetry} />
        </div>
      </div>
    </div>
  );
}
