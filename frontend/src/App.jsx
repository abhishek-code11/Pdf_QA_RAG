// App.jsx — the whole UI.
//   Left side:  the PDF (shown by the browser's built-in PDF viewer inside an <iframe>)
//   Right side: a chat box. Each question is sent to the Python backend (POST /ask).
import { useState } from 'react'

export default function App() {
  // useState = a value React remembers; changing it re-draws the screen.
  const [messages, setMessages] = useState([]) // chat history: [{ role: 'user'|'bot', text, sources? }]
  const [question, setQuestion] = useState('') // what's currently typed in the input box
  const [loading, setLoading] = useState(false) // true while waiting for the LLM

  async function ask(event) {
    event.preventDefault() // stop the <form> from reloading the page
    const q = question.trim()
    if (!q || loading) return

    // Show the user's question right away, and clear the input.
    setMessages((prev) => [...prev, { role: 'user', text: q }])
    setQuestion('')
    setLoading(true)

    try {
      // Send the question to Python. Vite's proxy (vite.config.js) forwards /ask to port 8000.
      const res = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      })
      if (!res.ok) throw new Error(`Server error ${res.status}`)
      const data = await res.json() // { answer, sources }
      setMessages((prev) => [...prev, { role: 'bot', text: data.answer, sources: data.sources }])
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'bot', text: `⚠️ ${err.message}. Is the backend running?` }])
    } finally {
      setLoading(false) // runs whether it worked or failed
    }
  }

  return (
    <div className="layout">
      {/* LEFT: the PDF. The backend serves it at /pdf; the browser renders it. */}
      <iframe className="pdf" src="/pdf" title="PDF document" />

      {/* RIGHT: the chat */}
      <div className="chat">
        <h2>Ask the PDF</h2>

        <div className="messages">
          {messages.length === 0 && <p className="hint">Try: "What is the candidate's experience?"</p>}

          {/* .map() draws one bubble per message */}
          {messages.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`}>
              {m.text}
              {/* Show which PDF chunks the answer was based on — this is the "R" in RAG */}
              {m.sources && (
                <details>
                  <summary>Sources from PDF ({m.sources.length})</summary>
                  {m.sources.map((s, j) => <p key={j} className="source">{s}</p>)}
                </details>
              )}
            </div>
          ))}

          {loading && <div className="bubble bot">Thinking…</div>}
        </div>

        <form onSubmit={ask}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about the PDF…"
            aria-label="Question"
          />
          <button disabled={loading || !question.trim()}>Ask</button>
        </form>
      </div>
    </div>
  )
}
