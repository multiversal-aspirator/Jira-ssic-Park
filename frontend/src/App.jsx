import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import HealthScore from './components/HealthScore';
import SprintCard from './components/SprintCard';
import RiskCard from './components/RiskCard';
import DependencyCard from './components/DependencyCard';
import ReportCard from './components/ReportCard';
import ForecastCard from './components/ForecastCard';
import TeamCard from './components/TeamCard';
import EventFeed from './components/EventFeed';
import SearchPanel from './components/SearchPanel';
import ProjectManager from './components/ProjectManager';
import AgentGrid from './components/AgentGrid';
import DinoIcon from './components/DinoIcon';
import { Kpi } from './components/Visuals';

const API_BASE = '/api';

// Updated dino-agent mapping per requirements:
// Sprint → Stegosaurus (steady), Risk → T-Rex (alert), Dependency → Raptor (fast),
// Forecasting → Ptero (bird's-eye), Reporting → Brachio (calm overview)
const AGENT_DEFS = [
  { id: 'sprint', name: 'Steggy', role: 'Sprint Agent', species: 'stego', accent: '#34c759', rate: 2.4 },
  { id: 'risk', name: 'Rexford', role: 'Risk Agent', species: 'trex', accent: '#f57c00', rate: 1.8 },
  { id: 'dependency', name: 'Velocity', role: 'Dependency Agent', species: 'raptor', accent: '#1976d2', rate: 2.2 },
  { id: 'forecast', name: 'Skyview', role: 'Forecasting Agent', species: 'ptero', accent: '#9c27b0', rate: 1.6 },
  { id: 'report', name: 'Alto', role: 'Reporting Agent', species: 'brachio', accent: '#558b2f', rate: 1.4 },
];

const idleAgents = () =>
  AGENT_DEFS.map((a) => ({ ...a, status: 'idle', progress: 0 }));

function statusForProgress(p) {
  if (p <= 0) return 'idle';
  if (p < 30) return 'fetching';
  if (p < 65) return 'thinking';
  if (p < 100) return 'analyzing';
  return 'completed';
}

export default function App() {
  const [projects, setProjects] = useState(() => {
    const saved = localStorage.getItem('pm_projects');
    return saved ? JSON.parse(saved) : [];
  });
  const [activeProject, setActiveProject] = useState(null);
  const [form, setForm] = useState({ project_key: '', sprint_id: '', github_repo: '', teams_channel: '' });
  const [report, setReport] = useState(null);
  const [teamData, setTeamData] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState('overview');

  // Agent activity simulation (visual only)
  const [agents, setAgents] = useState(idleAgents);
  const tickRef = useRef(null);

  useEffect(() => { localStorage.setItem('pm_projects', JSON.stringify(projects)); }, [projects]);
  useEffect(() => { if (activeProject) setForm(activeProject); }, [activeProject]);

  // Drive agent progress while loading
  useEffect(() => {
    if (loading) {
      setAgents(AGENT_DEFS.map((a) => ({ ...a, status: 'fetching', progress: 2 })));
      tickRef.current = setInterval(() => {
        setAgents((prev) =>
          prev.map((a) => {
            const next = Math.min(94, a.progress + a.rate + Math.random() * 2);
            return { ...a, progress: next, status: statusForProgress(next) };
          })
        );
      }, 220);
    } else {
      clearInterval(tickRef.current);
    }
    return () => clearInterval(tickRef.current);
  }, [loading]);

  useEffect(() => {
    if (report) setAgents(AGENT_DEFS.map((a) => ({ ...a, status: 'completed', progress: 100 })));
  }, [report]);

  const saveProject = (project) => {
    const existing = projects.find(p => p.project_key === project.project_key);
    if (existing) {
      setProjects(projects.map(p => p.project_key === project.project_key ? project : p));
    } else {
      setProjects([...projects, project]);
    }
    setActiveProject(project);
  };

  const removeProject = (projectKey) => {
    setProjects(projects.filter(p => p.project_key !== projectKey));
    if (activeProject?.project_key === projectKey) {
      setActiveProject(null);
      setForm({ project_key: '', sprint_id: '', github_repo: '', teams_channel: '' });
      setReport(null);
      setTeamData(null);
      setAgents(idleAgents());
    }
  };

  const handleChange = (e) => { setForm({ ...form, [e.target.name]: e.target.value }); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.project_key.trim()) return;

    setLoading(true);
    setError(null);
    setReport(null);
    setTeamData(null);

    try {
      const payload = {
        project_key: form.project_key,
        sprint_id: form.sprint_id || null,
        github_repo: form.github_repo || null,
        teams_channel: form.teams_channel || null,
        include_forecasting: true,
      };
      const { data } = await axios.post(`${API_BASE}/project/analyze`, payload);
      setReport(data);
      saveProject({ ...form });

      try {
        const teamRes = await axios.get(`${API_BASE}/team/overview`, { params: { project_key: form.project_key } });
        setTeamData(teamRes.data);
      } catch (e) { /* optional */ }

      try {
        const evtRes = await axios.get(`${API_BASE}/intelligence/events`, { params: { limit: 20 } });
        setEvents(evtRes.data.events || []);
      } catch (e) { /* optional */ }

    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      setAgents(idleAgents());
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    if (!form.project_key.trim()) return;
    setSyncing(true);
    setSyncStatus(null);
    try {
      const params = { project_key: form.project_key };
      if (form.github_repo) params.github_repo = form.github_repo;
      if (form.teams_channel) params.teams_channel = form.teams_channel;
      const { data } = await axios.post(`${API_BASE}/intelligence/sync`, null, { params });
      setSyncStatus(data);

      // Refresh team data after sync
      try {
        const teamRes = await axios.get(`${API_BASE}/team/overview`, { params: { project_key: form.project_key } });
        setTeamData(teamRes.data);
      } catch (e) { /* optional */ }

      // Refresh events
      try {
        const evtRes = await axios.get(`${API_BASE}/intelligence/events`, { params: { limit: 20 } });
        setEvents(evtRes.data.events || []);
      } catch (e) { /* optional */ }
    } catch (err) {
      setSyncStatus({ error: err.response?.data?.detail || err.message });
    } finally {
      setSyncing(false);
    }
  };

  const handleClearDB = async () => {
    if (!confirm(form.project_key
      ? `Clear all data for project "${form.project_key}"?`
      : 'Clear ALL data from the vector store?'
    )) return;

    try {
      const params = form.project_key ? { project_key: form.project_key } : {};
      await axios.delete(`${API_BASE}/intelligence/clear`, { params });
      setSyncStatus({ cleared: true, scope: form.project_key || 'all' });
      setTeamData(null);
      setEvents([]);
    } catch (err) {
      setSyncStatus({ error: err.response?.data?.detail || err.message });
    }
  };

  // Construct action links
  const jiraUrl = form.project_key ? `https://hackathon-gep.atlassian.net/jira/software/projects/${form.project_key}/boards` : null;
  const githubUrl = form.github_repo ? `https://github.com/${form.github_repo}` : null;
  const githubPRs = form.github_repo ? `https://github.com/${form.github_repo}/pulls` : null;

  const TABS = [
    { key: 'overview', label: 'Overview' },
    { key: 'agents', label: 'Agents' },
    { key: 'sprint', label: 'Sprint' },
    { key: 'risks', label: 'Risks' },
    { key: 'dependencies', label: 'Dependencies' },
    { key: 'team', label: 'Team' },
    { key: 'reports', label: 'Reports' },
    { key: 'search', label: 'Search' },
  ];

  return (
    <div className="app">
      {/* ── Park-Gate Header ── */}
      <header className="site-header">
        <span className="gate-vine" />
        <span className="header-dino"><DinoIcon species="trex" accent="#34c759" /></span>
        <div className="header-content">
          <h1>Jirassic Park</h1>
          <p>AI Project Manager Command Center</p>
        </div>
        <span className="header-spacer" />
        {/* Manager action buttons */}
        <div className="action-row" style={{ borderTop: 'none', paddingTop: 0, marginTop: 0 }}>
          {jiraUrl && (
            <a href={jiraUrl} target="_blank" rel="noopener noreferrer" className="btn-action">
              <span className="icon">📋</span> Open Jira Board
            </a>
          )}
          {githubUrl && (
            <a href={githubUrl} target="_blank" rel="noopener noreferrer" className="btn-action">
              <span className="icon">🐙</span> Open Repo
            </a>
          )}
          {githubPRs && (
            <a href={githubPRs} target="_blank" rel="noopener noreferrer" className="btn-action">
              <span className="icon">🔀</span> Pull Requests
            </a>
          )}
        </div>
        <span className="header-badge"><span className="live-dot" /> 5 AGENTS READY</span>
      </header>

      {/* ── Project Manager ── */}
      <ProjectManager
        projects={projects}
        activeProject={activeProject}
        onSelect={setActiveProject}
        onRemove={removeProject}
      />

      {/* ── Input Form ── */}
      <form className="panel form-section" onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="project_key">Jira Project Key *</label>
            <input id="project_key" name="project_key" value={form.project_key} onChange={handleChange} placeholder="e.g. PROJ" required />
          </div>
          <div className="form-group">
            <label htmlFor="sprint_id">Sprint ID</label>
            <input id="sprint_id" name="sprint_id" value={form.sprint_id} onChange={handleChange} placeholder="optional" />
          </div>
          <div className="form-group">
            <label htmlFor="github_repo">GitHub Repo</label>
            <input id="github_repo" name="github_repo" value={form.github_repo} onChange={handleChange} placeholder="owner/repo" />
          </div>
          <div className="form-group">
            <label htmlFor="teams_channel">Teams Channel</label>
            <input id="teams_channel" name="teams_channel" value={form.teams_channel} onChange={handleChange} placeholder="channel-id" />
          </div>
        </div>
        <div className="form-actions">
          <button className="btn-analyze" type="submit" disabled={loading}>
            {loading ? 'Releasing agents…' : '🦖 Release the Agents'}
          </button>
          <button type="button" className="btn-sync" onClick={handleSync} disabled={syncing || !form.project_key}>
            {syncing ? 'Syncing...' : 'Sync Data'}
          </button>
          <button type="button" className="btn-clear" onClick={handleClearDB}>
            Clear DB
          </button>
          {form.project_key && (
            <button type="button" className="btn-save" onClick={() => saveProject({ ...form })}>
              Save Project
            </button>
          )}
        </div>
        {syncStatus && (
          <div className={`sync-status ${syncStatus.error ? 'error' : ''}`}>
            {syncStatus.error
              ? `Sync failed: ${syncStatus.error}`
              : syncStatus.cleared
                ? `Cleared: ${syncStatus.scope === 'all' ? 'all data' : `project "${syncStatus.scope}"`}`
                : `Synced: ${syncStatus.ingested?.jira || 0} Jira, ${syncStatus.ingested?.github || 0} GitHub, ${syncStatus.ingested?.teams || 0} Teams`
            }
          </div>
        )}
      </form>

      {error && <div className="error">{error}</div>}

      {/* Loading hint */}
      {loading && (
        <div className="loading-hint">
          <p>The pack is on the hunt — 5 agents analyzing in parallel…</p>
          <div className="footprints"><span>🦶</span><span>🦶</span><span>🦶</span><span>🦶</span><span>🦶</span></div>
        </div>
      )}

      {/* ── Multi-tab Navigation ── */}
      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={tab === t.key ? 'tab active' : 'tab'}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {/* ── TAB: Overview ── */}
      {tab === 'overview' && (
        <>
          <AgentGrid agents={agents} />
          {report && (
            <>
              <HealthScore score={report.health_score} evidence={report.evidence_summary} />
              <div className="summary-strip">
                {report.sprint_analysis && (
                  <Kpi value={`${Math.round(report.sprint_analysis.completion_percentage || 0)}%`} label="Sprint Done" color="#2e7d32" icon="🦕" />
                )}
                {report.risk_analysis && (
                  <Kpi value={report.risk_analysis.risks?.length || 0} label="Active Risks" color="#e65100" icon="⚠️" />
                )}
                {report.dependency_analysis && (
                  <Kpi value={report.dependency_analysis.dependencies?.length || 0} label="Dependencies" color="#1565c0" icon="🔗" />
                )}
                {report.delivery_forecast && (
                  <Kpi value={`${Math.round((report.delivery_forecast.confidence_score || 0) * 100)}%`} label="Forecast" color="#7b1fa2" icon="🔭" />
                )}
              </div>
            </>
          )}
        </>
      )}

      {/* ── TAB: Agents ── */}
      {tab === 'agents' && <AgentGrid agents={agents} />}

      {/* ── TAB: Sprint ── */}
      {tab === 'sprint' && (
        report?.sprint_analysis
          ? <SprintCard data={report.sprint_analysis} jiraUrl={jiraUrl} />
          : <div className="card"><p style={{ color: '#5a7d62' }}>Run an analysis to see sprint data.</p></div>
      )}

      {/* ── TAB: Risks ── */}
      {tab === 'risks' && (
        report?.risk_analysis
          ? <RiskCard data={report.risk_analysis} />
          : <div className="card"><p style={{ color: '#5a7d62' }}>Run an analysis to see risk data.</p></div>
      )}

      {/* ── TAB: Dependencies ── */}
      {tab === 'dependencies' && (
        report?.dependency_analysis
          ? <DependencyCard data={report.dependency_analysis} />
          : <div className="card"><p style={{ color: '#5a7d62' }}>Run an analysis to see dependencies.</p></div>
      )}

      {/* ── TAB: Team ── */}
      {tab === 'team' && <TeamCard data={teamData} projectKey={form.project_key} />}

      {/* ── TAB: Reports ── */}
      {tab === 'reports' && (
        <>
          {report?.delivery_forecast && <ForecastCard data={report.delivery_forecast} />}
          {report?.stakeholder_report && <ReportCard data={report.stakeholder_report} />}
          {!report && <div className="card"><p style={{ color: '#5a7d62' }}>Run an analysis to generate reports.</p></div>}
          {report && <EventFeed events={events} />}
        </>
      )}

      {/* ── TAB: Search ── */}
      {tab === 'search' && <SearchPanel projectKey={form.project_key} />}
    </div>
  );
}
