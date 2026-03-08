'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    FileText,
    Download,
    Eye,
    Clock,
    ShieldCheck,
    Upload,
    Loader2,
    Trash2,
    Activity,
    Database,
    Search,
    ChevronRight,
    Sparkles,
    X,
    Camera
} from 'lucide-react';
import { analyzeImage, getPresignedUpload } from '@/services/api';
import { useSession } from '@/hooks/useSession';


const HISTORY_KEY = 'jansathi_vision_history';

interface HistoryItem {
    id: number;
    name: string;
    language: string;
    summary: string;
    date: string;
}

const DocumentsPage = () => {
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState<number | null>(null);
    const [visionResult, setVisionResult] = useState<string | null>(null);
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { sessionId, token } = useSession();


    useEffect(() => {
        const stored = localStorage.getItem(HISTORY_KEY);
        if (stored) {
            setHistory(JSON.parse(stored));
        }
    }, []);

    const saveHistory = (newHistory: HistoryItem[]) => {
        setHistory(newHistory);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory));
    };

    const [documents, setDocuments] = useState([
        { id: 1, name: "PM-Kisan Scheme Guidelines.pdf", date: "2024-01-15", size: "1.2 MB", status: "Verified", theme: "orange" },
        { id: 2, name: "Ration Card Application Form.pdf", date: "2024-02-01", size: "850 KB", status: "Official", theme: "blue" },
        { id: 3, name: "Digital Health ID Info.pdf", date: "2023-11-20", size: "2.4 MB", status: "Information", theme: "emerald" },
        { id: 4, name: "Crop Insurance Policy 2024.pdf", date: "2024-02-05", size: "3.1 MB", status: "Verified", theme: "purple" },
    ]);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.[0]) return;
        const file = e.target.files[0];
        setIsUploading(true);
        setUploadProgress(0);
        setVisionResult(null);

        try {
            // Step 1 – Get presigned S3 URL
            let s3Key: string | null = null;
            try {
                const presign = await getPresignedUpload(
                    sessionId || 'anonymous',
                    file.name,
                    token ?? undefined
                );

                // Step 2 – PUT file directly to S3 (or mock URL)
                const xhr = new XMLHttpRequest();
                xhr.open('PUT', presign.url);
                xhr.setRequestHeader('Content-Type', file.type);
                xhr.upload.onprogress = (ev) => {
                    if (ev.lengthComputable) {
                        setUploadProgress(Math.round((ev.loaded / ev.total) * 80));
                    }
                };
                await new Promise<void>((resolve, reject) => {
                    xhr.onload = () => (xhr.status < 300 ? resolve() : reject(new Error(`PUT failed: ${xhr.status}`)));
                    xhr.onerror = () => reject(new Error('Network error during upload'));
                    xhr.send(file);
                });
                s3Key = presign.key;
                setUploadProgress(85);
            } catch (uploadErr) {
                console.warn('[DocumentsPage] S3 upload failed, continuing with local analysis:', uploadErr);
            }

            // Step 3 – Analyse with Vision AI
            setUploadProgress(90);
            const data = await analyzeImage(file, 'hi');
            setVisionResult(data.analysis.text);
            setUploadProgress(100);

            const newRecord = {
                id: Date.now(),
                name: file.name,
                language: 'hi',
                summary: data.analysis.text.substring(0, 100) + '...',
                date: new Date().toISOString()
            };
            saveHistory([newRecord, ...history]);

            const newDoc = {
                id: Date.now(),
                name: file.name,
                date: new Date().toISOString().split('T')[0],
                size: (file.size / 1024 / 1024).toFixed(2) + ' MB',
                status: s3Key ? 'Stored in S3' : 'Uploaded',
                theme: 'gray'
            };
            setDocuments(prev => [newDoc, ...prev]);
        } catch (err) {
            console.error('[DocumentsPage] Upload error:', err);
        } finally {
            setIsUploading(false);
            setTimeout(() => setUploadProgress(null), 1500);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };


    const clearHistory = () => {
        if (confirm("Clear all analysis history?")) {
            saveHistory([]);
        }
    };

    const getThemeStyles = (theme: string) => {
        switch (theme) {
            case 'orange': return { icon: 'text-orange-500', bg: 'bg-orange-500/5', border: 'border-orange-500/20 hover:border-orange-500/40' };
            case 'blue': return { icon: 'text-blue-500', bg: 'bg-blue-500/5', border: 'border-blue-500/20 hover:border-blue-500/40' };
            case 'emerald': return { icon: 'text-emerald-500', bg: 'bg-emerald-500/5', border: 'border-emerald-500/20 hover:border-emerald-500/40' };
            case 'purple': return { icon: 'text-purple-500', bg: 'bg-purple-500/5', border: 'border-purple-500/20 hover:border-purple-500/40' };
            default: return { icon: 'text-foreground', bg: 'bg-secondary/20', border: 'border-border/50 hover:border-border/80' };
        }
    };

    return (
        <div className="min-h-full flex flex-col gap-8 pb-20 relative">

            {/* Header Section - Clean & Direct */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
            >
                <div className="max-w-xl">
                    <div className="flex items-center gap-2 mb-2 text-primary">
                        <Database className="w-5 h-5" />
                        <span className="text-xs font-bold uppercase tracking-widest">Document Storage</span>
                    </div>
                    <h2 className="text-4xl font-bold text-foreground mb-2 tracking-tight">
                        Your Documents
                    </h2>
                    <p className="text-base text-secondary-foreground font-medium opacity-70">
                        View official guidelines and manage your personal scheme documents.
                    </p>
                </div>

                <div className="flex gap-4 w-full md:w-auto flex-col">
                    <input type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden" ref={fileInputRef} onChange={handleFileUpload} />
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading}
                        className="w-full md:w-auto px-8 py-3 bg-primary text-white rounded-xl font-bold text-sm shadow-sm hover:opacity-90 transition-opacity flex items-center justify-center gap-3"
                    >
                        {isUploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Upload className="w-5 h-5" />}
                        <span>{isUploading ? (uploadProgress !== null ? `Uploading… ${uploadProgress}%` : 'Analyzing…') : 'Upload Document'}</span>
                    </button>
                    {/* Upload progress bar */}
                    {uploadProgress !== null && (
                        <div className="w-full h-1.5 rounded-full bg-secondary overflow-hidden">
                            <div
                                className="h-full bg-primary transition-all duration-300"
                                style={{ width: `${uploadProgress}%` }}
                            />
                        </div>
                    )}
                </div>

            </motion.div>

            {/* Analysis Result */}
            <AnimatePresence>
                {visionResult && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="p-8 rounded-2xl bg-card/60 backdrop-blur-xl border border-primary/20 relative overflow-hidden shadow-[0_8px_30px_rgba(234,88,12,0.15)] group"
                    >
                        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent opacity-50 pointer-events-none"></div>
                        <button onClick={() => setVisionResult(null)} className="absolute top-4 right-4 p-2 text-foreground/40 hover:text-foreground relative z-10 transition-colors">
                            <X className="w-5 h-5" />
                        </button>
                        <div className="flex items-center gap-2 mb-4 text-primary">
                            <Activity className="w-4 h-4" />
                            <h3 className="font-bold uppercase tracking-wider text-[10px]">Scanned Information</h3>
                        </div>
                        <div className="text-foreground text-lg leading-relaxed whitespace-pre-wrap font-semibold tracking-tight">
                            {visionResult}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Documents Grid - Adjusted columns for better space */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-8">
                {documents.map((doc, idx) => {
                    const styles = getThemeStyles(doc.theme);
                    return (
                        <motion.div
                            key={doc.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.05 }}
                            className={`p-8 rounded-2xl border shadow-[0_4px_20px_rgb(0,0,0,0.02)] flex flex-col justify-between min-h-[240px] transition-all hover:shadow-[0_8px_30px_rgba(0,0,0,0.08)] backdrop-blur-xl relative overflow-hidden group ${styles.bg} ${styles.border}`}
                        >
                            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
                            <div className="flex items-start justify-between mb-6 relative z-10">
                                <div className="w-12 h-12 rounded-xl bg-background/80 backdrop-blur-md flex items-center justify-center border border-border group-hover:scale-110 transition-transform">
                                    <FileText className={`w-6 h-6 ${styles.icon}`} />
                                </div>
                                <div className="flex flex-col items-end gap-2">
                                    <div className="px-3 py-1 rounded-full bg-background/80 backdrop-blur-md border border-border/50 shadow-xs">
                                        <span className="text-[9px] font-bold text-foreground opacity-60 tracking-wider flex items-center gap-1">
                                            <ShieldCheck className="w-3 h-3" /> {doc.status}
                                        </span>
                                    </div>
                                    <button
                                        onClick={() => setDocuments(prev => prev.filter(d => d.id !== doc.id))}
                                        className="p-2 text-secondary-foreground hover:text-red-500 transition-colors"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            <div>
                                <h3 className="font-bold text-lg text-foreground mb-1 leading-tight tracking-tight">{doc.name}</h3>
                                <p className="text-[10px] font-bold text-secondary-foreground opacity-50 uppercase tracking-widest">{doc.date} • {doc.size}</p>
                            </div>

                            <div className="flex gap-2 mt-6">
                                <button className="flex-1 py-2.5 rounded-lg bg-background border border-border hover:bg-secondary text-foreground text-[10px] font-bold uppercase tracking-widest transition-all">
                                    View
                                </button>
                                <button className="flex-1 py-2.5 rounded-lg bg-primary text-white text-[10px] font-bold uppercase tracking-widest transition-all hover:bg-primary/90">
                                    Export
                                </button>
                            </div>
                        </motion.div>
                    );
                })}
            </div>

            {/* Scan History */}
            <div className="mt-8">
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-1 h-6 bg-primary rounded-full"></div>
                    <h2 className="text-2xl font-bold text-foreground tracking-tight">Recent Scans</h2>
                    {history.length > 0 && (
                        <button
                            onClick={clearHistory}
                            className="ml-auto text-[10px] font-bold text-secondary-foreground hover:text-red-500 uppercase tracking-widest flex items-center gap-2 transition-colors px-3 py-1.5 rounded-lg hover:bg-red-500/5"
                        >
                            <Trash2 className="w-3 h-3" />
                            Clear History
                        </button>
                    )}
                </div>

                <div className="bg-card/60 backdrop-blur-xl rounded-2xl border border-border/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] overflow-hidden">
                    <div className="hidden md:block overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-secondary/40 text-[10px] font-bold uppercase tracking-widest text-secondary-foreground opacity-60 border-b border-border">
                                <tr>
                                    <th className="px-8 py-4">Document Name</th>
                                    <th className="px-8 py-4">Dialect</th>
                                    <th className="px-8 py-4">Information Type</th>
                                    <th className="px-8 py-4 text-right whitespace-nowrap">Time</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border/30">
                                {history.length === 0 ? (
                                    <tr>
                                        <td colSpan={4} className="px-8 py-12 text-center text-secondary-foreground font-bold uppercase tracking-widest text-[10px] opacity-40">
                                            No scan records yet
                                        </td>
                                    </tr>
                                ) : (
                                    history.map((item) => (
                                        <tr key={item.id} className="hover:bg-secondary/20 transition-colors cursor-pointer group">
                                            <td className="px-8 py-6">
                                                <div className="flex items-center gap-4">
                                                    <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                                                        <Camera className="w-5 h-5 text-primary opacity-40" />
                                                    </div>
                                                    <span className="font-bold text-base text-foreground truncate max-w-[200px]">{item.name}</span>
                                                </div>
                                            </td>
                                            <td className="px-8 py-6">
                                                <span className="text-xs font-bold text-secondary-foreground uppercase">
                                                    {item.language === 'hi' ? 'Hindi' : item.language}
                                                </span>
                                            </td>
                                            <td className="px-8 py-6 text-xs text-secondary-foreground opacity-60 font-medium">
                                                Extraction
                                            </td>
                                            <td className="px-8 py-6 text-right text-[10px] font-bold uppercase text-secondary-foreground opacity-40 whitespace-nowrap">
                                                {new Date(item.date).toLocaleDateString()}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>

                    <div className="md:hidden divide-y divide-border">
                        {history.map((item, i) => (
                            <div key={item.id} className="p-5 flex items-center justify-between hover:bg-secondary/20 transition-colors">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                                        <Activity className="w-5 h-5 text-primary opacity-40" />
                                    </div>
                                    <div>
                                        <p className="font-bold text-sm text-foreground">{item.name}</p>
                                        <p className="text-[10px] font-bold text-secondary-foreground opacity-60 uppercase">{item.language === 'hi' ? 'Hindi' : item.language}</p>
                                    </div>
                                </div>
                                <span className="text-[10px] font-bold text-secondary-foreground opacity-40">{new Date(item.date).toLocaleDateString()}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DocumentsPage;
