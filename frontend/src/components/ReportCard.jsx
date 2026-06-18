export default function ReportCard({ data }) {
  if (!data) return null;

  return (
    <div className="card" style={{ gridColumn: '1 / -1' }}>
      <h3>Stakeholder Report</h3>
      <p style={{ whiteSpace: 'pre-wrap', marginBottom: '1rem' }}>{data.executive_summary}</p>

      {data.key_metrics && Object.keys(data.key_metrics).length > 0 && (
        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
          {Object.entries(data.key_metrics).map(([key, val]) => (
            <div key={key} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#38bdf8' }}>{val}</div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{key}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
        <div>
          <h4 style={{ color: '#22c55e', marginBottom: '0.3rem' }}>Highlights</h4>
          <ul>{data.highlights?.map((h, i) => <li key={i}>{h}</li>)}</ul>
        </div>
        <div>
          <h4 style={{ color: '#f59e0b', marginBottom: '0.3rem' }}>Concerns</h4>
          <ul>{data.concerns?.map((c, i) => <li key={i}>{c}</li>)}</ul>
        </div>
        <div>
          <h4 style={{ color: '#38bdf8', marginBottom: '0.3rem' }}>Next Steps</h4>
          <ul>{data.next_steps?.map((n, i) => <li key={i}>{n}</li>)}</ul>
        </div>
      </div>
    </div>
  );
}
