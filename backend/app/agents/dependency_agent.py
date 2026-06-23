import json
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.services.jira_service import JiraService
from app.services.github_service import GitHubService
from app.services.llm_service import get_chat_model, parse_llm_json
from app.services.demo_data_service import load_demo_jira_issues, load_demo_github_prs
from app.models.project_models import DependencyAnalysis, Dependency
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


def _build_demo_dependency_analysis() -> DependencyAnalysis:
    """Build DependencyAnalysis from local demo data."""
    logger.info("[DependencyAgent] ⚡ Using DEMO FALLBACK data")
    jira = load_demo_jira_issues()
    prs = load_demo_github_prs()

    dependencies = [
        Dependency(
            source_issue="DEMO-102",
            target_issue="DEMO-101",
            dependency_type="is_blocked_by",
            status="Done",
            is_blocking=False,
        ),
        Dependency(
            source_issue="DEMO-108",
            target_issue="DEMO-102",
            dependency_type="blocks",
            status="Blocked",
            is_blocking=True,
        ),
        Dependency(
            source_issue="DEMO-102",
            target_issue="DEMO-106",
            dependency_type="blocks",
            status="In Progress",
            is_blocking=True,
        ),
        Dependency(
            source_issue="DEMO-102",
            target_issue="DEMO-110",
            dependency_type="blocks",
            status="In Progress",
            is_blocking=True,
        ),
        Dependency(
            source_issue="DEMO-108",
            target_issue="DEMO-110",
            dependency_type="blocks",
            status="Blocked",
            is_blocking=True,
        ),
        Dependency(
            source_issue="PR #237",
            target_issue="PR #234",
            dependency_type="is_blocked_by",
            status="merged",
            is_blocking=False,
        ),
        Dependency(
            source_issue="PR #242",
            target_issue="PR #237",
            dependency_type="is_blocked_by",
            status="open",
            is_blocking=True,
        ),
    ]

    conflicts = [
        "Cascading block: DEMO-108 → DEMO-102 → DEMO-106, DEMO-110 (3-level chain)",
        "PR #237 has merge conflicts with main branch after PR #234 merged",
    ]

    critical_path = [
        "DEMO-108 (SDK fix) → DEMO-102 (payment integration) → DEMO-110 (load testing) → production deployment",
    ]

    return DependencyAnalysis(
        dependencies=dependencies,
        conflicts=conflicts,
        critical_path=critical_path,
        summary="7 dependencies identified with 2 major conflicts. Critical blocker chain: "
                "payment SDK issue (DEMO-108) blocks payment integration (DEMO-102), "
                "which cascades to email notifications and load testing. "
                "PR dependency chain also has merge conflict issues.",
    )


async def run_dependency_agent(
    project_key: str,
    github_repo: str | None = None,
) -> DependencyAnalysis:
    logger.info(f"[DependencyAgent] Tracking dependencies for project {project_key}")

    # Stage 1: Fetch data (real services or demo fallback)
    try:
        jira = JiraService()
        jira_data = await jira.get_sprint_issues(project_key)

        github_data = []
        if github_repo:
            gh = GitHubService()
            github_data = await gh.get_open_prs(github_repo)

        source = "real"
        logger.info("[DependencyAgent] Fetched real data from external services")
    except Exception as e:
        logger.info(f"[DependencyAgent] External fetch failed: {e}. Using demo data as LLM input.")
        jira_data = load_demo_jira_issues()
        github_data = load_demo_github_prs()
        source = "demo"

    # Stage 2: LLM analysis
    try:
        llm = get_chat_model()
        logger.info(f"[DependencyAgent] Attempting LLM analysis (source: {source})")
        chain = DEPENDENCY_PROMPT | llm
        result = await chain.ainvoke({
            "jira_data": json.dumps(jira_data, default=str),
            "github_data": json.dumps(github_data, default=str),
        })
        parsed = parse_llm_json(result.content)
        analysis = DependencyAnalysis(**parsed)
        logger.info(f"[DependencyAgent] LLM analysis succeeded (source: {source})")
        return analysis
    except Exception as e:
        logger.warning(f"[DependencyAgent] LLM analysis failed: {e}. Using deterministic fallback.")
        return _build_demo_dependency_analysis()
