export default function ProjectManager({ projects, activeProject, onSelect, onRemove }) {
  if (projects.length === 0) return null;

  return (
    <div className="project-manager">
      <h3>Saved Projects</h3>
      <div className="project-chips">
        {projects.map((p) => (
          <div
            key={p.project_key}
            className={`project-chip ${activeProject?.project_key === p.project_key ? 'active' : ''}`}
          >
            <span onClick={() => onSelect(p)} className="chip-label">
              {p.project_key}
              {p.github_repo && <small> ({p.github_repo})</small>}
            </span>
            <button
              className="chip-remove"
              onClick={(e) => { e.stopPropagation(); onRemove(p.project_key); }}
              title="Remove project"
            >
              &times;
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
