import { useState, useEffect } from 'react';
import { Receipt, FileText, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import api from '../../services/api';

interface Invoice {
  id: string;
  invoice_number: string;
  status: string;
  issue_date: string;
  due_date: string;
  total: number;
}

interface Expense {
  id: string;
  category: string;
  description: string;
  amount: number;
  expense_date: string;
}

const INVOICE_STATUS_BADGES: Record<string, string> = {
  draft: 'badge-neutral',
  sent: 'badge-info',
  paid: 'badge-success',
  overdue: 'badge-danger',
  cancelled: 'badge-neutral',
};

export default function FinancePage() {
  const [tab, setTab] = useState<'invoices' | 'expenses'>('invoices');
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);

  // Modals
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  const [showExpenseModal, setShowExpenseModal] = useState(false);

  const [invoiceForm, setInvoiceForm] = useState({
    invoice_number: `INV-${Math.floor(1000 + Math.random() * 9000)}`,
    issue_date: new Date().toISOString().split('T')[0],
    due_date: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0],
    subtotal: 5000,
    tax_rate: 0,
    total: 5000,
    status: 'sent',
    line_items: [{ description: 'Enterprise License Tier', quantity: 1, unit_price: 5000, total: 5000 }],
  });

  const [expenseForm, setExpenseForm] = useState({
    category: 'software',
    description: '',
    amount: 150,
    expense_date: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    loadData();
  }, [tab]);

  async function loadData() {
    setLoading(true);
    try {
      if (tab === 'invoices') {
        const { data } = await api.get('/finance/invoices');
        setInvoices(data);
      } else {
        const { data } = await api.get('/finance/expenses');
        setExpenses(data);
      }
    } catch (err) {
      console.error('Failed to load finance records:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateInvoice(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post('/finance/invoices', invoiceForm);
      setShowInvoiceModal(false);
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error creating invoice');
    }
  }

  async function handleCreateExpense(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post('/finance/expenses', expenseForm);
      setShowExpenseModal(false);
      setExpenseForm({ category: 'software', description: '', amount: 150, expense_date: new Date().toISOString().split('T')[0] });
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error recording expense');
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Financial Ledger & Billing</h1>
          <p className="page-subtitle">Invoices, payments, expense management, and cash flow control</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowExpenseModal(true)}>
            <ArrowDownLeft size={15} color="#ef4444" />
            Record Expense
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => setShowInvoiceModal(true)}>
            <ArrowUpRight size={15} color="#fff" />
            Create Invoice
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-nav">
        <button className={`tab-btn ${tab === 'invoices' ? 'active' : ''}`} onClick={() => setTab('invoices')}>
          <FileText size={15} style={{ display: 'inline', marginRight: 6 }} />
          Invoices & Receivables
        </button>
        <button className={`tab-btn ${tab === 'expenses' ? 'active' : ''}`} onClick={() => setTab('expenses')}>
          <Receipt size={15} style={{ display: 'inline', marginRight: 6 }} />
          Expenses & Burn
        </button>
      </div>

      {/* Tables */}
      <div className="card table-container">
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center' }}>
            <span className="spinner" style={{ margin: '0 auto' }} />
          </div>
        ) : tab === 'invoices' ? (
          <table className="table">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Status</th>
                <th>Issue Date</th>
                <th>Due Date</th>
                <th>Total ($ USD)</th>
              </tr>
            </thead>
            <tbody>
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: 30, color: 'var(--color-text-muted)' }}>
                    No invoices recorded yet. Click "Create Invoice" to bill clients.
                  </td>
                </tr>
              ) : (
                invoices.map((inv) => (
                  <tr key={inv.id}>
                    <td style={{ fontWeight: 600 }}>{inv.invoice_number}</td>
                    <td>
                      <span className={`badge ${INVOICE_STATUS_BADGES[inv.status] || 'badge-neutral'}`}>
                        {inv.status.toUpperCase()}
                      </span>
                    </td>
                    <td>{inv.issue_date}</td>
                    <td>{inv.due_date}</td>
                    <td style={{ fontWeight: 700 }}>${Number(inv.total).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Description</th>
                <th>Category</th>
                <th>Expense Date</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              {expenses.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', padding: 30, color: 'var(--color-text-muted)' }}>
                    No expenses submitted. Click "Record Expense".
                  </td>
                </tr>
              ) : (
                expenses.map((exp) => (
                  <tr key={exp.id}>
                    <td style={{ fontWeight: 600 }}>{exp.description}</td>
                    <td><span className="badge badge-info">{exp.category.toUpperCase()}</span></td>
                    <td>{exp.expense_date}</td>
                    <td style={{ color: '#ef4444', fontWeight: 600 }}>-${Number(exp.amount).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Invoice Modal */}
      {showInvoiceModal && (
        <div className="modal-backdrop" onClick={() => setShowInvoiceModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Create Client Invoice</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowInvoiceModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreateInvoice}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Invoice Number</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    value={invoiceForm.invoice_number}
                    onChange={(e) => setInvoiceForm({ ...invoiceForm, invoice_number: e.target.value })}
                  />
                </div>
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Issue Date</label>
                    <input
                      type="date"
                      required
                      className="form-input"
                      value={invoiceForm.issue_date}
                      onChange={(e) => setInvoiceForm({ ...invoiceForm, issue_date: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Due Date</label>
                    <input
                      type="date"
                      required
                      className="form-input"
                      value={invoiceForm.due_date}
                      onChange={(e) => setInvoiceForm({ ...invoiceForm, due_date: e.target.value })}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Total Amount ($ USD)</label>
                  <input
                    type="number"
                    required
                    min="1"
                    className="form-input"
                    value={invoiceForm.total}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value) || 0;
                      setInvoiceForm({
                        ...invoiceForm,
                        total: val,
                        subtotal: val,
                        line_items: [{ description: 'Professional Services', quantity: 1, unit_price: val, total: val }],
                      });
                    }}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowInvoiceModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Generate Invoice
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Expense Modal */}
      {showExpenseModal && (
        <div className="modal-backdrop" onClick={() => setShowExpenseModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Record Operating Expense</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowExpenseModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreateExpense}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Expense Description</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. AWS Cloud Infrastructure - Oct"
                    value={expenseForm.description}
                    onChange={(e) => setExpenseForm({ ...expenseForm, description: e.target.value })}
                  />
                </div>
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Category</label>
                    <select
                      className="form-select"
                      value={expenseForm.category}
                      onChange={(e) => setExpenseForm({ ...expenseForm, category: e.target.value })}
                    >
                      <option value="infrastructure">Infrastructure</option>
                      <option value="software">Software & SaaS</option>
                      <option value="marketing">Marketing & Ads</option>
                      <option value="salaries">Salaries</option>
                      <option value="travel">Travel</option>
                      <option value="office">Office</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Amount ($ USD)</label>
                    <input
                      type="number"
                      required
                      min="0.01"
                      step="0.01"
                      className="form-input"
                      value={expenseForm.amount}
                      onChange={(e) => setExpenseForm({ ...expenseForm, amount: parseFloat(e.target.value) || 0 })}
                    />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowExpenseModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Expense
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
