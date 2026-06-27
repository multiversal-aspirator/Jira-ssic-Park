import AgentCard from './AgentCard';

const FANOUT_AGENT_IDS = ['sprint', 'risk', 'dependency'];
const MERGE_AGENT_IDS = ['forecast', 'report'];

export default function AgentGrid({ agents }) {
  const working = agents.filter((a) => a.status !== 'idle' && a.status !== 'completed').length;
  const done = agents.filter((a) => a.status === 'completed').length;

  const fanoutAgents = FANOUT_AGENT_IDS
    .map((id) => agents.find((agent) => agent.id === id))
    .filter(Boolean);

  const mergeAgents = MERGE_AGENT_IDS
    .map((id) => agents.find((agent) => agent.id === id))
    .filter(Boolean);

  return (
    <section className="agent-section">
      <div className="agent-section__head">
        <div>
          <h2 className="section-title">Agent Workflow</h2>
          <p className="section-sub">
            Three agents fan out in parallel, then forecasting and reporting merge the final intelligence.
          </p>
        </div>

        <div className="agent-section__stat">
          <span className="stat-pill"><b>{working}</b> working</span>
          <span className="stat-pill stat-pill--done"><b>{done}</b> done</span>
        </div>
      </div>

      <div className="agent-workflow">
        <div className="workflow-stage-label">Parallel fan-out</div>

        <div className="agent-grid agent-grid--fanout">
          {fanoutAgents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>

        <div className="workflow-merge-line">
          <span />
          <strong>Merge intelligence</strong>
          <span />
        </div>

        <div className="workflow-stage-label">Forecast & report</div>

        <div className="agent-grid agent-grid--merge">
          {mergeAgents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      </div>
    </section>
  );
}