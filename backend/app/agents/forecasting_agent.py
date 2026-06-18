import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.services.jira_service import JiraService
from app.models.project_models import DeliveryForecast, SprintAnalysis
from app.utils.logger import get_logger

logger = get_logger(__name__)

FORECASTING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Delivery Forecasting Agent. Predict sprint/project
completion likelihood based on current sprint data and historical trends.

Consider:
- Current sprint velocity vs planned
- Historical velocity data
- Number of blocked items
- Remaining work vs time left

Respond ONLY with valid JSON matching this schema:
{{
  "predicted_completion_date": "YYYY-MM-DD or null",
  "confidence_score": float (0.0 to 1.0),
  "completion_likelihood": "high|medium|low",
  "historical_velocity": [float],
  "trend": "improving|stable|declining",
  "factors": ["string"],
  "summary": "string"
}}"""),
    ("human", "Current sprint analysis:\n{sprint_data}\n\nHistorical sprint data:\n{historical_data}"),
])


async def run_forecasting_agent(
    project_key: str,
    sprint_analysis: SprintAnalysis | None = None,
) -> DeliveryForecast:
    logger.info(f"[ForecastingAgent] Forecasting delivery for project {project_key}")
    settings = get_settings()

    # Fetch historical sprint data for trend analysis
    jira = JiraService()
    historical_data = {}
    try:
        historical_data = await jira.get_sprint_issues(project_key)
    except Exception as e:
        logger.warning(f"[ForecastingAgent] Historical data fetch failed: {e}")

    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )

    chain = FORECASTING_PROMPT | llm
    result = await chain.ainvoke({
        "sprint_data": sprint_analysis.model_dump_json() if sprint_analysis else "No sprint data",
        "historical_data": str(historical_data),
    })

    parsed = json.loads(result.content)
    return DeliveryForecast(**parsed)
