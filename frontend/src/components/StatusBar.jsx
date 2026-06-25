export default function StatusBar({ progress, label, color = '#38bdf8', animated = false }) {
  const clampedProgress = Math.min(100, Math.max(0, progress || 0));

  return (
    <div className="status-bar-container">
      <div className="status-bar-label">{label}</div>
      <div className="status-bar-track">
        <div
          className={`status-bar-fill ${animated ? 'animated' : ''}`}
          style={{ width: `${clampedProgress}%`, background: color }}
        />
      </div>
      <span className="status-bar-value">{clampedProgress.toFixed(0)}%</span>
    </div>
  );
}
