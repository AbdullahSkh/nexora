import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

export default function RegisterPage() {
  const [form, setForm] = useState({
    organization_name: '',
    user_email: '',
    password: '',
    first_name: '',
    last_name: '',
  });
  const { register, loading, error } = useAuthStore();
  const navigate = useNavigate();

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(form);
      navigate('/');
    } catch {}
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="sidebar-logo-icon">N</div>
          <span className="sidebar-logo-text" style={{ fontSize: 20 }}>Nexora</span>
        </div>
        <h1 className="auth-title">Create your workspace</h1>
        <p className="auth-subtitle">Start your startup OS in seconds</p>

        {error && <div className="error-msg" style={{ marginBottom: 16 }}>{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Organization Name</label>
            <input id="org-name" className="input" placeholder="Acme Corp" value={form.organization_name} onChange={set('organization_name')} required />
          </div>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">First Name</label>
              <input id="first-name" className="input" placeholder="John" value={form.first_name} onChange={set('first_name')} required />
            </div>
            <div className="form-group">
              <label className="form-label">Last Name</label>
              <input id="last-name" className="input" placeholder="Doe" value={form.last_name} onChange={set('last_name')} required />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Work Email</label>
            <input id="reg-email" type="email" className="input" placeholder="john@acme.com" value={form.user_email} onChange={set('user_email')} required />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input id="reg-password" type="password" className="input" placeholder="Min 8 characters" value={form.password} onChange={set('password')} required minLength={8} />
          </div>
          <button
            type="submit"
            className="btn btn-primary w-full"
            disabled={loading}
            style={{ justifyContent: 'center', marginTop: 4 }}
          >
            {loading ? <span className="spinner" /> : 'Create Workspace'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
