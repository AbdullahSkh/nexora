import { useState, useEffect } from 'react';
import { Plus, Megaphone, UserPlus } from 'lucide-react';
import api from '../../services/api';

interface Campaign {
  id: string;
  name: string;
  type: string;
  status: string;
  budget: number;
  spend: number;
}

interface Lead {
  id: string;
  first_name?: string;
  last_name?: string;
  email: string;
  company?: string;
  status: string;
  score: number;
}

export default function MarketingPage() {
  const [tab, setTab] = useState<'campaigns' | 'leads'>('campaigns');
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);

  // Modals
  const [showCampModal, setShowCampModal] = useState(false);
  const [showLeadModal, setShowLeadModal] = useState(false);

  const [campForm, setCampForm] = useState({
    name: '',
    type: 'email',
    status: 'active',
    budget: 2500,
    spend: 0,
  });

  const [leadForm, setLeadForm] = useState({
    email: '',
    first_name: '',
    last_name: '',
    company: '',
    status: 'new',
    score: 50,
  });

  useEffect(() => {
    loadData();
  }, [tab]);

  async function loadData() {
    setLoading(true);
    try {
      if (tab === 'campaigns') {
        const { data } = await api.get('/marketing/campaigns');
        setCampaigns(data);
      } else {
        const { data } = await api.get('/marketing/leads');
        setLeads(data);
      }
    } catch (err) {
      console.error('Failed to load marketing data:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateCampaign(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post('/marketing/campaigns', campForm);
      setShowCampModal(false);
      setCampForm({ name: '', type: 'email', status: 'active', budget: 2500, spend: 0 });
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error creating campaign');
    }
  }

  async function handleCreateLead(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post('/marketing/leads', leadForm);
      setShowLeadModal(false);
      setLeadForm({ email: '', first_name: '', last_name: '', company: '', status: 'new', score: 50 });
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error creating lead');
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Growth & Marketing Campaigns</h1>
          <p className="page-subtitle">Track multi-channel campaigns, lead capture, and prospect scoring</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowLeadModal(true)}>
            <UserPlus size={15} />
            Capture Lead
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => setShowCampModal(true)}>
            <Plus size={15} />
            New Campaign
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-nav">
        <button className={`tab-btn ${tab === 'campaigns' ? 'active' : ''}`} onClick={() => setTab('campaigns')}>
          <Megaphone size={15} style={{ display: 'inline', marginRight: 6 }} />
          Campaigns
        </button>
        <button className={`tab-btn ${tab === 'leads' ? 'active' : ''}`} onClick={() => setTab('leads')}>
          <UserPlus size={15} style={{ display: 'inline', marginRight: 6 }} />
          Prospect Leads
        </button>
      </div>

      <div className="card table-container">
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center' }}>
            <span className="spinner" style={{ margin: '0 auto' }} />
          </div>
        ) : tab === 'campaigns' ? (
          <table className="table">
            <thead>
              <tr>
                <th>Campaign Name</th>
                <th>Channel</th>
                <th>Status</th>
                <th>Budget / Spend</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', padding: 30, color: 'var(--color-text-muted)' }}>
                    No campaigns launched yet. Click "New Campaign" to set up your growth engine.
                  </td>
                </tr>
              ) : (
                campaigns.map((c) => {
                  const spendPct = c.budget > 0 ? Math.min(100, Math.round((c.spend / c.budget) * 100)) : 0;
                  return (
                    <tr key={c.id}>
                      <td style={{ fontWeight: 600 }}>{c.name}</td>
                      <td>
                        <span className="badge badge-info">{c.type.toUpperCase()}</span>
                      </td>
                      <td>
                        <span className={`badge ${c.status === 'active' ? 'badge-success' : 'badge-neutral'}`}>
                          {c.status.toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <div style={{ width: 140 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 4 }}>
                            <span>${c.spend}</span>
                            <span style={{ color: 'var(--color-text-muted)' }}>${c.budget}</span>
                          </div>
                          <div style={{ height: 6, background: 'var(--color-surface-2)', borderRadius: 3, overflow: 'hidden' }}>
                            <div style={{ width: `${spendPct}%`, height: '100%', background: 'var(--color-primary)', borderRadius: 3 }} />
                          </div>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Lead</th>
                <th>Email</th>
                <th>Company</th>
                <th>Status</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {leads.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: 30, color: 'var(--color-text-muted)' }}>
                    No leads captured. Click "Capture Lead" to record inbound inquiries.
                  </td>
                </tr>
              ) : (
                leads.map((l) => (
                  <tr key={l.id}>
                    <td style={{ fontWeight: 600 }}>{l.first_name || l.last_name ? `${l.first_name || ''} ${l.last_name || ''}`.trim() : 'Anonymous Lead'}</td>
                    <td>{l.email}</td>
                    <td style={{ color: 'var(--color-text-muted)' }}>{l.company || '—'}</td>
                    <td>
                      <span className={`badge ${l.status === 'qualified' ? 'badge-success' : 'badge-neutral'}`}>
                        {l.status.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${l.score >= 70 ? 'badge-success' : l.score >= 40 ? 'badge-warning' : 'badge-neutral'}`}>
                        {l.score} pts
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Campaign Modal */}
      {showCampModal && (
        <div className="modal-backdrop" onClick={() => setShowCampModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Launch Campaign</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowCampModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreateCampaign}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Campaign Name</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. Q4 Inbound Search & Social"
                    value={campForm.name}
                    onChange={(e) => setCampForm({ ...campForm, name: e.target.value })}
                  />
                </div>
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Channel Type</label>
                    <select
                      className="form-select"
                      value={campForm.type}
                      onChange={(e) => setCampForm({ ...campForm, type: e.target.value })}
                    >
                      <option value="email">Email</option>
                      <option value="social">Social</option>
                      <option value="webinar">Webinar</option>
                      <option value="paid_ad">Paid Ads</option>
                      <option value="content">Content</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Budget ($ USD)</label>
                    <input
                      type="number"
                      required
                      min="0"
                      className="form-input"
                      value={campForm.budget}
                      onChange={(e) => setCampForm({ ...campForm, budget: parseFloat(e.target.value) || 0 })}
                    />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCampModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Campaign
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Lead Modal */}
      {showLeadModal && (
        <div className="modal-backdrop" onClick={() => setShowLeadModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Capture Inbound Lead</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowLeadModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreateLead}>
              <div className="modal-body">
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">First Name</label>
                    <input
                      type="text"
                      className="form-input"
                      value={leadForm.first_name}
                      onChange={(e) => setLeadForm({ ...leadForm, first_name: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Last Name</label>
                    <input
                      type="text"
                      className="form-input"
                      value={leadForm.last_name}
                      onChange={(e) => setLeadForm({ ...leadForm, last_name: e.target.value })}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Lead Email</label>
                  <input
                    type="email"
                    required
                    className="form-input"
                    value={leadForm.email}
                    onChange={(e) => setLeadForm({ ...leadForm, email: e.target.value })}
                  />
                </div>
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Company</label>
                    <input
                      type="text"
                      className="form-input"
                      value={leadForm.company}
                      onChange={(e) => setLeadForm({ ...leadForm, company: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Lead Score (0-100)</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      className="form-input"
                      value={leadForm.score}
                      onChange={(e) => setLeadForm({ ...leadForm, score: parseInt(e.target.value) || 0 })}
                    />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowLeadModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Record Lead
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
