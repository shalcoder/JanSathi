'use client';

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    CheckCircle2, X, MessageSquare, FileText, CreditCard,
    MapPin, User, Copy, ExternalLink
} from 'lucide-react';

interface ApplicationSuccessModalProps {
    caseId: string;
    schemeName?: string;
    smsSent?: boolean;
    phone?: string;
    onClose: () => void;
}

const DOC_CHECKLIST = [
    { icon: User,     label: 'Aadhaar Card',           hint: 'Linked to bank account' },
    { icon: CreditCard, label: 'Bank Passbook / Statement', hint: 'Last 3 months' },
    { icon: MapPin,   label: 'Land Ownership Record',  hint: 'Khatauni / Khasra (for rural schemes)' },
    { icon: FileText, label: 'Income Certificate',     hint: 'From Tehsildar or equivalent' },
];

export default function ApplicationSuccessModal({
    caseId,
    schemeName,
    smsSent,
    phone,
    onClose,
}: ApplicationSuccessModalProps) {
    // Close on Escape key
    useEffect(() => {
        const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
        document.addEventListener('keydown', handler);
        return () => document.removeEventListener('keydown', handler);
    }, [onClose]);

    const shortId = `JS-${caseId.replace('CASE-', '').slice(0, 8).toUpperCase()}`;

    const copyId = () => {
        navigator.clipboard.writeText(shortId).catch(() => {});
    };

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
                onClick={e => { if (e.target === e.currentTarget) onClose(); }}
            >
                <motion.div
                    initial={{ opacity: 0, y: 40, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 40 }}
                    transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                    className="w-full max-w-md bg-card border border-border/60 rounded-3xl shadow-2xl overflow-hidden"
                >
                    {/* Success header */}
                    <div className="relative bg-gradient-to-br from-emerald-500/20 to-emerald-600/10 px-6 py-6 border-b border-emerald-500/20">
                        <button
                            onClick={onClose}
                            className="absolute top-4 right-4 p-1.5 rounded-lg hover:bg-white/10 text-white/60 hover:text-white transition-colors"
                            aria-label="Close"
                        >
                            <X className="w-4 h-4" />
                        </button>

                        <div className="flex items-center gap-4">
                            <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
                                <CheckCircle2 className="w-8 h-8 text-emerald-400" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-foreground">Application Submitted!</h2>
                                <p className="text-sm text-muted-foreground mt-0.5">
                                    {schemeName ? `For ${schemeName}` : 'Government Scheme Application'}
                                </p>
                            </div>
                        </div>

                        {/* Case ID */}
                        <div className="mt-5 flex items-center gap-2 bg-background/40 border border-border/40 rounded-xl px-4 py-3">
                            <div className="flex-1">
                                <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Application Reference ID</p>
                                <p className="text-lg font-mono font-bold text-foreground tracking-wider mt-0.5">{shortId}</p>
                            </div>
                            <button
                                onClick={copyId}
                                className="p-2 rounded-lg hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground"
                                title="Copy Reference ID"
                            >
                                <Copy className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    <div className="px-6 py-5 space-y-5">
                        {/* SMS confirmation */}
                        {smsSent && (
                            <motion.div
                                initial={{ opacity: 0, x: -8 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.15 }}
                                className="flex items-start gap-3 p-3.5 bg-blue-500/10 border border-blue-500/20 rounded-2xl"
                            >
                                <div className="w-9 h-9 rounded-xl bg-blue-500/20 flex items-center justify-center shrink-0">
                                    <MessageSquare className="w-4.5 h-4.5 text-blue-400" />
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-foreground">SMS Confirmation Sent</p>
                                    <p className="text-xs text-muted-foreground mt-0.5">
                                        {phone
                                            ? `Sent to +91 ••••••${phone.slice(-4)}`
                                            : 'Sent to your registered mobile'
                                        }
                                    </p>
                                    <p className="text-xs text-blue-400 font-mono mt-1.5 italic">
                                        &ldquo;JanSathi: Application {shortId} submitted. Status updates will follow.&rdquo;
                                    </p>
                                </div>
                            </motion.div>
                        )}

                        {/* Document checklist */}
                        <div>
                            <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">
                                Documents to Keep Ready
                            </h3>
                            <div className="space-y-2">
                                {DOC_CHECKLIST.map((doc, i) => (
                                    <motion.div
                                        key={i}
                                        initial={{ opacity: 0, x: -6 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.1 + i * 0.06 }}
                                        className="flex items-center gap-3 p-3 bg-secondary/30 rounded-xl border border-border/30"
                                    >
                                        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                                            <doc.icon className="w-4 h-4 text-primary" />
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <p className="text-sm font-semibold text-foreground">{doc.label}</p>
                                            <p className="text-[11px] text-muted-foreground">{doc.hint}</p>
                                        </div>
                                        <CheckCircle2 className="w-4 h-4 text-muted-foreground/30 shrink-0" />
                                    </motion.div>
                                ))}
                            </div>
                        </div>

                        {/* Next steps */}
                        <div className="flex gap-3">
                            <a
                                href="https://pmkisan.gov.in"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-secondary/50 hover:bg-secondary text-sm font-semibold text-foreground transition-colors border border-border/40"
                            >
                                <ExternalLink className="w-4 h-4" /> Track Status
                            </a>
                            <button
                                onClick={onClose}
                                className="flex-1 py-2.5 rounded-xl bg-primary text-white text-sm font-bold transition-all hover:shadow-lg"
                            >
                                Done
                            </button>
                        </div>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}
