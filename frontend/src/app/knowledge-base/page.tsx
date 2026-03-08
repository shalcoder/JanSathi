'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    Database,
    TrendingUp,
    Zap,
    DollarSign,
    FileText,
    Activity
} from 'lucide-react';
import KnowledgeBaseUpload from '@/components/features/knowledge-base/KnowledgeBaseUpload';
import KnowledgeBaseQuery from '@/components/features/knowledge-base/KnowledgeBaseQuery';
import { getKBCacheStats, getKBHealth, KBCacheStats, KBHealthStatus } from '@/services/api';

export default function KnowledgeBasePage() {
    const [stats, setStats] = useState<KBCacheStats | null>(null);
    const [health, setHealth] = useState<KBHealthStatus | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setIsLoading(true);
        try {
            const [statsData, healthData] = await Promise.all([
                getKBCacheStats(),
                getKBHealth()
            ]);
            setStats(statsData);
            setHealth(healthData);
        } catch (error) {
            console.error('Failed to load KB data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleUploadSuccess = () => {
        // Refresh stats after successful upload
        loadData();
    };

    return (
        <div className="min-h-screen bg-background">
            {/* Header */}
            <div className="border-b border-border/50 bg-card/20 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex items-center gap-4"
                    >
                        <div className="p-3 bg-primary/10 rounded-xl">
                            <Database className="w-8 h-8 text-primary" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-foreground">
                                Knowledge Base
                            </h1>
                            <p className="text-secondary-foreground opacity-70 mt-1">
                                Upload documents and query with AI-powered search
                            </p>
                        </div>
                    </motion.div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Stats Cards */}
                {!isLoading && stats && health && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
                    >
                        {/* Status */}
                        <div className="p-4 bg-card/40 border border-border/50 rounded-xl">
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${health.working ? 'bg-emerald-500/10' : 'bg-red-500/10'}`}>
                                    <Activity className={`w-5 h-5 ${health.working ? 'text-emerald-500' : 'text-red-500'}`} />
                                </div>
                                <div>
                                    <p className="text-xs text-secondary-foreground opacity-70">Status</p>
                                    <p className="text-lg font-semibold text-foreground">
                                        {health.working ? 'Online' : 'Offline'}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Cached Queries */}
                        <div className="p-4 bg-card/40 border border-border/50 rounded-xl">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-blue-500/10 rounded-lg">
                                    <Database className="w-5 h-5 text-blue-500" />
                                </div>
                                <div>
                                    <p className="text-xs text-secondary-foreground opacity-70">Cached Queries</p>
                                    <p className="text-lg font-semibold text-foreground">
                                        {stats.total_cached_queries}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Last 24h */}
                        <div className="p-4 bg-card/40 border border-border/50 rounded-xl">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-purple-500/10 rounded-lg">
                                    <TrendingUp className="w-5 h-5 text-purple-500" />
                                </div>
                                <div>
                                    <p className="text-xs text-secondary-foreground opacity-70">Last 24h</p>
                                    <p className="text-lg font-semibold text-foreground">
                                        {stats.cached_last_24h}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Cost Saved */}
                        <div className="p-4 bg-card/40 border border-border/50 rounded-xl">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-emerald-500/10 rounded-lg">
                                    <DollarSign className="w-5 h-5 text-emerald-500" />
                                </div>
                                <div>
                                    <p className="text-xs text-secondary-foreground opacity-70">Cost Saved</p>
                                    <p className="text-lg font-semibold text-foreground">
                                        ${stats.estimated_cost_saved.toFixed(2)}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* Main Content */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Upload Section */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                    >
                        <div className="mb-4">
                            <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
                                <FileText className="w-5 h-5 text-primary" />
                                Upload Documents
                            </h2>
                            <p className="text-sm text-secondary-foreground opacity-70 mt-1">
                                Add PDFs to the shared knowledge base
                            </p>
                        </div>
                        <KnowledgeBaseUpload onUploadSuccess={handleUploadSuccess} />
                    </motion.div>

                    {/* Query Section */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <div className="mb-4">
                            <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
                                <Zap className="w-5 h-5 text-primary" />
                                Query Knowledge Base
                            </h2>
                            <p className="text-sm text-secondary-foreground opacity-70 mt-1">
                                Search through uploaded documents with AI
                            </p>
                        </div>
                        <KnowledgeBaseQuery language="en" />
                    </motion.div>
                </div>

                {/* Language Distribution */}
                {stats && stats.language_distribution && Object.keys(stats.language_distribution).length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="mt-8 p-6 bg-card/40 border border-border/50 rounded-xl"
                    >
                        <h3 className="text-lg font-semibold text-foreground mb-4">
                            Language Distribution
                        </h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {Object.entries(stats.language_distribution).map(([lang, count]) => (
                                <div key={lang} className="text-center">
                                    <p className="text-2xl font-bold text-primary">{count}</p>
                                    <p className="text-sm text-secondary-foreground opacity-70 uppercase">
                                        {lang}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                )}

                {/* Info Box */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="mt-8 p-6 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-xl"
                >
                    <div className="flex items-start gap-4">
                        <Zap className="w-6 h-6 text-blue-500 mt-1 flex-shrink-0" />
                        <div className="space-y-2">
                            <h3 className="text-lg font-semibold text-foreground">
                                Intelligent Caching System
                            </h3>
                            <p className="text-sm text-secondary-foreground opacity-80">
                                Our Knowledge Base uses intelligent caching to reduce costs by 85%. When you query a document, 
                                the response is cached for 24 hours. If another user asks the same question, they get an instant 
                                response at zero cost!
                            </p>
                            <div className="flex items-center gap-4 mt-4 text-xs text-secondary-foreground opacity-70">
                                <div className="flex items-center gap-1">
                                    <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                                    <span>Cache Hit: $0.00</span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <div className="w-2 h-2 bg-amber-500 rounded-full"></div>
                                    <span>Cache Miss: ~$0.02</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
