import { useState, useEffect } from 'react';
import { Plus, Folder, FileText, Search, History, Eye, Edit3 } from 'lucide-react';
import api from '../../services/api';

interface DocumentFolder {
  id: string;
  name: string;
  description?: string;
}

interface DocumentItem {
  id: string;
  title: string;
  content?: string;
  folder_id?: string;
  updated_at: string;
}

interface DocumentVersion {
  id: string;
  version_number: number;
  title: string;
  content?: string;
  change_summary?: string;
  created_at: string;
}

interface DocumentDetail extends DocumentItem {
  versions: DocumentVersion[];
}

export default function DocumentsPage() {
  const [folders, setFolders] = useState<DocumentFolder[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedFolderId, setSelectedFolderId] = useState<string>('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  // Active Document Viewer/Editor
  const [activeDoc, setActiveDoc] = useState<DocumentDetail | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [changeSummary, setChangeSummary] = useState('');

  // Modals
  const [showFolderModal, setShowFolderModal] = useState(false);
  const [showDocModal, setShowDocModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderDesc, setNewFolderDesc] = useState('');
  const [newDocTitle, setNewDocTitle] = useState('');
  const [newDocContent, setNewDocContent] = useState('');

  useEffect(() => {
    loadFolders();
    loadDocuments();
  }, []);

  useEffect(() => {
    loadDocuments(selectedFolderId);
  }, [selectedFolderId]);

  async function loadFolders() {
    try {
      const { data } = await api.get('/documents/folders');
      setFolders(data);
    } catch (err) {
      console.error('Failed to load folders:', err);
    }
  }

  async function loadDocuments(folderId?: string) {
    setLoading(true);
    try {
      const url = folderId ? `/documents/?folder_id=${folderId}` : '/documents/';
      const { data } = await api.get(url);
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setLoading(false);
    }
  }

  async function viewDocument(docId: string) {
    try {
      const { data } = await api.get(`/documents/${docId}`);
      setActiveDoc(data);
      setEditTitle(data.title);
      setEditContent(data.content || '');
      setChangeSummary('');
      setIsEditing(false);
    } catch (err) {
      console.error('Failed to get document detail:', err);
    }
  }

  async function handleCreateFolder(e: React.FormEvent) {
    e.preventDefault();
    try {
      const { data } = await api.post('/documents/folders', {
        name: newFolderName,
        description: newFolderDesc,
      });
      setFolders([...folders, data]);
      setShowFolderModal(false);
      setNewFolderName('');
      setNewFolderDesc('');
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error creating folder');
    }
  }

  async function handleCreateDocument(e: React.FormEvent) {
    e.preventDefault();
    try {
      const { data } = await api.post('/documents/', {
        title: newDocTitle,
        content: newDocContent,
        folder_id: selectedFolderId || undefined,
      });
      setDocuments([data, ...documents]);
      setShowDocModal(false);
      setNewDocTitle('');
      setNewDocContent('');
      viewDocument(data.id);
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error creating document');
    }
  }

  async function handleSaveDocument(e: React.FormEvent) {
    e.preventDefault();
    if (!activeDoc) return;
    try {
      const { data } = await api.patch(`/documents/${activeDoc.id}`, {
        title: editTitle,
        content: editContent,
        change_summary: changeSummary || undefined,
      });
      // Refresh detailed view
      await viewDocument(activeDoc.id);
      setDocuments(documents.map((d) => (d.id === activeDoc.id ? data : d)));
      setIsEditing(false);
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error updating document');
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Knowledge Base & Documents</h1>
          <p className="page-subtitle">Central wiki, architecture specs, SOPs, and version-controlled docs</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowFolderModal(true)}>
            <Plus size={15} />
            New Folder
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => setShowDocModal(true)}>
            <Plus size={15} />
            New Document
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: 20 }}>
        {/* Left Sidebar: Folders & Search */}
        <div>
          <div style={{ marginBottom: 12, position: 'relative' }}>
            <Search size={14} color="var(--color-text-muted)" style={{ position: 'absolute', left: 10, top: 11 }} />
            <input
              type="text"
              className="form-input"
              style={{ paddingLeft: 30, fontSize: 13, height: 36 }}
              placeholder="Filter titles..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="card" style={{ padding: '8px' }}>
            <div
              onClick={() => setSelectedFolderId('')}
              style={{
                padding: '8px 12px',
                borderRadius: 6,
                fontSize: 13,
                fontWeight: selectedFolderId === '' ? 600 : 400,
                background: selectedFolderId === '' ? 'var(--color-surface-2)' : 'transparent',
                color: selectedFolderId === '' ? 'var(--color-primary)' : 'var(--color-text)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <Folder size={15} />
              All Documents
            </div>
            {folders.map((f) => (
              <div
                key={f.id}
                onClick={() => setSelectedFolderId(f.id)}
                style={{
                  padding: '8px 12px',
                  borderRadius: 6,
                  fontSize: 13,
                  fontWeight: selectedFolderId === f.id ? 600 : 400,
                  background: selectedFolderId === f.id ? 'var(--color-surface-2)' : 'transparent',
                  color: selectedFolderId === f.id ? 'var(--color-primary)' : 'var(--color-text)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <Folder size={15} />
                {f.name}
              </div>
            ))}
          </div>

          {/* Documents list */}
          <div className="card" style={{ marginTop: 16, padding: '8px', maxHeight: 400, overflowY: 'auto' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-text-muted)', padding: '6px 12px', textTransform: 'uppercase' }}>
              Documents ({documents.length})
            </div>
            {loading ? (
              <div style={{ padding: 20, textAlign: 'center' }}>
                <span className="spinner" style={{ margin: '0 auto', width: 16, height: 16 }} />
              </div>
            ) : documents.length === 0 ? (
              <div style={{ padding: 16, fontSize: 13, color: 'var(--color-text-muted)', textAlign: 'center' }}>
                No documents found
              </div>
            ) : (
              documents
                .filter((d) => d.title.toLowerCase().includes(search.toLowerCase()))
                .map((d) => (
                  <div
                    key={d.id}
                    onClick={() => viewDocument(d.id)}
                    style={{
                      padding: '8px 12px',
                      borderRadius: 6,
                      fontSize: 13,
                      background: activeDoc?.id === d.id ? 'rgba(99,102,241,0.12)' : 'transparent',
                      color: activeDoc?.id === d.id ? 'var(--color-primary)' : 'var(--color-text)',
                      fontWeight: activeDoc?.id === d.id ? 600 : 400,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                    }}
                  >
                    <FileText size={15} />
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {d.title}
                    </span>
                  </div>
                ))
            )}
          </div>
        </div>

        {/* Right Content: Active Document Viewer or Editor */}
        <div className="card" style={{ minHeight: 520, padding: 24, display: 'flex', flexDirection: 'column' }}>
          {!activeDoc ? (
            <div className="empty-state" style={{ margin: 'auto' }}>
              <FileText size={48} color="var(--color-text-muted)" style={{ opacity: 0.3 }} />
              <h3>Select a document</h3>
              <p>Choose a document from the left sidebar or create a new one.</p>
            </div>
          ) : isEditing ? (
            <form onSubmit={handleSaveDocument} style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <input
                  type="text"
                  required
                  className="form-input"
                  style={{ fontSize: 18, fontWeight: 700, flex: 1, marginRight: 16 }}
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                />
                <div style={{ display: 'flex', gap: 8 }}>
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => setIsEditing(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary btn-sm">
                    Save Version
                  </button>
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: 12 }}>
                <input
                  type="text"
                  className="form-input"
                  style={{ fontSize: 12 }}
                  placeholder="Change summary (e.g. Added section on API endpoints)"
                  value={changeSummary}
                  onChange={(e) => setChangeSummary(e.target.value)}
                />
              </div>

              <textarea
                className="form-textarea"
                style={{ flex: 1, minHeight: 340, fontFamily: 'monospace', fontSize: 13 }}
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
              />
            </form>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--color-border)', paddingBottom: 16, marginBottom: 20 }}>
                <div>
                  <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>{activeDoc.title}</h2>
                  <div style={{ fontSize: 12, color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span>Last updated: {new Date(activeDoc.updated_at).toLocaleString()}</span>
                    <span>•</span>
                    <span className="badge badge-info" style={{ fontSize: 11 }}>
                      v{activeDoc.versions?.[0]?.version_number || 1}
                    </span>
                  </div>
                </div>
                <button className="btn btn-secondary btn-sm" onClick={() => setIsEditing(true)}>
                  <Edit3 size={14} />
                  Edit Document
                </button>
              </div>

              {/* Document Content */}
              <div style={{ flex: 1, whiteSpace: 'pre-wrap', lineHeight: 1.7, fontSize: 14 }}>
                {activeDoc.content || <span style={{ color: 'var(--color-text-muted)', fontStyle: 'italic' }}>No content in this document.</span>}
              </div>

              {/* Version History Accordion */}
              {activeDoc.versions && activeDoc.versions.length > 0 && (
                <div style={{ marginTop: 32, borderTop: '1px solid var(--color-border)', paddingTop: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: 12 }}>
                    <History size={14} /> Version History
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {activeDoc.versions.map((v) => (
                      <div
                        key={v.id}
                        style={{
                          padding: '8px 12px',
                          borderRadius: 'var(--radius-sm)',
                          background: 'var(--color-surface-2)',
                          fontSize: 12,
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                        }}
                      >
                        <div>
                          <span style={{ fontWeight: 700, marginRight: 8 }}>Version {v.version_number}</span>
                          <span style={{ color: 'var(--color-text-muted)' }}>{v.change_summary || 'Update'}</span>
                        </div>
                        <span style={{ color: 'var(--color-text-subtle)' }}>{new Date(v.created_at).toLocaleDateString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* New Folder Modal */}
      {showFolderModal && (
        <div className="modal-backdrop" onClick={() => setShowFolderModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">New Folder</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowFolderModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreateFolder}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Folder Name</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. Product Specs, HR Handbooks"
                    value={newFolderName}
                    onChange={(e) => setNewFolderName(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Description (Optional)</label>
                  <input
                    type="text"
                    className="form-input"
                    value={newFolderDesc}
                    onChange={(e) => setNewFolderDesc(e.target.value)}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowFolderModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Folder
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New Document Modal */}
      {showDocModal && (
        <div className="modal-backdrop" onClick={() => setShowDocModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Create New Document</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowDocModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreateDocument}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Document Title</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. Q4 Strategy Memo"
                    value={newDocTitle}
                    onChange={(e) => setNewDocTitle(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Initial Content</label>
                  <textarea
                    className="form-textarea"
                    style={{ minHeight: 180 }}
                    placeholder="Write initial draft or markdown..."
                    value={newDocContent}
                    onChange={(e) => setNewDocContent(e.target.value)}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowDocModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Document
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
