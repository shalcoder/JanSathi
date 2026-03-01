import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, AlertTriangle, CheckCircle2, RefreshCw, Clock, Mic, FileText, Radio } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import { getIvrSessions, IvrSession } from '@/services/api';

export default function IVRConsole() {
  const { getToken } = useAuth();
  const [activeTab, setActiveTab] = useState<'live' | 'history'>('live');
  const [sessions, setSessions] = useState<IvrSession[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(true);

  // Poll for active sessions
  useEffect(() => {
    let interval: NodeJS.Timeout;
    const fetchSessions = async () => {
      try {
        const token = await getToken();
        // Allow unauthenticated fallback for demo purposes or generic access
        const data = await getIvrSessions(token);
        if (Array.isArray(data)) {
          setSessions(data);
        }
      } catch (err) {
        console.error("Failed to poll IVR sessions:", err);
      }
    };

    if (activeTab === 'live' && isPolling) {
      fetchSessions(); // initial hit
      interval = setInterval(fetchSessions, 3000); // 3s polling
    }

    return () => { if (interval) clearInterval(interval); };
  }, [activeTab, isPolling, getToken]);

  const selectedSession = sessions.find(s => s.session_id === selectedSessionId);

  return (
    <div className="flex flex-col h-full space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight flex items-center gap-3">
            <Radio className="w-6 h-6 text-amber-500" />
            IVR Command Console
          </h2>
          <p className="text-secondary-foreground text-sm mt-1">Live monitoring and control of the Agentic 10-Layer Pipeline.</p>
        </div>
        
        {/* Toggle Live/History */}
        <div className="bg-secondary/50 p-1 rounded-xl flex items-center border border-border/50">
          <button 
            onClick={() => setActiveTab('live')}
            className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${activeTab === 'live' ? 'bg-background text-foreground shadow' : 'text-secondary-foreground hover:text-foreground'}`}
          >
            Live Sessions
          </button>
          <button 
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${activeTab === 'history' ? 'bg-background text-foreground shadow' : 'text-secondary-foreground hover:text-foreground'}`}
          >
            History
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 flex-1 min-h-[500px]">
        {/* Active Sessions List */}
        <div className="col-span-1 border border-border/50 bg-card/60 backdrop-blur-xl rounded-2xl flex flex-col overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
          <div className="p-4 border-b border-border/50 bg-secondary/20 flex justify-between items-center">
            <h3 className="font-bold text-sm uppercase tracking-wider">Active Calls ({sessions.length})</h3>
            <div className="flex gap-2 items-center">
              <button onClick={() => setIsPolling(!isPolling)} className={`p-1.5 rounded transition-colors ${isPolling ? 'text-emerald-500 hover:bg-emerald-500/10' : 'text-secondary-foreground hover:bg-secondary'}`} title={isPolling ? "Pause Polling" : "Resume Polling"}>
                  <RefreshCw className={`w-4 h-4 ${isPolling ? 'animate-spin-slow' : ''}`} />
              </button>
              {isPolling && (
                <span className="flex h-3 w-3 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                </span>
              )}
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            {sessions.length === 0 && (
               <div className="p-8 text-center text-secondary-foreground text-xs uppercase tracking-widest font-bold opacity-50">
                  No active calls on line.
               </div>
            )}
            <AnimatePresence>
              {sessions.map((sess) => (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  key={sess.session_id} 
                  onClick={() => setSelectedSessionId(sess.session_id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all duration-300 relative overflow-hidden group ${selectedSessionId === sess.session_id ? 'bg-amber-500/10 border-amber-500/40 shadow-[0_4px_20px_rgba(245,158,11,0.15)] dark:bg-amber-500/20' : 'bg-card/50 border-border/50 hover:border-amber-500/30'}`}
                >
                  {selectedSessionId === sess.session_id && (
                      <div className="absolute inset-0 bg-gradient-to-r from-amber-500/5 to-transparent opacity-50"></div>
                  )}
                  <div className="flex justify-between items-start mb-2 relative z-10">
                    <div>
                      <p className="font-mono text-sm font-bold">{sess.caller_number}</p>
                      <p className="text-[10px] text-secondary-foreground uppercase font-bold tracking-widest">{sess.language === 'hi' ? 'Hindi' : sess.language === 'en' ? 'English' : sess.language} • {sess.channel}</p>
                    </div>
                    <span className="text-[10px] font-mono bg-secondary px-2 py-1 rounded truncate max-w-[80px]">{sess.session_id.split('-')[1] || sess.session_id}</span>
                  </div>
                  <div className="flex items-center justify-between mt-4">
                    <div className="flex items-center gap-2">
                      {sess.current_state === 'completed' ? <CheckCircle2 className="w-4 h-4 text-emerald-500" /> : <Activity className="w-4 h-4 text-amber-500 animate-pulse" />}
                      <span className="text-xs font-bold text-foreground capitalize">{sess.current_state.replace('_', ' ')}</span>
                    </div>
                    <div className="flex items-center gap-1 text-xs font-mono text-secondary-foreground">
                      <Clock className="w-3 h-3" /> 
                      {new Date(sess.last_seen).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>

        {/* Selected Session Detail */}
        <div className="col-span-1 xl:col-span-2 border border-border/50 bg-card/60 backdrop-blur-xl rounded-2xl flex flex-col overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
           <div className="p-6 flex-1 flex flex-col border-b border-border/50 bg-secondary/5 overflow-y-auto">
              {!selectedSession ? (
                <div className="m-auto text-center max-w-md">
                   <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center mx-auto mb-4">
                      <Mic className="w-8 h-8 text-secondary-foreground/50" />
                   </div>
                   <h3 className="text-xl font-bold mb-2">Session Detail Viewer</h3>
                   <p className="text-sm text-secondary-foreground leading-relaxed">Select an active session from the left panel to view live details.</p>
                </div>
              ) : (
                <div className="space-y-6">
                   <div className="flex justify-between items-start">
                     <div>
                       <h3 className="text-xl font-bold text-foreground mb-1">Session {selectedSession.session_id}</h3>
                       <p className="text-sm text-secondary-foreground">Caller: <span className="font-mono text-foreground font-bold">{selectedSession.caller_number}</span></p>
                     </div>
                     <span className="px-3 py-1 bg-amber-500/10 text-amber-500 font-bold text-xs uppercase tracking-widest rounded-full">
                       {selectedSession.current_state}
                     </span>
                   </div>
                   
                   <div className="p-6 bg-[#0a0a0a] border border-white/10 rounded-xl shadow-inner relative overflow-hidden">
                      <div className="absolute top-0 right-0 p-4 opacity-5">
                          <Mic className="w-16 h-16 text-amber-500" />
                      </div>
                      <h4 className="text-[10px] font-bold uppercase tracking-widest text-amber-500 mb-3">Live Transcript</h4>
                      <p className="text-emerald-400 font-mono text-sm leading-relaxed">
                        <span className="text-zinc-500 mr-2">&gt;</span>
                        {selectedSession.last_transcript || 'Listening for audio stream...'}
                        <span className="inline-block w-2 h-4 ml-1 bg-emerald-400 animate-pulse"></span>
                      </p>
                   </div>
                   
                   {/* Minimal placeholder for extracted slots or logs */}
                   <div className="p-4 bg-[#0a0a0a] border border-white/10 rounded-xl shadow-inner">
                      <h4 className="text-xs font-bold uppercase tracking-widest text-zinc-500 mb-3 flex items-center gap-2">
                        <FileText className="w-3 h-3 text-emerald-500" /> Telemetry Stream
                      </h4>
                      <div className="font-mono text-xs text-zinc-400 space-y-2">
                        <div className="flex gap-3">
                           <span className="text-zinc-600">[{new Date(selectedSession.last_seen).toISOString().split('T')[1].substring(0, 8)}]</span>
                           <span className="text-emerald-500">INFO</span>
                           <span>State transitioned to <span className="text-amber-400">{selectedSession.current_state}</span>.</span>
                        </div>
                      </div>
                   </div>
                </div>
              )}
           </div>
           {/* Action Bar */}
           <div className="p-4 bg-background flex gap-3 justify-end items-center">
              <span className="mr-auto text-xs font-mono text-secondary-foreground">
                {selectedSession ? `Monitoring ${selectedSession.session_id}` : 'Awaiting selection...'}
              </span>
              <button disabled={!selectedSession} className="px-4 py-2 text-sm font-bold bg-amber-500/10 text-amber-600 rounded-lg flex items-center gap-2 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-amber-500/20 transition-colors">
                <AlertTriangle className="w-4 h-4" /> Escalate to HITL
              </button>
               <button disabled={!selectedSession} className="px-4 py-2 text-sm font-bold bg-emerald-500/10 text-emerald-600 rounded-lg flex items-center gap-2 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-emerald-500/20 transition-colors">
                <CheckCircle2 className="w-4 h-4" /> Force Approve
              </button>
           </div>
        </div>
      </div>
    </div>
  );
}
