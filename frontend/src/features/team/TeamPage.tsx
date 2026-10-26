import { useState, useEffect } from 'react';
import { UserPlus, Shield, User as UserIcon } from 'lucide-react';
import api from '../../services/api';
import { useAuthStore } from '../../stores/authStore';

interface TeamMember {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_superuser: boolean;
  is_active: boolean;
}

export default function TeamPage() {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const currentUser = useAuthStore((s) => s.user);

  const [form, setForm] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    is_superuser: false,
  });

  useEffect(() => {
    loadMembers();
  }, []);

  async function loadMembers() {
    setLoading(true);
    try {
      const { data } = await api.get('/users/');
      setMembers(data);
    } catch (err) {
      console.error('Failed to load team members:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleAddMember(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post('/users/', form);
      setShowModal(false);
      setForm({ email: '', password: '', first_name: '', last_name: '', is_superuser: false });
      loadMembers();
    } catch (err: any) {
      alert(err.response?.data?.message || err.response?.data?.detail || 'Error adding team member (Admin only)');
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Team & Workspace Members</h1>
          <p className="page-subtitle">Manage users, security permissions, and administrative access</p>
        </div>
        {currentUser?.is_superuser && (
          <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
            <UserPlus size={15} />
            Add Member
          </button>
        )}
      </div>

      <div className="card table-container">
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center' }}>
            <span className="spinner" style={{ margin: '0 auto' }} />
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Member</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {members.map((m) => (
                <tr key={m.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div
                        style={{
                          width: 32,
                          height: 32,
                          borderRadius: '50%',
                          background: m.is_superuser ? 'var(--gradient-brand)' : 'var(--color-surface-2)',
                          border: '1px solid var(--color-border)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: 13,
                          fontWeight: 700,
                          color: '#fff',
                        }}
                      >
                        {m.first_name?.[0] || 'U'}
                      </div>
                      <span style={{ fontWeight: 600 }}>
                        {m.first_name} {m.last_name}
                      </span>
                    </div>
                  </td>
                  <td>{m.email}</td>
                  <td>
                    {m.is_superuser ? (
                      <span className="badge badge-warning" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                        <Shield size={12} />
                        ADMIN
                      </span>
                    ) : (
                      <span className="badge badge-neutral" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                        <UserIcon size={12} />
                        MEMBER
                      </span>
                    )}
                  </td>
                  <td>
                    <span className={`badge ${m.is_active ? 'badge-success' : 'badge-danger'}`}>
                      {m.is_active ? 'ACTIVE' : 'DEACTIVATED'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Add Member Modal */}
      {showModal && (
        <div className="modal-backdrop" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Invite New Team Member</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <form onSubmit={handleAddMember}>
              <div className="modal-body">
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">First Name</label>
                    <input
                      type="text"
                      required
                      className="form-input"
                      value={form.first_name}
                      onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Last Name</label>
                    <input
                      type="text"
                      required
                      className="form-input"
                      value={form.last_name}
                      onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <input
                    type="email"
                    required
                    className="form-input"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Temporary Password</label>
                  <input
                    type="password"
                    required
                    minLength={6}
                    className="form-input"
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                  />
                </div>
                <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 12 }}>
                  <input
                    type="checkbox"
                    id="is_superuser"
                    checked={form.is_superuser}
                    onChange={(e) => setForm({ ...form, is_superuser: e.target.checked })}
                    style={{ width: 16, height: 16 }}
                  />
                  <label htmlFor="is_superuser" style={{ fontSize: 13, cursor: 'pointer' }}>
                    Grant Workspace Administrator privileges
                  </label>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Member
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
