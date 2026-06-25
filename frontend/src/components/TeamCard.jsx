import StatusBar from './StatusBar';

export default function TeamCard({ data, projectKey }) {
  if (!data) {
    return (
      <div className="card">
        <h3>Team Overview</h3>
        <p style={{ color: '#94a3b8' }}>No team data available. Sync project data first.</p>
      </div>
    );
  }

  const workloadColor = {
    light: '#22c55e',
    normal: '#38bdf8',
    heavy: '#f59e0b',
    overloaded: '#ef4444',
  };

  return (
    <div className="team-section">
      <div className="card">
        <h3>Team Workload ({data.total_members} members)</h3>
        {data.members.map((m) => (
          <div key={m.name} className="team-member">
            <div className="member-header">
              <strong>{m.name}</strong>
              <span className={`badge badge-${m.workload}`}>{m.workload}</span>
            </div>
            <StatusBar
              progress={(m.completed_tasks / Math.max(m.assigned_tasks, 1)) * 100}
              label={`${m.completed_tasks}/${m.assigned_tasks} tasks`}
              color={workloadColor[m.workload] || '#38bdf8'}
            />
            <div className="member-stats">
              <span>PRs: {m.open_prs}</span>
              <span>Blocked: {m.blocked_items}</span>
            </div>
          </div>
        ))}
      </div>

      {data.bottlenecks.length > 0 && (
        <div className="card">
          <h3>Bottlenecks</h3>
          <ul>
            {data.bottlenecks.map((b, i) => <li key={i}>{b}</li>)}
          </ul>
        </div>
      )}

      {data.recommendations.length > 0 && (
        <div className="card">
          <h3>Recommendations</h3>
          <ul>
            {data.recommendations.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
