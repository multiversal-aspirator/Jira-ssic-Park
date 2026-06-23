import { useState } from 'react';
import axios from 'axios';
import HealthScore from './components/HealthScore';
import SprintCard from './components/SprintCard';
import RiskCard from './components/RiskCard';
import DependencyCard from './components/DependencyCard';
import ReportCard from './components/ReportCard';
import ForecastCard from './components/ForecastCard';

const API_BASE = '/api/project';

export default function App() {
  const [form, setForm] = useState({
    project_key: '',
    sprint_id: '',
    github_repo: '',
    teams_channel: '',
  });
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.project_key.trim()) return;

    setLoading(true);
    setError(null);
    setReport(null);

    try {
      const payload = {
        project_key: form.project_key,
        sprint_id: form.sprint_id || null,
        github_repo: form.github_repo || null,
        teams_channel: form.teams_channel || null,
        include_forecasting: true,
      };
      const { data } = await axios.post(`${API_BASE}/analyze`, payload);
      setReport(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>AI Project Manager</h1>
        <p>Autonomous project health analysis for engineering teams</p>
      </header>

      <form className="form-section" onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="project_key">Jira Project Key *</label>
            <input
              id="project_key"
              name="project_key"
              value={form.project_key}
              onChange={handleChange}
              placeholder="e.g. PROJ"
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
        <button className="btn-analyze" type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Run Project Analysis'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {loading && (
        <div className="loading">
          <div className="spinner" />
          <p>Running 5 agents in parallel...</p>
        </div>
      )}

      {report && (
        <>
          <HealthScore score={report.health_score} evidence={report.evidence_summary} />
          <div className="report-grid">
            <SprintCard data={report.sprint_analysis} />
            <RiskCard data={report.risk_analysis} />
            <DependencyCard data={report.dependency_analysis} />
            <ReportCard data={report.stakeholder_report} />
            <ForecastCard data={report.delivery_forecast} />
          </div>
        </>
      )}
    </div>
  );
}
