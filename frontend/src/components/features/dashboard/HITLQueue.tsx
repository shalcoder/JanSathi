import React, { useState, useEffect } from 'react';
import { AlertTriangle, UserCheck, XCircle, Clock, Eye, RefreshCw, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@clerk/nextjs';
import { getHitlCases, resolveHitlCase, HitlCase } from '@/services/api';

export default function HITLQueue() {
  const { getToken } = useAuth();
  const [queue, setQueue] = useState<HitlCase[]>([]);
  const [isPolling, setIsPolling] = useState(true);
  const [resolvingId, setResolvingId] = useState<string | null>(null);

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
        console.error("Failed to fetch HITL cases", err);
      }
    };

    if (isPolling) {
      fetchCases();
      interval = setInterval(fetchCases, 3000);
    }
    return () => clearInterval(interval);
  }, [isPolling, getToken]);

  const handleResolve = async (id: string, action: 'approve' | 'reject') => {
    setResolvingId(id);
    try {
      const token = await getToken();
      await resolveHitlCase(id, action, token);
      // Immediately remove from UI
      setQueue(q => q.filter(item => item.id !== id));
    } catch (err) {
      console.error(`Failed to ${action} case`, err);
    } finally {
      setResolvingId(null);
    }
  };

  return (
    <div className="flex flex-col h-full space-y-6 max-w-5xl mx-auto w-full">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight flex items-center gap-3">
            <AlertTriangle className="w-6 h-6 text-red-500" />
            Human-In-The-Loop (HITL) Queue
          </h2>
          <p className="text-secondary-foreground text-sm mt-1">Manual verification layer for L4 escalations. Safety first.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={() => setIsPolling(!isPolling)} className={`p-2 rounded-xl transition-colors ${isPolling ? 'text-emerald-500 bg-emerald-500/10' : 'text-secondary-foreground bg-secondary'}`}>
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
           {queue.map((item, i) => (
             <motion.div 
               initial={{ opacity: 0, scale: 0.95 }}
               animate={{ opacity: 1, scale: 1 }}
               exit={{ opacity: 0, scale: 0.95 }}
               transition={{ delay: i * 0.05 }}
               key={item.id} 
               className="bg-card/60 backdrop-blur-xl border border-red-500/20 rounded-2xl p-6 flex flex-col items-start gap-6 hover:shadow-[0_8px_30px_rgba(239,68,68,0.1)] hover:border-red-500/40 transition-all relative overflow-hidden group"
             >
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                    <AlertTriangle className="w-24 h-24 text-red-500" />
                </div>
                <div className="w-full relative z-10">
                   <div className="flex items-center gap-3 mb-2 flex-wrap">
                      <span className="font-mono text-xs font-bold bg-secondary/80 px-2 py-1 rounded">Session: {item.session_id.split('-')[1] || item.session_id}</span>
                      <span className={`text-[10px] uppercase font-bold tracking-widest px-2 py-1 rounded-full ${item.confidence < 0.5 ? 'bg-red-500/20 text-red-500 border border-red-500/30' : 'bg-amber-500/20 text-amber-500 border border-amber-500/30'}`}>
                         Conf: {(item.confidence * 100).toFixed(0)}%
                      </span>
                      <span className="text-xs text-secondary-foreground flex items-center gap-1 ml-auto">
                        <Clock className="w-3 h-3" /> 
                        {new Date(item.created_at).toLocaleTimeString()}
                      </span>
                   </div>
                   
                   <div className="flex flex-col gap-4 mt-6 w-full bg-[#0a0a0a] border border-white/5 rounded-xl p-5 shadow-inner">
                      {/* User Bubble */}
                      <div className="flex gap-3 items-end">
                         <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center shrink-0 border border-zinc-700">
                            <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">{item.session_id.split('-')[1]?.substring(0, 2) || 'US'}</span>
                         </div>
                         <div className="bg-zinc-800/80 p-3 rounded-2xl rounded-bl-sm border border-zinc-700/50 max-w-[85%]">
                            <p className="text-sm text-zinc-200">&quot;{item.transcript}&quot;</p>
                         </div>
                      </div>
                      
                      {/* Agent Bubble */}
                      <div className="flex gap-3 justify-end items-end">
                         <div className="bg-emerald-500/10 p-3 rounded-2xl rounded-br-sm border border-emerald-500/20 max-w-[85%]">
                            <p className="text-sm font-mono text-emerald-400 font-medium">{item.response_text}</p>
                         </div>
                         <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 border border-emerald-500/30">
                            <span className="text-[10px] font-bold text-emerald-500">AI</span>
                         </div>
                      </div>
                   </div>
                </div>

                <div className="flex items-center justify-end gap-3 w-full border-t border-border/50 pt-4 mt-2 relative z-10">
                   <button disabled={resolvingId === item.id} className="flex-1 md:flex-none px-4 py-2 bg-secondary hover:bg-secondary/80 text-foreground font-bold rounded-lg text-sm transition-colors flex items-center justify-center gap-2">
                      <Eye className="w-4 h-4" /> Review
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
           ))}
         </AnimatePresence>
      </div>
    </div>
  );
}
