import DinoIcon from './DinoIcon';

const STATUS_META = {
  idle: { label: 'Idle', tone: 'neutral' },
  fetching: { label: 'Fetching', tone: 'info' },
  thinking: { label: 'Thinking', tone: 'amber' },
  analyzing: { label: 'Analyzing', tone: 'warn' },
  completed: { label: 'Completed', tone: 'good' },
};

// Agent-specific thought messages while active
const THOUGHTS = {
  sprint: ['Checking Jira sprint…', 'Counting story points…', 'Tracking velocity…'],
  risk: ['Scanning for blockers…', 'Assessing threat levels…', 'Finding vulnerabilities…'],
  dependency: ['Mapping issue links…', 'Scanning GitHub PRs…', 'Finding bottlenecks…'],
  forecast: ['Forecasting delivery…', 'Analyzing trends…', 'Computing confidence…'],
  report: ['Preparing manager report…', 'Summarizing highlights…', 'Compiling insights…'],
};

export default function AgentCard({ agent }) {
  const meta = STATUS_META[agent.status] || STATUS_META.idle;
  const active = agent.status !== 'idle' && agent.status !== 'completed';
  const done = agent.status === 'completed';

  // Pick thought based on progress phase
  const thoughts = THOUGHTS[agent.id] || ['Working…'];
  const thoughtIdx = Math.min(Math.floor((agent.progress || 0) / 35), thoughts.length - 1);
  const thought = thoughts[thoughtIdx];

  return (
    <div
      className={`agent-card ${active ? 'is-active' : ''} ${done ? 'is-done' : ''}`}
      style={{ '--accent': agent.accent }}
    >
      <div className="agent-card__glow" />

      <div className="agent-card__top">
        <div className={`agent-avatar ${active ? 'breathing' : ''}`}>
          <DinoIcon species={agent.species} accent={agent.accent} />
        </div>
        <div className="agent-id">
          <span className="agent-name">{agent.name}</span>
          <span className="agent-role">{agent.role}</span>
          <span className={`chip chip--${meta.tone} agent-status`}>
            <span className="status-dot" />
            {meta.label}
          </span>
        </div>
      </div>

      <div className={`thought-bubble ${active ? 'show' : ''}`}>
        <span className="thought-text">{thought}</span>
        <span className="thought-dots"><i /><i /><i /></span>
      </div>

      <div className="agent-progress">
        <div className="agent-progress__track">
          <div
            className={`agent-progress__fill ${active ? 'striped' : ''}`}
            style={{ width: `${Math.round(agent.progress || 0)}%` }}
          />
        </div>
        <span className="agent-progress__pct">{Math.round(agent.progress || 0)}%</span>
      </div>
    </div>
  );
}
