import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import HealthScore from './components/HealthScore';
import SprintCard from './components/SprintCard';
import RiskCard from './components/RiskCard';
import DependencyCard from './components/DependencyCard';
import ReportCard from './components/ReportCard';
import ForecastCard from './components/ForecastCard';
import TeamCard from './components/TeamCard';
import SearchPanel from './components/SearchPanel';
import ProjectManager from './components/ProjectManager';
import AgentGrid from './components/AgentGrid';
import headerLogo from './components/Logo.png';
import { Kpi } from './components/Visuals';
import OverviewPulse from './components/OverviewPulse';
import TabSummaryStrip from './components/TabSummaryStrip';

const API_BASE = '/api';

const AGENT_DEFS = [
  { id: 'sprint', name: 'Steggy', role: 'Sprint Agent', species: 'stego', accent: '#34c759' },
  { id: 'risk', name: 'Rexford', role: 'Risk Agent', species: 'trex', accent: '#f57c00' },
  { id: 'dependency', name: 'Velocity', role: 'Dependency Agent', species: 'raptor', accent: '#1976d2' },
  { id: 'forecast', name: 'Skyview', role: 'Forecasting Agent', species: 'ptero', accent: '#9c27b0' },
  { id: 'report', name: 'Alto', role: 'Reporting Agent', species: 'brachio', accent: '#558b2f' },
];

const WORKFLOW_STAGES = {
  sprint: [
    { from: 0, to: 1200, start: 0, end: 10 },
    { from: 1200, to: 3400, start: 10, end: 24 },
    { from: 3400, to: 6200, start: 24, end: 39 },
    { from: 6200, to: 9000, start: 39, end: 52 },
  ],
  risk: [
    { from: 1800, to: 3300, start: 0, end: 8 },
    { from: 3300, to: 5800, start: 8, end: 21 },
    { from: 5800, to: 8800, start: 21, end: 36 },
    { from: 8800, to: 11500, start: 36, end: 45 },
  ],
  dependency: [
    { from: 3200, to: 5000, start: 0, end: 9 },
    { from: 5000, to: 7600, start: 9, end: 23 },
    { from: 7600, to: 10800, start: 23, end: 39 },
    { from: 10800, to: 13500, start: 39, end: 48 },
  ],
  forecast: [
    { from: 5600, to: 7600, start: 0, end: 7 },
    { from: 7600, to: 10600, start: 7, end: 18 },
    { from: 10600, to: 14000, start: 18, end: 31 },
    { from: 14000, to: 16800, start: 31, end: 38 },
  ],
  report: [
    { from: 7600, to: 10200, start: 0, end: 5 },
    { from: 10200, to: 13800, start: 5, end: 12 },
    { from: 13800, to: 17800, start: 12, end: 22 },
    { from: 17800, to: 21000, start: 22, end: 30 },
  ],
};

const emptyForm = {
  project_key: '',
  sprint_id: '',
  epic_key: '',
  github_repo: '',
  teams_channel: '',
};

const idleAgents = () =>
  AGENT_DEFS.map((a) => ({ ...a, status: 'idle', progress: 0 }));

function statusForProgress(p) {
  if (p <= 0) return 'idle';
  if (p < 18) return 'fetching';
  if (p < 38) return 'thinking';
  if (p < 100) return 'analyzing';
  return 'completed';
}

function getWorkflowProgress(agentId, elapsed) {
  const stages = WORKFLOW_STAGES[agentId] || [];

  if (!stages.length || elapsed < stages[0].from) {
    return 0;
  }

  for (const stage of stages) {
    if (elapsed >= stage.from && elapsed <= stage.to) {
      const ratio = (elapsed - stage.from) / (stage.to - stage.from);
      return stage.start + ratio * (stage.end - stage.start);
    }
  }

  return stages[stages.length - 1].end;
}

function epicDisplayValue(epic) {
  return `${epic.summary} (${epic.key})`;
}

export default function App() {
  const [projects, setProjects] = useState(() => {
    const saved = localStorage.getItem('pm_projects');
    return saved ? JSON.parse(saved) : [];
  });
  const [activeProject, setActiveProject] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [report, setReport] = useState(null);
  const [teamData, setTeamData] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState('overview');

  const [epics, setEpics] = useState([]);
  const [epicsLoading, setEpicsLoading] = useState(false);
  const [epicsError, setEpicsError] = useState(null);

  const [agents, setAgents] = useState(idleAgents);
  const tickRef = useRef(null);
  const completionTimersRef = useRef([]);

  useEffect(() => {
    localStorage.setItem('pm_projects', JSON.stringify(projects));
  }, [projects]);

  useEffect(() => {
    if (activeProject) setForm({ ...emptyForm, ...activeProject });
  }, [activeProject]);

  useEffect(() => {
    const projectKey = form.project_key.trim();

    setEpics([]);
    setEpicsError(null);

    if (!projectKey) return;

    const timer = setTimeout(async () => {
      setEpicsLoading(true);
      try {
        const { data } = await axios.get(`${API_BASE}/project/epics`, {
          params: { project_key: projectKey },
        });
        setEpics(data.epics || []);
      } catch (err) {
        setEpicsError(err.response?.data?.detail || err.message);
      } finally {
        setEpicsLoading(false);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [form.project_key]);

  useEffect(() => {
    if (!loading) {
      clearInterval(tickRef.current);
      return;
    }

    completionTimersRef.current.forEach(clearTimeout);
    completionTimersRef.current = [];

    const startedAt = Date.now();
    setAgents(idleAgents());

    tickRef.current = setInterval(() => {
      const elapsed = Date.now() - startedAt;

      setAgents((prev) =>
        prev.map((agent) => {
          const targetProgress = getWorkflowProgress(agent.id, elapsed);
          const currentProgress = agent.progress || 0;

          const nextProgress =
            targetProgress > currentProgress
              ? currentProgress + Math.min(targetProgress - currentProgress, 2.2)
              : currentProgress;

          return {
            ...agent,
            progress: nextProgress,
            status: statusForProgress(nextProgress),
          };
        })
      );
    }, 500);

    return () => clearInterval(tickRef.current);
  }, [loading]);

  useEffect(() => {
    if (!report) return;

    clearInterval(tickRef.current);
    completionTimersRef.current.forEach(clearTimeout);
    completionTimersRef.current = [];

    AGENT_DEFS.forEach((agentDef, index) => {
      const timer = setTimeout(() => {
        setAgents((prev) =>
          prev.map((agent) =>
            agent.id === agentDef.id
              ? { ...agent, status: 'completed', progress: 100 }
              : agent
          )
        );
      }, index * 250);

      completionTimersRef.current.push(timer);
    });

    return () => {
      completionTimersRef.current.forEach(clearTimeout);
      completionTimersRef.current = [];
    };
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
      setForm(emptyForm);
      setReport(null);
      setTeamData(null);
      setAgents(idleAgents());
    }
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const getSelectedEpicKey = () => {
    const value = (form.epic_key || '').trim();

    if (!value) return '';

    const matchedEpic = epics.find(
      (epic) => epicDisplayValue(epic) === value || epic.key === value
    );

    return matchedEpic ? matchedEpic.key : value;
  };

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
        epic_key: getSelectedEpicKey() || null,
        github_repo: form.github_repo || null,
        teams_channel: form.teams_channel || null,
        include_forecasting: true,
      };

      const { data } = await axios.post(`${API_BASE}/project/analyze`, payload);
      setReport(data);
      saveProject({ ...form });

      try {
        const teamRes = await axios.get(`${API_BASE}/team/overview`, {
          params: { project_key: form.project_key },
        });
        setTeamData(teamRes.data);
      } catch (e) { /* optional */ }

      try {
        const evtRes = await axios.get(`${API_BASE}/intelligence/events`, {
          params: { limit: 20 },
        });
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

      const { data } = await axios.post(`${API_BASE}/intelligence/sync`, null, { params, timeout: 300000 });
      setSyncStatus(data);

      try {
        const teamRes = await axios.get(`${API_BASE}/team/overview`, {
          params: { project_key: form.project_key },
        });
        setTeamData(teamRes.data);
      } catch (e) { /* optional */ }

      try {
        const evtRes = await axios.get(`${API_BASE}/intelligence/events`, {
          params: { limit: 20 },
        });
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

  const jiraUrl = form.project_key ? `https://hackathon-gep.atlassian.net/jira/software/projects/${form.project_key}/boards/1` : null;
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
      <header className="site-header">
        <span className="gate-vine" />
        <span className="header-dino">
          <img className="header-dino__logo" src={headerLogo} alt="Jira-ssic Park logo" />
        </span>
        <div className="header-content">
          <h1>Jira-ssic Park</h1>
          <p>AI Project Manager Command Center</p>
        </div>
        <span className="header-spacer" />
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

      <ProjectManager
        projects={projects}
        activeProject={activeProject}
        onSelect={setActiveProject}
        onRemove={removeProject}
      />

      <form className="panel form-section" onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="project_key">Jira Project Key *</label>
            <input
              id="project_key"
              name="project_key"
              value={form.project_key}
              onChange={handleChange}
              placeholder="e.g. SCRUM"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="sprint_id">Sprint ID</label>
            <input
              id="sprint_id"
              name="sprint_id"
              value={form.sprint_id}
              onChange={handleChange}
              placeholder="optional"
            />
          </div>

          <div className="form-group">
            <label htmlFor="epic_key">Epic</label>
            <input
              id="epic_key"
              name="epic_key"
              list="epic-options"
              value={form.epic_key}
              onChange={handleChange}
              placeholder={epicsLoading ? 'Loading epics...' : 'Type or choose epic'}
              disabled={!form.project_key.trim() || epicsLoading}
            />
            <datalist id="epic-options">
              {epics.map((epic) => (
                <option key={epic.key} value={epicDisplayValue(epic)} />
              ))}
            </datalist>
            {epicsError && (
              <small className="field-error">
                Could not load epics: {epicsError}
              </small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="github_repo">GitHub Repo</label>
            <input
              id="github_repo"
              name="github_repo"
              value={form.github_repo}
              onChange={handleChange}
              placeholder="owner/repo"
            />
          </div>

          <div className="form-group">
            <label htmlFor="teams_channel">Teams Channel</label>
            <input
              id="teams_channel"
              name="teams_channel"
              value={form.teams_channel}
              onChange={handleChange}
              placeholder="channel-id"
            />
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

      {loading && (
        <div className="loading-hint">
          <p>The pack is following the workflow — sprint signals first, then risks, dependencies, forecast, and final report…</p>
          <div className="footprints"><span>.</span><span>.</span><span>.</span><span>.</span><span>.</span><span>.</span><span>.</span></div>
        </div>
      )}

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

      <TabSummaryStrip tab={tab} report={report} teamData={teamData} />

      {tab === 'overview' && (
        <>
          <AgentGrid agents={agents} />
          {report && (
            <>
              <HealthScore score={report.health_score} evidence={report.evidence_summary} />
              <OverviewPulse report={report} />
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

      {tab === 'agents' && <AgentGrid agents={agents} />}

      {tab === 'sprint' && (
        report?.sprint_analysis
          ? <SprintCard data={report.sprint_analysis} jiraUrl={jiraUrl} />
          : <div className="card"><p style={{ color: '#5a7d62' }}>Run an analysis to see sprint data.</p></div>
      )}

      {tab === 'risks' && (
        report?.risk_analysis
          ? <RiskCard data={report.risk_analysis} />
          : <div className="card"><p style={{ color: '#5a7d62' }}>Run an analysis to see risk data.</p></div>
      )}

      {tab === 'dependencies' && (
        report?.dependency_analysis
          ? <DependencyCard data={report.dependency_analysis} />
          : <div className="card"><p style={{ color: '#5a7d62' }}>Run an analysis to see dependencies.</p></div>
      )}

      {tab === 'team' && <TeamCard data={teamData} projectKey={form.project_key} />}

      {tab === 'reports' && (
        <>
          {report?.delivery_forecast && <ForecastCard data={report.delivery_forecast} />}
          {report?.stakeholder_report && <ReportCard data={report.stakeholder_report} />}
          {!report && <div className="card"><p style={{ color: '#5a7d62' }}>Run an analysis to generate reports.</p></div>}
        </>
      )}

      {tab === 'search' && <SearchPanel projectKey={form.project_key} />}
    </div>
  );
}