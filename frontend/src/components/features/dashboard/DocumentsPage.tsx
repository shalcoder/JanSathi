import React, { useState, useRef } from 'react';
import { FileText, Download, Eye, Clock, ShieldCheck, Upload, Loader2, Camera, Trash2 } from 'lucide-react';
import { analyzeImage } from '@/services/api';

const DocumentsPage = () => {
    const [isUploading, setIsUploading] = useState(false);
    const [visionResult, setVisionResult] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Converted to state to support deletion
    const [documents, setDocuments] = useState([
        { id: 1, name: "PM-Kisan Scheme Guidelines.pdf", date: "2024-01-15", size: "1.2 MB", status: "Verified" },
        { id: 2, name: "Ration Card Application Form.pdf", date: "2024-02-01", size: "850 KB", status: "Official" },
        { id: 3, name: "Digital Health ID Info.pdf", date: "2023-11-20", size: "2.4 MB", status: "Information" },
        { id: 4, name: "Crop Insurance Policy 2024.pdf", date: "2024-02-05", size: "3.1 MB", status: "Verified" },
    ]);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setIsUploading(true);
            try {
                // Simulate upload delay
                await new Promise(resolve => setTimeout(resolve, 1500));

                // Add new document to state
                const newDoc = {
                    id: Date.now(),
                    name: file.name,
                    date: new Date().toISOString().split('T')[0],
                    size: (file.size / 1024 / 1024).toFixed(2) + " MB",
                    status: "Uploaded"
                };
                setDocuments(prev => [newDoc, ...prev]);

                // Optional: Analyze after upload if needed
                // const data = await analyzeImage(file, 'hi');
                // setVisionResult(data.analysis.text);
            } catch (err) {
                alert("Upload failed. Please check your connection.");
            } finally {
                setIsUploading(false);
                if (fileInputRef.current) fileInputRef.current.value = '';
            }
        }
    };

    const handleDelete = (id: number) => {
        if (confirm("Are you sure you want to delete this document?")) {
            setDocuments(prev => prev.filter(doc => doc.id !== id));
        }
    };

    const handleView = (doc: any) => {
        alert(`Viewing ${doc.name} (Simulated)`);
        // In a real app, this would open a modal with the PDF viewer
    };

    const handleDownload = (doc: any) => {
        alert(`Downloading ${doc.name} (Simulated)`);
        // In a real app, this would trigger a file download
    };

    return (
        <div className="min-h-full flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
                <div>
                    <h2 className="text-4xl font-black text-white mb-3 transition-colors tracking-tighter">Government Intelligence</h2>
                    <p className="text-slate-400 font-bold transition-colors">Review official guidelines or upload your own documents for analysis.</p>
                </div>
                <div className="flex gap-3">
                    <input
                        type="file"
                        accept=".pdf,.jpg,.jpeg,.png"
                        className="hidden"
                        ref={fileInputRef}
                        onChange={handleFileUpload}
                    />
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading}
                        className="flex items-center justify-center gap-3 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-[1.8rem] font-black transition-all shadow-xl shadow-blue-600/30 active:scale-95 disabled:opacity-50 group relative overflow-hidden"
                    >
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-[shimmer_2s_infinite]"></div>
                        {isUploading ? <Loader2 className="w-5 h-5 animate-spin relative z-10" /> : <Upload className="w-5 h-5 relative z-10" />}
                        <span className="relative z-10">{isUploading ? 'Uploading Intelligence...' : 'Upload Document'}</span>
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

            {documents.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-12 glass-panel rounded-3xl border border-dashed border-white/10 text-slate-500">
                    <Upload className="w-12 h-12 mb-4 opacity-50" />
                    <p className="font-bold">No documents found. Upload one to get started.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-10">
                    {documents.map((doc) => (
                        <div key={doc.id} className="glass-panel p-8 rounded-[3rem] group hover:border-blue-500/30 transition-all duration-500 relative shadow-premium hover:shadow-premium-hover bg-slate-900 border border-white/5">
                            <div className="flex items-start justify-between mb-6">
                                <div className="w-14 h-14 rounded-2xl bg-blue-500/10 flex items-center justify-center border border-blue-500/20 shadow-inner group-hover:scale-110 transition-transform">
                                    <FileText className="w-7 h-7 text-blue-500" />
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 shadow-sm">
                                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                                        <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">{doc.status}</span>
                                    </div>
                                    <button
                                        onClick={() => handleDelete(doc.id)}
                                        className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
                                        title="Delete Document"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                            <h3 className="font-black text-xl text-white mb-2 truncate transition-colors tracking-tight" title={doc.name}>{doc.name}</h3>
                            <div className="flex items-center gap-2 mb-8">
                                <Clock className="w-3 h-3 text-slate-400" />
                                <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest">{doc.date} • {doc.size}</p>
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={() => handleView(doc)}
                                    className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-xs font-black text-white transition-all shadow-sm active:scale-95"
                                >
                                    <Eye className="w-4 h-4" />
                                    View
                                </button>
                                <button
                                    onClick={() => handleDownload(doc)}
                                    className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-xs font-black text-white transition-all shadow-xl shadow-blue-500/20 active:scale-95"
                                >
                                    <Download className="w-4 h-4" />
                                    Download
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Drishti Vision Records */}
            <div className="mt-8">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2 transition-colors">
                    <Clock className="w-5 h-5 text-blue-400" />
                    Drishti Vision History
                </h2>
                <div className="glass-panel rounded-[2.5rem] overflow-hidden shadow-premium border border-white/5 bg-slate-900">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-white/5 text-slate-500 font-black uppercase tracking-[0.2em] text-[10px] border-b border-white/5">
                            <tr>
                                <th className="px-8 py-5">Image Analysis</th>
                                <th className="px-8 py-5">Language</th>
                                <th className="px-8 py-5">Result Summary</th>
                                <th className="px-8 py-5 text-right">Date</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {[1, 2].map((i) => (
                                <tr key={i} className="hover:bg-white/[0.02] transition-colors cursor-pointer group text-slate-200">
                                    <td className="px-8 py-5 flex items-center gap-4">
                                        <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 overflow-hidden shadow-inner group-hover:scale-105 transition-transform duration-500">
                                            <div className="w-full h-full bg-gradient-to-br from-blue-500/20 to-purple-500/20"></div>
                                        </div>
                                        <span className="font-black tracking-tight text-base">Document Scan #{i}</span>
                                    </td>
                                    <td className="px-8 py-5">
                                        <span className="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest bg-blue-500/10 text-blue-400 border border-blue-500/20">
                                            {i === 1 ? 'Hindi' : 'English'}
                                        </span>
                                    </td>
                                    <td className="px-8 py-5 truncate max-w-[200px] font-bold text-slate-400">Summary of government notice regarding...</td>
                                    <td className="px-8 py-5 text-slate-500 text-right font-black text-xs uppercase tracking-widest">2 hours ago</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default DocumentsPage;
