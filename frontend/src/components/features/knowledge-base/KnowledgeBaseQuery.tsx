'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search,
    Loader2,
    FileText,
    ExternalLink,
    TrendingUp,
    Database,
    Zap,
    DollarSign
} from 'lucide-react';
import { queryKnowledgeBase, KBQueryResponse } from '@/services/api';
import { useSession } from '@/hooks/useSession';

interface KnowledgeBaseQueryProps {
    initialQuestion?: string;
    language?: string;
    onQueryComplete?: (response: KBQueryResponse) => void;
}

export default function KnowledgeBaseQuery({
    initialQuestion = '',
    language = 'en',
    onQueryComplete
}: KnowledgeBaseQueryProps) {
    const [question, setQuestion] = useState(initialQuestion);
    const [isQuerying, setIsQuerying] = useState(false);
    const [response, setResponse] = useState<KBQueryResponse | null>(null);
    const { token } = useSession();

    const handleQuery = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!question.trim() || isQuerying) return;

        setIsQuerying(true);
        setResponse(null);

        try {
            const result = await queryKnowledgeBase(
                {
                    question: question.trim(),
                    language,
                    max_results: 3
                },
                token ?? undefined
            );

            setResponse(result);
            onQueryComplete?.(result);
        } catch (error) {
            console.error('Query error:', error);
            setResponse({
                answer: 'Failed to query Knowledge Base. Please try again.',
                sources: [],
                cached: false,
                cost_saved: 0,
                language,
                error: 'Query failed'
            });
        } finally {
            setIsQuerying(false);
        }
    };

    return (
        <div className="w-full space-y-6">
            {/* Query Input */}
            <form onSubmit={handleQuery} className="relative">
                <div className="relative">
                    <input
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Ask a question about uploaded documents..."
                        className="w-full px-4 py-3 pl-12 pr-24 bg-card/40 border border-border/50 rounded-xl text-foreground placeholder:text-secondary-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all"
                        disabled={isQuerying}
                    />
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-foreground/50" />
                    <motion.button
                        type="submit"
                        disabled={isQuerying || !question.trim()}
                        className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        {isQuerying ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <Zap className="w-4 h-4" />
                        )}
                        Query
                    </motion.button>
                </div>
            </form>

            {/* Loading State */}
            <AnimatePresence>
                {isQuerying && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="flex items-center justify-center gap-3 p-6 bg-blue-500/5 border border-blue-500/20 rounded-xl"
                    >
                        <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                        <span className="text-sm text-secondary-foreground">
                            Searching Knowledge Base...
                        </span>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Response */}
            <AnimatePresence>
                {response && !isQuerying && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="space-y-4"
                    >
                        {/* Cache Status Badge */}
                        <div className="flex items-center gap-2 flex-wrap">
                            {response.cached && (
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-xs font-medium text-emerald-500"
                                >
                                    <Zap className="w-3 h-3" />
                                    Cached Response
                                    {response.cache_age_hours && (
                                        <span className="opacity-70">
                                            ({response.cache_age_hours}h old)
                                        </span>
                                    )}
                                </motion.div>
                            )}
                            {response.cost_saved > 0 && (
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="flex items-center gap-1.5 px-3 py-1 bg-amber-500/10 border border-amber-500/20 rounded-full text-xs font-medium text-amber-500"
                                >
                                    <DollarSign className="w-3 h-3" />
                                    Saved ${response.cost_saved.toFixed(2)}
                                </motion.div>
                            )}
                            <div className="flex items-center gap-1.5 px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-xs font-medium text-blue-500">
                                <Database className="w-3 h-3" />
                                {response.sources.length} sources
                            </div>
                        </div>

                        {/* Answer */}
                        <div className="p-6 bg-card/40 border border-border/50 rounded-xl">
                            <div className="flex items-start gap-3 mb-4">
                                <div className="p-2 bg-primary/10 rounded-lg">
                                    <FileText className="w-5 h-5 text-primary" />
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-lg font-semibold text-foreground mb-2">
                                        Answer
                                    </h3>
                                    <div className="prose prose-sm max-w-none text-secondary-foreground">
                                        {response.answer.split('\n').map((line, i) => (
                                            <p key={i} className="mb-2 last:mb-0">
                                                {line}
                                            </p>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Sources */}
                        {response.sources.length > 0 && (
                            <div className="space-y-3">
                                <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                                    <TrendingUp className="w-4 h-4 text-primary" />
                                    Source Documents
                                </h4>
                                <div className="space-y-2">
                                    {response.sources.map((source, index) => (
                                        <motion.div
                                            key={index}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                            className="p-4 bg-card/40 border border-border/50 rounded-lg hover:border-primary/50 transition-colors group"
                                        >
                                            <div className="flex items-start justify-between gap-3">
                                                <div className="flex-1 space-y-2">
                                                    <div className="flex items-center gap-2">
                                                        <div className="px-2 py-0.5 bg-primary/10 rounded text-xs font-medium text-primary">
                                                            Score: {(source.score * 100).toFixed(0)}%
                                                        </div>
                                                        <div className="px-2 py-0.5 bg-secondary/50 rounded text-xs font-medium text-secondary-foreground">
                                                            {source.type}
                                                        </div>
                                                    </div>
                                                    <p className="text-sm text-secondary-foreground line-clamp-3">
                                                        {source.text}
                                                    </p>
                                                    {source.source && source.source !== 'Unknown' && (
                                                        <a
                                                            href={source.source}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                                                        >
                                                            View Source
                                                            <ExternalLink className="w-3 h-3" />
                                                        </a>
                                                    )}
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Error State */}
                        {response.error && (
                            <div className="p-4 bg-red-500/5 border border-red-500/20 rounded-lg">
                                <p className="text-sm text-red-500">
                                    {response.error}
                                </p>
                            </div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
