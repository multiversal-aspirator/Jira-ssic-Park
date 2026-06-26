import DinoIcon from './DinoIcon';
import { Kpi } from './Visuals';

const formatMetricLabel = (key) =>
  key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (ch) => ch.toUpperCase());
 

export default function ReportCard({ data }) {
  if (!data) return null;

  return (
    <div className="card report-card">
      <div className="card-head">
        <span className="card-head__dino"><DinoIcon species="brachio" accent="#558b2f" /></span>
        <h3>Reporting Agent</h3>
      </div>

      {data.key_metrics && Object.keys(data.key_metrics).length > 0 && (
        <div className="kpi-row" style={{ marginBottom: '1rem' }}>
          {Object.entries(data.key_metrics).map(([key, val]) => (
            <Kpi key={key} value={val} label={formatMetricLabel(key)} color="#34d27b" />
          ))}
        </div>
      )}

      {data.executive_summary && (
        <p className="report-summary">{data.executive_summary}</p>
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
