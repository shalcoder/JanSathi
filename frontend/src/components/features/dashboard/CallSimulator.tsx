import React, { useState } from 'react';
import { PlayCircle, FileTerminal, RefreshCw, Loader2, CheckCircle2, ChevronRight, Hash } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import { simulateIvrCall } from '@/services/api';

// Helper to avoid Next.js Strict Mode "impure function" warnings during render
const getRandomId = () => `sim_${Math.round(Date.now() / 1000).toString(16)}`;

export default function CallSimulator() {
  const [scenario, setScenario] = useState('pm-kisan-eligible');
  const [sessionData, setSessionData] = useState({ id: 'sim_init', time: new Date().toISOString() });
  const [isDispatching, setIsDispatching] = useState(false);
  const [dispatchSuccess, setDispatchSuccess] = useState(false);
  const { getToken } = useAuth();

  const generatePayload = () => {
    setSessionData({
      id: getRandomId(),
      time: new Date().toISOString()
    });
  };

  const handleScenarioChange = (newScenario: string) => {
    setScenario(newScenario);
    generatePayload();
    setDispatchSuccess(false);
  };

  const handleDispatch = async () => {
    setIsDispatching(true);
    setDispatchSuccess(false);
    try {
      const token = await getToken();
      
      // Map UI scenario to a basic Amazon Connect payload 
      // This mimics what AWS sends to our webhook
      const connectPayload = {
        contactId: sessionData.id,
        callerNumber: "+919876543210",
        language: "hi",
        consent: true,
        text: scenario === 'pm-kisan-eligible' ? "PM Kisan ka paisa check karna hai aur mere pas aadhaar hai" 
            : scenario === 'pm-kisan-missing' ? "PM Kisan ke liye apply karna hai lekin aadhaar nahi hai" 
            : "Mujhe kuch scheme ke bare mein batao samajh nahi aa raha", // HITL trigger
        sessionAttributes: {}
      };

      await simulateIvrCall(connectPayload, token);
      setDispatchSuccess(true);
      setTimeout(() => setDispatchSuccess(false), 3000);
      generatePayload(); // setup next
    } catch (err) {
      console.error("Failed to dispatch simulation:", err);
    } finally {
      setIsDispatching(false);
    }
  };

  return (
    <div className="flex flex-col h-full space-y-6 max-w-5xl mx-auto w-full">
      <div>
        <h2 className="text-3xl font-black tracking-tight flex items-center gap-3">
          <PlayCircle className="w-8 h-8 text-rose-500" />
          Call Simulator
        </h2>
        <p className="text-secondary-foreground text-base mt-2 font-medium">Inject strict L1 Event Payloads to perfectly replicate demo flows without telecom latency.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Scenario Selector */}
        <div className="col-span-1 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-secondary-foreground">Pre-built Scenarios</h3>
          
          <div className="space-y-3">
            {[
              { id: 'pm-kisan-eligible', name: '🟢 PM-Kisan (Eligible)', desc: 'Perfect green-path. Results in instant receipt.' },
              { id: 'pm-kisan-missing', name: '🔴 PM-Kisan (Missing Docs)', desc: 'Fails L4 Decision Rules. Triggers notification payload.' },
              { id: 'hitl-escalation', name: '🟠 Low Confidence (HITL)', desc: 'Intent unclear. Escalates to human verifier queue.' },
            ].map(s => (
              <button 
                key={s.id}
                onClick={() => handleScenarioChange(s.id)}
                className={`w-full text-left p-5 rounded-2xl border transition-all duration-300 group ${scenario === s.id ? 'bg-rose-500/10 border-rose-500/30 shadow-[0_4px_20px_rgba(244,63,94,0.1)]' : 'bg-card/60 backdrop-blur-xl border-border/50 hover:border-border hover:shadow-md'}`}
              >
                <div className="flex justify-between items-center mb-2">
                    <div className="font-bold text-sm text-foreground">{s.name}</div>
                    {scenario === s.id && <CheckCircle2 className="w-4 h-4 text-rose-500 shrink-0" />}
                </div>
                <div className="text-xs text-secondary-foreground leading-relaxed">{s.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Payload Editor */}
        <div className="col-span-1 md:col-span-2 border border-border/50 bg-[#0a0a0a] rounded-2xl flex flex-col overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.12)]">
          <div className="p-4 border-b border-white/10 bg-white/5 flex justify-between items-center backdrop-blur-md">
            <h3 className="font-bold text-sm flex items-center gap-2 text-white">
                <FileTerminal className="w-4 h-4 text-rose-500" /> 
                <span className="tracking-wide">Event Payload Injector</span>
            </h3>
            <div className="flex gap-2">
              <button onClick={generatePayload} className="p-1.5 text-zinc-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors" title="Regenerate Session ID">
                  <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="flex-1 p-6 overflow-y-auto font-mono text-xs md:text-sm text-emerald-400/90 leading-relaxed bg-[#0a0a0a] select-text">
            <span>{`{`}</span><br/>
            <span className="pl-4 text-rose-400">&quot;ContactId&quot;</span>: <span className="text-amber-300">&quot;{sessionData.id}&quot;</span>,<br/>
            <span className="pl-4 text-rose-400">&quot;Parameters&quot;</span>: {`{`}<br/>
            <span className="pl-8 text-rose-400">&quot;callerNumber&quot;</span>: <span className="text-amber-300">&quot;+919876543210&quot;</span>,<br/>
            <span className="pl-8 text-rose-400">&quot;language&quot;</span>: <span className="text-amber-300">&quot;hi&quot;</span>,<br/>
            <span className="pl-8 text-rose-400">&quot;consentGiven&quot;</span>: <span className="text-indigo-400">true</span>,<br/>
            <span className="pl-8 text-rose-400">&quot;transcript&quot;</span>: <span className="text-amber-300">&quot;{
                scenario === 'pm-kisan-eligible' ? "PM Kisan ka paisa check karna hai aur mere pas aadhaar hai" 
                : scenario === 'pm-kisan-missing' ? "PM Kisan ke liye apply karna hai lekin aadhaar nahi hai" 
                : "Mujhe kuch scheme ke bare mein batao samajh nahi aa raha"
            }&quot;</span><br/>
            <span className="pl-4">{`}`}</span>,<br/>
            <span className="pl-4 text-rose-400">&quot;Timestamp&quot;</span>: <span className="text-amber-300">&quot;{sessionData.time}&quot;</span><br/>
            <span>{`}`}</span>
          </div>

          <div className="p-4 border-t border-white/10 bg-white/5 flex items-center justify-between backdrop-blur-md">
            <div className="flex items-center gap-2 text-zinc-400 text-xs">
                <Hash className="w-4 h-4" />
                <span>Target: POST /api/v1/ivrhook</span>
            </div>
            
            <button 
              onClick={handleDispatch}
              disabled={isDispatching}
              className={`
                px-8 py-3 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg
                ${dispatchSuccess ? 'bg-emerald-500 text-white shadow-emerald-500/20' 
                  : isDispatching ? 'bg-secondary text-secondary-foreground cursor-not-allowed' 
                  : 'bg-rose-500 hover:bg-rose-600 text-white active:scale-95 shadow-rose-500/20'}
              `}
            >
              {isDispatching ? <Loader2 className="w-5 h-5 animate-spin" /> : 
               dispatchSuccess ? <CheckCircle2 className="w-5 h-5" /> : 
               <>Inject Payload <ChevronRight className="w-4 h-4" /></>}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
