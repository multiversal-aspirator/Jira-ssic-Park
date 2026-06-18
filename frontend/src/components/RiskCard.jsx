export default function RiskCard({ data }) {
  if (!data) return null;

  return (
    <div className="card">
      <h3>
        Risk Analysis
        <span className={`badge badge-${data.overall_risk_level}`}>
          {data.overall_risk_level?.toUpperCase()}
        </span>
      </h3>
      {data.risks?.length > 0 ? (
        <ul>
          {data.risks.map((risk, i) => (
            <li key={i} style={{ padding: '0.5rem 0' }}>
              <strong>{risk.title}</strong>
              <span className={`badge badge-${risk.severity}`}>{risk.severity}</span>
              <br />
              <small style={{ color: '#94a3b8' }}>
                Evidence: {risk.evidence}<br />
                Impact: {risk.impact}<br />
                Action: {risk.recommendation}
              </small>
            </li>
          ))}
        </ul>
      ) : (
        <p style={{ color: '#22c55e' }}>No risks detected</p>
      )}
      <p style={{ marginTop: '0.8rem', fontSize: '0.9rem', color: '#94a3b8' }}>{data.summary}</p>
    </div>
  );
}
