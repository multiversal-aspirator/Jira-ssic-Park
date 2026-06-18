import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.services.jira_service import JiraService
from app.services.github_service import GitHubService
from app.models.project_models import DependencyAnalysis
from app.utils.logger import get_logger

logger = get_logger(__name__)

DEPENDENCY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Dependency Tracking Agent for engineering projects.
Analyze issue links from Jira and PR dependencies from GitHub to identify:
- All dependencies between issues/PRs
- Dependency conflicts (circular deps, blocked chains)
- Critical path items

Respond ONLY with valid JSON matching this schema:
{{
  "dependencies": [{{
    "source_issue": "string",
    "target_issue": "string",
    "dependency_type": "blocks|is_blocked_by|relates_to",
    "status": "string",
    "is_blocking": bool
  }}],
  "conflicts": ["string"],
  "critical_path": ["string"],
  "summary": "string"
}}"""),
    ("human", "Jira issues with links:\n{jira_data}\n\nGitHub PRs:\n{github_data}"),
])


async def run_dependency_agent(
    project_key: str,
    github_repo: str | None = None,
) -> DependencyAnalysis:
    logger.info(f"[DependencyAgent] Tracking dependencies for project {project_key}")
    settings = get_settings()

    jira = JiraService()
    jira_data = {}
    try:
        jira_data = await jira.get_sprint_issues(project_key)
    except Exception as e:
        logger.warning(f"[DependencyAgent] Jira fetch failed: {e}")

    github_data = []
    if github_repo:
        try:
            gh = GitHubService()
            github_data = await gh.get_open_prs(github_repo)
        except Exception as e:
            logger.warning(f"[DependencyAgent] GitHub fetch failed: {e}")

    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )

    chain = DEPENDENCY_PROMPT | llm
    result = await chain.ainvoke({
        "jira_data": str(jira_data),
        "github_data": str(github_data),
    })

    parsed = json.loads(result.content)
    return DependencyAnalysis(**parsed)
