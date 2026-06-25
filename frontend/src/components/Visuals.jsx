// Reusable, text-light visual primitives for the dashboard.

export function CircularGauge({ value = 0, size = 120, stroke = 10, label, sublabel, color = '#2e7d32' }) {
  const v = Math.min(100, Math.max(0, value || 0));
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const offset = c - (v / 100) * c;
  return (
    <div className="gauge" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="gauge-svg">
        <circle cx={size / 2} cy={size / 2} r={r} stroke="rgba(34,139,59,0.1)" strokeWidth={stroke} fill="none" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke={color}
          strokeWidth={stroke}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          className="gauge-arc"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="gauge-center">
        <span className="gauge-value" style={{ color }}>{label ?? `${Math.round(v)}%`}</span>
        {sublabel && <span className="gauge-sub">{sublabel}</span>}
      </div>
    </div>
  );
}

export function Donut({ segments = [], size = 130, stroke = 16, centerLabel, centerSub }) {
  const total = segments.reduce((s, x) => s + (x.value || 0), 0) || 1;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  let acc = 0;
  return (
    <div className="donut" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle cx={size / 2} cy={size / 2} r={r} stroke="rgba(34,139,59,0.1)" strokeWidth={stroke} fill="none" />
        {segments.map((seg, i) => {
          const frac = (seg.value || 0) / total;
          const dash = frac * c;
          const gap = c - dash;
          const off = -acc * c;
          acc += frac;
          return (
            <circle
              key={i}
              cx={size / 2}
              cy={size / 2}
              r={r}
              stroke={seg.color}
              strokeWidth={stroke}
              fill="none"
              strokeDasharray={`${dash} ${gap}`}
              strokeDashoffset={off}
              className="donut-seg"
              transform={`rotate(-90 ${size / 2} ${size / 2})`}
            />
          );
        })}
      </svg>
      <div className="gauge-center">
        <span className="gauge-value">{centerLabel}</span>
        {centerSub && <span className="gauge-sub">{centerSub}</span>}
      </div>
    </div>
  );
}

export function Kpi({ value, label, color = '#e8f5ec', icon }) {
  return (
    <div className="kpi">
      {icon && <div className="kpi-icon">{icon}</div>}
      <div className="kpi-value" style={{ color }}>{value}</div>
      <div className="kpi-label">{label}</div>
    </div>
  );
}

export function Chip({ children, tone = 'neutral' }) {
  return <span className={`chip chip--${tone}`}>{children}</span>;
}

export function MiniBar({ value = 0, color = '#34d27b', height = 8 }) {
  const v = Math.min(100, Math.max(0, value || 0));
  return (
    <div className="minibar" style={{ height }}>
      <div className="minibar-fill" style={{ width: `${v}%`, background: color }} />
    </div>
  );
}

// Severity-aware tone helper
export const toneForRisk = (level) =>
  ({ critical: 'danger', high: 'warn', medium: 'amber', low: 'good' }[level] || 'neutral');
