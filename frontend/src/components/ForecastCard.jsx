export default function ForecastCard({ data }) {
  if (!data) return null;

  const likelihoodColor = {
    high: '#22c55e',
    medium: '#f59e0b',
    low: '#ef4444',
  };

  return (
    <div className="card">
      <h3>Delivery Forecast</h3>
      <div style={{ textAlign: 'center', margin: '1rem 0' }}>
        <div style={{
          fontSize: '2rem',
          fontWeight: 700,
          color: likelihoodColor[data.completion_likelihood] || '#94a3b8',
        }}>
          {Math.round(data.confidence_score * 100)}%
        </div>
        <p style={{ color: '#94a3b8' }}>Confidence</p>
      </div>
      <ul>
        <li>Likelihood: <strong>{data.completion_likelihood?.toUpperCase()}</strong></li>
        <li>Trend: {data.trend}</li>
        {data.predicted_completion_date && (
          <li>Predicted Completion: {data.predicted_completion_date}</li>
        )}
      </ul>
      {data.factors?.length > 0 && (
        <>
          <h4 style={{ marginTop: '0.8rem', fontSize: '0.9rem', color: '#94a3b8' }}>Factors</h4>
          <ul>
            {data.factors.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        </>
      )}
      <p style={{ marginTop: '0.8rem', fontSize: '0.9rem', color: '#94a3b8' }}>{data.summary}</p>
    </div>
  );
}
