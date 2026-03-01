import React, { useState, useEffect } from 'react';
import { ShieldCheck, Lock, CheckCircle2, FileText, Database, RefreshCw } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import { getAuditLogs, AuditRecord } from '@/services/api';

export default function SecurityAuditPanel() {
  const { getToken } = useAuth();
  const [logs, setLogs] = useState<AuditRecord[]>([]);
  const [isPolling, setIsPolling] = useState(true);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    const fetchLogs = async () => {
      try {
        const token = await getToken();
        const data = await getAuditLogs(token);
        // show most recent first
        setLogs(data.reverse().slice(0, 50));
      } catch (err) {
        console.error("Failed to fetch audit logs", err);
      }
    };

    if (isPolling) {
      fetchLogs();
      interval = setInterval(fetchLogs, 3000);
    }
    return () => clearInterval(interval);
  }, [isPolling, getToken]);

  return (
    <div className="flex flex-col h-full space-y-6 max-w-5xl mx-auto w-full">
      <div>
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-3">
          <ShieldCheck className="w-6 h-6 text-emerald-500" />
          Security & Consent Audit (DPDP)
        </h2>
        <p className="text-secondary-foreground text-sm mt-1">Immutability, traceability, and verifiable DPDP compliance for every pipeline event.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
         {/* Compliance Pillars */}
         <div className="space-y-4">
            <div className="p-6 bg-card/60 backdrop-blur-xl border border-border/50 rounded-2xl flex gap-4 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-md hover:border-emerald-500/30 transition-all group overflow-hidden relative">
               <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
               <div className="mt-1 w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center shrink-0 border border-emerald-500/20 group-hover:scale-110 transition-transform relative z-10">
                  <Lock className="w-5 h-5 text-emerald-500" />
               </div>
               <div className="relative z-10">
                  <h3 className="font-bold mb-1 text-foreground">Layer 2 Auto-Masking</h3>
                  <p className="text-sm text-secondary-foreground leading-relaxed">All phone numbers and detected Aadhaar variables are stripped from the payload <span className="text-emerald-500 font-mono text-xs bg-emerald-500/10 px-1 rounded">*before*</span> LLM inferencing begins. The system only processes contextual intent.</p>
               </div>
            </div>
            
            <div className="p-6 bg-card/60 backdrop-blur-xl border border-border/50 rounded-2xl flex gap-4 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-md hover:border-blue-500/30 transition-all group overflow-hidden relative">
               <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
               <div className="mt-1 w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center shrink-0 border border-blue-500/20 group-hover:scale-110 transition-transform relative z-10">
                  <CheckCircle2 className="w-5 h-5 text-blue-500" />
               </div>
               <div className="relative z-10">
                  <h3 className="font-bold mb-1 text-foreground">Layer 8 Explicit Consent</h3>
                  <p className="text-sm text-secondary-foreground leading-relaxed">The workflow explicitly halts at state <span className="font-mono text-xs text-blue-400 bg-blue-500/10 px-1 rounded">AWAIT_CONSENT</span>. Unverified requests are hard-blocked by AWS API Gateway WAF rules.</p>
               </div>
            </div>
            
            <div className="p-6 bg-card/60 backdrop-blur-xl border border-border/50 rounded-2xl flex gap-4 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-md hover:border-purple-500/30 transition-all group overflow-hidden relative">
               <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
               <div className="mt-1 w-10 h-10 rounded-full bg-purple-500/10 flex items-center justify-center shrink-0 border border-purple-500/20 group-hover:scale-110 transition-transform relative z-10">
                  <Database className="w-5 h-5 text-purple-500" />
               </div>
               <div className="relative z-10">
                  <h3 className="font-bold mb-1 text-foreground">Data Sovereignty</h3>
                  <p className="text-sm text-secondary-foreground leading-relaxed">Database clusters and AI deployments instances operate strictly within <span className="font-mono text-xs text-purple-400 bg-purple-500/10 px-1 rounded">ap-south-1</span> (Mumbai). No cross-border data transfer.</p>
               </div>
            </div>
         </div>

         {/* Immutable Log Stream */}
         {/* Immutable Log Stream */}
         <div className="bg-[#0a0a0a] rounded-2xl border border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.1)] flex flex-col overflow-hidden relative">
            <div className="absolute inset-0 bg-[linear-gradient(rgba(16,185,129,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(16,185,129,0.03)_1px,transparent_1px)] bg-[size:20px_20px] pointer-events-none"></div>
            <div className="p-4 border-b border-white/10 bg-black/50 flex items-center justify-between backdrop-blur-md relative z-10">
               <div className="flex items-center gap-2">
                 <FileText className="w-4 h-4 text-emerald-400" />
                 <h3 className="font-bold text-sm text-emerald-400 tracking-widest uppercase">Immutable Hash Chain</h3>
               </div>
               <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
               </span>
            </div>
            <div className="flex-1 p-0 overflow-y-auto max-h-[400px] relative z-10">
               <table className="w-full text-left text-[11px] md:text-xs">
                  <thead className="bg-[#0f1411] border-b border-white/5 font-mono text-emerald-600 sticky top-0 uppercase tracking-widest">
                     <tr>
                        <th className="px-4 py-3 font-bold">Time (UTC)</th>
                        <th className="px-4 py-3 font-bold">Action</th>
                        <th className="px-4 py-3 font-bold">Security Guard</th>
                        <th className="px-4 py-3 font-bold text-right">SHA-256</th>
                     </tr>
                  </thead>
                  <tbody className="font-mono divide-y divide-white/5 bg-[#0a0a0a]/80">
                     {logs.map((log, i) => {
                        const timeStr = new Date(log.ts).toTimeString().split(' ')[0];
                        const hashDisplay = log.integrity_hash ? log.integrity_hash.substring(0, 10) + '...' : 'pending';
                        const piiDisplay = Object.keys(log.payload || {}).join(', ') || 'verified';
                        
                        return (
                          <tr key={log.record_id || i} className="hover:bg-emerald-500/5 transition-colors group">
                             <td className="px-4 py-3 text-emerald-400/70 group-hover:text-emerald-400 transition-colors">{timeStr}</td>
                             <td className="px-4 py-3 text-zinc-300">{log.record_type.toUpperCase()}</td>
                             <td className="px-4 py-3 text-indigo-400">{piiDisplay}</td>
                             <td className="px-4 py-3 text-right text-emerald-500/50 group-hover:text-emerald-400 transition-colors">{hashDisplay}</td>
                          </tr>
                        );
                     })}
                  </tbody>
               </table>
            </div>
            <div className="p-3 bg-[#0f1411] border-t border-emerald-500/10 text-center relative z-10">
               <p className="text-[10px] text-emerald-600/60 uppercase tracking-widest font-bold">AWS QLDB Formatted Log Stream</p>
            </div>
         </div>
      </div>
    </div>
  );
}
