import { useState, useEffect } from 'react';
import { Plus, Users, Calendar, Check, X } from 'lucide-react';
import api from '../../services/api';
import { useAuthStore } from '../../stores/authStore';

interface Employee {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  status: string;
  hire_date?: string;
}

interface LeaveRequest {
  id: string;
  employee_id: string;
  start_date: string;
  end_date: string;
  reason?: string;
  status: string;
}

export default function HrPage() {
  const [tab, setTab] = useState<'employees' | 'leave'>('employees');
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const user = useAuthStore((s) => s.user);

  // Modals
  const [showEmployeeModal, setShowEmployeeModal] = useState(false);
  const [showLeaveModal, setShowLeaveModal] = useState(false);

  const [employeeForm, setEmployeeForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    hire_date: new Date().toISOString().split('T')[0],
  });

  const [leaveForm, setLeaveForm] = useState({
    employee_id: '',
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date(Date.now() + 3 * 86400000).toISOString().split('T')[0],
    leave_type: 'vacation',
    reason: 'Annual family holiday',
  });

  useEffect(() => {
    loadData();
  }, [tab]);

  async function loadData() {
    setLoading(true);
    try {
      if (tab === 'employees') {
        const { data } = await api.get('/hr/employees');
        setEmployees(data);
        if (data.length > 0 && !leaveForm.employee_id) {
          setLeaveForm((prev) => ({ ...prev, employee_id: data[0].id }));
        }
      } else {
        const { data } = await api.get('/hr/leave-requests');
        setLeaveRequests(data);
      }
    } catch (err) {
      console.error('Failed to load HR data:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateEmployee(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post('/hr/employees', employeeForm);
      setShowEmployeeModal(false);
      setEmployeeForm({ first_name: '', last_name: '', email: '', hire_date: new Date().toISOString().split('T')[0] });
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error creating employee');
    }
  }

  async function handleSubmitLeave(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post('/hr/leave-requests', leaveForm);
      setShowLeaveModal(false);
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error submitting leave request');
    }
  }

  async function handleApproveLeave(id: string, approved: boolean) {
    try {
      await api.post(`/hr/leave-requests/${id}/approve`, {
        approved,
        rejection_reason: approved ? undefined : 'Scheduling conflict',
      });
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Action failed (Admin only)');
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Human Resources & Personnel</h1>
          <p className="page-subtitle">Team directory, department structure, and leave request management</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowLeaveModal(true)}>
            <Calendar size={15} />
            Request Leave
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => setShowEmployeeModal(true)}>
            <Plus size={15} />
            Add Employee
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-nav">
        <button className={`tab-btn ${tab === 'employees' ? 'active' : ''}`} onClick={() => setTab('employees')}>
          <Users size={15} style={{ display: 'inline', marginRight: 6 }} />
          Employee Directory
        </button>
        <button className={`tab-btn ${tab === 'leave' ? 'active' : ''}`} onClick={() => setTab('leave')}>
          <Calendar size={15} style={{ display: 'inline', marginRight: 6 }} />
          Leave Approvals
        </button>
      </div>

      {/* Content Table */}
      <div className="card table-container">
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center' }}>
            <span className="spinner" style={{ margin: '0 auto' }} />
          </div>
        ) : tab === 'employees' ? (
          <table className="table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Work Email</th>
                <th>Status</th>
                <th>Hire Date</th>
              </tr>
            </thead>
            <tbody>
              {employees.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', padding: 30, color: 'var(--color-text-muted)' }}>
                    No employees enrolled yet. Click "Add Employee" to register staff.
                  </td>
                </tr>
              ) : (
                employees.map((emp) => (
                  <tr key={emp.id}>
                    <td style={{ fontWeight: 600 }}>{emp.first_name} {emp.last_name}</td>
                    <td>{emp.email}</td>
                    <td><span className="badge badge-success">ACTIVE</span></td>
                    <td style={{ color: 'var(--color-text-muted)' }}>{emp.hire_date || '—'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Duration</th>
                <th>Reason</th>
                <th>Status</th>
                {user?.is_superuser && <th>Action</th>}
              </tr>
            </thead>
            <tbody>
              {leaveRequests.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', padding: 30, color: 'var(--color-text-muted)' }}>
                    No leave requests found.
                  </td>
                </tr>
              ) : (
                leaveRequests.map((req) => (
                  <tr key={req.id}>
                    <td style={{ fontWeight: 600 }}>{req.start_date} to {req.end_date}</td>
                    <td>{req.reason || 'Personal leave'}</td>
                    <td>
                      <span className={`badge ${req.status === 'approved' ? 'badge-success' : req.status === 'rejected' ? 'badge-danger' : 'badge-warning'}`}>
                        {req.status.toUpperCase()}
                      </span>
                    </td>
                    {user?.is_superuser && (
                      <td>
                        {req.status === 'pending' && (
                          <div style={{ display: 'flex', gap: 6 }}>
                            <button
                              className="btn btn-secondary btn-sm"
                              style={{ padding: '2px 8px', color: '#22d3a5' }}
                              onClick={() => handleApproveLeave(req.id, true)}
                              title="Approve"
                            >
                              <Check size={14} />
                            </button>
                            <button
                              className="btn btn-secondary btn-sm"
                              style={{ padding: '2px 8px', color: '#ef4444' }}
                              onClick={() => handleApproveLeave(req.id, false)}
                              title="Reject"
                            >
                              <X size={14} />
                            </button>
                          </div>
                        )}
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Employee Modal */}
      {showEmployeeModal && (
        <div className="modal-backdrop" onClick={() => setShowEmployeeModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">New Employee Onboarding</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowEmployeeModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreateEmployee}>
              <div className="modal-body">
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">First Name</label>
                    <input
                      type="text"
                      required
                      className="form-input"
                      value={employeeForm.first_name}
                      onChange={(e) => setEmployeeForm({ ...employeeForm, first_name: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Last Name</label>
                    <input
                      type="text"
                      required
                      className="form-input"
                      value={employeeForm.last_name}
                      onChange={(e) => setEmployeeForm({ ...employeeForm, last_name: e.target.value })}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Work Email</label>
                  <input
                    type="email"
                    required
                    className="form-input"
                    value={employeeForm.email}
                    onChange={(e) => setEmployeeForm({ ...employeeForm, email: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Hire Date</label>
                  <input
                    type="date"
                    required
                    className="form-input"
                    value={employeeForm.hire_date}
                    onChange={(e) => setEmployeeForm({ ...employeeForm, hire_date: e.target.value })}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowEmployeeModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Register Employee
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Leave Request Modal */}
      {showLeaveModal && (
        <div className="modal-backdrop" onClick={() => setShowLeaveModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Submit Leave Request</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowLeaveModal(false)}>✕</button>
            </div>
            <form onSubmit={handleSubmitLeave}>
              <div className="modal-body">
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Start Date</label>
                    <input
                      type="date"
                      required
                      className="form-input"
                      value={leaveForm.start_date}
                      onChange={(e) => setLeaveForm({ ...leaveForm, start_date: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">End Date</label>
                    <input
                      type="date"
                      required
                      className="form-input"
                      value={leaveForm.end_date}
                      onChange={(e) => setLeaveForm({ ...leaveForm, end_date: e.target.value })}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Reason / Notes</label>
                  <textarea
                    className="form-textarea"
                    required
                    value={leaveForm.reason}
                    onChange={(e) => setLeaveForm({ ...leaveForm, reason: e.target.value })}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowLeaveModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
