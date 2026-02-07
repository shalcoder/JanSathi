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
        <div className="h-full flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2 underline decoration-blue-500/30">Government Intelligence</h2>
                    <p className="text-slate-400">Review official guidelines or upload your own documents for analysis.</p>
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
                        className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-bold transition-all shadow-xl shadow-blue-600/20 active:scale-95 disabled:opacity-50"
                    >
                        {isUploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Upload className="w-5 h-5" />}
                        {isUploading ? 'Uploading...' : 'Upload Document'}
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
                    <p>No documents found. Upload one to get started.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {documents.map((doc) => (
                        <div key={doc.id} className="glass-panel p-5 rounded-3xl border border-white/5 group hover:border-blue-500/30 transition-all relative">
                            <div className="flex items-start justify-between mb-4">
                                <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center">
                                    <FileText className="w-6 h-6 text-blue-500" />
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                                        <ShieldCheck className="w-3 h-3 text-emerald-500" />
                                        <span className="text-[10px] font-bold text-emerald-500 uppercase">{doc.status}</span>
                                    </div>
                                    <button
                                        onClick={() => handleDelete(doc.id)}
                                        className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                                        title="Delete Document"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                            <h3 className="font-bold text-slate-100 mb-1 truncate" title={doc.name}>{doc.name}</h3>
                            <p className="text-xs text-slate-500 mb-6">{doc.date} • {doc.size}</p>

                            <div className="flex gap-2">
                                <button
                                    onClick={() => handleView(doc)}
                                    className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-xs font-semibold transition-all"
                                >
                                    <Eye className="w-4 h-4" />
                                    View
                                </button>
                                <button
                                    onClick={() => handleDownload(doc)}
                                    className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-xs font-semibold transition-all shadow-lg shadow-blue-500/20"
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
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <Clock className="w-5 h-5 text-blue-400" />
                    Drishti Vision History
                </h2>
                <div className="glass-panel rounded-3xl overflow-hidden border border-white/5">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-white/5 text-slate-400 font-medium">
                            <tr>
                                <th className="px-6 py-4">Image Analysis</th>
                                <th className="px-6 py-4">Language</th>
                                <th className="px-6 py-4">Result Summary</th>
                                <th className="px-6 py-4 text-right">Date</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {[1, 2].map((i) => (
                                <tr key={i} className="hover:bg-white/5 transition-colors cursor-pointer group">
                                    <td className="px-6 py-4 flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-lg bg-slate-800 border border-white/10 overflow-hidden">
                                            <div className="w-full h-full bg-gradient-to-br from-blue-500/20 to-purple-500/20"></div>
                                        </div>
                                        <span className="font-medium text-slate-300">Document Scan #{i}</span>
                                    </td>
                                    <td className="px-6 py-4 text-slate-400 capitalize">{i === 1 ? 'Hindi' : 'English'}</td>
                                    <td className="px-6 py-4 text-slate-400 truncate max-w-[200px]">Summary of government notice regarding...</td>
                                    <td className="px-6 py-4 text-slate-500 text-right">2 hours ago</td>
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
