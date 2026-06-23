import json
from langsmith import traceable
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.services.jira_service import JiraService
from app.services.llm_service import get_chat_model, parse_llm_json
from app.services.demo_data_service import load_demo_jira_issues
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


def _build_demo_delivery_forecast(sprint_analysis: SprintAnalysis | None = None) -> DeliveryForecast:
    """Build DeliveryForecast from local demo data."""
    logger.info("[ForecastingAgent] ⚡ Using DEMO FALLBACK data")
    jira = load_demo_jira_issues()
    historical = jira.get("historical_velocity", [38, 42, 35, 40, 37])

    return DeliveryForecast(
        predicted_completion_date="2026-06-22",
        confidence_score=0.55,
        completion_likelihood="medium",
        historical_velocity=[float(v) for v in historical],
        trend="stable",
        factors=[
            "Payment SDK blocker adds 2-4 days to critical path",
            "2 blocked items will carry over to Sprint 22",
            "Team velocity is stable at ~38 SP/sprint but current sprint tracking below average",
            "In-progress items (DEMO-104, DEMO-109) likely completable within 1-2 days",
            "No resource availability issues — team at full capacity",
        ],
        summary="Sprint 21 will likely miss its end date by 3-4 days due to the payment SDK blocker. "
                "Predicted completion: June 22. Confidence is medium (55%) given dependency on "
                "third-party provider resolution. Historical velocity is stable but current sprint "
                "is underperforming at 15/40 SP delivered.",
    )


@traceable(name="ForecastingAgent")
async def run_forecasting_agent(
    project_key: str,
    sprint_analysis: SprintAnalysis | None = None,
) -> DeliveryForecast:
    logger.info(f"[ForecastingAgent] Forecasting delivery for project {project_key}")

    # Stage 1: Fetch historical data (real Jira or demo fallback)
    try:
        jira = JiraService()
        historical_data = await jira.get_sprint_issues(project_key)
        source = "jira"
        logger.info("[ForecastingAgent] Fetched real historical data from Jira")
    except Exception as e:
        logger.info(f"[ForecastingAgent] Jira fetch failed: {e}. Using demo data as LLM input.")
        historical_data = load_demo_jira_issues()
        source = "demo"

    # Stage 2: LLM analysis
    try:
        llm = get_chat_model()
        logger.info(f"[ForecastingAgent] Attempting LLM analysis (source: {source})")
        chain = FORECASTING_PROMPT | llm
        result = await chain.ainvoke({
            "sprint_data": sprint_analysis.model_dump_json() if sprint_analysis else "No sprint data",
            "historical_data": json.dumps(historical_data, default=str),
        })
        parsed = parse_llm_json(result.content)
        forecast = DeliveryForecast(**parsed)
        logger.info(f"[ForecastingAgent] LLM analysis succeeded (source: {source})")
        return forecast
    except Exception as e:
        logger.warning(f"[ForecastingAgent] LLM analysis failed: {e}. Using deterministic fallback.")
        return _build_demo_delivery_forecast(sprint_analysis)
