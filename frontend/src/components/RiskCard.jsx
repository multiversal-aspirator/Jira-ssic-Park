import DinoIcon from './DinoIcon';
import { Chip, toneForRisk } from './Visuals';

const SEV_COLOR = { critical: '#e5564b', high: '#f59e0b', medium: '#e0a52a', low: '#34d27b' };

export default function RiskCard({ data }) {
  if (!data) return null;

  const risks = data.risks || [];
  const counts = risks.reduce((acc, r) => {
    acc[r.severity] = (acc[r.severity] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="card">
      <div className="card-head">
        <span className="card-head__dino"><DinoIcon species="trex" accent="#f57c00" /></span>
        <h3>Risk Agent</h3>
        <Chip tone={toneForRisk(data.overall_risk_level)}>{data.overall_risk_level?.toUpperCase()}</Chip>
      </div>

      <div className="legend" style={{ marginBottom: '0.8rem' }}>
        {['critical', 'high', 'medium', 'low'].map((sev) => (
          <span key={sev} className="legend-item">
            <span className="legend-dot" style={{ background: SEV_COLOR[sev] }} />
            {sev} {counts[sev] || 0}
          </span>
        ))}
      </div>

      {risks.length > 0 ? (
        <div>
          {risks.map((risk, i) => (
            <div key={i} className="risk-row">
              <span className="risk-sev-bar" style={{ background: SEV_COLOR[risk.severity] || '#3a5c47' }} />
              <div className="risk-row__body">
                <div className="risk-row__title">
                  <strong>{risk.title}</strong>
                  <Chip tone={toneForRisk(risk.severity)}>{risk.severity}</Chip>
                </div>
                <div className="risk-row__detail">{risk.recommendation || risk.impact}</div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p style={{ color: '#34d27b' }}>No risks detected — the herd is calm.</p>
      )}
    </div>
  );
}
