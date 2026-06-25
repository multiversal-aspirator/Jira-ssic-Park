import AgentCard from './AgentCard';

export default function AgentGrid({ agents }) {
  const working = agents.filter((a) => a.status !== 'idle' && a.status !== 'completed').length;
  const done = agents.filter((a) => a.status === 'completed').length;

  return (
    <section className="agent-section">
      <div className="agent-section__head">
        <div>
          <h2 className="section-title">The Pack</h2>
          <p className="section-sub">5 specialist agents hunting your project signals in parallel</p>
        </div>
        <div className="agent-section__stat">
          <span className="stat-pill"><b>{working}</b> working</span>
          <span className="stat-pill stat-pill--done"><b>{done}</b> done</span>
        </div>
      </div>
      <div className="agent-grid">
        {agents.map((a) => (
          <AgentCard key={a.id} agent={a} />
        ))}
      </div>
    </section>
  );
}
