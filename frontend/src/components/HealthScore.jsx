import DinoIcon from './DinoIcon';
import { CircularGauge, Chip } from './Visuals';

export default function HealthScore({ score, evidence }) {
  const s = Math.round(score || 0);
  const color = s >= 70 ? '#2e7d32' : s >= 40 ? '#f57c00' : '#d32f2f';
  const label = s >= 70 ? 'Healthy' : s >= 40 ? 'At Risk' : 'Critical';
  const tone = s >= 70 ? 'good' : s >= 40 ? 'amber' : 'danger';
  const species = s >= 70 ? 'brachio' : s >= 40 ? 'stego' : 'trex';

  return (
    <div className="panel health-hero">
      <span className="hero-dino"><DinoIcon species={species} accent={color} /></span>
      <CircularGauge value={s} size={130} stroke={12} sublabel="Health" color={color} />
      <div className="health-hero__body">
        <div className="health-hero__label" style={{ color }}>{label}</div>
        <div className="health-hero__sub">Overall project health across all 5 agents</div>
        {evidence && evidence.length > 0 && (
          <div className="health-evidence">
            {evidence.slice(0, 5).map((e, i) => (
              <Chip key={i} tone={tone}>{e}</Chip>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
