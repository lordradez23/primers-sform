import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'
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
  { label: "Analyze codebase", prompt: "analyze corpus" },
  { label: "Review engine", prompt: "review engine.py" },
  { label: "Compare modules", prompt: "compare engine.py vs judge.py" },
  { label: "Explain architecture", prompt: "explain your architecture" },
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
  const endRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isTyping = input.trim().length > 0;
  const [currentEmotion, setCurrentEmotion] = useState<string>('neutral');

  // Fetch Stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_URL}/stats`);
        const data = await res.json();
        setStats(data);
      } catch (e) { console.error("Stats fetch failed", e); }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
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
    setMessages([]);
    setInput('');
    setShowTrace(null);
  };

  const isEmpty = messages.length === 0;

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

        {/* Recents */}
        {messages.filter(m => m.role === 'user').length > 0 && (
          <div className="sidebar-section">
            <div className="section-label">Recent</div>
            {messages.filter(m => m.role === 'user').slice(-6).reverse().map(m => (
              <button key={m.id} className="history-btn" onClick={() => send(m.content)}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
                {m.content.length > 28 ? m.content.slice(0, 26) + '…' : m.content}
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
            <div className="status-dot green"></div>
            <span>Hybrid Inference Active</span>
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
                    {m.meta?.current_code && m.meta?.proposed_code && (
                      <DiffViewer
                        oldCode={m.meta.current_code}
                        newCode={m.meta.proposed_code}
                        fileName={m.meta.target_file}
                      />
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
