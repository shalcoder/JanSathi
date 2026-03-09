'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Circle, ChevronRight } from 'lucide-react';

interface SlotCollectionProgressProps {
    slots: Record<string, string | number | boolean>;
    slotsComplete: boolean;
    schemeName?: string;
}

// Human-readable labels for common slot keys
const SLOT_LABELS: Record<string, string> = {
    name:              'Full Name',
    aadhaar:           'Aadhaar Number',
    mobile:            'Mobile Number',
    state:             'State',
    district:          'District',
    annual_income:     'Annual Income',
    land_hectares:     'Land Area (hectares)',
    bank_account:      'Bank Account Number',
    ifsc:              'IFSC Code',
    age:               'Age',
    gender:            'Gender',
    caste:             'Caste Category',
    occupation:        'Occupation',
    scheme_name:       'Scheme',
    consent:           'Consent Given',
};

function formatValue(val: string | number | boolean): string {
    if (typeof val === 'boolean') return val ? 'Yes' : 'No';
    if (val === '' || val === null || val === undefined) return '—';
    const str = String(val);
    // Mask aadhaar: show only last 4 digits
    if (str.match(/^\d{12}$/)) return `XXXX XXXX ${str.slice(-4)}`;
    return str;
}

export default function SlotCollectionProgress({
    slots,
    slotsComplete,
    schemeName,
}: SlotCollectionProgressProps) {
    const entries = Object.entries(slots).filter(([, v]) => v !== null && v !== undefined && v !== '');
    if (entries.length === 0) return null;

    const displayEntries = entries.map(([key, val]) => ({
        key,
        label: SLOT_LABELS[key] || key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
        value: formatValue(val),
        filled: true,
    }));

    return (
        <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-3 rounded-2xl border border-primary/20 bg-primary/[0.04] backdrop-blur-sm overflow-hidden"
        >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2.5 bg-primary/8 border-b border-primary/15">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                    <span className="text-[11px] font-black uppercase tracking-widest text-primary">
                        Collecting Eligibility Info
                        {schemeName ? ` — ${schemeName}` : ''}
                    </span>
                </div>
                {slotsComplete ? (
                    <span className="text-[10px] font-bold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/30">
                        Complete ✓
                    </span>
                ) : (
                    <span className="text-[10px] font-bold text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/30">
                        In Progress
                    </span>
                )}
            </div>

            {/* Slot list */}
            <div className="px-4 py-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
                {displayEntries.map((entry, i) => (
                    <motion.div
                        key={entry.key}
                        initial={{ opacity: 0, x: -6 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.04 }}
                        className="flex items-center gap-2.5"
                    >
                        {entry.filled ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                        ) : (
                            <Circle className="w-4 h-4 text-muted-foreground/40 shrink-0" />
                        )}
                        <div className="min-w-0">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground block">
                                {entry.label}
                            </span>
                            <span className="text-sm font-semibold text-foreground truncate block">
                                {entry.value}
                            </span>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Progress bar */}
            {!slotsComplete && (
                <div className="px-4 pb-3">
                    <div className="flex items-center gap-2 text-[11px] text-muted-foreground font-medium">
                        <ChevronRight className="w-3 h-3" />
                        <span>Please answer the question above to continue</span>
                    </div>
                </div>
            )}
        </motion.div>
    );
}
