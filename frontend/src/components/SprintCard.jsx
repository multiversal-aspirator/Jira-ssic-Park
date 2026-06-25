import DinoIcon from './DinoIcon';
import { Donut, Kpi, Chip } from './Visuals';

export default function SprintCard({ data, jiraUrl }) {
  if (!data) return null;

  const statusMeta = {
    on_track: { color: '#34d27b', tone: 'good' },
    at_risk: { color: '#e0a52a', tone: 'amber' },
    off_track: { color: '#e5564b', tone: 'danger' },
  };
  const meta = statusMeta[data.status] || { color: '#9cc2ab', tone: 'neutral' };

  const completed = data.completed || 0;
  const inProgress = data.in_progress || 0;
  const blocked = data.blocked || 0;
  const total = data.total_issues || 0;
  const todo = Math.max(0, total - completed - inProgress - blocked);

  const segments = [
    { value: completed, color: '#2e7d32' },
    { value: inProgress, color: '#1976d2' },
    { value: blocked, color: '#d32f2f' },
    { value: todo, color: '#e0e0e0' },
  ];

  return (
    <div className="card">
      <div className="card-head">
        <span className="card-head__dino"><DinoIcon species="stego" accent="#34c759" /></span>
        <h3>Sprint Agent</h3>
        <Chip tone={meta.tone}>{data.status?.replace('_', ' ').toUpperCase()}</Chip>
      </div>

      <div className="card-visual">
        <Donut
          segments={segments}
          size={130}
          stroke={16}
          centerLabel={`${Math.round(data.completion_percentage || 0)}%`}
          centerSub="done"
        />
        <div className="card-visual__meta">
          <div className="stat-line"><span>Sprint</span><span>{data.sprint_name || '—'}</span></div>
          <div className="stat-line"><span>Velocity</span><span>{data.velocity ?? '—'}</span></div>
          <div className="legend">
            <span className="legend-item"><span className="legend-dot" style={{ background: '#2e7d32' }} />Done {completed}</span>
            <span className="legend-item"><span className="legend-dot" style={{ background: '#1976d2' }} />Active {inProgress}</span>
            <span className="legend-item"><span className="legend-dot" style={{ background: '#d32f2f' }} />Blocked {blocked}</span>
            <span className="legend-item"><span className="legend-dot" style={{ background: '#e0e0e0' }} />To do {todo}</span>
          </div>
        </div>
      </div>

      <div className="kpi-row">
        <Kpi value={total} label="Issues" />
        <Kpi value={completed} label="Completed" color="#2e7d32" />
        <Kpi value={blocked} label="Blocked" color={blocked ? '#d32f2f' : '#8fa898'} />
      </div>

      {jiraUrl && (
        <div className="action-row">
          <a href={jiraUrl} target="_blank" rel="noopener noreferrer" className="btn-action">
            <span className="icon">📋</span> Open Jira Board
          </a>
        </div>
      )}
    </div>
  );
}
