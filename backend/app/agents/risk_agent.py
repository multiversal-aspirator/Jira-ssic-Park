import json
from langsmith import traceable
from langchain_core.prompts import ChatPromptTemplate
from app.services.jira_service import JiraService
from app.services.github_service import GitHubService
from app.services.teams_service import TeamsService
from app.services.llm_service import get_chat_model, parse_llm_json
from app.services.demo_data_service import load_demo_jira_issues, load_demo_github_prs, load_demo_teams_messages, load_demo_meeting_notes
from app.models.project_models import RiskAnalysis, Risk, RiskSeverity
from app.utils.logger import get_logger

logger = get_logger(__name__)

RISK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Risk Detection Agent for engineering projects.
Analyze the provided project data from Jira, GitHub, and Microsoft Teams to identify risks.

For each risk you MUST provide:
- title: concise risk name
- severity: "low", "medium", "high", or "critical"
- evidence: specific data points that indicate this risk
- impact: what happens if the risk materializes
- recommendation: concrete action to mitigate
- source: which data source revealed this risk

Also provide an overall_risk_level and a summary.

Respond ONLY with valid JSON matching this schema:
{{
  "risks": [{{
    "title": "string",
    "severity": "low|medium|high|critical",
    "evidence": "string",
    "impact": "string",
    "recommendation": "string",
    "source": "string"
  }}],
  "overall_risk_level": "low|medium|high|critical",
  "summary": "string"
}}"""),
    ("human", "Jira data:\n{jira_data}\n\nGitHub data:\n{github_data}\n\nTeams data:\n{teams_data}"),
])


def _build_demo_risk_analysis() -> RiskAnalysis:
    """Build RiskAnalysis from local demo data."""
    logger.info("[RiskAgent] ⚡ Using DEMO FALLBACK data")
    jira = load_demo_jira_issues()
    prs = load_demo_github_prs()
    messages = load_demo_teams_messages()

    blocked_issues = [i for i in jira.get("issues", []) if i.get("status", "") == "Blocked"]
    stale_prs = [p for p in prs if p.get("status", "") == "open" and p.get("open_days", 0) > 5]
    failing_prs = [p for p in prs if p.get("failing_checks")]

    risks = [
        Risk(
            title="Payment SDK instability blocking critical path",
            severity=RiskSeverity.CRITICAL,
            evidence=f"DEMO-108 blocked for 6+ days. Payment provider returning 503. Support ticket open with no ETA.",
            impact="Payment integration (8 SP) cannot be completed. Cascading block on DEMO-106, DEMO-110, and production deployment.",
            recommendation="Implement retry/circuit-breaker pattern as workaround. Escalate provider support ticket. Consider backup payment provider.",
            source="Jira (DEMO-108) + Teams (Bob Martinez reports)",
        ),
        Risk(
            title="Sprint delivery at risk — 2 items blocked, 3 in progress on final day",
            severity=RiskSeverity.HIGH,
            evidence=f"{len(blocked_issues)} blocked issues, sprint ends today with only 50% completion. 15 story points likely to miss.",
            impact="Sprint goal will not be met. Auth module complete but payment integration incomplete.",
            recommendation="Carry over blocked items to Sprint 22. Focus remaining effort on completing in-progress items (DEMO-104, DEMO-109).",
            source="Jira sprint burndown + meeting notes",
        ),
        Risk(
            title="PR #237 has merge conflicts and failing checks",
            severity=RiskSeverity.HIGH,
            evidence=f"PR #237 (payment gateway) open for 8 days, has merge conflicts and 2 failing checks (integration-tests, lint). Changes requested in review.",
            impact="Even when SDK issue resolves, PR needs significant rework before merge. Additional delay likely.",
            recommendation="Rebase PR #237 immediately. Fix lint issues. Run integration tests with mocked SDK responses.",
            source="GitHub PR data",
        ),
        Risk(
            title="Zero test coverage on payment flow",
            severity=RiskSeverity.MEDIUM,
            evidence="Eve Rodriguez flagged no test coverage on payment flow in Teams. Load testing (DEMO-110) blocked.",
            impact="High regression risk if payment code is rushed to merge without testing.",
            recommendation="Write unit tests with mocked SDK before attempting integration tests. Do not merge without minimum coverage.",
            source="Teams (Eve Rodriguez) + Jira (DEMO-110)",
        ),
    ]

    return RiskAnalysis(
        risks=risks,
        overall_risk_level=RiskSeverity.HIGH,
        summary="Project faces HIGH risk. Critical payment SDK dependency is unresolved, blocking 3 downstream items. "
                "Sprint will miss its goal with ~15 story points carried over. PR hygiene issues compound the delay.",
    )


@traceable(name="RiskAgent")
async def run_risk_agent(
    project_key: str,
    github_repo: str | None = None,
    teams_channel: str | None = None,
    jira_data: dict | None = None,
    github_data: dict | list | None = None,
    teams_data: list | None = None,
) -> RiskAnalysis:
    logger.info(f"[RiskAgent] Detecting risks for project {project_key}")

    # Stage 1: Use pre-fetched data or fetch (real services or demo fallback)
    if jira_data is not None:
        _jira_data = jira_data
        _github_data = github_data or {}
        _teams_data = teams_data or []
        source = "pre-fetched"
        logger.info("[RiskAgent] Using pre-fetched data from orchestrator")
    else:
        try:
            jira = JiraService()
            _jira_data = await jira.get_sprint_issues(project_key)

            _github_data = {}
            if github_repo:
                gh = GitHubService()
                _github_data = {
                    "open_prs": await gh.get_open_prs(github_repo),
                    "issues": await gh.get_repo_issues(github_repo),
                }

            _teams_data = []
            if teams_channel:
                teams = TeamsService()
                _teams_data = await teams.get_channel_messages(teams_channel, limit=30)

            source = "real"
            logger.info("[RiskAgent] Fetched real data from external services")
        except Exception as e:
            logger.info(f"[RiskAgent] External fetch failed: {e}. Using demo data as LLM input.")
            _jira_data = load_demo_jira_issues()
            _github_data = load_demo_github_prs()
            _teams_data = load_demo_teams_messages()
            source = "demo"

    # Stage 2: LLM analysis
    try:
        llm = get_chat_model()
        logger.info(f"[RiskAgent] Attempting LLM analysis (source: {source})")
        chain = RISK_PROMPT | llm
        result = await chain.ainvoke({
            "jira_data": json.dumps(_jira_data, default=str),
            "github_data": json.dumps(_github_data, default=str),
            "teams_data": json.dumps(_teams_data, default=str),
        })
        parsed = parse_llm_json(result.content)
        analysis = RiskAnalysis(**parsed)
        logger.info(f"[RiskAgent] LLM analysis succeeded (source: {source})")
        return analysis
    except Exception as e:
        logger.warning(f"[RiskAgent] LLM analysis failed: {e}. Using deterministic fallback.")
        return _build_demo_risk_analysis()
