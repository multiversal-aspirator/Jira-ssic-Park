from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.services.jira_service import JiraService
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


async def run_sprint_agent(project_key: str, sprint_id: str | None = None) -> SprintAnalysis:
    logger.info(f"[SprintAgent] Analyzing sprint for project {project_key}")
    settings = get_settings()
    jira = JiraService()

    try:
        sprint_data = await jira.get_sprint_issues(project_key, sprint_id)
    except Exception as e:
        logger.warning(f"[SprintAgent] Jira fetch failed: {e}. Using fallback.")
        sprint_data = {"issues": [], "total": 0}

    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )

    chain = SPRINT_PROMPT | llm
    result = await chain.ainvoke({"sprint_data": str(sprint_data)})

    import json
    parsed = json.loads(result.content)
    return SprintAnalysis(**parsed)
