import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.services.jira_service import JiraService
from app.services.github_service import GitHubService
from app.services.slack_service import SlackService
from app.models.project_models import RiskAnalysis
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


async def run_risk_agent(
    project_key: str,
    github_repo: str | None = None,
    slack_channel: str | None = None,
) -> RiskAnalysis:
    logger.info(f"[RiskAgent] Detecting risks for project {project_key}")
    settings = get_settings()

    jira = JiraService()
    jira_data = {}
    try:
        jira_data = await jira.get_sprint_issues(project_key)
    except Exception as e:
        logger.warning(f"[RiskAgent] Jira fetch failed: {e}")

    github_data = {}
    if github_repo:
        try:
            gh = GitHubService()
            github_data = {
                "open_prs": await gh.get_open_prs(github_repo),
                "issues": await gh.get_repo_issues(github_repo),
            }
        except Exception as e:
            logger.warning(f"[RiskAgent] GitHub fetch failed: {e}")

    slack_data = []
    if slack_channel:
        try:
            slack = SlackService()
            slack_data = await slack.get_channel_messages(slack_channel, limit=30)
        except Exception as e:
            logger.warning(f"[RiskAgent] Slack fetch failed: {e}")

    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )

    chain = RISK_PROMPT | llm
    result = await chain.ainvoke({
        "jira_data": str(jira_data),
        "github_data": str(github_data),
        "slack_data": str(slack_data),
    })

    parsed = json.loads(result.content)
    return RiskAnalysis(**parsed)
