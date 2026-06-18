export default function HealthScore({ score, evidence }) {
  const colorClass = score >= 70 ? 'score-good' : score >= 40 ? 'score-warn' : 'score-bad';
  const label = score >= 70 ? 'Healthy' : score >= 40 ? 'At Risk' : 'Critical';

  return (
    <div className="health-score">
      <div className={`score-value ${colorClass}`}>{Math.round(score)}</div>
      <p style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>{label}</p>
      {evidence && evidence.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0, color: '#94a3b8', fontSize: '0.9rem' }}>
          {evidence.map((e, i) => (
            <li key={i}>{e}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
