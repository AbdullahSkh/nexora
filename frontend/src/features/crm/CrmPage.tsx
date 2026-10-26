import { useState, useEffect } from 'react';
import { Plus, Search, Building2, UserCheck, TrendingUp } from 'lucide-react';
import api from '../../services/api';

interface Deal {
  id: string;
  title: string;
  value: number;
  stage: string;
  created_at: string;
}

interface Contact {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
}

interface Company {
  id: string;
  name: string;
  industry?: string;
  website?: string;
}

const STAGE_COLORS: Record<string, string> = {
  lead: 'badge-neutral',
  qualified: 'badge-info',
  proposal: 'badge-warning',
  negotiation: 'badge-warning',
  closed_won: 'badge-success',
  closed_lost: 'badge-danger',
};

export default function CrmPage() {
  const [tab, setTab] = useState<'deals' | 'contacts' | 'companies'>('deals');
  const [deals, setDeals] = useState<Deal[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  // Modals
  const [showModal, setShowModal] = useState(false);
  const [dealForm, setDealForm] = useState({ title: '', value: 10000, stage: 'lead' });
  const [contactForm, setContactForm] = useState({ first_name: '', last_name: '', email: '', phone: '' });
  const [companyForm, setCompanyForm] = useState({ name: '', industry: 'SaaS', website: '' });

  useEffect(() => {
    loadData();
  }, [tab]);

  async function loadData() {
    setLoading(true);
    try {
      if (tab === 'deals') {
        const { data } = await api.get('/crm/deals');
        setDeals(data);
      } else if (tab === 'contacts') {
        const { data } = await api.get('/crm/contacts');
        setContacts(data);
      } else {
        const { data } = await api.get('/crm/companies');
        setCompanies(data);
      }
    } catch (err) {
      console.error('Failed to load CRM data:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    try {
      if (tab === 'deals') {
        await api.post('/crm/deals', dealForm);
      } else if (tab === 'contacts') {
        await api.post('/crm/contacts', contactForm);
      } else {
        await api.post('/crm/companies', companyForm);
      }
      setShowModal(false);
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error creating record');
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">CRM & Pipeline</h1>
          <p className="page-subtitle">Track accounts, decision makers, and high-value sales deals</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
          <Plus size={16} />
          Add {tab === 'deals' ? 'Deal' : tab === 'contacts' ? 'Contact' : 'Company'}
        </button>
      </div>

      {/* Tabs */}
      <div className="tabs-nav">
        <button className={`tab-btn ${tab === 'deals' ? 'active' : ''}`} onClick={() => setTab('deals')}>
          <TrendingUp size={15} style={{ display: 'inline', marginRight: 6 }} />
          Deals Pipeline
        </button>
        <button className={`tab-btn ${tab === 'contacts' ? 'active' : ''}`} onClick={() => setTab('contacts')}>
          <UserCheck size={15} style={{ display: 'inline', marginRight: 6 }} />
          Contacts
        </button>
        <button className={`tab-btn ${tab === 'companies' ? 'active' : ''}`} onClick={() => setTab('companies')}>
          <Building2 size={15} style={{ display: 'inline', marginRight: 6 }} />
          Companies
        </button>
      </div>

      {/* Search Bar */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 18 }}>
        <div style={{ position: 'relative', width: 320 }}>
          <Search size={15} color="var(--color-text-muted)" style={{ position: 'absolute', left: 12, top: 11 }} />
          <input
            type="text"
            className="form-input"
            style={{ paddingLeft: 34 }}
            placeholder={`Filter ${tab}...`}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Table view */}
      <div className="card table-container">
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center' }}>
            <span className="spinner" style={{ margin: '0 auto' }} />
          </div>
        ) : tab === 'deals' ? (
          <table className="table">
            <thead>
              <tr>
                <th>Deal Name</th>
                <th>Value</th>
                <th>Stage</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {deals.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', padding: 30, color: 'var(--color-text-muted)' }}>
                    No deals created yet. Click "Add Deal" to build your pipeline.
                  </td>
                </tr>
              ) : (
                deals
                  .filter((d) => d.title.toLowerCase().includes(search.toLowerCase()))
                  .map((d) => (
                    <tr key={d.id}>
                      <td style={{ fontWeight: 600 }}>{d.title}</td>
                      <td>${d.value.toLocaleString()}</td>
                      <td>
                        <span className={`badge ${STAGE_COLORS[d.stage] || 'badge-neutral'}`}>
                          {d.stage.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td style={{ color: 'var(--color-text-muted)' }}>
                        {new Date(d.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))
              )}
            </tbody>
          </table>
        ) : tab === 'contacts' ? (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
              </tr>
            </thead>
            <tbody>
              {contacts.length === 0 ? (
                <tr>
                  <td colSpan={3} style={{ textAlign: 'center', padding: 30, color: 'var(--color-text-muted)' }}>
                    No contacts recorded yet. Click "Add Contact" to start.
                  </td>
                </tr>
              ) : (
                contacts
                  .filter((c) => `${c.first_name} ${c.last_name} ${c.email}`.toLowerCase().includes(search.toLowerCase()))
                  .map((c) => (
                    <tr key={c.id}>
                      <td style={{ fontWeight: 600 }}>{c.first_name} {c.last_name}</td>
                      <td>{c.email}</td>
                      <td style={{ color: 'var(--color-text-muted)' }}>{c.phone || '—'}</td>
                    </tr>
                  ))
              )}
            </tbody>
          </table>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Company Name</th>
                <th>Industry</th>
                <th>Website</th>
              </tr>
            </thead>
            <tbody>
              {companies.length === 0 ? (
                <tr>
                  <td colSpan={3} style={{ textAlign: 'center', padding: 30, color: 'var(--color-text-muted)' }}>
                    No companies recorded yet. Click "Add Company".
                  </td>
                </tr>
              ) : (
                companies
                  .filter((c) => c.name.toLowerCase().includes(search.toLowerCase()))
                  .map((c) => (
                    <tr key={c.id}>
                      <td style={{ fontWeight: 600 }}>{c.name}</td>
                      <td><span className="badge badge-info">{c.industry || 'General'}</span></td>
                      <td>{c.website ? <a href={c.website} target="_blank" rel="noreferrer" style={{ color: 'var(--color-primary)' }}>{c.website}</a> : '—'}</td>
                    </tr>
                  ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Creation Modal */}
      {showModal && (
        <div className="modal-backdrop" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">New {tab === 'deals' ? 'Deal' : tab === 'contacts' ? 'Contact' : 'Company'}</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="modal-body">
                {tab === 'deals' ? (
                  <>
                    <div className="form-group">
                      <label className="form-label">Deal Title</label>
                      <input
                        type="text"
                        required
                        className="form-input"
                        placeholder="e.g. Acme Enterprise Annual Contract"
                        value={dealForm.title}
                        onChange={(e) => setDealForm({ ...dealForm, title: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Value ($ USD)</label>
                      <input
                        type="number"
                        required
                        min="0"
                        className="form-input"
                        value={dealForm.value}
                        onChange={(e) => setDealForm({ ...dealForm, value: parseFloat(e.target.value) || 0 })}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Initial Stage</label>
                      <select
                        className="form-select"
                        value={dealForm.stage}
                        onChange={(e) => setDealForm({ ...dealForm, stage: e.target.value })}
                      >
                        <option value="lead">Lead</option>
                        <option value="qualified">Qualified</option>
                        <option value="proposal">Proposal Sent</option>
                        <option value="negotiation">Negotiation</option>
                        <option value="closed_won">Closed Won</option>
                        <option value="closed_lost">Closed Lost</option>
                      </select>
                    </div>
                  </>
                ) : tab === 'contacts' ? (
                  <>
                    <div className="form-group">
                      <label className="form-label">First Name</label>
                      <input
                        type="text"
                        required
                        className="form-input"
                        value={contactForm.first_name}
                        onChange={(e) => setContactForm({ ...contactForm, first_name: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Last Name</label>
                      <input
                        type="text"
                        required
                        className="form-input"
                        value={contactForm.last_name}
                        onChange={(e) => setContactForm({ ...contactForm, last_name: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Email Address</label>
                      <input
                        type="email"
                        required
                        className="form-input"
                        value={contactForm.email}
                        onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Phone Number (Optional)</label>
                      <input
                        type="tel"
                        className="form-input"
                        value={contactForm.phone}
                        onChange={(e) => setContactForm({ ...contactForm, phone: e.target.value })}
                      />
                    </div>
                  </>
                ) : (
                  <>
                    <div className="form-group">
                      <label className="form-label">Company Name</label>
                      <input
                        type="text"
                        required
                        className="form-input"
                        placeholder="e.g. Stripe, Acme Corp"
                        value={companyForm.name}
                        onChange={(e) => setCompanyForm({ ...companyForm, name: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Industry</label>
                      <input
                        type="text"
                        className="form-input"
                        value={companyForm.industry}
                        onChange={(e) => setCompanyForm({ ...companyForm, industry: e.target.value })}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Website</label>
                      <input
                        type="url"
                        className="form-input"
                        placeholder="https://example.com"
                        value={companyForm.website}
                        onChange={(e) => setCompanyForm({ ...companyForm, website: e.target.value })}
                      />
                    </div>
                  </>
                )}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
