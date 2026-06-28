const FALLBACK = {
  overview: 'Mission control view of delivery health, sprint pace, and risk pressure.',
  agents: 'Live pulse of every specialist agent as they process project signals.',
  sprint: 'Execution telemetry for completion, blocked work, and velocity balance.',
  risks: 'Risk radar with severity mix, impact magnitude, and mitigation priorities.',
  dependencies: 'Critical path and blockers shaping feature delivery flow.',
  team: 'Capacity and collaboration signals across engineering contributors.',
  reports: 'Stakeholder-ready forecast and action-ready management insights.',
  search: 'Ask AI for context or run semantic retrieval across project memory.',
};

export default function TabSummaryStrip({ tab, report, teamData }) {
  const dynamic = {
    overview: report
      ? `Health is at ${Math.round(report.health_score || 0)} with ${report.risk_analysis?.risks?.length || 0} active risks and forecast confidence at ${Math.round((report.delivery_forecast?.confidence_score || 0) * 100)}.`
      : null,
    agents: report ? 'All five agents have completed their latest hunt. Re-run analysis to watch the pack in motion.' : null,
    sprint: report?.sprint_analysis
      ? `${report.sprint_analysis.completed}/${report.sprint_analysis.total_issues} sprint issues are complete with ${report.sprint_analysis.blocked} blocked right now.`
      : null,
    risks: report?.risk_analysis
      ? `${report.risk_analysis.risks?.length || 0} tracked risks, overall level ${report.risk_analysis.overall_risk_level}. Focus on critical and high clusters first.`
      : null,
    dependencies: report?.dependency_analysis
      ? `${report.dependency_analysis.dependencies?.length || 0} dependencies found with ${report.dependency_analysis.conflicts?.length || 0} active conflicts on the path.`
      : null,
    team: teamData
      ? `${teamData.members?.length || 0} members profiled. ${teamData.bottlenecks?.length || 0} bottlenecks flagged for capacity balancing.`
      : null,
    reports: report?.stakeholder_report
      ? `${report.stakeholder_report.highlights?.length || 0} highlights, ${report.stakeholder_report.concerns?.length || 0} concerns, ${report.stakeholder_report.recommendations?.length || 0} recommendations generated.`
      : null,
    search: 'Switch between Ask AI and Semantic Search to either synthesize or retrieve raw context.',
  };

  return (
    <details className="tab-summary" open>
      <summary>
        <span>Quick Pulse</span>
      </summary>
      <p>{dynamic[tab] || FALLBACK[tab]}</p>
    </details>
  );
}
