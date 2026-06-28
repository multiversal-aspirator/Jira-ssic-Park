import DinoIcon from './DinoIcon';
import { CircularGauge } from './Visuals';

export default function HealthScore({ score }) {
  const s = Math.round(score || 0);
  const color = s >= 70 ? '#2e7d32' : s >= 40 ? '#f57c00' : '#d32f2f';
  const label = s >= 70 ? 'Healthy' : s >= 40 ? 'At Risk' : 'Critical';
  const species = s >= 70 ? 'brachio' : s >= 40 ? 'stego' : 'trex';

  return (
    <div className="panel health-hero">
      <span className="hero-dino">
        <DinoIcon species={species} accent={color} />
      </span>

      <CircularGauge
        value={s}
        size={150}
        stroke={13}
        sublabel="Health"
        color={color}
      />

      <div className="health-hero__body">
        <div className="health-hero__label" style={{ color }}>
          {label}
        </div>
        <div className="health-hero__sub">
          Overall project health across sprint, risk, dependency, forecast, and reporting signals.
        </div>
      </div>
    </div>
  );
}