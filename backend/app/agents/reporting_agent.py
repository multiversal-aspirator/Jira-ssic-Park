import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.models.project_models import StakeholderReport, SprintAnalysis, RiskAnalysis, DependencyAnalysis
from app.utils.logger import get_logger

logger = get_logger(__name__)

REPORTING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Stakeholder Reporting Agent. Your job is to produce
executive-ready status reports from raw analysis data.

You will receive sprint analysis, risk analysis, and dependency analysis.
Synthesize them into a clear, concise report suitable for non-technical stakeholders.

Respond ONLY with valid JSON matching this schema:
{{
  "executive_summary": "string (2-3 paragraphs)",
  "key_metrics": {{"metric_name": "value"}},
  "highlights": ["string"],
  "concerns": ["string"],
  "next_steps": ["string"]
}}"""),
    ("human", "Sprint Analysis:\n{sprint}\n\nRisk Analysis:\n{risks}\n\nDependency Analysis:\n{dependencies}"),
])


async def run_reporting_agent(
    sprint: SprintAnalysis | None = None,
    risks: RiskAnalysis | None = None,
    dependencies: DependencyAnalysis | None = None,
) -> StakeholderReport:
    logger.info("[ReportingAgent] Generating stakeholder report")
    settings = get_settings()

    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )

    chain = REPORTING_PROMPT | llm
    result = await chain.ainvoke({
        "sprint": sprint.model_dump_json() if sprint else "No sprint data available",
        "risks": risks.model_dump_json() if risks else "No risk data available",
        "dependencies": dependencies.model_dump_json() if dependencies else "No dependency data available",
    })

    parsed = json.loads(result.content)
    return StakeholderReport(**parsed)
