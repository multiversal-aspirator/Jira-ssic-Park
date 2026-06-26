import DinoIcon from './DinoIcon';
import CircularAgentLoader from './CircularAgentLoader';

const STATUS_META = {
  idle: { label: 'Idle', tone: 'neutral' },
  fetching: { label: 'Fetching', tone: 'info' },
  thinking: { label: 'Thinking', tone: 'amber' },
  analyzing: { label: 'Analyzing', tone: 'warn' },
  completed: { label: 'Completed', tone: 'good' },
};

// Agent-specific thought messages while active
const THOUGHTS = {
  sprint: [
    'Steggy is sprinting through Jira jungle trails...',
    'Crunching story points before they fossilize...',
    'Velocity tracks found. Herd momentum looks real.',
    'Burndown bones aligned. Sprint cadence is roaring.',
  ],
  risk: [
    'Rexford is sniffing out risk footprints...',
    'Triaging red flags before they hatch into chaos...',
    'Pattern hunt: blocker DNA detected in the wild.',
    'Threat map updated. No asteroid surprises today.',
  ],
  dependency: [
    'Velocity is untangling issue vines and PR roots...',
    'Dependency fossils linked. Finding the true choke point...',
    'Merge meteor shower predicted. Rerouting critical path...',
    'Graph stabilized. Bottlenecks are now on the radar.',
  ],
  forecast: [
    'Skyview is gliding over trend lines...',
    'Reading velocity weather before delivery landfall...',
    'Confidence currents computed. ETA skyline in sight.',
    'Forecast locked. Probability pterodactyl approves.',
  ],
  report: [
    'Alto is polishing executive signals into insight...',
    'Turning data footprints into product-ready story arcs...',
    'Key metrics assembled. Concern radar calibrated...',
    'Report roar loaded. Stakeholder briefing incoming.',
  ],
};

export default function AgentCard({ agent }) {
  const meta = STATUS_META[agent.status] || STATUS_META.idle;
  const active = agent.status !== 'idle' && agent.status !== 'completed';
  const done = agent.status === 'completed';

  // Pick thought based on progress phase
  const thoughts = THOUGHTS[agent.id] || ['Working…'];
  const thoughtIdx = Math.min(Math.floor((agent.progress || 0) / 25), thoughts.length - 1);
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

      <CircularAgentLoader
        progress={agent.progress || 0}
        status={agent.status}
        active={active}
      />
    </div>
  );
}
