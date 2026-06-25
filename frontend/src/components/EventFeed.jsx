import DinoIcon from './DinoIcon';

export default function EventFeed({ events }) {
  if (!events || events.length === 0) {
    return (
      <div className="card">
        <div className="card-head">
          <span className="card-head__dino"><DinoIcon species="stego" accent="#34c759" /></span>
          <h3>Event Feed</h3>
        </div>
        <p style={{ color: '#5a7d62' }}>No events ingested yet. Configure webhooks or run a manual sync.</p>
      </div>
    );
  }

  const eventIcon = {
    github_push: '🔀',
    github_pr: '📥',
    github_issue: '🐛',
    jira_update: '📋',
    teams_message: '💬',
  };

  return (
    <div className="card event-feed">
      <div className="card-head">
        <span className="card-head__dino"><DinoIcon species="stego" accent="#34c759" /></span>
        <h3>Live Tracks ({events.length})</h3>
      </div>
      <div className="event-list">
        {events.map((evt, i) => (
          <div key={i} className="event-item">
            <span className="event-icon">{eventIcon[evt.type] || '📌'}</span>
            <div className="event-content">
              <span className="event-type">{evt.type.replace('_', ' ')}</span>
              <span className="event-time">{new Date(evt.timestamp).toLocaleString()}</span>
            </div>
            <span className={`event-status ${evt.processed ? 'processed' : 'pending'}`}>
              {evt.processed ? '✓' : '⏳'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
