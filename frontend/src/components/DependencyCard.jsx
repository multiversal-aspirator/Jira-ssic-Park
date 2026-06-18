export default function DependencyCard({ data }) {
  if (!data) return null;

  return (
    <div className="card">
      <h3>Dependency Tracking</h3>
      {data.dependencies?.length > 0 && (
        <>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.5rem' }}>
            {data.dependencies.length} dependencies found
          </p>
          <ul>
            {data.dependencies.map((dep, i) => (
              <li key={i}>
                {dep.source_issue} → {dep.target_issue}
                <span style={{ color: dep.is_blocking ? '#ef4444' : '#94a3b8', marginLeft: '0.5rem' }}>
                  ({dep.dependency_type}{dep.is_blocking ? ' ⚠ BLOCKING' : ''})
                </span>
              </li>
            ))}
          </ul>
        </>
      )}
      {data.conflicts?.length > 0 && (
        <>
          <h4 style={{ color: '#ef4444', marginTop: '0.8rem' }}>Conflicts</h4>
          <ul>
            {data.conflicts.map((c, i) => (
              <li key={i} style={{ color: '#fca5a5' }}>{c}</li>
            ))}
          </ul>
        </>
      )}
      {data.critical_path?.length > 0 && (
        <>
          <h4 style={{ color: '#f59e0b', marginTop: '0.8rem' }}>Critical Path</h4>
          <p style={{ fontSize: '0.9rem' }}>{data.critical_path.join(' → ')}</p>
        </>
      )}
      <p style={{ marginTop: '0.8rem', fontSize: '0.9rem', color: '#94a3b8' }}>{data.summary}</p>
    </div>
  );
}
