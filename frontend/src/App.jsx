import { useState, useEffect } from 'react';
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
import StatusBar from './components/StatusBar';

const API_BASE = '/api';

export default function App() {
  // Saved projects from localStorage
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
  const [tab, setTab] = useState('analysis');

  // Persist projects to localStorage
  useEffect(() => {
    localStorage.setItem('pm_projects', JSON.stringify(projects));
  }, [projects]);

  // Load active project into form
  useEffect(() => {
    if (activeProject) {
      setForm(activeProject);
    }
  }, [activeProject]);

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
    }
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
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
        github_repo: form.github_repo || null,
        teams_channel: form.teams_channel || null,
        include_forecasting: true,
      };
      const { data } = await axios.post(`${API_BASE}/project/analyze`, payload);
      setReport(data);

      // Save project config on successful analysis
      saveProject({ ...form });

      // Fetch team data
      try {
        const teamRes = await axios.get(`${API_BASE}/team/overview`, { params: { project_key: form.project_key } });
        setTeamData(teamRes.data);
      } catch (e) { /* team data optional */ }

      // Fetch events
      try {
        const evtRes = await axios.get(`${API_BASE}/intelligence/events`, { params: { limit: 20 } });
        setEvents(evtRes.data.events || []);
      } catch (e) { /* events optional */ }

    } catch (err) {
      setError(err.response?.data?.detail || err.message);
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

  return (
    <div className="app">
      <header>
        <h1>AI Project Intelligence</h1>
        <p>Continuous project monitoring & report generation</p>
      </header>

      {/* Project Manager — saved projects */}
      <ProjectManager
        projects={projects}
        activeProject={activeProject}
        onSelect={setActiveProject}
        onRemove={removeProject}
      />

      {/* Input Form */}
      <form className="form-section" onSubmit={handleSubmit}>
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
            {loading ? 'Analyzing...' : 'Run Project Analysis'}
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
        <div className="loading">
          <div className="spinner" />
          <p>Running 5 agents in parallel...</p>
          <StatusBar progress={0} label="Initializing..." animated />
        </div>
      )}

      {report && (
        <>
          {/* Tab navigation */}
          <nav className="tabs">
            <button className={tab === 'analysis' ? 'tab active' : 'tab'} onClick={() => setTab('analysis')}>Analysis</button>
            <button className={tab === 'team' ? 'tab active' : 'tab'} onClick={() => setTab('team')}>Team</button>
            <button className={tab === 'events' ? 'tab active' : 'tab'} onClick={() => setTab('events')}>Events</button>
            <button className={tab === 'search' ? 'tab active' : 'tab'} onClick={() => setTab('search')}>Search</button>
          </nav>

          {tab === 'analysis' && (
            <>
              <HealthScore score={report.health_score} evidence={report.evidence_summary} />

              {/* Progress bars */}
              <div className="status-bars">
                {report.sprint_analysis && (
                  <StatusBar
                    progress={report.sprint_analysis.completion_percentage}
                    label={`Sprint: ${report.sprint_analysis.completion_percentage?.toFixed(0)}% complete`}
                    color={report.sprint_analysis.status === 'on_track' ? '#22c55e' : report.sprint_analysis.status === 'at_risk' ? '#f59e0b' : '#ef4444'}
                  />
                )}
                {report.delivery_forecast && (
                  <StatusBar
                    progress={report.delivery_forecast.confidence_score * 100}
                    label={`Forecast Confidence: ${(report.delivery_forecast.confidence_score * 100).toFixed(0)}%`}
                    color="#8b5cf6"
                  />
                )}
                <StatusBar
                  progress={report.health_score}
                  label={`Health Score: ${report.health_score?.toFixed(0)}/100`}
                  color={report.health_score >= 70 ? '#22c55e' : report.health_score >= 40 ? '#f59e0b' : '#ef4444'}
                />
              </div>

              <div className="report-grid">
                <SprintCard data={report.sprint_analysis} />
                <RiskCard data={report.risk_analysis} />
                <DependencyCard data={report.dependency_analysis} />
                <ReportCard data={report.stakeholder_report} />
                <ForecastCard data={report.delivery_forecast} />
              </div>
            </>
          )}

          {tab === 'team' && <TeamCard data={teamData} projectKey={form.project_key} />}
          {tab === 'events' && <EventFeed events={events} />}
          {tab === 'search' && <SearchPanel projectKey={form.project_key} />}
        </>
      )}
    </div>
  );
}
