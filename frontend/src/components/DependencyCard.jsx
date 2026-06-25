import DinoIcon from './DinoIcon';
import { Kpi, Chip } from './Visuals';

export default function DependencyCard({ data }) {
  if (!data) return null;

  const deps = data.dependencies || [];
  const blocking = deps.filter((d) => d.is_blocking).length;

  return (
    <div className="card">
      <div className="card-head">
        <span className="card-head__dino"><DinoIcon species="raptor" accent="#1976d2" /></span>
        <h3>Dependency Agent</h3>
        {blocking > 0 && <Chip tone="danger">{blocking} blocking</Chip>}
      </div>

      <div className="kpi-row" style={{ marginBottom: '1rem' }}>
        <Kpi value={deps.length} label="Links" color="#38bdf8" />
        <Kpi value={blocking} label="Blocking" color={blocking ? '#e5564b' : '#9cc2ab'} />
        <Kpi value={data.conflicts?.length || 0} label="Conflicts" color={data.conflicts?.length ? '#f59e0b' : '#9cc2ab'} />
      </div>

      {deps.length > 0 && (
        <div>
          {deps.slice(0, 6).map((dep, i) => (
            <div key={i} className="dep-row">
              <span className="dep-node">{dep.source_issue}</span>
              <span className={`dep-arrow ${dep.is_blocking ? 'blocking' : ''}`}>
                {dep.is_blocking ? '⛔' : '→'}
              </span>
              <span className="dep-node">{dep.target_issue}</span>
              <Chip tone={dep.is_blocking ? 'danger' : 'neutral'}>{dep.dependency_type}</Chip>
            </div>
          ))}
        </div>
      )}

      {data.critical_path?.length > 0 && (
        <>
          <h4 style={{ marginTop: '0.9rem' }}>Critical Path</h4>
          <div className="dep-row" style={{ flexWrap: 'wrap', borderBottom: 'none' }}>
            {data.critical_path.map((node, i) => (
              <span key={i} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                <span className="dep-node">{node}</span>
                {i < data.critical_path.length - 1 && <span className="dep-arrow">→</span>}
              </span>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
