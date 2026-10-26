import { useState, useEffect } from 'react';
import { Plus, LifeBuoy, Send, User, ShieldAlert } from 'lucide-react';
import api from '../../services/api';

interface Comment {
  id: string;
  author_id?: string;
  is_internal: boolean;
  body: string;
  created_at: string;
}

interface Ticket {
  id: string;
  customer_email: string;
  customer_name?: string;
  subject: string;
  description: string;
  status: string;
  priority: string;
  created_at: string;
}

interface TicketDetail extends Ticket {
  comments: Comment[];
}

const STATUS_BADGES: Record<string, string> = {
  open: 'badge-danger',
  in_progress: 'badge-warning',
  waiting_on_customer: 'badge-info',
  resolved: 'badge-success',
  closed: 'badge-neutral',
};

const PRIORITY_BADGES: Record<string, string> = {
  low: 'badge-neutral',
  medium: 'badge-info',
  high: 'badge-warning',
  urgent: 'badge-danger',
};

export default function SupportPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [activeTicket, setActiveTicket] = useState<TicketDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  // Comment input
  const [newComment, setNewComment] = useState('');
  const [isInternal, setIsInternal] = useState(false);

  // New Ticket Modal
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    customer_email: '',
    customer_name: '',
    subject: '',
    description: '',
    priority: 'medium',
  });

  useEffect(() => {
    loadTickets();
  }, [statusFilter]);

  async function loadTickets() {
    setLoading(true);
    try {
      const url = statusFilter ? `/support/?status=${statusFilter}` : '/support/';
      const { data } = await api.get(url);
      setTickets(data);
      if (data.length > 0 && !activeTicket) {
        loadDetail(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load tickets:', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadDetail(id: string) {
    try {
      const { data } = await api.get(`/support/${id}`);
      setActiveTicket(data);
    } catch (err) {
      console.error('Failed to load ticket detail:', err);
    }
  }

  async function handleCreateTicket(e: React.FormEvent) {
    e.preventDefault();
    try {
      const { data } = await api.post('/support/', form);
      setShowModal(false);
      setTickets([data, ...tickets]);
      loadDetail(data.id);
      setForm({ customer_email: '', customer_name: '', subject: '', description: '', priority: 'medium' });
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error creating ticket');
    }
  }

  async function handleAddComment(e: React.FormEvent) {
    e.preventDefault();
    if (!activeTicket || !newComment.trim()) return;
    try {
      await api.post(`/support/${activeTicket.id}/comments`, {
        body: newComment,
        is_internal: isInternal,
      });
      setNewComment('');
      loadDetail(activeTicket.id);
    } catch (err) {
      console.error('Failed to post comment:', err);
    }
  }

  async function updateStatus(nextStatus: string) {
    if (!activeTicket) return;
    try {
      const { data } = await api.patch(`/support/${activeTicket.id}`, { status: nextStatus });
      setActiveTicket({ ...activeTicket, status: data.status });
      setTickets(tickets.map((t) => (t.id === activeTicket.id ? { ...t, status: data.status } : t)));
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Customer Support Helpdesk</h1>
          <p className="page-subtitle">Manage customer issues, inquiries, and internal agent notes</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
          <Plus size={15} />
          Create Ticket
        </button>
      </div>

      {/* Filter Bar */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 18 }}>
        <select
          className="form-select"
          style={{ width: 180 }}
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="waiting_on_customer">Waiting on Customer</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 20 }}>
        {/* Ticket List */}
        <div className="card" style={{ padding: 12, maxHeight: 600, overflowY: 'auto' }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--color-text-muted)', padding: '6px 8px', textTransform: 'uppercase' }}>
            Tickets Queue ({tickets.length})
          </div>
          {loading ? (
            <div style={{ padding: 20, textAlign: 'center' }}>
              <span className="spinner" style={{ margin: '0 auto', width: 18, height: 18 }} />
            </div>
          ) : tickets.length === 0 ? (
            <div style={{ padding: 24, textAlign: 'center', color: 'var(--color-text-muted)', fontSize: 13 }}>
              No tickets found in this queue.
            </div>
          ) : (
            tickets.map((t) => {
              const isSelected = activeTicket?.id === t.id;
              return (
                <div
                  key={t.id}
                  onClick={() => loadDetail(t.id)}
                  style={{
                    padding: '12px',
                    borderRadius: 'var(--radius-sm)',
                    background: isSelected ? 'rgba(99,102,241,0.12)' : 'var(--color-surface-2)',
                    border: `1px solid ${isSelected ? 'var(--color-primary)' : 'var(--color-border)'}`,
                    marginBottom: 10,
                    cursor: 'pointer',
                    transition: 'var(--transition)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <span className={`badge ${PRIORITY_BADGES[t.priority] || 'badge-neutral'}`} style={{ fontSize: 10 }}>
                      {t.priority.toUpperCase()}
                    </span>
                    <span className={`badge ${STATUS_BADGES[t.status] || 'badge-neutral'}`} style={{ fontSize: 10 }}>
                      {t.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <div style={{ fontWeight: 600, fontSize: 13.5, marginBottom: 4 }}>{t.subject}</div>
                  <div style={{ fontSize: 12, color: 'var(--color-text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {t.customer_name ? `${t.customer_name} • ` : ''}{t.customer_email}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Ticket Discussion View */}
        <div className="card" style={{ padding: 24, minHeight: 520, display: 'flex', flexDirection: 'column' }}>
          {!activeTicket ? (
            <div className="empty-state" style={{ margin: 'auto' }}>
              <LifeBuoy size={48} color="var(--color-text-muted)" style={{ opacity: 0.3 }} />
              <h3>Select a ticket</h3>
              <p>Choose a support ticket from the queue to view thread and reply.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
              <div style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: 16, marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <h2 style={{ fontSize: 18, fontWeight: 700 }}>{activeTicket.subject}</h2>
                  <select
                    className="form-select"
                    style={{ width: 'auto', padding: '4px 8px', fontSize: 12, height: 32 }}
                    value={activeTicket.status}
                    onChange={(e) => updateStatus(e.target.value)}
                  >
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="waiting_on_customer">Waiting on Customer</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
                <div style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>
                  From: <strong>{activeTicket.customer_name || 'Customer'}</strong> ({activeTicket.customer_email}) • {new Date(activeTicket.created_at).toLocaleString()}
                </div>
                <div style={{ marginTop: 12, padding: 12, background: 'var(--color-surface-2)', borderRadius: 'var(--radius-sm)', fontSize: 13, lineHeight: 1.6 }}>
                  {activeTicket.description}
                </div>
              </div>

              {/* Comments Thread */}
              <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 16 }}>
                {activeTicket.comments?.length === 0 ? (
                  <span style={{ fontSize: 13, color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
                    No replies yet. Use the reply box below to communicate or leave an internal note.
                  </span>
                ) : (
                  activeTicket.comments?.map((c) => (
                    <div
                      key={c.id}
                      style={{
                        padding: '12px',
                        borderRadius: 'var(--radius-sm)',
                        background: c.is_internal ? 'rgba(245, 158, 11, 0.08)' : 'var(--color-surface-2)',
                        border: `1px solid ${c.is_internal ? 'rgba(245, 158, 11, 0.3)' : 'var(--color-border)'}`,
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                        <span style={{ fontSize: 12, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
                          {c.is_internal ? (
                            <>
                              <ShieldAlert size={14} color="#f59e0b" />
                              <span style={{ color: '#f59e0b' }}>INTERNAL AGENT NOTE</span>
                            </>
                          ) : (
                            <>
                              <User size={14} color="var(--color-primary)" />
                              <span>Support Agent Response</span>
                            </>
                          )}
                        </span>
                        <span style={{ fontSize: 11, color: 'var(--color-text-subtle)' }}>
                          {new Date(c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <div style={{ fontSize: 13, lineHeight: 1.5 }}>{c.body}</div>
                    </div>
                  ))
                )}
              </div>

              {/* Reply Box */}
              <form onSubmit={handleAddComment} style={{ borderTop: '1px solid var(--color-border)', paddingTop: 14 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={isInternal}
                      onChange={(e) => setIsInternal(e.target.checked)}
                      style={{ width: 14, height: 14 }}
                    />
                    <span style={{ color: isInternal ? '#f59e0b' : 'var(--color-text-muted)', fontWeight: isInternal ? 600 : 400 }}>
                      Post as internal team note (hidden from customer)
                    </span>
                  </label>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder={isInternal ? 'Type internal note for other agents...' : 'Type public reply to customer...'}
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                  />
                  <button type="submit" className="btn btn-primary" style={{ padding: '0 16px' }}>
                    <Send size={15} />
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>

      {/* New Ticket Modal */}
      {showModal && (
        <div className="modal-backdrop" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Create Support Ticket</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreateTicket}>
              <div className="modal-body">
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Customer Name</label>
                    <input
                      type="text"
                      className="form-input"
                      value={form.customer_name}
                      onChange={(e) => setForm({ ...form, customer_name: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Customer Email</label>
                    <input
                      type="email"
                      required
                      className="form-input"
                      value={form.customer_email}
                      onChange={(e) => setForm({ ...form, customer_email: e.target.value })}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Priority</label>
                  <select
                    className="form-select"
                    value={form.priority}
                    onChange={(e) => setForm({ ...form, priority: e.target.value })}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Subject</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    value={form.subject}
                    onChange={(e) => setForm({ ...form, subject: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Description / Problem details</label>
                  <textarea
                    className="form-textarea"
                    required
                    style={{ minHeight: 120 }}
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Submit Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
