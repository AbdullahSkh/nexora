import React, { useEffect } from 'react';
import { useNavigate, NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Briefcase,
  FolderKanban,
  DollarSign,
  Contact,
  FileText,
  Calendar,
  LifeBuoy,
  Megaphone,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import NotificationBell from '../components/NotificationBell';

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard, to: '/' },
  { label: 'CRM', icon: Contact, to: '/crm' },
  { label: 'Projects', icon: FolderKanban, to: '/projects' },
  { label: 'Finance', icon: DollarSign, to: '/finance' },
  { label: 'Documents', icon: FileText, to: '/documents' },
  { label: 'Meetings', icon: Calendar, to: '/meetings' },
  { label: 'Support', icon: LifeBuoy, to: '/support' },
  { label: 'Marketing', icon: Megaphone, to: '/marketing' },
  { label: 'HR', icon: Users, to: '/hr' },
  { label: 'Team', icon: Briefcase, to: '/team' },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, logout, fetchMe } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) fetchMe();
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">N</div>
          <span className="sidebar-logo-text">Nexora</span>
          <div style={{ marginLeft: 'auto' }}>
            <NotificationBell />
          </div>
        </div>

        <nav className="sidebar-nav">
          <span className="sidebar-section-label">Workspace Modules</span>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              <item.icon size={16} />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* User info at bottom */}
        <div style={{ padding: '16px 10px', borderTop: '1px solid var(--color-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 10px' }}>
            <div
              style={{
                width: 30,
                height: 30,
                borderRadius: '50%',
                background: 'var(--gradient-brand)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 13,
                fontWeight: 700,
                color: 'white',
                flexShrink: 0,
              }}
            >
              {user?.first_name?.[0] ?? 'U'}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div
                style={{
                  fontSize: 13,
                  fontWeight: 600,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {user?.first_name} {user?.last_name}
              </div>
              <div
                style={{
                  fontSize: 11,
                  color: 'var(--color-text-muted)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {user?.is_superuser ? 'Admin' : 'Member'}
              </div>
            </div>
            <button
              className="btn btn-ghost btn-sm"
              onClick={handleLogout}
              title="Logout"
              style={{ padding: '4px 6px' }}
            >
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}
