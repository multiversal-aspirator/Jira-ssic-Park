from langsmith import traceable
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm_service import get_chat_model, parse_llm_json
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
  "key_metrics": {{"metric_name": "value"}},
  "highlights": ["string"],
  "concerns": ["string"],
  "recommendations": ["string"]
}}"""),
    ("human", "Sprint Analysis:\n{sprint}\n\nRisk Analysis:\n{risks}\n\nDependency Analysis:\n{dependencies}"),
])


def _build_demo_stakeholder_report(
    sprint: SprintAnalysis | None = None,
    risks: RiskAnalysis | None = None,
    dependencies: DependencyAnalysis | None = None,
) -> StakeholderReport:
    """Build StakeholderReport from available agent outputs or demo defaults."""
    logger.info("[ReportingAgent] ⚡ Using DEMO FALLBACK data")

    completion = f"{sprint.completion_percentage:.0f}%" if sprint else "50%"
    risk_level = risks.overall_risk_level.value if risks else "high"
    num_blockers = len(dependencies.conflicts) if dependencies else 2

    return StakeholderReport(
        key_metrics={
            "sprint_completion": completion,
            "story_points_delivered": "15/40",
            "blocked_items": str(num_blockers),
            "risk_level": risk_level,
            "team_velocity_trend": "stable",
        },
        highlights=[
            "OAuth2 login flow completed and deployed to staging",
            "CI/CD pipeline fully operational — staging deployments automated",
            "Webhook event processor merged on schedule",
            "Rate limiting middleware in final review",
        ],
        concerns=[
            "Payment SDK returning 503 — no ETA from provider support",
            "Payment integration PR has merge conflicts and failing tests",
            "Zero test coverage on payment flow increases regression risk",
            "3 items likely to carry over to next sprint",
        ],
        recommendations=[
            "Escalate payment provider support ticket to account manager",
            "Implement circuit-breaker pattern as SDK workaround",
            "Carry over DEMO-106 and DEMO-110 to Sprint 22",
            "Complete race condition fix (DEMO-104) before sprint close",
            "Schedule retrospective to discuss third-party dependency risks",
        ],
    )


@traceable(name="ReportingAgent")
async def run_reporting_agent(
    sprint: SprintAnalysis | None = None,
    risks: RiskAnalysis | None = None,
    dependencies: DependencyAnalysis | None = None,
) -> StakeholderReport:
    logger.info("[ReportingAgent] Generating stakeholder report")

    # Stage: LLM analysis (reporting agent receives data from prior nodes, no external fetch)
    try:
        llm = get_chat_model()
        logger.info("[ReportingAgent] Attempting LLM analysis")
        chain = REPORTING_PROMPT | llm
        result = await chain.ainvoke({
            "sprint": sprint.model_dump_json() if sprint else "No sprint data available",
            "risks": risks.model_dump_json() if risks else "No risk data available",
            "dependencies": dependencies.model_dump_json() if dependencies else "No dependency data available",
        })
        parsed = parse_llm_json(result.content)
        report = StakeholderReport(**parsed)
        logger.info("[ReportingAgent] LLM analysis succeeded")
        return report
    except Exception as e:
        logger.warning(f"[ReportingAgent] LLM analysis failed: {e}. Using deterministic fallback.")
        return _build_demo_stakeholder_report(sprint, risks, dependencies)
