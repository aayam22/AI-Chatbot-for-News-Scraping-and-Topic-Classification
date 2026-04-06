import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = 'http://127.0.0.1:8000';

export default function NewsTerminal() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const generateMessageId = () => `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendQuestion = async () => {
    if (!question.trim()) return;

    const userMsg = { 
      id: generateMessageId(), 
      role: 'user', 
      text: question, 
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) 
    };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion('');
    setLoading(true);

    try {
      const res = await axios.post(`${BACKEND_URL}/ask`, { question: userMsg.text });
      const data = res.data;

      // Format assistant message
      const assistantMsg = { 
        id: generateMessageId(), 
        role: 'assistant', 
        text: data.answer, 
        sources: data.sources?.map(s => ({
          ...s,
          image_url: s.image_url || null
        })) || [], 
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }),
        latency: '14MS',
        tokens: '442'
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [...prev, { 
        id: generateMessageId(), 
        role: 'assistant', 
        text: '❌ Error: ' + err.message, 
        sources: [], 
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const clearMemory = async () => {
    setLoading(true);
    try {
      await axios.post(`${BACKEND_URL}/clear-memory`);
      setMessages([{ 
        id: generateMessageId(), 
        role: 'assistant', 
        text: '🗑 Memory cleared!', 
        sources: [], 
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) 
      }]);
    } catch (err) {
      setMessages((prev) => [...prev, { 
        id: generateMessageId(), 
        role: 'assistant', 
        text: '❌ Error clearing memory: ' + err.message, 
        sources: [], 
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f5f5f5', color: '#000', fontFamily: '"Space Grotesk", sans-serif', overflow: 'hidden' }}>
      {/* Sidebar */}
      <aside style={{ width: '260px', borderRight: '4px solid #000', backgroundColor: '#eee', display: 'flex', flexDirection: 'column', zIndex: 10 }}>
        <div style={{ padding: '24px', borderBottom: '2px solid #000' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '900', margin: 0 }}>INTEL_CORE</h2>
          <div style={{ fontSize: '10px', opacity: 0.6, marginTop: '4px' }}>STATUS: OPTIMAL</div>
        </div>
        
        <nav style={{ flex: 1, padding: '12px 0' }}>
          {['FEED', 'ANALYSIS', 'ARCHIVE', 'SYSTEM'].map((item, idx) => (
            <div key={item} style={{
              padding: '16px 24px',
              fontWeight: '900',
              fontSize: '14px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              backgroundColor: idx === 0 ? '#000' : 'transparent',
              color: idx === 0 ? '#fff' : '#000',
              borderBottom: '1px solid rgba(0,0,0,0.1)'
            }}>
              <span style={{ fontSize: '18px' }}>{['▤', '◒', '▥', '⚙'][idx]}</span>
              {item}
            </div>
          ))}
        </nav>

        <div style={{ padding: '24px', borderTop: '2px solid #000' }}>
          <button style={{
            width: '100%',
            padding: '12px',
            backgroundColor: 'transparent',
            border: '2px solid #000',
            fontWeight: '900',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px'
          }}>
            <span>↩</span> LOGOUT
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' }}>
        {/* Top Header */}
        <header style={{ height: '64px', borderBottom: '4px solid #000', backgroundColor: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 32px', zIndex: 5 }}>
          <h1 style={{ fontSize: '24px', fontWeight: '900', margin: 0, letterSpacing: '-1px' }}>NEWS_TERMINAL_V2</h1>
          <div style={{ display: 'flex', gap: '32px', fontWeight: '900', fontSize: '12px' }}>
            <span style={{ borderBottom: '4px solid #000', paddingBottom: '20px' }}>FEED</span>
            <span>ANALYSIS</span>
            <span>ARCHIVE</span>
          </div>
          <div style={{ display: 'flex', gap: '20px' }}>
            <span>((●))</span>
            <span>⚙</span>
            <span>👤</span>
          </div>
        </header>

        {/* Chat Stream */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '40px', display: 'flex', flexDirection: 'column', gap: '40px', backgroundColor: '#fff' }}>
          {/* Session Info */}
          <div style={{ textAlign: 'center', marginBottom: '20px' }}>
            <span style={{ fontSize: '10px', fontWeight: 'bold', padding: '4px 12px', border: '2px solid #000', backgroundColor: '#fff' }}>
              TERMINAL_SESSION_0923 // [ENCRYPTION: AES-256]
            </span>
          </div>

          {messages.length === 0 && (
            <div style={{ maxWidth: '800px', border: '4px solid #000', padding: '32px', backgroundColor: '#fff', boxShadow: '8px 8px 0px #000' }}>
              <p style={{ margin: 0, fontSize: '16px', lineHeight: '1.6' }}>
                Analyzing global market fluctuations following the sudden shift in tech-sector regulations. The current trend indicates a 14.2% volatility spike in decentralized assets.
              </p>
            </div>
          )}

          {messages.map((m) => (
            <div key={m.id} style={{ display: 'flex', flexDirection: 'column', alignItems: m.role === 'user' ? 'flex-end' : 'flex-start', width: '100%' }}>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '8px', fontSize: '10px', fontWeight: '900', alignItems: 'center' }}>
                <span style={{ textTransform: 'uppercase' }}>{m.role === 'user' ? '■ USER_INPUT' : '■ ANALYSIS_BOT'}</span>
                <span style={{ opacity: 0.5 }}>[{m.time}]</span>
              </div>

              <div style={{ maxWidth: '85%', backgroundColor: m.role === 'user' ? '#000' : '#fff', color: m.role === 'user' ? '#fff' : '#000', border: '4px solid #000', padding: '24px', boxShadow: m.role === 'user' ? 'none' : '8px 8px 0px #000', position: 'relative' }}>
                {m.role === 'assistant' && (
                  <div style={{ borderLeft: '4px solid #000', paddingLeft: '16px', marginBottom: '16px', fontStyle: 'italic', opacity: 0.7 }}>
                    Querying distributed intelligence nodes... Cross-referencing {m.sources.length || 0} sources...
                  </div>
                )}
                
                <div style={{ fontSize: '16px', lineHeight: '1.6' }}>{m.text}</div>

                {m.role === 'assistant' && m.sources && m.sources.length > 0 && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '24px' }}>
                    {m.sources.map((s, idx) => (
                      <div key={idx} style={{ border: '2px solid #000', padding: '12px' }}>
                        <div style={{ fontSize: '10px', fontWeight: '900', marginBottom: '4px' }}>{s.category || 'SOURCE_INTEL'}</div>
                        <div style={{ fontSize: '12px', fontWeight: 'bold' }}>{s.title}</div>
                        {s.image_url && <img src={s.image_url} alt={s.title} style={{ marginTop: '8px', maxHeight: '120px', width: '100%', objectFit: 'cover' }} />}
                      </div>
                    ))}
                  </div>
                )}

                {m.role === 'assistant' && (
                  <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid rgba(0,0,0,0.1)', display: 'flex', justifyContent: 'space-between', fontSize: '10px', fontWeight: 'bold', opacity: 0.5 }}>
                    <span>[LATENCY: {m.latency || '12MS'}] [TOKEN_COUNT: {m.tokens || '442'}]</span>
                    <div>
                      <span style={{ marginRight: '12px', cursor: 'pointer' }}>COPY</span>
                      <span style={{ cursor: 'pointer' }}>RE-GENERATE</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <div style={{ width: '12px', height: '12px', backgroundColor: '#000', animation: 'pulse 1s infinite' }}></div>
              <span style={{ fontWeight: '900', fontSize: '12px' }}>PROCESSING_REQUEST...</span>
            </div>
          )}
          
          <div ref={chatEndRef} />
        </div>

        {/* Footer Input */}
        <footer style={{ padding: '24px 40px', borderTop: '4px solid #000', backgroundColor: '#f9f9f9', display: 'flex', gap: '20px', alignItems: 'center' }}>
          <button onClick={clearMemory} style={{ width: '48px', height: '48px', border: '3px solid #000', backgroundColor: '#fff', cursor: 'pointer', fontSize: '20px' }}>🗑</button>
          
          <div style={{ flex: 1, position: 'relative' }}>
            <div style={{ position: 'absolute', top: '-10px', left: '12px', backgroundColor: '#f9f9f9', padding: '0 8px', fontSize: '10px', fontWeight: '900' }}>PROMPT_INPUT_COMMAND</div>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendQuestion()}
              placeholder="ENTER QUERY..."
              style={{ width: '100%', padding: '16px', border: '3px solid #000', backgroundColor: '#fff', fontFamily: '"Space Grotesk", monospace', fontSize: '14px', fontWeight: 'bold', outline: 'none' }}
            />
          </div>

          <button onClick={sendQuestion} style={{ backgroundColor: '#000', color: '#fff', border: 'none', padding: '0 32px', height: '54px', fontWeight: '900', fontSize: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '12px' }}>
            SEND <span style={{ fontSize: '18px' }}>✉</span>
          </button>
        </footer>

        <style>{`
          @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.8); }
            100% { opacity: 1; transform: scale(1); }
          }
          *::-webkit-scrollbar { width: 8px; }
          *::-webkit-scrollbar-track { background: #eee; }
          *::-webkit-scrollbar-thumb { background: #000; }
        `}</style>
      </main>
    </div>
  );
}