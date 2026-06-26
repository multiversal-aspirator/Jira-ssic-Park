import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export default function OverviewPulse({ report }) {
  if (!report) return null;

  const velocitySeries = (report.delivery_forecast?.historical_velocity || []).map((points, idx) => ({
    sprint: `S${idx + 1}`,
    points,
  }));

  const signalBars = [
    { label: 'Health', value: Math.round(report.health_score || 0) },
    { label: 'Sprint', value: Math.round(report.sprint_analysis?.completion_percentage || 0) },
    { label: 'Forecast', value: Math.round((report.delivery_forecast?.confidence_score || 0) * 100) },
    { label: 'Risk Load', value: Math.min(100, (report.risk_analysis?.risks?.length || 0) * 20) },
    { label: 'Dependency', value: Math.min(100, (report.dependency_analysis?.dependencies?.length || 0) * 12) },
  ];

  return (
    <section className="overview-pulse-grid">
      <div className="card overview-pulse-card">
        <h3>Delivery Momentum</h3>
        <p className="section-sub">Velocity trend across recent sprint windows</p>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={velocitySeries.length ? velocitySeries : [{ sprint: 'S1', points: signalBars[1].value }]} margin={{ top: 10, right: 12, left: -18, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(34, 139, 59, 0.15)" />
            <XAxis dataKey="sprint" tick={{ fill: '#5a7d62', fontSize: 11 }} />
            <YAxis tick={{ fill: '#5a7d62', fontSize: 11 }} />
            <Tooltip formatter={(value) => [value, 'story points']} />
            <Line type="monotone" dataKey="points" stroke="#2f9fda" strokeWidth={2.6} dot={{ r: 3 }} activeDot={{ r: 5 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card overview-pulse-card">
        <h3>Signal Strength Index</h3>
        <p className="section-sub">Cross-agent snapshot normalized to a 100-point scale</p>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={signalBars} margin={{ top: 10, right: 12, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(34, 139, 59, 0.15)" />
            <XAxis dataKey="label" tick={{ fill: '#5a7d62', fontSize: 11 }} />
            <YAxis tick={{ fill: '#5a7d62', fontSize: 11 }} />
            <Tooltip formatter={(value) => [value, 'index']} />
            <Bar dataKey="value" radius={[6, 6, 0, 0]} fill="#34d27b" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
