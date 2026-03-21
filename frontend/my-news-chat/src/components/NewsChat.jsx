import { useState } from 'react'
import axios from 'axios'

export default function NewsChat() {
  const [question, setQuestion] = useState('')
  const [answerData, setAnswerData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // --- Test backend connection ---
  const testBackend = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/')
      alert(`Backend status: ${res.data.message}\nServices ready: ${res.data.services_ready}`)
    } catch (err) {
      alert('Cannot reach backend → ' + err.message)
    }
  }

  // --- Send question ---
  const sendQuestion = async () => {
    if (!question) return
    setLoading(true)
    setError('')
    setAnswerData(null)

    try {
      const res = await axios.post('http://127.0.0.1:8000/ask', { question })
      setAnswerData(res.data)
    } catch (err) {
      console.error(err)
      setError('Error sending question → ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: '700px', margin: '40px auto', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ textAlign: 'center', color: '#1e40af' }}>News Chat – Test Version</h1>

      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <button
          onClick={testBackend}
          style={{
            padding: '10px 24px',
            fontSize: '16px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
          }}
        >
          Test Backend
        </button>
      </div>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question here..."
          style={{ flex: 1, padding: '10px', fontSize: '16px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
          disabled={loading}
        />
        <button
          onClick={sendQuestion}
          disabled={loading}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            background: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
          }}
        >
          {loading ? 'Sending...' : 'Ask'}
        </button>
      </div>

      {/* --- Display Answer --- */}
      <div
        style={{
          padding: '20px',
          background: '#f1f5f9',
          borderRadius: '12px',
          minHeight: '120px',
          whiteSpace: 'pre-wrap',
        }}
      >
        {error && <span style={{ color: 'red' }}>{error}</span>}
        {!error && !answerData && 'Your answer will appear here...'}
        {answerData && (
          <div>
            <strong>Answer:</strong>
            <p>{answerData.answer}</p>

            {answerData.sources && answerData.sources.length > 0 && (
              <>
                <strong>Sources:</strong>
                <ul>
                  {answerData.sources.map((src, idx) => (
                    <li key={idx}>
                      {src.title} {src.link && <a href={src.link} target="_blank" rel="noopener noreferrer">(link)</a>}
                    </li>
                  ))}
                </ul>
              </>
            )}
            <em>Status: {answerData.status}</em>
          </div>
        )}
      </div>

      <p style={{ marginTop: '40px', textAlign: 'center', color: '#6b7280', fontSize: '14px' }}>
        React + Vite frontend. Make sure your FastAPI backend is running on port 8000.
      </p>
    </div>
  )
}