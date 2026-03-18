'use client';

import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, 
  RotateCcw, 
  ChevronRight, 
  MessageSquare, 
  ShieldCheck, 
  Zap, 
  Database, 
  Activity, 
  Cpu, 
  Upload, 
  Send,
  Terminal,
  LayoutDashboard,
  RefreshCw
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Components
import Avatar from '@/components/Avatar';
import DiffViewer from '@/components/DiffViewer';
import Mermaid from '@/components/Mermaid';
import ExecutiveDashboard from '@/components/ExecutiveDashboard';

/** Utility for Tailwind classes */
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const SUGGESTIONS = [
  { label: "Executive Insights", prompt: "show executive report", icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: "Analyze codebase", prompt: "analyze corpus", icon: <Database className="w-4 h-4" /> },
  { label: "Review engine", prompt: "review engine.py", icon: <Terminal className="w-4 h-4" /> },
  { label: "Comparative Audit", prompt: "compare engine.py vs main.py", icon: <ShieldCheck className="w-4 h-4" /> },
];

// --- Interfaces ---
interface ReasoningStep {
  step_id: string;
  intent: string;
  action: string;
  confidence: number;
  output_summary: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  trace?: ReasoningStep[];
  level?: string;
  tone?: string;
  confidence?: number;
  meta?: any;
  type?: string;
}

export default function PrimersIntelligence() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [showTrace, setShowTrace] = useState<string | null>(null);
  const [stats, setStats] = useState({
    cpu: 0,
    memory: 0,
    knowledge_nodes: 0,
    uptime: '0h 0m',
    intelligence_mode: 'Hybrid Inference Active',
    health_score: 100,
    proactive_alert: null as string | null
  });
  const [connectionError, setConnectionError] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState<string>('neutral');
  const [history, setHistory] = useState<{ id: string, title: string, messages: Message[] }[]>([]);
  const [isEnterprise, setIsEnterprise] = useState<boolean>(false);
  const [applyingRefactor, setApplyingRefactor] = useState(false);
  const [isIdle, setIsIdle] = useState(false);

  const endRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const idleTimerRef = useRef<NodeJS.Timeout | null>(null);

  // --- Effects ---

  // Auto-scroll chat
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Polling for backend stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_URL}/stats`);
        if (!res.ok) throw new Error();
        const data = await res.json();
        setStats(prev => ({ ...prev, ...data }));
        setConnectionError(false);
      } catch {
        setConnectionError(true);
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  // Idle tracking for Avatar
  const resetIdle = () => {
    setIsIdle(false);
    if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    idleTimerRef.current = setTimeout(() => setIsIdle(true), 5000);
  };

  useEffect(() => {
    const handleEvents = () => resetIdle();
    window.addEventListener('mousemove', handleEvents);
    window.addEventListener('keydown', handleEvents);
    resetIdle();
    return () => {
      window.removeEventListener('mousemove', handleEvents);
      window.removeEventListener('keydown', handleEvents);
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    };
  }, []);

  // Sync mouse position for Parallax
  useEffect(() => {
    const handleMouse = (e: MouseEvent) => setMousePos({ x: e.clientX, y: e.clientY });
    window.addEventListener('mousemove', handleMouse);
    return () => window.removeEventListener('mousemove', handleMouse);
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  // --- Actions ---

  const send = async (overrideText?: string) => {
    const textToSend = (overrideText || input).trim();
    if (!textToSend || loading) return;

    if (!overrideText) setInput('');
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: textToSend };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: textToSend })
      });
      const data = await res.json();
      const engineRes = data.response;

      // Emotion Mapping
      const emotionMap: Record<string, string> = {
        'assertive': 'serious',
        'cautious': 'cautious',
        'calm': 'calm',
        'analytical': 'analytical',
        'curious': 'curious',
      };
      setCurrentEmotion(emotionMap[engineRes.tone?.toLowerCase()] || 'neutral');

      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: engineRes.content,
        trace: engineRes.trace,
        level: engineRes.level,
        tone: engineRes.tone,
        confidence: engineRes.confidence,
        meta: engineRes.meta,
        type: engineRes.intent === 'PLANNING' || engineRes.intent === 'AUDIT' ? 'plan' : 'chat'
      }]);
    } catch {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'System integration failure. Unable to contact Primers Intelligence backend. Ensure local server is operational on port 8000.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const uploadFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_URL}/upload`, { method: 'POST', body: formData });
      const data = await res.json();
      const userMsg: Message = { id: Date.now().toString(), role: 'user', content: `Source Ingested: ${file.name}` };
      setMessages(prev => [...prev, userMsg, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response.content,
        meta: data.response.meta,
        tone: data.response.tone
      }]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleApplyRefactor = async (targetFile: string, proposedCode: string) => {
    setApplyingRefactor(true);
    await send(`apply refactor to ${targetFile}\nProposed Code:\n${proposedCode}`);
    setApplyingRefactor(false);
  };

  const startNewSession = () => {
    if (messages.length > 0) {
      const title = messages.find(m => m.role === 'user')?.content || 'New Analysis';
      setHistory(prev => [{ id: Date.now().toString(), title, messages }, ...prev].slice(0, 10));
    }
    setMessages([]);
    setCurrentEmotion('neutral');
  };

  // --- Render Helpers ---

  const AIIcon = () => (
    <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center border border-white/10 shrink-0">
      <Zap className="w-4 h-4 text-white/50" />
    </div>
  );

  const UserIcon = () => (
    <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center border border-blue-400/30 shrink-0">
      <div className="w-4 h-4 text-white flex items-center justify-center font-bold text-[10px]">U</div>
    </div>
  );

  return (
    <div className={cn(
      "flex h-screen w-full bg-background text-foreground overflow-hidden relative",
      stats.proactive_alert && "proactive-alert-active"
    )}>
      
      {/* --- Sidebar --- */}
      <aside className="w-[300px] flex flex-col bg-neutral-900 border-r border-white/5 shrink-0 relative z-20 shadow-2xl">
        {/* Brand */}
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-neutral-800 to-black flex items-center justify-center border border-white/10 shadow-lg">
             <span className="text-xl font-black text-white italic tracking-tighter">P</span>
          </div>
          <div className="flex flex-col">
            <h1 className="text-sm font-black tracking-tight text-white uppercase italic">Primers Intelligence</h1>
            <span className="text-[10px] text-white/30 font-bold tracking-widest leading-none">SOVEREIGN V3.0</span>
          </div>
        </div>

        {/* Navigation */}
        <div className="px-4 space-y-2 mt-2">
          <button 
            onClick={startNewSession}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 hover:border-white/10 transition-all text-sm font-medium"
          >
            <Plus className="w-4 h-4" />
            New Intelligence Session
          </button>
          
          <button 
            onClick={() => send("sync ecosystem")}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 hover:bg-emerald-500/20 transition-all text-sm font-medium text-emerald-400"
          >
            <RefreshCw className="w-4 h-4 animate-pulse-subtle" />
            Sync Global Ecosystem
          </button>
        </div>

        {/* Enterprise Upgrade */}
        {!isEnterprise && (
          <div 
            onClick={() => setIsEnterprise(true)}
            className="m-4 p-4 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 relative overflow-hidden group cursor-pointer shadow-xl shadow-blue-900/10"
          >
            <div className="absolute -right-2 -top-2 opacity-10 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-20 h-20" />
            </div>
            <span className="text-[10px] font-black bg-black/20 text-white/80 px-2 py-0.5 rounded-full mb-2 inline-block">SYSTEM PRO</span>
            <h3 className="text-xs font-bold text-white mb-1">Upgrade To Enterprise</h3>
            <p className="text-[10px] text-white/60 leading-tight">Unlock Autonomous Self-Healing & Compliance Guardrails.</p>
          </div>
        )}

        {isEnterprise && (
          <div className="mx-4 my-2 p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center gap-2 text-blue-400">
             <ShieldCheck className="w-4 h-4" />
             <span className="text-[10px] font-black uppercase tracking-widest">Enterprise License Active</span>
          </div>
        )}

        {/* Recent Sessions */}
        {history.length > 0 && (
          <div className="px-4 mt-8 flex-1 overflow-y-auto">
            <h4 className="px-2 text-[10px] font-black text-white/20 uppercase tracking-[0.2em] mb-4">Chronology</h4>
            <div className="space-y-1">
              {history.map(s => (
                <button 
                  key={s.id} 
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/5 text-xs text-white/50 text-left transition-colors truncate"
                  onClick={() => setMessages(s.messages)}
                >
                  <MessageSquare className="w-3 h-3 opacity-30" />
                  <span className="truncate">{s.title}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="flex-1" />

        {/* Avatar Area */}
        <div className="p-8 border-t border-white/5 flex justify-center bg-black/20">
          <Avatar 
            isTyping={input.trim().length > 0} 
            isResponding={loading} 
            mousePos={mousePos} 
            isIdle={isIdle} 
            emotion={currentEmotion} 
            hasAlert={!!stats.proactive_alert} 
          />
        </div>

        {/* System Stats Sidebar */}
        <div className="p-6 bg-black/40 border-t border-white/5">
           <div className="flex items-center gap-2 text-emerald-400 mb-4">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.5)]" />
              <span className="text-[10px] font-bold uppercase tracking-widest">{stats.intelligence_mode}</span>
           </div>
           
           <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="p-2 rounded-lg bg-white/5 border border-white/5">
                <span className="text-[8px] font-bold text-white/30 uppercase block mb-1">Knowledge Nodes</span>
                <span className="text-xs font-bold text-white/80">{stats.knowledge_nodes}</span>
              </div>
              <div className="p-2 rounded-lg bg-white/5 border border-white/5">
                <span className="text-[8px] font-bold text-white/30 uppercase block mb-1">Architecture Uptime</span>
                <span className="text-xs font-bold text-white/80">{stats.uptime}</span>
              </div>
           </div>

           <div className="space-y-2">
              <div className="flex justify-between text-[8px] font-bold text-white/30 uppercase tracking-widest">
                <span>Structural Integrity</span>
                <span>{stats.health_score}/100</span>
              </div>
              <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                <div 
                  className={cn(
                    "h-full transition-all duration-500",
                    stats.health_score > 80 ? "bg-emerald-500" : stats.health_score > 50 ? "bg-yellow-500" : "bg-red-500"
                  )}
                  style={{ width: `${stats.health_score}%` }}
                />
              </div>
           </div>
        </div>
      </aside>

      {/* --- Main Content --- */}
      <main className="flex-1 flex flex-col relative z-10">
        
        {/* Top Header */}
        <header className="h-[64px] px-8 flex items-center justify-between border-b border-white/5 bg-neutral-900/50 backdrop-blur-xl shrink-0">
          <div className="flex items-center gap-4">
            <h2 className="text-sm font-bold text-white uppercase tracking-tighter italic">Intelligence Core</h2>
            <div className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[10px] font-black text-white/40 tracking-[0.2em]">SOVEREIGN V3.0</div>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className={cn("w-2 h-2 rounded-full animate-pulse", connectionError ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" : "bg-emerald-500 shadow-[0_0_8px_rgba(52,211,153,0.5)]")} />
              <span className="text-[10px] font-bold text-white/40 uppercase tracking-widest">
                {connectionError ? 'Backend Disconnected' : 'Cognitive Bridge Synchronized'}
              </span>
            </div>
            <div className="h-4 w-px bg-white/10" />
            <div className="flex items-center gap-4">
               <div className="flex items-center gap-2">
                  <Cpu className="w-3 h-3 text-white/30" />
                  <span className="text-[10px] font-mono text-white/60">{stats.cpu}%</span>
               </div>
               <div className="flex items-center gap-2">
                  <Database className="w-3 h-3 text-white/30" />
                  <span className="text-[10px] font-mono text-white/60">{stats.memory}%</span>
               </div>
            </div>
          </div>
        </header>

        {/* Chat / Viewport */}
        <div className="flex-1 overflow-y-auto px-8 py-12 custom-scrollbar">
          <div className="max-w-[900px] mx-auto w-full">
            
            <AnimatePresence mode="popLayout">
              {messages.length === 0 ? (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="h-full flex flex-col items-center justify-center pt-20"
                >
                  <motion.div 
                    animate={{ y: [0, -10, 0] }}
                    transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                    className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center mb-10 shadow-3xl shadow-blue-500/20"
                  >
                     <Zap className="w-8 h-8 text-white" />
                  </motion.div>
                  <h2 className="text-3xl font-black text-white mb-4 italic tracking-tighter">Initiate Cognitive Analysis.</h2>
                  <p className="text-white/40 text-sm mb-12 max-w-md text-center leading-relaxed">System sovereignty established. Cross-referencing neural patterns with code architecture in real-time. What shall we optimize today?</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                    {SUGGESTIONS.map((s, i) => (
                      <motion.button
                        key={i}
                        whileHover={{ scale: 1.02, backgroundColor: "rgba(255,255,255,0.06)" }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => send(s.prompt)}
                        className="p-5 rounded-2xl bg-white/5 border border-white/5 flex flex-col items-start gap-4 text-left transition-all"
                      >
                         <div className="p-2 rounded-lg bg-white/5 border border-white/10 text-white/40">{s.icon}</div>
                         <div className="flex flex-col">
                           <span className="text-xs font-bold text-white/80">{s.label}</span>
                           <span className="text-[10px] text-white/30 font-mono italic">{s.prompt}</span>
                         </div>
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              ) : (
                <div className="flex flex-col gap-10">
                  {messages.map((m, idx) => (
                    <motion.div 
                      key={m.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={cn("flex gap-6", m.role === 'user' ? "flex-row-reverse" : "flex-row")}
                    >
                      {m.role === 'assistant' ? <AIIcon /> : <UserIcon />}
                        
                      <div className={cn("flex flex-col max-w-[85%]", m.role === 'user' ? "items-end" : "items-start")}>
                        <div className={cn(
                          "px-6 py-4 rounded-2xl text-sm leading-relaxed",
                          m.role === 'user' ? "bg-blue-600 text-white font-medium" : "bg-neutral-900 border border-white/5 text-white/80"
                        )}>
                          {m.role === 'assistant' ? (
                            <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/5 prose-code:text-blue-400">
                                <ReactMarkdown
                                  components={{
                                    code({ className, children, ...props }: any) {
                                      const match = /language-mermaid/.exec(className || '');
                                      const isBlock = className && className.startsWith('language-');
                                      return isBlock && match ? (
                                        <Mermaid chart={String(children).replace(/\n$/, '')} />
                                      ) : (
                                        <code className={cn(className, "rounded px-1.5 py-0.5 bg-white/5 text-blue-300")} {...props}>
                                          {children}
                                        </code>
                                      );
                                    }
                                  }}
                                >
                                  {m.content}
                                </ReactMarkdown>
                            </div>
                          ) : (
                            <p>{m.content}</p>
                          )}
                        </div>

                        {/* Special Renders: Diff, Dashboard, Meta */}
                        {m.role === 'assistant' && (
                          <div className="w-full space-y-4 pt-2">
                             {m.type === 'plan' && m.meta && (
                               <div className="w-full">
                                  <DiffViewer 
                                    diff={m.meta} 
                                    onApply={() => handleApplyRefactor(m.meta.target_file, m.meta.proposed_code)}
                                    isApplying={applyingRefactor}
                                  />
                               </div>
                             )}

                             {m.meta?.insights && (
                               <ExecutiveDashboard insights={m.meta.insights} />
                             )}

                             {/* Metadata Rails */}
                             {(m.confidence !== undefined || (m.trace && m.trace.length > 0)) && (
                               <div className="flex flex-wrap gap-2 items-center">
                                  {m.confidence !== undefined && (
                                    <div className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[9px] font-black text-white/30 uppercase tracking-widest">
                                      {(m.confidence * 100).toFixed(0)}% Certainty
                                    </div>
                                  )}
                                  {m.tone && (
                                    <div className="px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-[9px] font-black text-blue-400 uppercase tracking-widest">
                                      Cognitive Tone: {m.tone}
                                    </div>
                                  )}
                                  {m.trace && m.trace.length > 0 && (
                                    <button 
                                      onClick={() => setShowTrace(showTrace === m.id ? null : m.id)}
                                      className="text-[10px] font-bold text-white/30 hover:text-white/60 transition-colors uppercase tracking-widest flex items-center gap-1"
                                    >
                                      {showTrace === m.id ? 'Collapse Neural Trace' : 'Expand Neural Trace'}
                                      <ChevronRight className={cn("w-3 h-3 transition-transform", showTrace === m.id && "rotate-90")} />
                                    </button>
                                  )}
                               </div>
                             )}

                             {/* Neural Trace Panel */}
                             {showTrace === m.id && m.trace && (
                               <motion.div 
                                 initial={{ height: 0, opacity: 0 }}
                                 animate={{ height: 'auto', opacity: 1 }}
                                 className="bg-black/50 border border-white/5 rounded-2xl overflow-hidden shadow-inner"
                               >
                                 <div className="px-4 py-3 border-b border-white/5 flex items-center gap-2 bg-white/5">
                                    <Activity className="w-3 h-3 text-white/30" />
                                    <span className="text-[10px] font-black text-white/40 uppercase tracking-[0.2em]">Neural Processing Trace</span>
                                 </div>
                                 <div className="p-4 space-y-3 font-mono text-[10px]">
                                    {m.trace.map(t => (
                                      <div key={t.step_id} className="flex gap-4 items-start group">
                                         <span className="text-blue-500/50 font-black group-hover:text-blue-400 transition-colors shrink-0">{t.intent}</span>
                                         <span className="text-white/40 flex-1 leading-normal italic">{t.action}: {t.output_summary}</span>
                                         <span className="text-white/20">{(t.confidence * 100).toFixed(0)}%</span>
                                      </div>
                                    ))}
                                 </div>
                               </motion.div>
                             )}
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}

                  {loading && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-6 items-start">
                      <AIIcon />
                      <div className="flex flex-col gap-2 pt-2">
                        <div className="flex gap-1.5">
                          <motion.div animate={{ scale: [1, 1.5, 1] }} transition={{ repeat: Infinity, duration: 1 }} className="w-1.5 h-1.5 rounded-full bg-white/20" />
                          <motion.div animate={{ scale: [1, 1.5, 1] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-1.5 h-1.5 rounded-full bg-white/20" />
                          <motion.div animate={{ scale: [1, 1.5, 1] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-1.5 h-1.5 rounded-full bg-white/20" />
                        </div>
                        <span className="text-[9px] font-black text-white/20 uppercase tracking-[0.3em]">Synthesizing response...</span>
                      </div>
                    </motion.div>
                  )}
                  <div ref={endRef} className="h-4" />
                </div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Input Dock */}
        <div className="p-8 shrink-0 relative bg-gradient-to-t from-background via-background to-transparent pt-12">
          <div className="max-w-[800px] mx-auto w-full relative z-20">
            
            <div className="bg-neutral-900 border border-white/5 rounded-2xl p-2 flex items-end gap-2 shadow-[0_20px_60px_-15px_rgba(0,0,0,0.6)] group-focus-within:border-white/10 transition-all">
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={uploadFile} 
                  className="hidden" 
                />
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  className="w-11 h-11 flex items-center justify-center rounded-xl bg-white/5 hover:bg-white/10 text-white/30 hover:text-white transition-all border border-transparent hover:border-white/10 shrink-0"
                >
                  <Upload className="w-5 h-5" />
                </button>

                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      send();
                    }
                  }}
                  rows={1}
                  placeholder="Inquire Primers Intelligence..."
                  className="flex-1 bg-transparent border-none outline-none text-sm text-white/90 py-3.5 px-2 resize-none leading-relaxed placeholder:text-white/20"
                />

                <button 
                  onClick={() => send()}
                  disabled={!input.trim() || loading}
                  className={cn(
                    "w-11 h-11 flex items-center justify-center rounded-xl transition-all border shrink-0",
                    input.trim() && !loading 
                      ? "bg-white text-black border-white shadow-lg shadow-white/5 scale-100" 
                      : "bg-white/5 text-white/10 border-transparent scale-95 cursor-not-allowed"
                  )}
                >
                   <Send className="w-4 h-4" />
                </button>
            </div>
            <div className="flex justify-center mt-3 gap-6">
              <span className="text-[9px] font-bold text-white/20 uppercase tracking-widest flex items-center gap-1.5">
                <Terminal className="w-2.5 h-2.5" />
                Enter to Process
              </span>
              <span className="text-[9px] font-bold text-white/20 uppercase tracking-widest flex items-center gap-1.5">
                <RotateCcw className="w-2.5 h-2.5" />
                Shift + Enter for new node
              </span>
            </div>
          </div>
        </div>
      </main>

      {/* Background Ambience */}
      <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
         <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-blue-600/5 blur-[120px] rounded-full translate-x-1/2 -translate-y-1/2" />
         <div className="absolute bottom-0 left-0 w-[800px] h-[800px] bg-indigo-600/5 blur-[120px] rounded-full -translate-x-1/2 translate-y-1/2" />
         <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full opacity-20 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] blend-overlay" />
      </div>

    </div>
  );
}
