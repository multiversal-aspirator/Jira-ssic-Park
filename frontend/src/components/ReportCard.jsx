import DinoIcon from './DinoIcon';
import { Kpi } from './Visuals';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const formatMetricLabel = (key) =>
  key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (ch) => ch.toUpperCase());

const parseMetricValue = (value) => {
  if (typeof value === 'number') return value;
  if (typeof value !== 'string') return null;

  if (/\d+\s*\/\s*\d+/.test(value)) {
    const [done, total] = value.split('/').map((v) => Number(v.trim()));
    if (total > 0) return Math.round((done / total) * 100);
  }

  const match = value.match(/-?\d+(\.\d+)?/);
  return match ? Number(match[0]) : null;
};

export default function ReportCard({ data }) {
  if (!data) return null;

  const metricEntries = data.key_metrics && Object.keys(data.key_metrics).length > 0
    ? Object.entries(data.key_metrics)
    : [];

  const chartData = metricEntries
    .map(([key, raw]) => ({
      key,
      label: formatMetricLabel(key),
      value: parseMetricValue(raw),
      raw,
    }))
    .filter((entry) => typeof entry.value === 'number' && Number.isFinite(entry.value))
    .slice(0, 8);

  const barPalette = ['#34d27b', '#2f9fda', '#e0a52a', '#f57c00', '#7b61ff', '#558b2f', '#d36b4d', '#3da5a5'];

  return (
    <div className="card report-card">
      <div className="card-head">
        <span className="card-head__dino"><DinoIcon species="brachio" accent="#558b2f" /></span>
        <h3>Reporting Agent</h3>
      </div>

      {metricEntries.length > 0 && (
        <div className="kpi-row" style={{ marginBottom: '1rem' }}>
          {metricEntries.map(([key, val]) => (
            <Kpi key={key} value={val} label={formatMetricLabel(key)} color="#34d27b" />
          ))}
        </div>
      )}

      {chartData.length > 0 && (
        <div className="report-metrics-chart">
          <h4 style={{ marginBottom: '0.35rem' }}>Metric Snapshot</h4>
          <ResponsiveContainer width="100%" height={230}>
            <BarChart data={chartData} margin={{ top: 8, right: 12, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(34, 139, 59, 0.15)" />
              <XAxis
                dataKey="label"
                tick={{ fill: '#5a7d62', fontSize: 10 }}
                interval={0}
                angle={-22}
                textAnchor="end"
                height={62}
              />
              <YAxis tick={{ fill: '#5a7d62', fontSize: 11 }} />
              <Tooltip formatter={(value, _name, item) => [item?.payload?.raw ?? value, item?.payload?.label || 'value']} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {chartData.map((entry, idx) => (
                  <Cell key={entry.key} fill={barPalette[idx % barPalette.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="report-cols">
        <div>
          <h4 style={{ color: '#34d27b' }}>Highlights</h4>
          <ul className="report-list">{data.highlights?.map((h, i) => <li key={i}>{h}</li>)}</ul>
        </div>
        <div>
          <h4 style={{ color: '#e0a52a' }}>Concerns</h4>
          <ul className="report-list">{data.concerns?.map((c, i) => <li key={i}>{c}</li>)}</ul>
        </div>
        <div>
          <h4 style={{ color: '#38bdf8' }}>Recommendations</h4>
          <ul className="report-list">{data.recommendations?.map((r, i) => <li key={i}>{r}</li>)}</ul>
        </div>
      </div>
    </div>
  );
}
