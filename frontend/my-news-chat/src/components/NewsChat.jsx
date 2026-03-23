import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = 'http://127.0.0.1:8000';

export default function NewsChat() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Auto-scroll on new message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendQuestion = async () => {
    if (!question.trim()) return;

    const userMsg = { role: 'user', text: question };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion('');
    setLoading(true);

    try {
      const res = await axios.post(`${BACKEND_URL}/ask`, { question: userMsg.text });
      const data = res.data;
      const assistantMsg = { role: 'assistant', text: data.answer };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', text: '❌ Error: ' + err.message }]);
    } finally {
      setLoading(false);
    }
  };

  const clearMemory = async () => {
    setLoading(true);
    try {
      await axios.post(`${BACKEND_URL}/clear-memory`);
      setMessages([{ role: 'assistant', text: '🗑 Memory cleared!' }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', text: '❌ Error clearing memory: ' + err.message }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      maxWidth: '700px',
      margin: '40px auto',
      fontFamily: 'Courier New, monospace',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px'
    }}>
      <h1 style={{
        textAlign: 'center',
        border: '2px solid #000',
        display: 'inline-block',
        padding: '8px 12px',
        marginBottom: '20px',
        boxShadow: '2px 2px 0px #000'
      }}>
        AI NEWS CHATBOT
      </h1>

      <div style={{
        flex: 1,
        border: '1px solid #ccc',
        borderRadius: '8px',
        padding: '12px',
        height: '400px',
        overflowY: 'auto',
        background: '#fefefe',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}>
        {messages.map((m, i) => (
          <div key={i} style={{
            alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '80%',
            display: 'flex',
            flexDirection: 'column',
            gap: '4px'
          }}>
            {m.role === 'user' ? (
              <div style={{
                background: '#000',
                color: '#fff',
                padding: '10px 14px',
                borderRadius: '12px 12px 4px 12px',
                boxShadow: '2px 2px 4px rgba(0,0,0,0.3)',
                fontSize: '14px'
              }}>
                [USER MESSAGE]<br />{m.text}
              </div>
            ) : (
              <div style={{
                background: '#fff',
                border: '1px solid #000',
                padding: '10px 14px',
                borderRadius: '12px 12px 12px 4px',
                boxShadow: '2px 2px 4px rgba(0,0,0,0.1)',
                fontSize: '14px'
              }}>
                [AI RESPONSE]<br />{m.text}
              </div>
            )}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <div style={{ display: 'flex', gap: '8px' }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question here..."
          style={{
            flex: 1,
            padding: '10px',
            borderRadius: '8px',
            border: '1px solid #ccc',
            fontFamily: 'Courier New, monospace'
          }}
          disabled={loading}
          onKeyDown={(e) => { if (e.key === 'Enter') sendQuestion(); }}
        />
        <button
          onClick={sendQuestion}
          disabled={loading}
          style={{
            padding: '10px 20px',
            background: '#000',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            boxShadow: '2px 2px 0px #000'
          }}
        >
          SEND
        </button>
        <button
          onClick={clearMemory}
          disabled={loading}
          style={{
            padding: '10px 20px',
            background: '#e11d48',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            boxShadow: '2px 2px 0px #b91c1c'
          }}
        >
          CLEAR
        </button>
      </div>
    </div>
  );
}