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
  const inReview = data.in_review || 0;
  const total = data.total_issues || 0;
  const todo = Math.max(0, total - completed - inProgress - inReview);

  const segments = [
    { value: completed, color: '#2e7d32' },
    { value: inProgress, color: '#1976d2' },
    { value: inReview, color: '#d32f2f' },
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
          
        </div>
      </div>

      <div className="kpi-row">
        <div
          onClick={() => window.open("https://hackathon-gep.atlassian.net/jira/software/projects/SCRUM/boards/1", "_blank")}
          style={{ cursor: "pointer" }}
        >
          <Kpi value={total} label="Tickets" color="#f3a807" />
        </div>
        <div
          onClick={() => window.open("https://hackathon-gep.atlassian.net/jira/software/projects/SCRUM/boards/1?jql=status%20%3D%20Done", "_blank")}
          style={{ cursor: "pointer" }}
        >
        <Kpi value={completed} label="Completed" color="#2e7d32" />
        </div>
         <div
          onClick={() => window.open("https://hackathon-gep.atlassian.net/jira/software/projects/SCRUM/boards/1?jql=status%20%3D%20%22In%20Progress%22", "_blank")}
          style={{ cursor: "pointer" }}
        >
        <Kpi value={inProgress} label="In Progress" color="#df0a98" />
        </div>
        <div
          onClick={() => window.open("https://hackathon-gep.atlassian.net/jira/software/projects/SCRUM/boards/1?jql=status%20%3D%20%22In%20Review%22", "_blank")}
          style={{ cursor: "pointer" }}
        >
        <Kpi value={inReview} label="In Review" color="#2fb5d3" />
        </div>
        <div
          onClick={() => window.open("https://hackathon-gep.atlassian.net/jira/software/projects/SCRUM/boards/1?jql=status%20%3D%20%22To%20Do%22", "_blank")}
          style={{ cursor: "pointer" }}
        >
        <Kpi value={todo} label="To Do" color="#2b13a5" />
        </div>
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
