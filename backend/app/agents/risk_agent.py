import json
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.services.jira_service import JiraService
from app.services.github_service import GitHubService
from app.services.slack_service import SlackService
from app.services.llm_service import get_chat_model, parse_llm_json
from app.services.demo_data_service import load_demo_jira_issues, load_demo_github_prs, load_demo_slack_messages, load_demo_meeting_notes
from app.models.project_models import RiskAnalysis, Risk, RiskSeverity
from app.utils.logger import get_logger

logger = get_logger(__name__)

RISK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Risk Detection Agent for engineering projects.
Analyze the provided project data from Jira, GitHub, and Slack to identify risks.

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
    ("human", "Jira data:\n{jira_data}\n\nGitHub data:\n{github_data}\n\nSlack data:\n{slack_data}"),
])


def _build_demo_risk_analysis() -> RiskAnalysis:
    """Build RiskAnalysis from local demo data."""
    logger.info("[RiskAgent] ⚡ Using DEMO FALLBACK data")
    jira = load_demo_jira_issues()
    prs = load_demo_github_prs()
    messages = load_demo_slack_messages()

    blocked_issues = [i for i in jira.get("issues", []) if i["status"] == "Blocked"]
    stale_prs = [p for p in prs if p["status"] == "open" and p["open_days"] > 5]
    failing_prs = [p for p in prs if p.get("failing_checks")]

    risks = [
        Risk(
            title="Payment SDK instability blocking critical path",
            severity=RiskSeverity.CRITICAL,
            evidence=f"DEMO-108 blocked for 6+ days. Payment provider returning 503. Support ticket open with no ETA.",
            impact="Payment integration (8 SP) cannot be completed. Cascading block on DEMO-106, DEMO-110, and production deployment.",
            recommendation="Implement retry/circuit-breaker pattern as workaround. Escalate provider support ticket. Consider backup payment provider.",
            source="Jira (DEMO-108) + Slack (Bob Martinez reports)",
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
            evidence="Eve Rodriguez flagged no test coverage on payment flow in Slack. Load testing (DEMO-110) blocked.",
            impact="High regression risk if payment code is rushed to merge without testing.",
            recommendation="Write unit tests with mocked SDK before attempting integration tests. Do not merge without minimum coverage.",
            source="Slack (Eve Rodriguez) + Jira (DEMO-110)",
        ),
    ]

    return RiskAnalysis(
        risks=risks,
        overall_risk_level=RiskSeverity.HIGH,
        summary="Project faces HIGH risk. Critical payment SDK dependency is unresolved, blocking 3 downstream items. "
                "Sprint will miss its goal with ~15 story points carried over. PR hygiene issues compound the delay.",
    )


async def run_risk_agent(
    project_key: str,
    github_repo: str | None = None,
    slack_channel: str | None = None,
) -> RiskAnalysis:
    logger.info(f"[RiskAgent] Detecting risks for project {project_key}")

    # Stage 1: Fetch data (real services or demo fallback)
    try:
        jira = JiraService()
        jira_data = await jira.get_sprint_issues(project_key)

        github_data = {}
        if github_repo:
            gh = GitHubService()
            github_data = {
                "open_prs": await gh.get_open_prs(github_repo),
                "issues": await gh.get_repo_issues(github_repo),
            }

        slack_data = []
        if slack_channel:
            slack = SlackService()
            slack_data = await slack.get_channel_messages(slack_channel, limit=30)

        source = "real"
        logger.info("[RiskAgent] Fetched real data from external services")
    except Exception as e:
        logger.info(f"[RiskAgent] External fetch failed: {e}. Using demo data as LLM input.")
        jira_data = load_demo_jira_issues()
        github_data = load_demo_github_prs()
        slack_data = load_demo_slack_messages()
        source = "demo"

    # Stage 2: LLM analysis
    try:
        llm = get_chat_model()
        logger.info(f"[RiskAgent] Attempting LLM analysis (source: {source})")
        chain = RISK_PROMPT | llm
        result = await chain.ainvoke({
            "jira_data": json.dumps(jira_data, default=str),
            "github_data": json.dumps(github_data, default=str),
            "slack_data": json.dumps(slack_data, default=str),
        })
        parsed = parse_llm_json(result.content)
        analysis = RiskAnalysis(**parsed)
        logger.info(f"[RiskAgent] LLM analysis succeeded (source: {source})")
        return analysis
    except Exception as e:
        logger.warning(f"[RiskAgent] LLM analysis failed: {e}. Using deterministic fallback.")
        return _build_demo_risk_analysis()
