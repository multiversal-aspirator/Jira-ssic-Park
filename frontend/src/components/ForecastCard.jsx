import DinoIcon from './DinoIcon';
import { CircularGauge, Chip } from './Visuals';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export default function ForecastCard({ data }) {
  if (!data) return null;

  const likeMeta = {
    high: { color: '#34d27b', tone: 'good' },
    medium: { color: '#e0a52a', tone: 'amber' },
    low: { color: '#e5564b', tone: 'danger' },
  };
  const meta = likeMeta[data.completion_likelihood] || { color: '#9cc2ab', tone: 'neutral' };
  const pct = Math.round((data.confidence_score || 0) * 100);

  const trendIcon = { improving: '▲', stable: '▬', declining: '▼' }[data.trend] || '▬';
  const velocitySeries = (data.historical_velocity || []).map((points, idx) => ({
    sprint: `S${idx + 1}`,
    points,
  }));

  return (
    <div className="card">
      <div className="card-head">
        <span className="card-head__dino"><DinoIcon species="ptero" accent="#9c27b0" /></span>
        <h3>Forecasting Agent</h3>
        <Chip tone={meta.tone}>{data.completion_likelihood?.toUpperCase()}</Chip>
      </div>

      <div className="card-visual">
        <CircularGauge value={pct} size={120} stroke={11} sublabel="Confidence" color={meta.color} />
        <div className="card-visual__meta">
          <div className="stat-line"><span>Trend</span><span style={{ color: meta.color }}>{trendIcon} {data.trend}</span></div>
          {data.predicted_completion_date && (
            <div className="stat-line"><span>ETA</span><span>{data.predicted_completion_date}</span></div>
          )}
          <div className="stat-line"><span>Likelihood</span><span>{data.completion_likelihood}</span></div>
        </div>
      </div>

      {data.factors?.length > 0 && (
        <div className="legend forecast-factors">
          {data.factors.slice(0, 6).map((f, i) => (
            <Chip key={i} tone="neutral">{f}</Chip>
          ))}
        </div>
      )}

      {velocitySeries.length > 0 && (
        <div className="forecast-chart-card">
          <h4>Velocity Trend</h4>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={velocitySeries} margin={{ top: 6, right: 12, left: -18, bottom: 0 }}>
              <defs>
                <linearGradient id="forecastArea" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={meta.color} stopOpacity={0.45} />
                  <stop offset="95%" stopColor={meta.color} stopOpacity={0.06} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(34, 139, 59, 0.16)" />
              <XAxis dataKey="sprint" tick={{ fill: '#5a7d62', fontSize: 11 }} />
              <YAxis tick={{ fill: '#5a7d62', fontSize: 11 }} />
              <Tooltip formatter={(value) => [value, 'story points']} />
              <Area type="monotone" dataKey="points" stroke={meta.color} fill="url(#forecastArea)" strokeWidth={2.5} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
