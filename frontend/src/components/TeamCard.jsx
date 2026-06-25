import DinoIcon from './DinoIcon';
import { MiniBar, Chip, Kpi } from './Visuals';

export default function TeamCard({ data, projectKey }) {
  if (!data) {
    return (
      <div className="card">
        <div className="card-head">
          <span className="card-head__dino"><DinoIcon species="brachio" accent="#558b2f" /></span>
          <h3>Team Overview</h3>
        </div>
        <p style={{ color: '#5a7d62' }}>No team data available. Sync project data first.</p>
      </div>
    );
  }

  const workloadMeta = {
    light: { color: '#34d27b', tone: 'good' },
    normal: { color: '#38bdf8', tone: 'info' },
    heavy: { color: '#f59e0b', tone: 'warn' },
    overloaded: { color: '#e5564b', tone: 'danger' },
  };

  return (
    <div className="team-section">
      <div className="card">
        <div className="card-head">
          <span className="card-head__dino"><DinoIcon species="brachio" accent="#558b2f" /></span>
          <h3>Team Workload</h3>
          <Chip tone="neutral">{data.total_members} members</Chip>
        </div>
        {data.members.map((m) => {
          const meta = workloadMeta[m.workload] || { color: '#38bdf8', tone: 'neutral' };
          const pct = (m.completed_tasks / Math.max(m.assigned_tasks, 1)) * 100;
          return (
            <div key={m.name} className="team-member">
              <div className="member-header">
                <strong>{m.name}</strong>
                <Chip tone={meta.tone}>{m.workload}</Chip>
              </div>
              <MiniBar value={pct} color={meta.color} height={8} />
              <div className="member-stats">
                <span>{m.completed_tasks}/{m.assigned_tasks} tasks</span>
                <span>PRs: {m.open_prs}</span>
                <span>Blocked: {m.blocked_items}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        {data.bottlenecks.length > 0 && (
          <div className="card">
            <h4 style={{ color: '#f59e0b' }}>Bottlenecks</h4>
            <ul>{data.bottlenecks.map((b, i) => <li key={i}>{b}</li>)}</ul>
          </div>
        )}
        {data.recommendations.length > 0 && (
          <div className="card">
            <h4 style={{ color: '#34d27b' }}>Recommendations</h4>
            <ul>{data.recommendations.map((r, i) => <li key={i}>{r}</li>)}</ul>
          </div>
        )}
      </div>
    </div>
  );
}
