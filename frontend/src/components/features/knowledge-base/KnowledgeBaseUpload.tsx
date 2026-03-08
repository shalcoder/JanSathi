'use client';

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Upload,
    FileText,
    Loader2,
    CheckCircle,
    AlertCircle,
    X,
    Clock,
    Database
} from 'lucide-react';
import { uploadPDFToKnowledgeBase } from '@/services/api';
import { useSession } from '@/hooks/useSession';

interface KnowledgeBaseUploadProps {
    onUploadSuccess?: (documentId: string) => void;
    onUploadError?: (error: string) => void;
}

export default function KnowledgeBaseUpload({ 
    onUploadSuccess, 
    onUploadError 
}: KnowledgeBaseUploadProps) {
    const [isUploading, setIsUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
    const [uploadMessage, setUploadMessage] = useState('');
    const [documentId, setDocumentId] = useState('');
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { token } = useSession();

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        // Validate file type
        if (file.type !== 'application/pdf') {
            setUploadStatus('error');
            setUploadMessage('Only PDF files are allowed');
            onUploadError?.('Only PDF files are allowed');
            return;
        }

        // Validate file size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            setUploadStatus('error');
            setUploadMessage('File size must be less than 10MB');
            onUploadError?.('File size must be less than 10MB');
            return;
        }

        setIsUploading(true);
        setUploadStatus('uploading');
        setUploadMessage('Uploading to Knowledge Base...');

        try {
            const result = await uploadPDFToKnowledgeBase(
                file,
                'user_' + Date.now(),
                'scheme_document',
                token ?? undefined
            );

            setUploadStatus('success');
            setUploadMessage(result.message || 'Document uploaded successfully!');
            setDocumentId(result.document_id);
            onUploadSuccess?.(result.document_id);

            // Reset after 5 seconds
            setTimeout(() => {
                setUploadStatus('idle');
                setUploadMessage('');
                setDocumentId('');
                if (fileInputRef.current) {
                    fileInputRef.current.value = '';
                }
            }, 5000);

        } catch (error) {
            console.error('Upload error:', error);
            setUploadStatus('error');
            setUploadMessage('Upload failed. Please try again.');
            onUploadError?.('Upload failed');

            // Reset after 3 seconds
            setTimeout(() => {
                setUploadStatus('idle');
                setUploadMessage('');
            }, 3000);
        } finally {
            setIsUploading(false);
        }
    };

    const triggerFileInput = () => {
        fileInputRef.current?.click();
    };

    const getStatusIcon = () => {
        switch (uploadStatus) {
            case 'uploading':
                return <Loader2 className="w-5 h-5 animate-spin text-blue-500" />;
            case 'success':
                return <CheckCircle className="w-5 h-5 text-emerald-500" />;
            case 'error':
                return <AlertCircle className="w-5 h-5 text-red-500" />;
            default:
                return <Upload className="w-5 h-5 text-foreground" />;
        }
    };

    const getStatusColor = () => {
        switch (uploadStatus) {
            case 'uploading':
                return 'border-blue-500/50 bg-blue-500/5';
            case 'success':
                return 'border-emerald-500/50 bg-emerald-500/5';
            case 'error':
                return 'border-red-500/50 bg-red-500/5';
            default:
                return 'border-border/50 hover:border-primary/50 bg-card/40';
        }
    };

    return (
        <div className="w-full">
            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                className="hidden"
            />

            <motion.div
                className={`relative border-2 border-dashed rounded-xl p-6 transition-all duration-300 ${getStatusColor()}`}
                whileHover={uploadStatus === 'idle' ? { scale: 1.01 } : {}}
                whileTap={uploadStatus === 'idle' ? { scale: 0.99 } : {}}
            >
                <div className="flex flex-col items-center justify-center space-y-4">
                    {/* Icon */}
                    <div className="relative">
                        {getStatusIcon()}
                        {uploadStatus === 'uploading' && (
                            <motion.div
                                className="absolute inset-0 rounded-full border-2 border-blue-500/30"
                                animate={{ scale: [1, 1.5], opacity: [0.5, 0] }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                            />
                        )}
                    </div>

                    {/* Status Message */}
                    <AnimatePresence mode="wait">
                        {uploadStatus === 'idle' ? (
                            <motion.div
                                key="idle"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="text-center"
                            >
                                <h3 className="text-lg font-semibold text-foreground mb-2">
                                    Upload to Knowledge Base
                                </h3>
                                <p className="text-sm text-secondary-foreground opacity-70">
                                    Upload PDF documents to make them searchable for all users
                                </p>
                                <p className="text-xs text-secondary-foreground opacity-50 mt-2">
                                    Max 10MB • PDF only
                                </p>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="status"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="text-center"
                            >
                                <p className="text-sm font-medium text-foreground">
                                    {uploadMessage}
                                </p>
                                {uploadStatus === 'success' && documentId && (
                                    <div className="mt-3 space-y-2">
                                        <div className="flex items-center justify-center gap-2 text-xs text-secondary-foreground opacity-70">
                                            <Database className="w-3 h-3" />
                                            <span>Document ID: {documentId.substring(0, 20)}...</span>
                                        </div>
                                        <div className="flex items-center justify-center gap-2 text-xs text-amber-500">
                                            <Clock className="w-3 h-3" />
                                            <span>Indexing in progress (5-10 minutes)</span>
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Upload Button */}
                    {uploadStatus === 'idle' && (
                        <motion.button
                            onClick={triggerFileInput}
                            disabled={isUploading}
                            className="px-6 py-2.5 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                        >
                            <FileText className="w-4 h-4" />
                            Select PDF
                        </motion.button>
                    )}
                </div>

                {/* Progress Indicator */}
                {uploadStatus === 'uploading' && (
                    <motion.div
                        className="absolute bottom-0 left-0 h-1 bg-blue-500 rounded-b-xl"
                        initial={{ width: '0%' }}
                        animate={{ width: '100%' }}
                        transition={{ duration: 2, ease: 'easeInOut' }}
                    />
                )}
            </motion.div>

            {/* Info Box */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="mt-4 p-4 bg-blue-500/5 border border-blue-500/20 rounded-lg"
            >
                <div className="flex items-start gap-3">
                    <Database className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                    <div className="text-sm text-secondary-foreground space-y-1">
                        <p className="font-medium text-foreground">How it works:</p>
                        <ul className="list-disc list-inside space-y-1 opacity-80">
                            <li>Upload PDF documents (scheme guidelines, policies, etc.)</li>
                            <li>Documents are indexed in Bedrock Knowledge Base</li>
                            <li>All users can query the documents through chat</li>
                            <li>Responses are cached for cost efficiency (85% savings)</li>
                        </ul>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
