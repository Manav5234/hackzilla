import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../services/api';

const EXAMPLES = [
  "How's traffic on NH48 right now?",
  'Best time to travel from Delhi to Noida?',
  'Is there congestion near Connaught Place?',
];

export default function ChatBot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Hello! I\'m TrafficAI. Ask me about Indian traffic conditions.' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (msg) => {
    const text = msg || input;
    if (!text.trim()) return;
    setMessages(prev => [...prev, { role: 'user', text }]);
    setInput('');
    setLoading(true);
    const reply = await sendChatMessage(text);
    setMessages(prev => [...prev, { role: 'assistant', text: reply }]);
    setLoading(false);
  };

  return (
    <>
      <button className="chat-toggle" onClick={() => setOpen(!open)}>
        {open ? '✕' : '💬'}
      </button>

      {open && (
        <div className="chat-panel">
          <div className="chat-header">
            <span>TrafficAI Chat</span>
            <span className="chat-status">● Online</span>
          </div>

          <div className="chat-messages">
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg ${m.role}`}>
                {m.text}
              </div>
            ))}
            {loading && <div className="chat-msg assistant">Thinking...</div>}
            <div ref={bottomRef} />
          </div>

          <div className="chat-examples">
            {EXAMPLES.map((ex, i) => (
              <button key={i} className="example-chip" onClick={() => handleSend(ex)}>
                {ex}
              </button>
            ))}
          </div>

          <div className="chat-input-row">
            <input
              type="text"
              placeholder="Ask about traffic..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
            />
            <button className="chat-send" onClick={() => handleSend()} disabled={loading}>
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}
