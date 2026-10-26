import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
   Users,
   FolderKanban,
   DollarSign,
   Contact,
   TrendingUp,
   CheckCircle,
   LifeBuoy,
   Sparkles,
   ArrowRight,
 } from 'lucide-react';
import api from '../../services/api';

interface OverviewData {
  total_revenue: number;
  total_expenses: number;
  net_profit: number;
  active_projects: number;
  open_tasks: number;
  pipeline_value: number;
  open_deals_count: number;
  total_employees: number;
  open_tickets_count: number;
  active_campaigns_count: number;
  total_leads_count: number;
}

const modules = [
  { name: 'CRM', desc: 'Leads, deals pipeline, contacts, and customer companies', icon: Contact, path: '/crm', color: '#6366f1' },
  { name: 'Projects', desc: 'Agile sprints, Kanban task board, and team collaboration', icon: FolderKanban, path: '/projects', color: '#8b5cf6' },
  { name: 'Finance', desc: 'Invoices, expense tracking, budgets, and payments', icon: DollarSign, path: '/finance', color: '#22d3a5' },
  { name: 'HR', desc: 'Employee directory, departments, and leave approvals', icon: Users, path: '/hr', color: '#f59e0b' },
];

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMetrics() {
      try {
        const { data } = await api.get('/analytics/overview');
        setMetrics(data);
      } catch (err) {
        console.error('Failed to load overview analytics:', err);
      } finally {
        setLoading(false);
      }
    }
    loadMetrics();
  }, []);

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Executive Dashboard</h1>
          <p className="page-subtitle">Real-time overview of your startup operations</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <Link to="/projects" className="btn btn-primary btn-sm">
            <CheckCircle size={15} />
            View Active Tasks
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(34, 211, 165, 0.12)' }}>
            <DollarSign size={18} color="#22d3a5" />
          </div>
          <div className="stat-value">
            {loading ? <span className="spinner" /> : formatCurrency(metrics?.total_revenue ?? 0)}
          </div>
          <div className="stat-label">Total Revenue Collected</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(99, 102, 241, 0.12)' }}>
            <TrendingUp size={18} color="#6366f1" />
          </div>
          <div className="stat-value">
            {loading ? <span className="spinner" /> : formatCurrency(metrics?.pipeline_value ?? 0)}
          </div>
          <div className="stat-label">Active Pipeline Value ({metrics?.open_deals_count ?? 0} deals)</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(139, 92, 246, 0.12)' }}>
            <FolderKanban size={18} color="#8b5cf6" />
          </div>
          <div className="stat-value">
            {loading ? <span className="spinner" /> : metrics?.active_projects ?? 0}
          </div>
          <div className="stat-label">Active Projects</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(56, 189, 248, 0.12)' }}>
            <CheckCircle size={18} color="#38bdf8" />
          </div>
          <div className="stat-value">
            {loading ? <span className="spinner" /> : metrics?.open_tasks ?? 0}
          </div>
          <div className="stat-label">Open Tasks in Backlog/Sprints</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.12)' }}>
            <Users size={18} color="#f59e0b" />
          </div>
          <div className="stat-value">
            {loading ? <span className="spinner" /> : metrics?.total_employees ?? 0}
          </div>
          <div className="stat-label">Team Members & Staff</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(239, 68, 68, 0.12)' }}>
            <LifeBuoy size={18} color="#ef4444" />
          </div>
          <div className="stat-value">
            {loading ? <span className="spinner" /> : metrics?.open_tickets_count ?? 0}
          </div>
          <div className="stat-label">Open Support Tickets</div>
        </div>
      </div>

      {/* AI Assistant Banner */}
      <div
        className="card"
        style={{
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.08) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          marginBottom: 28,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '20px 24px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 12,
              background: 'var(--gradient-brand)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 14px rgba(99,102,241,0.35)',
            }}
          >
            <Sparkles size={22} color="#fff" />
          </div>
          <div>
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 2 }}>Nexora AI Copilot Ready</h3>
            <p style={{ fontSize: 13, color: 'var(--color-text-muted)', margin: 0 }}>
              Use AI to summarize documents, generate email campaigns, and analyze pipeline conversions.
            </p>
          </div>
        </div>
        <Link to="/crm" className="btn btn-secondary btn-sm">
          Explore AI Insights <ArrowRight size={14} />
        </Link>
      </div>

      {/* Core Modules Grid */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ fontSize: 16, fontWeight: 700, letterSpacing: '-0.2px' }}>Operational Modules</h2>
      </div>

      <div className="grid-2" style={{ gap: 16 }}>
        {modules.map((m) => (
          <Link
            key={m.name}
            to={m.path}
            className="card"
            style={{
              display: 'flex',
              gap: 16,
              alignItems: 'flex-start',
              transition: 'all 150ms ease',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = m.color + '60';
              (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
              (e.currentTarget as HTMLElement).style.boxShadow = `0 8px 24px ${m.color}20`;
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = '';
              (e.currentTarget as HTMLElement).style.transform = '';
              (e.currentTarget as HTMLElement).style.boxShadow = '';
            }}
          >
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: 12,
                flexShrink: 0,
                background: m.color + '18',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <m.icon size={22} color={m.color} />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                <span style={{ fontWeight: 700, fontSize: 15 }}>{m.name}</span>
                <ArrowRight size={14} color="var(--color-text-muted)" />
              </div>
              <div style={{ fontSize: 13, color: 'var(--color-text-muted)', lineHeight: 1.5 }}>{m.desc}</div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
