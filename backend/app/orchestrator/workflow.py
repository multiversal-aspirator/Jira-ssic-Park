import asyncio
from typing import TypedDict
from langgraph.graph import StateGraph, END

from app.agents.sprint_agent import run_sprint_agent
from app.agents.risk_agent import run_risk_agent
from app.agents.dependency_agent import run_dependency_agent
from app.agents.reporting_agent import run_reporting_agent
from app.agents.forecasting_agent import run_forecasting_agent
from app.models.project_models import (
    ProjectUpdateRequest,
    ProjectHealthReport,
    SprintAnalysis,
    RiskAnalysis,
    DependencyAnalysis,
    StakeholderReport,
    DeliveryForecast,
    SprintStatus,
    RiskSeverity,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ── LangGraph State ──


class ProjectState(TypedDict, total=False):
    request: ProjectUpdateRequest
    sprint_analysis: SprintAnalysis | None
    risk_analysis: RiskAnalysis | None
    dependency_analysis: DependencyAnalysis | None
    stakeholder_report: StakeholderReport | None
    delivery_forecast: DeliveryForecast | None
    health_report: ProjectHealthReport | None


# ── Node Functions ──


async def analyze_sprint(state: ProjectState) -> dict:
    req = state["request"]
    logger.info("[Orchestrator] Running Sprint Analysis Agent")
    try:
        result = await run_sprint_agent(req.project_key, req.sprint_id)
    except Exception as e:
        logger.error(f"[Orchestrator] Sprint agent failed: {e}")
        result = None
    return {"sprint_analysis": result}


async def detect_risks(state: ProjectState) -> dict:
    req = state["request"]
    logger.info("[Orchestrator] Running Risk Detection Agent")
    try:
        result = await run_risk_agent(req.project_key, req.github_repo, req.teams_channel)
    except Exception as e:
        logger.error(f"[Orchestrator] Risk agent failed: {e}")
        result = None
    return {"risk_analysis": result}


async def track_dependencies(state: ProjectState) -> dict:
    req = state["request"]
    logger.info("[Orchestrator] Running Dependency Tracking Agent")
    try:
        result = await run_dependency_agent(req.project_key, req.github_repo)
    except Exception as e:
        logger.error(f"[Orchestrator] Dependency agent failed: {e}")
        result = None
    return {"dependency_analysis": result}


async def generate_report(state: ProjectState) -> dict:
    logger.info("[Orchestrator] Running Stakeholder Reporting Agent")
    try:
        result = await run_reporting_agent(
            sprint=state.get("sprint_analysis"),
            risks=state.get("risk_analysis"),
            dependencies=state.get("dependency_analysis"),
        )
    except Exception as e:
        logger.error(f"[Orchestrator] Reporting agent failed: {e}")
        result = None
    return {"stakeholder_report": result}


async def forecast_delivery(state: ProjectState) -> dict:
    req = state["request"]
    if not req.include_forecasting:
        return {"delivery_forecast": None}

    logger.info("[Orchestrator] Running Delivery Forecasting Agent")
    try:
        result = await run_forecasting_agent(
            req.project_key,
            sprint_analysis=state.get("sprint_analysis"),
        )
    except Exception as e:
        logger.error(f"[Orchestrator] Forecasting agent failed: {e}")
        result = None
    return {"delivery_forecast": result}


def _compute_health_score(state: ProjectState) -> float:
    score = 50.0

    sprint = state.get("sprint_analysis")
    if sprint:
        if sprint.status == SprintStatus.ON_TRACK:
            score += 20
        elif sprint.status == SprintStatus.AT_RISK:
            score += 5
        else:
            score -= 10
        score += min(sprint.completion_percentage * 0.2, 15)

    risk = state.get("risk_analysis")
    if risk:
        severity_penalty = {
            RiskSeverity.LOW: 2,
            RiskSeverity.MEDIUM: 5,
            RiskSeverity.HIGH: 10,
            RiskSeverity.CRITICAL: 20,
        }
        score -= severity_penalty.get(risk.overall_risk_level, 0)

    deps = state.get("dependency_analysis")
    if deps:
        score -= len(deps.conflicts) * 3

    forecast = state.get("delivery_forecast")
    if forecast:
        score += forecast.confidence_score * 10

    return max(0.0, min(100.0, score))


async def merge_results(state: ProjectState) -> dict:
    logger.info("[Orchestrator] Merging results into health report")
    req = state["request"]

    evidence = []
    if state.get("sprint_analysis"):
        evidence.append(f"Sprint: {state['sprint_analysis'].summary}")
    if state.get("risk_analysis"):
        evidence.append(f"Risks: {state['risk_analysis'].summary}")
    if state.get("dependency_analysis"):
        evidence.append(f"Dependencies: {state['dependency_analysis'].summary}")
    if state.get("delivery_forecast"):
        evidence.append(f"Forecast: {state['delivery_forecast'].summary}")

    report = ProjectHealthReport(
        project_key=req.project_key,
        health_score=_compute_health_score(state),
        sprint_analysis=state.get("sprint_analysis"),
        risk_analysis=state.get("risk_analysis"),
        dependency_analysis=state.get("dependency_analysis"),
        stakeholder_report=state.get("stakeholder_report"),
        delivery_forecast=state.get("delivery_forecast"),
        evidence_summary=evidence,
    )

    return {"health_report": report}


# ── Build LangGraph Workflow ──


def build_workflow() -> StateGraph:
    workflow = StateGraph(ProjectState)

    # Phase 1: parallel data-gathering agents
    workflow.add_node("analyze_sprint", analyze_sprint)
    workflow.add_node("detect_risks", detect_risks)
    workflow.add_node("track_dependencies", track_dependencies)

    # Phase 2: depends on Phase 1 outputs
    workflow.add_node("generate_report", generate_report)
    workflow.add_node("forecast_delivery", forecast_delivery)

    # Phase 3: merge everything
    workflow.add_node("merge_results", merge_results)

    # Fan-out: entry point fans out to 3 parallel agents
    workflow.set_entry_point("analyze_sprint")

    # Wire Phase 1 → Phase 2
    workflow.add_edge("analyze_sprint", "generate_report")
    workflow.add_edge("detect_risks", "generate_report")
    workflow.add_edge("track_dependencies", "generate_report")

    workflow.add_edge("analyze_sprint", "forecast_delivery")

    # Phase 2 → merge
    workflow.add_edge("generate_report", "merge_results")
    workflow.add_edge("forecast_delivery", "merge_results")

    # merge → END
    workflow.add_edge("merge_results", END)

    return workflow


async def run_project_analysis(request: ProjectUpdateRequest) -> ProjectHealthReport:
    logger.info(f"[Orchestrator] Starting analysis for project {request.project_key}")

    workflow = build_workflow()
    app = workflow.compile()

    initial_state: ProjectState = {"request": request}
    final_state = await app.ainvoke(initial_state)

    report = final_state["health_report"]
    logger.info(f"[Orchestrator] Analysis complete. Health score: {report.health_score}")
    return report
