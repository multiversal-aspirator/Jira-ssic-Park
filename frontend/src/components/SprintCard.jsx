export default function SprintCard({ data }) {
  if (!data) return null;

  const statusColor = {
    on_track: '#22c55e',
    at_risk: '#f59e0b',
    off_track: '#ef4444',
  };

  return (
    <div className="card">
      <h3>Sprint Analysis</h3>
      <p><strong>{data.sprint_name}</strong></p>
      <p style={{ color: statusColor[data.status] || '#94a3b8', fontWeight: 600 }}>
        {data.status?.replace('_', ' ').toUpperCase()}
      </p>
      <ul>
        <li>Total Issues: {data.total_issues}</li>
        <li>Completed: {data.completed}</li>
        <li>In Progress: {data.in_progress}</li>
        <li>Blocked: {data.blocked}</li>
        <li>Completion: {data.completion_percentage?.toFixed(1)}%</li>
        <li>Velocity: {data.velocity}</li>
      </ul>
      <p style={{ marginTop: '0.8rem', fontSize: '0.9rem', color: '#94a3b8' }}>{data.summary}</p>
    </div>
  );
}
