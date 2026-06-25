import DinoIcon from './DinoIcon';
import { CircularGauge, Chip } from './Visuals';

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
        <div className="legend">
          {data.factors.slice(0, 4).map((f, i) => (
            <Chip key={i} tone="neutral">{f}</Chip>
          ))}
        </div>
      )}
    </div>
  );
}
