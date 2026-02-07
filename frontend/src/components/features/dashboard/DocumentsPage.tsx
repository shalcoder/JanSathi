import React, { useState, useRef, useEffect } from 'react';
import { FileText, Download, Eye, Clock, ShieldCheck, Upload, Loader2, Camera, Trash2 } from 'lucide-react';
import { analyzeImage } from '@/services/api';

const HISTORY_KEY = 'jansathi_vision_history';

const DocumentsPage = () => {
    const [isUploading, setIsUploading] = useState(false);
    const [visionResult, setVisionResult] = useState<string | null>(null);
    const [history, setHistory] = useState<any[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        const stored = localStorage.getItem(HISTORY_KEY);
        if (stored) {
            setHistory(JSON.parse(stored));
        }
    }, []);

    const saveHistory = (newHistory: any[]) => {
        setHistory(newHistory);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory));
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setIsUploading(true);
            try {
                const data = await analyzeImage(file, 'hi');
                setVisionResult(data.analysis.text);

                const newRecord = {
                    id: Date.now(),
                    name: file.name,
                    language: 'hi',
                    summary: data.analysis.text.substring(0, 100) + '...',
                    date: new Date().toISOString()
                };
                saveHistory([newRecord, ...history]);
            } catch (err) {
                alert("Analysis failed. Please check your connection.");
            } finally {
                setIsUploading(false);
            }
        }
    };

    const clearHistory = () => {
        if (confirm("Clear all analysis history?")) {
            saveHistory([]);
        }
    };

    const documents = [
        { id: 1, name: "PM-Kisan Scheme Guidelines.pdf", date: "2024-01-15", size: "1.2 MB", status: "Verified" },
        { id: 2, name: "Ration Card Application Form.pdf", date: "2024-02-01", size: "850 KB", status: "Official" },
        { id: 3, name: "Digital Health ID Info.pdf", date: "2023-11-20", size: "2.4 MB", status: "Information" },
        { id: 4, name: "Crop Insurance Policy 2024.pdf", date: "2024-02-05", size: "3.1 MB", status: "Verified" },
    ];

    return (
        <div className="min-h-full flex flex-col gap-4 sm:gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-end gap-4">
                <div>
                    <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2 underline decoration-blue-500/30">Government Intelligence</h2>
                    <p className="text-sm sm:text-base text-slate-400">Review official guidelines or use Drishti AI to analyze your own documents.</p>
                </div>
                <div className="flex gap-3">
                    <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        ref={fileInputRef}
                        onChange={handleFileUpload}
                    />
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading}
                        className="flex items-center gap-2 px-4 sm:px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-bold transition-all shadow-xl shadow-blue-600/20 active:scale-95 disabled:opacity-50 text-sm sm:text-base whitespace-nowrap"
                    >
                        {isUploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Camera className="w-5 h-5" />}
                        {isUploading ? 'Analyzing...' : 'Analyze Document'}
                    </button>
                </div>
            </div>

            {visionResult && (
                <div className="glass-panel p-6 rounded-3xl border border-blue-500/30 bg-blue-500/5 animate-in slide-in-from-top-4 relative group">
                    <button onClick={() => setVisionResult(null)} className="absolute top-4 right-4 text-slate-500 hover:text-white">×</button>
                    <h3 className="text-blue-400 font-black uppercase tracking-widest text-[10px] mb-3">Drishti AI Analysis Result</h3>
                    <div className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">
                        {visionResult}
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {documents.map((doc) => (
                    <div key={doc.id} className="glass-panel p-4 sm:p-5 rounded-2xl sm:rounded-3xl border border-white/5 group hover:border-blue-500/30 transition-all">
                        <div className="flex items-start justify-between mb-4">
                            <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center">
                                <FileText className="w-6 h-6 text-blue-500" />
                            </div>
                            <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                                <ShieldCheck className="w-3 h-3 text-emerald-500" />
                                <span className="text-[10px] font-bold text-emerald-500 uppercase">{doc.status}</span>
                            </div>
                        </div>
                        <h3 className="font-bold text-slate-100 mb-1 truncate">{doc.name}</h3>
                        <p className="text-xs text-slate-500 mb-6">{doc.date} • {doc.size}</p>

                        <div className="flex gap-2">
                            <button className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-xs font-semibold transition-all">
                                <Eye className="w-4 h-4" />
                                View
                            </button>
                            <button className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-xs font-semibold transition-all shadow-lg shadow-blue-500/20">
                                <Download className="w-4 h-4" />
                                Download
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Drishti Vision Records */}
            <div className="mt-8">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg sm:text-xl font-bold text-white flex items-center gap-2">
                        <Clock className="w-4 h-4 sm:w-5 sm:h-5 text-blue-400" />
                        Drishti Vision History
                    </h2>
                    {history.length > 0 && (
                        <button
                            onClick={clearHistory}
                            className="text-[10px] font-black text-slate-500 hover:text-red-400 uppercase tracking-widest flex items-center gap-2 transition-colors px-2 sm:px-3 py-1.5 rounded-lg hover:bg-red-500/5"
                        >
                            <Trash2 className="w-3 h-3" />
                            <span className="hidden sm:inline">Clear Records</span>
                        </button>
                    )}
                </div>

                <div className="glass-panel rounded-2xl sm:rounded-3xl overflow-hidden border border-white/5">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm min-w-[600px]">
                            <thead className="bg-white/5 text-slate-400 font-medium">
                                <tr>
                                    <th className="px-4 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm">Image Analysis</th>
                                    <th className="px-4 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm">Language</th>
                                    <th className="px-4 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm">Result Summary</th>
                                    <th className="px-4 sm:px-6 py-3 sm:py-4 text-right text-xs sm:text-sm">Date</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {history.length === 0 ? (
                                    <tr>
                                        <td colSpan={4} className="px-4 sm:px-6 py-8 sm:py-12 text-center text-slate-600 font-bold uppercase tracking-widest text-[10px]">
                                            No analyze records yet
                                        </td>
                                    </tr>
                                ) : (
                                    history.map((item) => (
                                        <tr key={item.id} className="hover:bg-white/5 transition-colors cursor-pointer group">
                                            <td className="px-4 sm:px-6 py-3 sm:py-4 flex items-center gap-3">
                                                <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 overflow-hidden flex items-center justify-center flex-shrink-0">
                                                    <Camera className="w-3 h-3 sm:w-4 sm:h-4 text-blue-500" />
                                                </div>
                                                <span className="font-medium text-slate-300 text-xs sm:text-sm truncate">{item.name}</span>
                                            </td>
                                            <td className="px-4 sm:px-6 py-3 sm:py-4 text-slate-400 capitalize text-xs sm:text-sm">{item.language === 'hi' ? 'Hindi' : item.language}</td>
                                            <td className="px-4 sm:px-6 py-3 sm:py-4 text-slate-400 truncate max-w-[150px] sm:max-w-[200px] text-xs sm:text-sm" title={item.summary}>
                                                {item.summary}
                                            </td>
                                            <td className="px-4 sm:px-6 py-3 sm:py-4 text-slate-500 text-right text-xs sm:text-sm whitespace-nowrap">
                                                {new Date(item.date).toLocaleDateString()}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DocumentsPage;
