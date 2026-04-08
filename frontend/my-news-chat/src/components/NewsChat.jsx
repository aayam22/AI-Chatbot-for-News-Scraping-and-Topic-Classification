import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = 'http://127.0.0.1:8000';

export default function NewsChat({ messages, setMessages }) {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const token = localStorage.getItem("token"); // JWT token

  const generateMessageId = () => `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  // Scroll to bottom whenever messages change
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendQuestion = async () => {
    if (!question.trim() || !token) return;

    const userMsg = {
      id: generateMessageId(),
      role: 'user',
      text: question,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
    };

    setMessages(prev => [...prev, userMsg]);
    setQuestion('');
    setLoading(true);

    try {
      const res = await axios.post(
        `${BACKEND_URL}/ask`,
        { question: userMsg.text },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const data = res.data;
      // Ensure answer is a string, not an object
      const answerText = typeof data.answer === 'string' ? data.answer : JSON.stringify(data.answer);
      const assistantMsg = {
        id: generateMessageId(),
        role: 'assistant',
        text: answerText,
        sources: Array.isArray(data.sources) ? data.sources.map(s => ({ 
          category: s.category || 'SOURCE',
          title: s.title || 'Untitled',
          image_url: s.image_url || null 
        })) : [],
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }),
        latency: '14MS',
        tokens: '442'
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        id: generateMessageId(),
        role: 'assistant',
        text: '❌ Error: ' + (err.response?.data?.detail || err.message || 'Unknown error'),
        sources: [],
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
      }]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async () => {
    if (!token) return;
    setLoading(true);
    try {
      await axios.post(
        `${BACKEND_URL}/clear-memory`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
    } catch (err) {
      console.warn("Error clearing backend memory:", err.response?.data?.detail || err.message);
    } finally {
      setMessages([]);
      localStorage.removeItem("chat_messages");
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', fontFamily: '"Space Grotesk", sans-serif' }}>
      
      {/* Chat messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {messages.length === 0 && (
          <div style={{ padding: '16px', border: '2px solid #000', maxWidth: '600px' }}>
            Start a conversation or ask about the latest news...
          </div>
        )}

        {messages.map(m => (
          <div key={m.id} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{
              padding: '16px',
              backgroundColor: m.role === 'user' ? '#000' : '#fff',
              color: m.role === 'user' ? '#fff' : '#000',
              border: '2px solid #000',
              maxWidth: '70%',
              position: 'relative'
            }}>
              {m.role === 'assistant' && Array.isArray(m.sources) && m.sources.length > 0 && (
                <div style={{ fontSize: '10px', fontStyle: 'italic', marginBottom: '8px' }}>
                  Cross-referencing {m.sources.length} source(s)...
                </div>
              )}
              <div style={{ fontSize: '14px', lineHeight: '1.5' }}>{String(m.text)}</div>

              {m.role === 'assistant' && Array.isArray(m.sources) && m.sources.length > 0 && (
                <div style={{ marginTop: '8px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  {m.sources.map((s, idx) => (
                    <div key={idx} style={{ border: '1px solid #000', padding: '8px', fontSize: '12px' }}>
                      <div style={{ fontWeight: '900', fontSize: '10px' }}>{String(s.category || 'SOURCE')}</div>
                      <div style={{ fontWeight: 'bold' }}>{String(s.title || 'Untitled')}</div>
                      {s.image_url && typeof s.image_url === 'string' && <img src={s.image_url} alt={s.title} style={{ width: '100%', maxHeight: '100px', objectFit: 'cover', marginTop: '4px' }} />}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ fontWeight: '900', opacity: 0.6 }}>Processing request...</div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div style={{ display: 'flex', padding: '16px', borderTop: '2px solid #000' }}>
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendQuestion()}
          placeholder="Type your question..."
          style={{ flex: 1, padding: '12px', fontWeight: 'bold', border: '2px solid #000', marginRight: '8px' }}
        />
        <button onClick={sendQuestion} style={{ padding: '12px', fontWeight: '900', border: '2px solid #000' }}>Send</button>
        <button onClick={clearChat} style={{ padding: '12px', fontWeight: '900', border: '2px solid #000', marginLeft: '8px' }}>Clear</button>
      </div>
    </div>
  );
}