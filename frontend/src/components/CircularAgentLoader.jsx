export default function CircularAgentLoader({ progress = 0, status = 'idle', active = false }) {
  const normalized = Math.min(100, Math.max(0, Math.round(progress)));
  const angle = (normalized / 100) * 360;
  const label =
    status === 'completed'
      ? 'Mission complete'
      : status === 'idle'
        ? 'Waiting for release'
        : status === 'fetching'
          ? 'Gathering footprints'
          : status === 'thinking'
            ? 'Crunching dino data'
            : 'Analyzing signal trails';

  return (
    <div className={`agent-orbit-loader ${active ? 'is-active' : ''} ${status === 'completed' ? 'is-done' : ''}`}>
      <div className="agent-orbit-loader__ring">
        <div className="agent-orbit-loader__track" />
        <div
          className="agent-orbit-loader__arc"
          style={{ transform: `rotate(${angle}deg)` }}
          aria-hidden="true"
        />
        <div className="agent-orbit-loader__core" />
      </div>
      <div className="agent-orbit-loader__label">{label}</div>
    </div>
  );
}
