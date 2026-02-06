'use client';

import React from 'react';
import { FileText, Download, Eye, Clock, ShieldCheck } from 'lucide-react';

const DocumentsPage = () => {
    const documents = [
        { id: 1, name: "PM-Kisan Scheme Guidelines.pdf", date: "2024-01-15", size: "1.2 MB", status: "Verified" },
        { id: 2, name: "Ration Card Application Form.pdf", date: "2024-02-01", size: "850 KB", status: "Official" },
        { id: 3, name: "Digital Health ID Info.pdf", date: "2023-11-20", size: "2.4 MB", status: "Information" },
        { id: 4, name: "Crop Insurance Policy 2024.pdf", date: "2024-02-05", size: "3.1 MB", status: "Verified" },
    ];

    return (
        <div className="h-full flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-2">Government Documents</h2>
                    <p className="text-slate-400">Official guidelines and forms for various citizen services.</p>
                </div>
                <div className="flex gap-3">
                    <div className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs font-medium">
                        <Clock className="w-4 h-4 text-blue-400" />
                        <span>Last Updated: Today</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {documents.map((doc) => (
                    <div key={doc.id} className="glass-panel p-5 rounded-3xl border border-white/5 group hover:border-blue-500/30 transition-all">
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
