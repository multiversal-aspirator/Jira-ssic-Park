import json
from langsmith import traceable
from langchain_core.prompts import ChatPromptTemplate

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


DONE_STATUSES = {"done", "closed", "resolved", "complete", "completed"}
IN_PROGRESS_STATUSES = {
    "in progress",
    "in review",
    "review",
    "code review",
    "qa",
    "testing",
    "development",
}
BLOCKED_STATUSES = {"blocked", "impediment"}


def _status_name(issue: dict) -> str:
    return str(issue.get("status", "Unknown")).strip()


def _is_completed(issue: dict) -> bool:
    return _status_name(issue).lower() in DONE_STATUSES


def _is_in_progress(issue: dict) -> bool:
    status = _status_name(issue).lower()
    return status in IN_PROGRESS_STATUSES


def _is_blocked(issue: dict) -> bool:
    status = _status_name(issue).lower()
    return bool(issue.get("is_blocked")) or status in BLOCKED_STATUSES or "block" in status


def _story_points(issue: dict) -> float:
    value = issue.get("story_points", 0)
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _build_sprint_analysis_from_data(sprint_data: dict, source: str = "unknown") -> SprintAnalysis:
    """Build SprintAnalysis deterministically from normalized Jira/demo issue data."""
    logger.info(f"[SprintAgent] Using deterministic sprint analysis (source: {source})")

    issues = sprint_data.get("issues", []) or []
    total = len(issues)

    completed = sum(1 for issue in issues if _is_completed(issue))
    blocked = sum(1 for issue in issues if _is_blocked(issue))
    in_progress = sum(1 for issue in issues if _is_in_progress(issue))

    completion_pct = (completed / total * 100) if total else 0.0

    completed_points = sum(_story_points(issue) for issue in issues if _is_completed(issue))
    total_points = sum(_story_points(issue) for issue in issues)

    if total == 0:
        status = SprintStatus.OFF_TRACK
    elif blocked > 0 and completion_pct < 70:
        status = SprintStatus.AT_RISK
    elif completion_pct >= 70:
        status = SprintStatus.ON_TRACK
    elif completion_pct >= 40:
        status = SprintStatus.AT_RISK
    else:
        status = SprintStatus.OFF_TRACK

    sprint_name = (
        sprint_data.get("sprint_name")
        or (f"Sprint {sprint_data.get('sprint_id')}" if sprint_data.get("sprint_id") else "Current Sprint")
    )

    return SprintAnalysis(
        sprint_name=sprint_name,
        total_issues=total,
        completed=completed,
        in_progress=in_progress,
        blocked=blocked,
        completion_percentage=round(completion_pct, 2),
        velocity=float(completed_points),
        status=status,
        summary=(
            f"Sprint analysis from {source}: {completed}/{total} issues completed "
            f"({completion_pct:.0f}%). {blocked} blocked, {in_progress} in progress. "
            f"Velocity: {completed_points:g}/{total_points:g} story points completed."
        ),
    )


@traceable(name="SprintAgent")
async def run_sprint_agent(project_key: str, sprint_id: str | None = None, jira_data: dict | None = None) -> SprintAnalysis:
    logger.info(f"[SprintAgent] Analyzing sprint for project {project_key}")

    # Stage 1: Use pre-fetched data or fetch (real Jira or demo fallback)
    if jira_data:
        sprint_data = jira_data
        source = "pre-fetched"
        logger.info(f"[SprintAgent] Using pre-fetched Jira data ({sprint_data.get('total', 0)} issues)")
    else:
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
        return _build_sprint_analysis_from_data(sprint_data, source=source)