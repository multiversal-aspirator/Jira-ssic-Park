import DinoIcon from './DinoIcon';
import { Chip, toneForRisk } from './Visuals';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const SEV_COLOR = { critical: '#e5564b', high: '#f59e0b', medium: '#e0a52a', low: '#34d27b' };

export default function RiskCard({ data }) {
  if (!data) return null;

  const risks = data.risks || [];
  const counts = risks.reduce((acc, r) => {
    acc[r.severity] = (acc[r.severity] || 0) + 1;
    return acc;
  }, {});

  const severityOrder = ['critical', 'high', 'medium', 'low'];
  const severityData = severityOrder.map((severity) => ({
    severity,
    count: counts[severity] || 0,
    color: SEV_COLOR[severity],
  }));

  const impactSignals = risks.map((risk, index) => {
    const impactText = `${risk.impact || ''} ${risk.recommendation || ''}`.toLowerCase();
    const severityWeight = { low: 1, medium: 2, high: 3, critical: 4 }[risk.severity] || 1;
    const magnitude = Math.min(100, 20 + severityWeight * 16 + Math.min(32, impactText.length / 12));

    return {
      id: index + 1,
      title: risk.title,
      severity: risk.severity,
      magnitude: Math.round(magnitude),
    };
  });

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

      {risks.length > 0 && (
        <div className="risk-viz-grid">
          <div className="risk-viz-card">
            <h4>Severity Distribution</h4>
            <div className="risk-pie-wrap">
              <ResponsiveContainer width="100%" height={210}>
                <PieChart>
                  <Pie
                    data={severityData}
                    dataKey="count"
                    nameKey="severity"
                    innerRadius={48}
                    outerRadius={78}
                    paddingAngle={2}
                  >
                    {severityData.map((entry) => (
                      <Cell key={entry.severity} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value, name) => [value, name]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="risk-viz-card">
            <h4>Risk Magnitude Index</h4>
            <ResponsiveContainer width="100%" height={210}>
              <BarChart data={impactSignals} margin={{ top: 8, right: 12, left: -18, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(34, 139, 59, 0.15)" />
                <XAxis dataKey="id" tick={{ fill: '#5a7d62', fontSize: 11 }} />
                <YAxis tick={{ fill: '#5a7d62', fontSize: 11 }} />
                <Tooltip
                  formatter={(value, key, item) => [value, 'magnitude']}
                  labelFormatter={(label) => `Risk #${label}`}
                />
                <Bar dataKey="magnitude" radius={[6, 6, 0, 0]}>
                  {impactSignals.map((entry) => (
                    <Cell key={entry.id} fill={SEV_COLOR[entry.severity] || '#5a7d62'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

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
