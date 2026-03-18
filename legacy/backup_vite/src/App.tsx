import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'
import './Insights.css'
import Avatar from './components/Avatar'
import Mermaid from './components/Mermaid'
import DiffViewer from './components/DiffViewer'

interface ReasoningStep {
  step_id: string;
  intent: string;
  action: string;
  confidence: number;
  output_summary: string;
}

interface EngineResponse {
  content: string;
  intent: string;
  confidence: number;
  level: string;
  tone: string;
  trace: ReasoningStep[];
  meta: any;
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
}

const API_URL = import.meta.env.PROD ? "/api" : "http://localhost:8000";

const SUGGESTIONS = [
  { label: "Executive Insights", prompt: "show executive report" },
  { label: "Analyze codebase", prompt: "analyze corpus" },
  { label: "Review engine", prompt: "review engine.py" },
  { label: "Comparative Audit", prompt: "compare engine.py vs judge.py" },
];

// Simple icon components
const PIcon = () => (
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
    <rect width="28" height="28" rx="6" fill="url(#pGrad)" />
    <defs>
      <linearGradient id="pGrad" x1="0" y1="0" x2="28" y2="28">
        <stop stopColor="#404040" />
        <stop offset="1" stopColor="#171717" />
      </linearGradient>
    </defs>
    <text x="7" y="20" fill="#d4d4d4" fontSize="14" fontWeight="700" fontFamily="'Inter', sans-serif">P</text>
  </svg>
);

const UserIcon = () => (
  <div className="avatar-bubble user-bubble">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  </div>
);

const AIIcon = () => (
  <div className="avatar-bubble ai-bubble">
    <PIcon />
  </div>
);

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [showTrace, setShowTrace] = useState<string | null>(null);
  const [stats, setStats] = useState({
    cpu: 12,
    memory: 24,
    knowledge_nodes: 0,
    uptime: '0h 0m',
    intelligence_mode: '...',
    health_score: 100,
    proactive_alert: null as string | null
  });
  const [connectionError, setConnectionError] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isTyping = input.trim().length > 0;
  const [currentEmotion, setCurrentEmotion] = useState<string>('neutral');
  const [history, setHistory] = useState<{ id: string, title: string, messages: Message[] }[]>([]);
  const [isEnterprise, setIsEnterprise] = useState<boolean>(false);
  const [applyingRefactor, setApplyingRefactor] = useState(false);

  // Fetch Stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_URL}/stats`);
        if (!res.ok) throw new Error("Backend unreachable");
        const data = await res.json();
        setStats(data);
        setConnectionError(false);
      } catch (e) { 
        console.error("Stats fetch failed", e);
        setConnectionError(true);
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 10000); // 10s for more responsive status
    return () => clearInterval(interval);
  }, []);

  const [isIdle, setIsIdle] = useState(false);
  const idleTimerRef = useRef<any>(null);

  const resetIdle = () => {
    setIsIdle(false);
    if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    idleTimerRef.current = setTimeout(() => setIsIdle(true), 5000); // 5s idle
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
      resetIdle();
    };
    const handleKeyDown = () => resetIdle();

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('keydown', handleKeyDown);
    resetIdle();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('keydown', handleKeyDown);
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    };
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 160) + 'px';
    }
  }, [input]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      const userMsg: Message = { id: Date.now().toString(), role: 'user', content: `Uploaded file: ${file.name}` };
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response.content,
        trace: data.response.trace,
        level: data.response.level,
        tone: data.response.tone,
        confidence: data.response.confidence,
        meta: data.response.meta,
      };
      setMessages(prev => [...prev, userMsg, aiMsg]);
    } catch (e) {
      console.error("Upload failed", e);
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const send = async (overrideText?: string) => {
    const textToSend = (overrideText || input).trim();
    if (!textToSend) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: textToSend };
    setMessages(p => [...p, userMsg]);
    if (!overrideText) setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: textToSend })
      });
      const data = await res.json();
      const engineRes: EngineResponse = data.response;

      // Map Tone to Emotion
      const emotionMap: Record<string, string> = {
        'assertive': 'serious',
        'cautious': 'cautious',
        'calm': 'calm',
        'analytical': 'analytical',
        'curious': 'curious',
        'inconclusive': 'neutral'
      };
      const emotion = emotionMap[engineRes.tone?.toLowerCase() || ''] || 'neutral';
      setCurrentEmotion(emotion);

      setMessages(p => [...p, {
        id: Date.now().toString(),
        role: 'assistant',
        content: engineRes.content,
        trace: engineRes.trace,
        level: engineRes.level,
        tone: engineRes.tone,
        confidence: engineRes.confidence,
        meta: engineRes.meta
      }]);
    } catch {
      setMessages(p => [...p, {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Unable to reach the Primers Intelligence backend. Please ensure the server is running.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const newSession = () => {
    if (messages.length > 0) {
      const firstMsg = messages.find(m => m.role === 'user')?.content || 'New Chat';
      setHistory(h => [{ id: Date.now().toString(), title: firstMsg, messages }, ...h].slice(0, 10));
    }
    setMessages([]);
    setInput('');
    setShowTrace(null);
  };

  const loadSession = (session: { title: string, messages: Message[] }) => {
    setMessages(session.messages);
    setShowTrace(null);
  };

  const isEmpty = messages.length === 0;

  const handleApplyRefactor = async (targetFile: string, proposedCode: string) => {
    setApplyingRefactor(true);
    await send(`apply refactor to ${targetFile}\nProposed Code:\n${proposedCode}`);
    setApplyingRefactor(false);
  };

  return (
    <div className={`app ${stats.proactive_alert ? 'proactive-alert-active' : ''}`}>
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        {/* Brand */}
        <div className="brand">
          <PIcon />
          <span className="brand-name">Primers Intelligence</span>
        </div>

        {/* New Chat */}
        <button className="new-chat-btn" onClick={newSession}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></svg>
          New Chat
        </button>

        <button className="new-chat-btn sync-btn" onClick={() => send("sync ecosystem")}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M21 2v6h-6M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6M21 12a9 9 0 0 1-15 6.7L3 16" /></svg>
          Sync Ecosystem
        </button>

        {!isEnterprise && (
          <div className="commercial-card" onClick={() => setIsEnterprise(true)}>
            <div className="card-tag">PRO</div>
            <div className="card-title">Upgrade to Enterprise</div>
            <div className="card-desc">Unlock Autonomous Self-Healing & Compliance Guardrails.</div>
          </div>
        )}

        {isEnterprise && (
          <div className="enterprise-badge">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" style={{ marginRight: '6px' }}><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z" /></svg>
            ENTERPRISE LICENSE ACTIVE
          </div>
        )}

        {/* Recents */}
        {history.length > 0 && (
          <div className="sidebar-section">
            <div className="section-label">Recent Sessions</div>
            {history.map(s => (
              <button key={s.id} className="history-btn" onClick={() => loadSession(s)}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
                {s.title.length > 28 ? s.title.slice(0, 26) + '…' : s.title}
              </button>
            ))}
          </div>
        )}

        {/* Spacer */}
        <div style={{ flex: 1 }} />

        {/* Avatar Section */}
        <div className="avatar-section" style={{ padding: '2rem 1rem', display: 'flex', justifyContent: 'center' }}>
          <Avatar isTyping={isTyping} isResponding={loading} mousePos={mousePos} isIdle={isIdle} emotion={currentEmotion} hasAlert={!!stats.proactive_alert} />
        </div>

        {/* Status */}
        <div className="sidebar-footer">
          <div className="status-row">
            <span className="status-dot" />
            <span>{stats.intelligence_mode}</span>
          </div>
          <div className="stats-grid" style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <div className="stat-box">
              <div className="stat-label">Knowledge</div>
              <div className="stat-value">{stats.knowledge_nodes} nodes</div>
            </div>
            <div className="stat-box">
              <div className="stat-label">Uptime</div>
              <div className="stat-value">{stats.uptime}</div>
            </div>
          </div>

          <div className="health-section" style={{ marginTop: '1rem' }}>
            <div className="stat-label">Structural Health</div>
            <div className="health-bar-container">
              <div className={`health-bar-fill ${stats.health_score <= 50 ? 'health-critical' : ''}`} style={{ width: `${stats.health_score}%`, background: stats.health_score > 80 ? '#3fb950' : stats.health_score > 50 ? '#d29922' : '#f85149' }} />
            </div>
            <div className="stat-value" style={{ marginTop: '4px', textAlign: 'right' }}>{stats.health_score}/100</div>
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="main">
        {/* Topbar */}
        <header className="topbar">
          <div className="topbar-left">
            <h2 className="topbar-title">Primers Intelligence</h2>
            <div className="model-badge">Sovereign v3.0</div>
          </div>
          <div className="intelligence-status">
            <div className={`status-dot ${connectionError ? 'red' : 'green'}`}></div>
            <span>{connectionError ? 'Backend Offline' : 'Hybrid Inference Active'}</span>
          </div>
        </header>

        {/* Proactive Auditor Notification */}
        {stats.proactive_alert && (
          <div className="proactive-notification">
            <div className="notif-icon">🛡️</div>
            <div className="notif-content">
              <div className="notif-label">Autonomous Auditor Alert</div>
              <p>{stats.proactive_alert}</p>
            </div>
            <button className="notif-action" onClick={() => send(stats.proactive_alert || '')}>Initiate Audit</button>
          </div>
        )}

        {/* Chat or Empty State */}
        <div className="chat-area">
          {isEmpty ? (
            <div className="empty-state">
              <div className="empty-icon"><PIcon /></div>
              <h2 className="empty-title">Primers Intelligence</h2>
              <p className="empty-sub">Your intelligent code-architecture assistant. Ask anything.</p>
              <div className="suggestion-grid">
                {SUGGESTIONS.map(s => (
                  <button key={s.prompt} className="suggestion-card" onClick={() => send(s.prompt)}>
                    <span className="suggestion-label">{s.label}</span>
                    <span className="suggestion-prompt">{s.prompt}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map(m => (
                <div key={m.id} className={`message-row ${m.role}`}>
                  {m.role === 'assistant' ? <AIIcon /> : <UserIcon />}
                  <div className="message-body">
                    <div className="message-text">
                      {m.role === 'assistant' ? (
                        <ReactMarkdown
                          components={{
                            code({ className, children, ...props }) {
                              const match = /language-mermaid/.exec(className || '');
                              const isBlock = className && className.startsWith('language-');
                              return isBlock && match ? (
                                <Mermaid chart={String(children).replace(/\n$/, '')} />
                              ) : (
                                <code className={className} {...props}>
                                  {children}
                                </code>
                              );
                            }
                          }}
                        >
                          {m.content}
                        </ReactMarkdown>
                      ) : (
                        <p>{m.content}</p>
                      )}
                    </div>

                    {/* Diff Viewer Integration */}
                    {m.type === 'plan' && m.meta && (
                      <div className="diff-wrapper">
                        <DiffViewer
                          diff={m.meta}
                          onApply={() => handleApplyRefactor(m.meta.target_file, m.meta.proposed_code)}
                          isApplying={applyingRefactor}
                        />
                        <button
                          className="apply-fix-btn"
                          onClick={() => send(`apply refactor to ${m.meta.target_file}`)}
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ marginRight: '6px' }}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>
                          Apply Fix & Repay Debt
                        </button>
                      </div>
                    )}

                    {/* Executive Insights Dashboard */}
                    {m.meta?.insights && (
                      <div className="executive-dashboard">
                        <div className="dash-header">
                          <span className="dash-title">Executive Intelligence Dashboard</span>
                          <span className="dash-badge">Proprietary Heuristics v3.0</span>
                        </div>
                        <div className="dash-grid">
                          <div className="dash-stat">
                            <div className="d-label">Architectural Health</div>
                            <div className="d-val">{m.meta.insights.metrics.architectural_health?.toFixed(1) || '0.0'}%</div>
                            <div className="d-progress"><div className="d-fill" style={{ width: `${m.meta.insights.metrics.architectural_health || 0}%` }} /></div>
                          </div>
                          <div className="dash-stat">
                            <div className="d-label">Base Exposure</div>
                            <div className="d-val text-dim">${m.meta.insights.metrics.base_debt_exposure?.toLocaleString() || '0'}</div>
                            <div className="d-sub">Market benchmark (raw)</div>
                          </div>
                          <div className="dash-stat">
                            <div className="d-label">Adjusted Debt (V4)</div>
                            <div className="d-val text-red">${m.meta.insights.metrics.technical_debt_cost?.toLocaleString() || '0'}</div>
                            <div className="d-sub">Risk Adjusted exposure</div>
                          </div>
                          <div className="dash-stat">
                            <div className="d-label">PDM Multiplier</div>
                            <div className="d-val text-gold">{m.meta.insights.metrics.pdm_multiplier || '1.00x'}</div>
                            <div className="d-sub">Structural friction coefficient</div>
                          </div>
                          <div className="dash-stat">
                            <div className="d-label">Total Debt Repaid</div>
                            <div className="d-val text-green">${m.meta.insights.metrics.total_debt_repaid?.toLocaleString() || '0'}</div>
                            <div className="d-sub">Autonomous Value Generated</div>
                          </div>
                        </div>

                        <div className="dash-divider" />

                        <div className="dash-grid">
                          <div className="dash-stat">
                            <div className="d-label">Annual Savings Plan</div>
                            <div className="d-val text-gold">${m.meta.insights.metrics.annual_savings_forecast?.toLocaleString() || '0'}</div>
                            <div className="d-sub">Efficiency gain projection</div>
                          </div>
                          <div className="dash-stat">
                            <div className="d-label">Efficiency ROI</div>
                            <div className="d-val text-green">{m.meta.insights.metrics.efficiency_roi || '0.0%'}</div>
                            <div className="d-sub">Workflow acceleration</div>
                          </div>
                          <div className="dash-stat">
                            <div className="d-label">Global Compliance</div>
                            <div className="d-val text-blue">{m.meta.insights.metrics.global_compliance_rating || '0%'}</div>
                            <div className="d-sub">Policy Governance</div>
                          </div>
                          <div className="dash-stat">
                            <div className="d-label">Market Velocity</div>
                            <div className={`d-val ${m.meta.insights.metrics.velocity_risk === 'HIGH' ? 'text-red' : 'text-green'}`}>
                              {m.meta.insights.metrics.velocity_risk || 'STABLE'}
                            </div>
                            <div className="d-sub">Risk Profile</div>
                          </div>
                        </div>

                        <div className="dash-divider" />

                        <div className="dash-section">
                          <div className="d-label">Systemic Fragility Hotspots</div>
                          <div className="hotspot-list">
                            {m.meta.insights.metrics.fragility_hotspots.map((h: any, i: number) => (
                              <div key={i} className={`hotspot-item risk-${h.risk_type.toLowerCase()}`}>
                                <div className="h-info">
                                  <div className="h-name">{h.node}</div>
                                  <div className="h-meta">Blast Radius: {h.blast_radius}%</div>
                                </div>
                                <div className="h-score">
                                  <div className="h-val">{h.score}</div>
                                  <div className="h-label">RISK INDEX</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Meta row */}
                    {m.role === 'assistant' && (m.confidence || (m.trace && m.trace.length > 0)) && (
                      <div className="message-meta">
                        {m.confidence && (
                          <span className="meta-chip">
                            {(m.confidence * 100).toFixed(0)}% confidence
                          </span>
                        )}
                        {m.tone && <span className={`meta-chip tone-${m.tone}`}>{m.tone}</span>}
                        {m.trace && m.trace.length > 0 && (
                          <button className="trace-toggle" onClick={() => setShowTrace(showTrace === m.id ? null : m.id)}>
                            {showTrace === m.id ? 'Hide' : 'Show'} reasoning
                          </button>
                        )}
                      </div>
                    )}

                    {/* Trace */}
                    {showTrace === m.id && m.trace && (
                      <div className="trace-panel">
                        <div className="trace-panel-title">Reasoning Graph · {m.level}</div>
                        {m.trace.map(t => (
                          <div key={t.step_id} className="trace-row">
                            <span className="trace-tag">{t.intent}</span>
                            <span className="trace-desc">{t.action}: {t.output_summary}</span>
                            <span className="trace-score">{(t.confidence * 100).toFixed(0)}%</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message-row assistant">
                  <AIIcon />
                  <div className="message-body">
                    <div className="typing-indicator">
                      <span /><span /><span />
                    </div>
                  </div>
                </div>
              )}
              <div ref={endRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="input-area">
          <div className="input-box">
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={uploadFile}
            />
            <button
              className="upload-btn"
              onClick={() => fileInputRef.current?.click()}
              title="Upload file for analysis"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="Ask Primers Intelligence anything..."
            />
            <button
              className={`send-btn ${input.trim() ? 'active' : ''}`}
              onClick={() => send()}
              disabled={!input.trim() && !loading}
            >
              <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
              </svg>
            </button>
          </div>
          <p className="input-hint">Enter to send · Shift + Enter for new line</p>
        </div>
      </main>
    </div>
  );
}

export default App;
