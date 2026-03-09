import React, { useState, useEffect } from 'react';
import { AlertTriangle, UserCheck, XCircle, Clock, Eye, RefreshCw, Loader2, FileText, Phone, Banknote } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth, getToken } from '@/hooks/useAuth';
import { getHitlCases, resolveHitlCase, HitlCase } from '@/services/api';

// Confidence label helpers
function confLabel(conf: number) {
  if (conf >= 0.8) return { text: 'High Risk', color: 'bg-red-500/20 text-red-500 border-red-500/30' };
  if (conf >= 0.5) return { text: 'Medium Risk', color: 'bg-amber-500/20 text-amber-500 border-amber-500/30' };
  return { text: 'Low Confidence', color: 'bg-slate-500/20 text-slate-400 border-slate-500/30' };
}

function getSchemeName(item: HitlCase): string {
  // Try benefit_receipt.scheme_name, fallback to parsing transcript
  const receipt = (item as any).benefit_receipt;
  if (receipt?.scheme_name) return receipt.scheme_name;
  // guess from transcript
  const t = (item.transcript || '').toLowerCase();
  if (t.includes('kisan') || t.includes('farmer')) return 'PM-KISAN';
  if (t.includes('ayushman') || t.includes('health')) return 'Ayushman Bharat';
  if (t.includes('awas') || t.includes('housing')) return 'PM Awas Yojana';
  if (t.includes('shram') || t.includes('labour')) return 'e-Shram';
  return 'Government Scheme';
}

function getCitizenName(item: HitlCase): string {
  const slots = (item as any).slots as Record<string, string> | undefined;
  return slots?.name || slots?.full_name || `Citizen ${item.session_id.split('-')[1]?.slice(0, 6).toUpperCase() || '???'}`;
}

export default function HITLQueue() {
  const { user, loading: isLoaded } = useAuth();
    
  const [queue, setQueue] = useState<HitlCase[]>([]);
  const [isPolling, setIsPolling] = useState(true);
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    const fetchCases = async () => {
      try {
        const token = await getToken();
        const data = await getHitlCases(token);
        if (Array.isArray(data)) {
          setQueue(data);
        }
      } catch (err) {
        // Silently handle - getHitlCases already returns empty array on error
        if (process.env.NODE_ENV === 'development') {
          console.debug("HITL cases polling (no pending cases)");
        }
      }
    };

    if (isPolling) {
      fetchCases();
      interval = setInterval(fetchCases, 3000);
    }
    return () => clearInterval(interval);
  }, [isPolling]);

  const handleResolve = async (id: string, action: 'approve' | 'reject') => {
    setResolvingId(id);
    try {
      const token = await getToken();
      await resolveHitlCase(id, action, token);
      setQueue(q => q.filter(item => item.id !== id));
    } catch (err) {
      console.error(`Failed to ${action} case`, err);
    } finally {
      setResolvingId(null);
    }
  };

  return (
    <div className="flex flex-col h-full space-y-6 max-w-5xl mx-auto w-full">
      <div className="flex justify-between items-center flex-wrap gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight flex items-center gap-3">
            <AlertTriangle className="w-6 h-6 text-red-500" />
            Human-In-The-Loop (HITL) Queue
          </h2>
          <p className="text-secondary-foreground text-sm mt-1">Manual verification layer for L4 escalations. Safety first.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsPolling(!isPolling)}
            title={isPolling ? 'Pause polling' : 'Resume polling'}
            aria-label={isPolling ? 'Pause polling' : 'Resume polling'}
            className={`p-2 rounded-xl transition-colors ${isPolling ? 'text-emerald-500 bg-emerald-500/10' : 'text-secondary-foreground bg-secondary'}`}
          >
            <RefreshCw className={`w-4 h-4 ${isPolling ? 'animate-spin-slow' : ''}`} />
          </button>
          <div className="px-4 py-2 bg-red-500/10 text-red-500 rounded-lg text-sm font-bold border border-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.2)]">
            <span className="flex h-2 w-2 relative inline-block mr-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
            </span>
            {queue.length} Pending Cases
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
         {queue.length === 0 && (
           <div className="p-12 text-center text-secondary-foreground font-bold tracking-widest uppercase opacity-50 border border-dashed border-border/50 rounded-2xl">
              Queue is empty. Operations normal.
           </div>
         )}
         <AnimatePresence>
           {queue.map((item, i) => {
             const risk = confLabel(item.confidence);
             const schemeName = getSchemeName(item);
             const citizenName = getCitizenName(item);
             const isExpanded = expandedId === item.id;
             const confPct = Math.round(item.confidence * 100);

             return (
               <motion.div
                 initial={{ opacity: 0, scale: 0.95 }}
                 animate={{ opacity: 1, scale: 1 }}
                 exit={{ opacity: 0, scale: 0.95 }}
                 transition={{ delay: i * 0.05 }}
                 key={item.id}
                 className="bg-card/60 backdrop-blur-xl border border-red-500/20 rounded-2xl overflow-hidden hover:shadow-[0_8px_30px_rgba(239,68,68,0.1)] hover:border-red-500/40 transition-all"
               >
                 {/* Case header */}
                 <div className="px-6 py-4 flex items-start gap-4 flex-wrap">
                   {/* Scheme + citizen info */}
                   <div className="flex-1 min-w-0">
                     <div className="flex items-center gap-2 flex-wrap mb-1">
                       <span className="text-base font-bold text-foreground truncate">{schemeName}</span>
                       <span className={`text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full border ${risk.color}`}>
                         {risk.text}
                       </span>
                     </div>
                     <div className="flex items-center gap-3 text-sm text-secondary-foreground flex-wrap">
                       <span className="flex items-center gap-1.5">
                         <FileText className="w-3.5 h-3.5" />
                         {citizenName}
                       </span>
                       <span className="font-mono text-xs bg-secondary/80 px-2 py-0.5 rounded">
                         {item.session_id.slice(0, 12)}
                       </span>
                       <span className="flex items-center gap-1">
                         <Clock className="w-3 h-3" />
                         {new Date(item.created_at).toLocaleTimeString()}
                       </span>
                     </div>
                   </div>

                   {/* Confidence meter */}
                   <div className="w-32 shrink-0">
                     <div className="flex justify-between text-[10px] font-bold mb-1">
                       <span className="text-secondary-foreground uppercase tracking-wider">Confidence</span>
                       <span className={confPct >= 80 ? 'text-emerald-500' : confPct >= 50 ? 'text-amber-500' : 'text-red-500'}>
                         {confPct}%
                       </span>
                     </div>
                     <div className="w-full h-1.5 rounded-full bg-secondary overflow-hidden">
                       <div
                         className={`h-full rounded-full transition-all ${confPct >= 80 ? 'bg-emerald-500' : confPct >= 50 ? 'bg-amber-500' : 'bg-red-500'} w-[var(--conf-pct)]`}
                         // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
                         {...{ style: { '--conf-pct': `${confPct}%` } as React.CSSProperties }}
                       />
                     </div>
                   </div>
                 </div>

                 {/* Benefit amount badge */}
                 {(item as any).benefit_receipt?.eligible && (
                   <div className="px-6 pb-3">
                     <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-lg">
                       <Banknote className="w-3.5 h-3.5" /> Eligible — direct transfer pending review
                     </span>
                   </div>
                 )}

                 {/* Conversation bubble (collapsible) */}
                 <div
                   className="mx-6 mb-4 flex flex-col gap-3 bg-[#0a0a0a] border border-white/5 rounded-xl p-5 cursor-pointer"
                   onClick={() => setExpandedId(isExpanded ? null : item.id)}
                   role="button"
                   tabIndex={0}
                   aria-label="Toggle conversation detail"
                   onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') setExpandedId(isExpanded ? null : item.id); }}
                 >
                   <div className="flex gap-3 items-end">
                     <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center shrink-0 border border-zinc-700 text-[10px] font-bold text-zinc-400">
                       {citizenName.slice(0, 2).toUpperCase()}
                     </div>
                     <div className="bg-zinc-800/80 p-3 rounded-2xl rounded-bl-sm border border-zinc-700/50 max-w-[85%]">
                       <p className="text-sm text-zinc-200">&quot;{item.transcript}&quot;</p>
                     </div>
                   </div>

                   {isExpanded && (
                     <motion.div
                       initial={{ opacity: 0, y: 4 }}
                       animate={{ opacity: 1, y: 0 }}
                       className="flex gap-3 justify-end items-end"
                     >
                       <div className="bg-emerald-500/10 p-3 rounded-2xl rounded-br-sm border border-emerald-500/20 max-w-[85%]">
                         <p className="text-sm font-mono text-emerald-400 font-medium">{item.response_text}</p>
                       </div>
                       <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 border border-emerald-500/30 text-[10px] font-bold text-emerald-500">
                         AI
                       </div>
                     </motion.div>
                   )}
                 </div>

                 {/* Action bar */}
                 <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-border/50 bg-background/20">
                   <button
                     disabled={resolvingId === item.id}
                     onClick={() => setExpandedId(isExpanded ? null : item.id)}
                     className="flex-1 md:flex-none px-4 py-2 bg-secondary hover:bg-secondary/80 text-foreground font-bold rounded-lg text-sm transition-colors flex items-center justify-center gap-2"
                   >
                     <Eye className="w-4 h-4" /> {isExpanded ? 'Collapse' : 'Review'}
                   </button>
                   <button
                     onClick={() => handleResolve(item.id, 'approve')}
                     disabled={resolvingId === item.id}
                     className="flex-1 md:flex-none px-4 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-600 font-bold rounded-lg text-sm transition-colors flex items-center justify-center gap-2"
                   >
                     {resolvingId === item.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <UserCheck className="w-4 h-4" />}
                     Approve
                   </button>
                   <button
                     onClick={() => handleResolve(item.id, 'reject')}
                     disabled={resolvingId === item.id}
                     className="flex-1 md:flex-none px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-500 font-bold rounded-lg text-sm transition-colors flex items-center justify-center gap-2"
                   >
                     {resolvingId === item.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <XCircle className="w-4 h-4" />}
                     Reject
                   </button>
                 </div>
               </motion.div>
             );
           })}
         </AnimatePresence>
      </div>
    </div>
  );
}

