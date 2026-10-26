import { useState } from 'react';
import { Sparkles, X, Send, Bot, User as UserIcon } from 'lucide-react';
import api from '../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function AiAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hi! I am your Nexora AI Copilot. Ask me to draft email campaigns, analyze deals, or summarize documents.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: 'user', content: input };
    const newHistory = [...messages, userMsg];
    setMessages(newHistory);
    setInput('');
    setLoading(true);

    try {
      const { data } = await api.post('/ai/chat', {
        messages: newHistory.map((m) => ({ role: m.role, content: m.content })),
        context_module: 'general',
      });
      setMessages([...newHistory, { role: 'assistant', content: data.reply }]);
    } catch (err) {
      setMessages([
        ...newHistory,
        { role: 'assistant', content: 'Apologies, could not process query right now. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(true)}
        style={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 999,
          width: 52,
          height: 52,
          borderRadius: '50%',
          background: 'var(--gradient-brand)',
          border: 'none',
          color: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 8px 24px rgba(99, 102, 241, 0.45)',
          cursor: 'pointer',
          transition: 'transform 150ms ease',
        }}
        onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.transform = 'scale(1.08)')}
        onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.transform = 'scale(1)')}
        title="Open Nexora AI Copilot"
      >
        <Sparkles size={24} />
      </button>

      {/* Slide-over Dialog */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            bottom: 86,
            right: 24,
            width: 380,
            height: 500,
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)',
            boxShadow: '0 20px 48px rgba(0, 0, 0, 0.5)',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 1000,
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '14px 16px',
              borderBottom: '1px solid var(--color-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'var(--color-surface-2)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 6,
                  background: 'var(--gradient-brand)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Sparkles size={16} color="#fff" />
              </div>
              <span style={{ fontSize: 14, fontWeight: 700 }}>Nexora AI Copilot</span>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={() => setIsOpen(false)} style={{ padding: '2px 6px' }}>
              <X size={16} />
            </button>
          </div>

          {/* Messages Body */}
          <div
            style={{
              flex: 1,
              padding: '16px',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: 12,
            }}
          >
            {messages.map((m, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  gap: 10,
                  alignItems: 'flex-start',
                  alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '88%',
                }}
              >
                {m.role === 'assistant' && (
                  <div
                    style={{
                      width: 24,
                      height: 24,
                      borderRadius: 6,
                      background: 'rgba(99,102,241,0.2)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}
                  >
                    <Bot size={14} color="var(--color-primary)" />
                  </div>
                )}
                <div
                  style={{
                    padding: '8px 12px',
                    borderRadius: 10,
                    fontSize: 13,
                    lineHeight: 1.5,
                    background: m.role === 'user' ? 'var(--color-primary)' : 'var(--color-surface-2)',
                    color: m.role === 'user' ? '#fff' : 'var(--color-text)',
                    border: m.role === 'assistant' ? '1px solid var(--color-border)' : 'none',
                  }}
                >
                  {m.content}
                </div>
                {m.role === 'user' && (
                  <div
                    style={{
                      width: 24,
                      height: 24,
                      borderRadius: '50%',
                      background: 'var(--color-surface-2)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}
                  >
                    <UserIcon size={12} color="var(--color-text-muted)" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                <span className="spinner" style={{ width: 14, height: 14 }} />
                <span style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>Thinking...</span>
              </div>
            )}
          </div>

          {/* Input Footer */}
          <form
            onSubmit={handleSend}
            style={{
              padding: '12px',
              borderTop: '1px solid var(--color-border)',
              display: 'flex',
              gap: 8,
              background: 'var(--color-surface)',
            }}
          >
            <input
              type="text"
              className="form-input"
              style={{ fontSize: 13, height: 38 }}
              placeholder="Ask anything..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button
              type="submit"
              className="btn btn-primary"
              style={{ height: 38, width: 38, padding: 0, flexShrink: 0 }}
              disabled={loading}
            >
              <Send size={15} />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
