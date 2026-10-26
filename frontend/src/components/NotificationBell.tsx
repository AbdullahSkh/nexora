import { useState, useEffect } from 'react';
import { Bell, CheckCheck } from 'lucide-react';
import api from '../services/api';

interface Notification {
  id: string;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
}

export default function NotificationBell() {
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadUnreadCount();
    const interval = setInterval(loadUnreadCount, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  async function loadUnreadCount() {
    try {
      const { data } = await api.get('/notifications/unread-count');
      setUnreadCount(data.unread_count);
    } catch {
      // Ignore if unauthenticated
    }
  }

  async function toggleOpen() {
    const nextState = !isOpen;
    setIsOpen(nextState);
    if (nextState) {
      try {
        const { data } = await api.get('/notifications/?limit=15');
        setNotifications(data);
      } catch (err) {
        console.error('Failed to load notifications:', err);
      }
    }
  }

  async function markAsRead(id: string) {
    try {
      await api.post(`/notifications/${id}/read`);
      setNotifications(notifications.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
      setUnreadCount(Math.max(0, unreadCount - 1));
    } catch (err) {
      console.error('Failed to mark notification read:', err);
    }
  }

  async function markAllAsRead() {
    try {
      await api.post('/notifications/read-all');
      setNotifications(notifications.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Failed to mark all notifications read:', err);
    }
  }

  return (
    <div style={{ position: 'relative' }}>
      <button
        className="btn btn-ghost btn-sm"
        onClick={toggleOpen}
        title="Notifications"
        style={{
          position: 'relative',
          padding: '6px 8px',
          borderRadius: 8,
          color: unreadCount > 0 ? 'var(--color-primary)' : 'var(--color-text-muted)',
        }}
      >
        <Bell size={18} />
        {unreadCount > 0 && (
          <span
            style={{
              position: 'absolute',
              top: 2,
              right: 2,
              minWidth: 16,
              height: 16,
              borderRadius: 8,
              background: '#ef4444',
              color: '#fff',
              fontSize: 10,
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '0 4px',
            }}
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: 40,
            right: 0,
            width: 320,
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius)',
            boxShadow: '0 12px 32px rgba(0,0,0,0.4)',
            zIndex: 1100,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid var(--color-border)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'var(--color-surface-2)',
            }}
          >
            <span style={{ fontSize: 13, fontWeight: 700 }}>Notifications</span>
            {unreadCount > 0 && (
              <button
                className="btn btn-ghost btn-sm"
                onClick={markAllAsRead}
                style={{ fontSize: 11, padding: '2px 6px', display: 'flex', alignItems: 'center', gap: 4 }}
              >
                <CheckCheck size={12} /> Mark all read
              </button>
            )}
          </div>

          <div style={{ maxHeight: 320, overflowY: 'auto' }}>
            {notifications.length === 0 ? (
              <div style={{ padding: 24, textAlign: 'center', color: 'var(--color-text-muted)', fontSize: 13 }}>
                No notifications right now
              </div>
            ) : (
              notifications.map((n) => (
                <div
                  key={n.id}
                  onClick={() => !n.is_read && markAsRead(n.id)}
                  style={{
                    padding: '12px 16px',
                    borderBottom: '1px solid var(--color-border)',
                    background: n.is_read ? 'transparent' : 'rgba(99,102,241,0.06)',
                    cursor: n.is_read ? 'default' : 'pointer',
                    transition: 'var(--transition)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                    <span style={{ fontSize: 13, fontWeight: n.is_read ? 500 : 700, color: 'var(--color-text)' }}>
                      {n.title}
                    </span>
                    {!n.is_read && (
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--color-primary)' }} />
                    )}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--color-text-muted)', lineHeight: 1.4 }}>{n.message}</div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
