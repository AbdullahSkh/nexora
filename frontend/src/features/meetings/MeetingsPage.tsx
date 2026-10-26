import { useState, useEffect } from 'react';
import { Plus, Calendar, Clock, Video, CheckCircle2, Circle, MessageSquare, Users } from 'lucide-react';
import api from '../../services/api';

interface Attendee {
  id: string;
  email: string;
  status: string;
}

interface Note {
  id: string;
  content: string;
  created_at: string;
}

interface ActionItem {
  id: string;
  title: string;
  is_completed: boolean;
  due_date?: string;
}

interface Meeting {
  id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  status: string;
}

interface MeetingDetail extends Meeting {
  attendees: Attendee[];
  notes: Note[];
  action_items: ActionItem[];
}

export default function MeetingsPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [activeMeeting, setActiveMeeting] = useState<MeetingDetail | null>(null);
  const [loading, setLoading] = useState(true);

  // Notes & Action items inputs
  const [newNote, setNewNote] = useState('');
  const [newActionItem, setNewActionItem] = useState('');

  // Schedule Modal
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    title: '',
    description: '',
    start_time: new Date(Date.now() + 3600000).toISOString().slice(0, 16),
    end_time: new Date(Date.now() + 7200000).toISOString().slice(0, 16),
    location: 'https://meet.google.com/xyz',
    attendees: [{ email: '', status: 'invited' }],
  });

  useEffect(() => {
    loadMeetings();
  }, []);

  async function loadMeetings() {
    setLoading(true);
    try {
      const { data } = await api.get('/meetings/');
      setMeetings(data);
      if (data.length > 0 && !activeMeeting) {
        loadDetail(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load meetings:', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadDetail(id: string) {
    try {
      const { data } = await api.get(`/meetings/${id}`);
      setActiveMeeting(data);
    } catch (err) {
      console.error('Failed to load meeting detail:', err);
    }
  }

  async function handleSchedule(e: React.FormEvent) {
    e.preventDefault();
    try {
      const validAttendees = form.attendees.filter((a) => a.email.trim());
      const { data } = await api.post('/meetings/', {
        ...form,
        attendees: validAttendees.length > 0 ? validAttendees : undefined,
      });
      setShowModal(false);
      setMeetings([...meetings, data]);
      loadDetail(data.id);
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error scheduling meeting');
    }
  }

  async function handleAddNote(e: React.FormEvent) {
    e.preventDefault();
    if (!activeMeeting || !newNote.trim()) return;
    try {
      await api.post(`/meetings/${activeMeeting.id}/notes`, { content: newNote });
      setNewNote('');
      loadDetail(activeMeeting.id);
    } catch (err) {
      console.error('Failed to add note:', err);
    }
  }

  async function handleAddActionItem(e: React.FormEvent) {
    e.preventDefault();
    if (!activeMeeting || !newActionItem.trim()) return;
    try {
      await api.post(`/meetings/${activeMeeting.id}/action-items`, { title: newActionItem });
      setNewActionItem('');
      loadDetail(activeMeeting.id);
    } catch (err) {
      console.error('Failed to add action item:', err);
    }
  }

  async function toggleActionItem(itemId: string, currentState: boolean) {
    try {
      await api.patch(`/meetings/action-items/${itemId}`, { is_completed: !currentState });
      if (activeMeeting) loadDetail(activeMeeting.id);
    } catch (err) {
      console.error('Failed to toggle action item:', err);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Meetings & Action Items</h1>
          <p className="page-subtitle">Schedule strategic sessions, capture notes, and track team actionables</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
          <Plus size={15} />
          Schedule Meeting
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 20 }}>
        {/* Left Column: Meetings List */}
        <div className="card" style={{ padding: 12, maxHeight: 600, overflowY: 'auto' }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--color-text-muted)', padding: '6px 8px', textTransform: 'uppercase' }}>
            Scheduled Sessions ({meetings.length})
          </div>
          {loading ? (
            <div style={{ padding: 20, textAlign: 'center' }}>
              <span className="spinner" style={{ margin: '0 auto', width: 18, height: 18 }} />
            </div>
          ) : meetings.length === 0 ? (
            <div style={{ padding: 20, textAlign: 'center', color: 'var(--color-text-muted)', fontSize: 13 }}>
              No meetings scheduled.
            </div>
          ) : (
            meetings.map((m) => {
              const startDate = new Date(m.start_time);
              const isSelected = activeMeeting?.id === m.id;
              return (
                <div
                  key={m.id}
                  onClick={() => loadDetail(m.id)}
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
                  <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>{m.title}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--color-text-muted)', marginBottom: 4 }}>
                    <Clock size={12} />
                    <span>{startDate.toLocaleDateString()} at {startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                  {m.location && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'var(--color-primary)' }}>
                      <Video size={12} />
                      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{m.location}</span>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Right Column: Meeting Detail (Notes & Action Items) */}
        <div className="card" style={{ padding: 24, minHeight: 500, display: 'flex', flexDirection: 'column' }}>
          {!activeMeeting ? (
            <div className="empty-state" style={{ margin: 'auto' }}>
              <Calendar size={48} color="var(--color-text-muted)" style={{ opacity: 0.3 }} />
              <h3>Select a meeting</h3>
              <p>Select a meeting from the list to view attendee RSVPs, notes, and action items.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
              <div style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: 16, marginBottom: 20 }}>
                <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 6 }}>{activeMeeting.title}</h2>
                <div style={{ display: 'flex', gap: 16, fontSize: 13, color: 'var(--color-text-muted)' }}>
                  <span>{new Date(activeMeeting.start_time).toLocaleString()}</span>
                  {activeMeeting.location && (
                    <a href={activeMeeting.location} target="_blank" rel="noreferrer" style={{ color: 'var(--color-primary)', display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Video size={14} /> Join Meeting
                    </a>
                  )}
                </div>
                {activeMeeting.description && (
                  <p style={{ marginTop: 10, fontSize: 13, color: 'var(--color-text-muted)' }}>{activeMeeting.description}</p>
                )}
              </div>

              {/* Attendees */}
              <div style={{ marginBottom: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: 8 }}>
                  <Users size={14} /> Attendees ({activeMeeting.attendees?.length || 0})
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {activeMeeting.attendees?.map((a) => (
                    <span key={a.id} className="badge badge-neutral" style={{ fontSize: 12 }}>
                      {a.email} ({a.status})
                    </span>
                  ))}
                </div>
              </div>

              {/* Grid 2: Notes & Action Items */}
              <div className="grid-2" style={{ gap: 24, flex: 1 }}>
                {/* Action Items */}
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <CheckCircle2 size={16} color="var(--color-primary)" />
                    Action Items
                  </div>

                  <form onSubmit={handleAddActionItem} style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                    <input
                      type="text"
                      className="form-input"
                      style={{ fontSize: 13, height: 34 }}
                      placeholder="Add an action item..."
                      value={newActionItem}
                      onChange={(e) => setNewActionItem(e.target.value)}
                    />
                    <button type="submit" className="btn btn-primary btn-sm" style={{ height: 34 }}>
                      Add
                    </button>
                  </form>

                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {activeMeeting.action_items?.length === 0 ? (
                      <span style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>No action items assigned.</span>
                    ) : (
                      activeMeeting.action_items?.map((item) => (
                        <div
                          key={item.id}
                          onClick={() => toggleActionItem(item.id, item.is_completed)}
                          style={{
                            padding: '8px 12px',
                            background: 'var(--color-surface-2)',
                            borderRadius: 'var(--radius-sm)',
                            border: '1px solid var(--color-border)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 10,
                            cursor: 'pointer',
                          }}
                        >
                          {item.is_completed ? (
                            <CheckCircle2 size={16} color="var(--color-success)" />
                          ) : (
                            <Circle size={16} color="var(--color-text-muted)" />
                          )}
                          <span
                            style={{
                              fontSize: 13,
                              textDecoration: item.is_completed ? 'line-through' : 'none',
                              color: item.is_completed ? 'var(--color-text-muted)' : 'var(--color-text)',
                            }}
                          >
                            {item.title}
                          </span>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* Meeting Notes */}
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <MessageSquare size={16} color="var(--color-secondary)" />
                    Discussion Notes
                  </div>

                  <form onSubmit={handleAddNote} style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 12 }}>
                    <textarea
                      className="form-textarea"
                      style={{ fontSize: 13, height: 70 }}
                      placeholder="Record key takeaway or decision..."
                      value={newNote}
                      onChange={(e) => setNewNote(e.target.value)}
                    />
                    <button type="submit" className="btn btn-secondary btn-sm" style={{ alignSelf: 'flex-end' }}>
                      Add Note
                    </button>
                  </form>

                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 220, overflowY: 'auto' }}>
                    {activeMeeting.notes?.map((n) => (
                      <div
                        key={n.id}
                        style={{
                          padding: '10px 12px',
                          background: 'var(--color-surface-2)',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: 13,
                          lineHeight: 1.5,
                        }}
                      >
                        {n.content}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Schedule Meeting Modal */}
      {showModal && (
        <div className="modal-backdrop" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Schedule New Meeting</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <form onSubmit={handleSchedule}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Meeting Title</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. Weekly Product Sync"
                    value={form.title}
                    onChange={(e) => setForm({ ...form, title: e.target.value })}
                  />
                </div>
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Start Time</label>
                    <input
                      type="datetime-local"
                      required
                      className="form-input"
                      value={form.start_time}
                      onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">End Time</label>
                    <input
                      type="datetime-local"
                      required
                      className="form-input"
                      value={form.end_time}
                      onChange={(e) => setForm({ ...form, end_time: e.target.value })}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Location / Video Call Link</label>
                  <input
                    type="text"
                    className="form-input"
                    value={form.location}
                    onChange={(e) => setForm({ ...form, location: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Invite Attendee Email</label>
                  <input
                    type="email"
                    className="form-input"
                    placeholder="teammate@company.com"
                    value={form.attendees[0]?.email || ''}
                    onChange={(e) => setForm({ ...form, attendees: [{ email: e.target.value, status: 'invited' }] })}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Meeting
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
