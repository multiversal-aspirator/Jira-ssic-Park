import json
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.services.jira_service import JiraService
from app.services.llm_service import get_chat_model, parse_llm_json
from app.services.demo_data_service import load_demo_jira_issues
from app.models.project_models import SprintAnalysis, SprintStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)

SPRINT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Sprint Analysis Agent for an engineering team.
Analyze the provided Jira sprint data and produce a structured sprint status report.

Evaluate:
- How many issues are done vs in-progress vs blocked
- Current velocity compared to planned capacity
- Whether the sprint is on track, at risk, or off track

Respond ONLY with valid JSON matching this schema:
{{
  "sprint_name": "string",
  "total_issues": int,
  "completed": int,
  "in_progress": int,
  "blocked": int,
  "completion_percentage": float,
  "velocity": float,
  "status": "on_track" | "at_risk" | "off_track",
  "summary": "string"
}}"""),
    ("human", "Sprint data:\n{sprint_data}"),
])


def _build_demo_sprint_analysis() -> SprintAnalysis:
    """Build SprintAnalysis from local demo data."""
    logger.info("[SprintAgent] ⚡ Using DEMO FALLBACK data")
    data = load_demo_jira_issues()
    issues = data.get("issues", [])

    total = len(issues)
    completed = sum(1 for i in issues if i["status"] == "Done")
    in_progress = sum(1 for i in issues if i["status"] == "In Progress")
    blocked = sum(1 for i in issues if i["status"] == "Blocked")
    completion_pct = (completed / total * 100) if total else 0

    completed_points = sum(i["story_points"] for i in issues if i["status"] == "Done")
    total_points = sum(i["story_points"] for i in issues)

    if completion_pct >= 70:
        status = SprintStatus.ON_TRACK
    elif completion_pct >= 40:
        status = SprintStatus.AT_RISK
    else:
        status = SprintStatus.OFF_TRACK

    return SprintAnalysis(
        sprint_name=data.get("sprint_name", "Sprint 21"),
        total_issues=total,
        completed=completed,
        in_progress=in_progress,
        blocked=blocked,
        completion_percentage=completion_pct,
        velocity=float(completed_points),
        status=status,
        summary=f"Sprint has {completed}/{total} issues done ({completion_pct:.0f}%). "
                f"{blocked} items blocked. {in_progress} in progress. "
                f"Velocity: {completed_points}/{total_points} story points completed.",
    )


async def run_sprint_agent(project_key: str, sprint_id: str | None = None) -> SprintAnalysis:
    logger.info(f"[SprintAgent] Analyzing sprint for project {project_key}")

    # Stage 1: Fetch data (real Jira or demo fallback)
    try:
        jira = JiraService()
        sprint_data = await jira.get_sprint_issues(project_key, sprint_id)
        source = "jira"
        logger.info(f"[SprintAgent] Fetched real Jira data ({sprint_data.get('total', 0)} issues)")
    except Exception as e:
        logger.info(f"[SprintAgent] Jira fetch failed: {e}. Using demo data as LLM input.")
        sprint_data = load_demo_jira_issues()
        source = "demo"

    # Stage 2: LLM analysis
    try:
        llm = get_chat_model()
        logger.info(f"[SprintAgent] Attempting LLM analysis (source: {source})")
        chain = SPRINT_PROMPT | llm
        result = await chain.ainvoke({"sprint_data": json.dumps(sprint_data, default=str)})
        parsed = parse_llm_json(result.content)
        analysis = SprintAnalysis(**parsed)
        logger.info(f"[SprintAgent] LLM analysis succeeded (source: {source})")
        return analysis
    except Exception as e:
        logger.warning(f"[SprintAgent] LLM analysis failed: {e}. Using deterministic fallback.")
        return _build_demo_sprint_analysis()
