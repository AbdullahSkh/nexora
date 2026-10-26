import { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import api from '../../services/api';

interface Project {
  id: string;
  name: string;
  description?: string;
  status: string;
}

interface Task {
  id: string;
  title: string;
  status: string;
  priority: string;
  project_id: string;
  story_points?: number;
}

const COLUMNS = [
  { key: 'todo', label: 'To Do', color: '#6366f1' },
  { key: 'in_progress', label: 'In Progress', color: '#f59e0b' },
  { key: 'in_review', label: 'In Review', color: '#8b5cf6' },
  { key: 'done', label: 'Done', color: '#22d3a5' },
];

const PRIORITY_BADGES: Record<string, string> = {
  low: 'badge-neutral',
  medium: 'badge-info',
  high: 'badge-warning',
  critical: 'badge-danger',
};

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [loading, setLoading] = useState(true);

  // Modals
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '', status: 'active' });
  const [newTask, setNewTask] = useState({ title: '', priority: 'medium', status: 'todo' });

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      loadTasks(selectedProjectId);
    }
  }, [selectedProjectId]);

  async function loadProjects() {
    setLoading(true);
    try {
      const { data } = await api.get('/projects');
      setProjects(data);
      if (data.length > 0 && !selectedProjectId) {
        setSelectedProjectId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadTasks(projId: string) {
    try {
      const { data } = await api.get(`/projects/tasks?project_id=${projId}`);
      setTasks(data);
    } catch (err) {
      console.error('Failed to load tasks:', err);
    }
  }

  async function handleCreateProject(e: React.FormEvent) {
    e.preventDefault();
    try {
      const { data } = await api.post('/projects', newProject);
      setProjects([...projects, data]);
      setSelectedProjectId(data.id);
      setShowProjectModal(false);
      setNewProject({ name: '', description: '', status: 'active' });
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error creating project');
    }
  }

  async function handleCreateTask(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedProjectId) return;
    try {
      const { data } = await api.post('/projects/tasks', {
        ...newTask,
        project_id: selectedProjectId,
      });
      setTasks([...tasks, data]);
      setShowTaskModal(false);
      setNewTask({ title: '', priority: 'medium', status: 'todo' });
    } catch (err: any) {
      alert(err.response?.data?.message || 'Error creating task');
    }
  }

  async function updateTaskStatus(taskId: string, nextStatus: string) {
    try {
      const { data } = await api.patch(`/projects/tasks/${taskId}`, { status: nextStatus });
      setTasks(tasks.map((t) => (t.id === taskId ? data : t)));
    } catch (err) {
      console.error('Failed to update task status:', err);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Project Management & Board</h1>
          <p className="page-subtitle">Agile sprints, backlogs, and task delivery pipelines</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowProjectModal(true)}>
            <Plus size={15} />
            New Project
          </button>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => setShowTaskModal(true)}
            disabled={!selectedProjectId}
          >
            <Plus size={15} />
            Add Task
          </button>
        </div>
      </div>

      {/* Project Selector Tabs */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-muted)' }}>Project:</span>
        {projects.length === 0 && !loading ? (
          <span style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>
            No projects yet. Click "New Project" to create one.
          </span>
        ) : (
          <select
            className="form-select"
            style={{ width: 260 }}
            value={selectedProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Kanban Columns */}
      <div className="kanban-board">
        {COLUMNS.map((col) => {
          const colTasks = tasks.filter((t) => t.status === col.key);
          return (
            <div key={col.key} className="kanban-col">
              <div className="kanban-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: col.color,
                      display: 'inline-block',
                    }}
                  />
                  <span>{col.label}</span>
                </div>
                <span className="badge badge-neutral" style={{ fontSize: 11 }}>
                  {colTasks.length}
                </span>
              </div>

              <div style={{ flex: 1, minHeight: 200 }}>
                {colTasks.length === 0 ? (
                  <div
                    style={{
                      border: '1px dashed var(--color-border)',
                      borderRadius: 'var(--radius-sm)',
                      padding: 16,
                      textAlign: 'center',
                      color: 'var(--color-text-subtle)',
                      fontSize: 12,
                    }}
                  >
                    No tasks
                  </div>
                ) : (
                  colTasks.map((t) => (
                    <div key={t.id} className="kanban-card">
                      <div style={{ fontSize: 13.5, fontWeight: 600, marginBottom: 8 }}>{t.title}</div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span className={`badge ${PRIORITY_BADGES[t.priority] || 'badge-neutral'}`} style={{ fontSize: 10 }}>
                          {t.priority.toUpperCase()}
                        </span>
                        <select
                          className="form-select"
                          style={{ width: 'auto', padding: '2px 6px', fontSize: 11, height: 26 }}
                          value={t.status}
                          onChange={(e) => updateTaskStatus(t.id, e.target.value)}
                        >
                          <option value="todo">To Do</option>
                          <option value="in_progress">In Progress</option>
                          <option value="in_review">In Review</option>
                          <option value="done">Done</option>
                        </select>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* New Project Modal */}
      {showProjectModal && (
        <div className="modal-backdrop" onClick={() => setShowProjectModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Create New Project</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowProjectModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreateProject}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Project Name</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. Next-Gen Mobile App"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Description (Optional)</label>
                  <textarea
                    className="form-textarea"
                    placeholder="Project vision and primary deliverables"
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowProjectModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New Task Modal */}
      {showTaskModal && (
        <div className="modal-backdrop" onClick={() => setShowTaskModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Add Task</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowTaskModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreateTask}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Task Title</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. Design Stripe Checkout webhook"
                    value={newTask.title}
                    onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Priority</label>
                  <select
                    className="form-select"
                    value={newTask.priority}
                    onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Status</label>
                  <select
                    className="form-select"
                    value={newTask.status}
                    onChange={(e) => setNewTask({ ...newTask, status: e.target.value })}
                  >
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="in_review">In Review</option>
                    <option value="done">Done</option>
                  </select>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowTaskModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Add Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
