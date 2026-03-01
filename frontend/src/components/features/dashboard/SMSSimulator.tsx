'use client';

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, X, ExternalLink, CheckCheck } from 'lucide-react';

export interface SMSMessage {
  id: string;
  body: string;
  timestamp: string;
  receiptUrl?: string;
  artifactType?: 'receipt' | 'grievance' | 'checklist';
}

interface SMSSimulatorProps {
  messages: SMSMessage[];
  onDismiss?: (id: string) => void;
}

export default function SMSSimulator({ messages, onDismiss }: SMSSimulatorProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const typeColor = (type?: string) => {
    if (type === 'receipt') return 'text-emerald-400';
    if (type === 'grievance') return 'text-amber-400';
    if (type === 'checklist') return 'text-blue-400';
    return 'text-primary';
  };

  return (
    <div className="flex flex-col gap-3 w-full">
      <AnimatePresence initial={false}>
        {messages.map((msg) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 24, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9, x: 40 }}
            transition={{ type: 'spring', stiffness: 380, damping: 28 }}
            className="relative bg-[#1c1c1e] border border-white/10 rounded-2xl p-4 shadow-[0_8px_30px_rgba(0,0,0,0.4)] overflow-hidden"
          >
            {/* Subtle green scan-line overlay */}
            <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(52,199,89,0.02)_50%)] bg-[size:100%_4px] pointer-events-none" />

            {/* Header */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
                  <MessageSquare className="w-4 h-4 text-emerald-400" />
                </div>
                <div>
                  <p className="text-[11px] font-bold text-white/90 tracking-wide">JanSathi Gov</p>
                  <p className="text-[9px] text-white/40 font-mono">{msg.timestamp}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <CheckCheck className="w-4 h-4 text-blue-400" />
                {onDismiss && (
                  <button onClick={() => onDismiss(msg.id)} className="p-1 hover:bg-white/10 rounded-lg transition-colors">
                    <X className="w-3.5 h-3.5 text-white/40" />
                  </button>
                )}
              </div>
            </div>

            {/* Body */}
            <p className="text-sm text-white/80 leading-relaxed font-medium">{msg.body}</p>

            {/* Receipt Link */}
            {msg.receiptUrl && (
              <a
                href={msg.receiptUrl}
                target="_blank"
                rel="noopener noreferrer"
                className={`mt-3 flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider ${typeColor(msg.artifactType)} hover:underline`}
              >
                <ExternalLink className="w-3 h-3" />
                {msg.artifactType === 'receipt' && 'View Benefit Receipt'}
                {msg.artifactType === 'grievance' && 'View Grievance Draft'}
                {msg.artifactType === 'checklist' && 'View Document Checklist'}
                {!msg.artifactType && 'View Artifact'}
              </a>
            )}
          </motion.div>
        ))}
      </AnimatePresence>
      <div ref={bottomRef} />
    </div>
  );
}
