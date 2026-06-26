from datetime import datetime, timezone
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

from app.agents.sprint_agent import run_sprint_agent
from app.agents.risk_agent import run_risk_agent
from app.agents.dependency_agent import run_dependency_agent
from app.agents.reporting_agent import run_reporting_agent
from app.agents.forecasting_agent import run_forecasting_agent
from app.services.jira_service import JiraService
from app.services.github_service import GitHubService
from app.services.teams_service import TeamsService
from app.services.demo_data_service import load_demo_jira_issues, load_demo_github_prs, load_demo_teams_messages
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


# ── Trace accumulator (LangGraph reducer) ──


def _merge_traces(left: list[str], right: list[str]) -> list[str]:
    """LangGraph reducer: append new trace entries to existing list."""
    return left + right


# ── LangGraph State ──


class ProjectState(TypedDict, total=False):
    request: ProjectUpdateRequest
    jira_data: dict
    github_data: dict | list
    teams_data: list
    sprint_analysis: SprintAnalysis | None
    risk_analysis: RiskAnalysis | None
    dependency_analysis: DependencyAnalysis | None
    stakeholder_report: StakeholderReport | None
    delivery_forecast: DeliveryForecast | None
    escalation_recommendations: list[str]
    health_report: ProjectHealthReport | None
    agent_trace: Annotated[list[str], _merge_traces]


# ── Helper ──


def _trace(msg: str) -> str:
    """Create a timestamped trace entry."""
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    return f"[{ts}] {msg}"


# ── Node Functions ──


async def load_project_context(state: ProjectState) -> dict:
    """Fetch all external data once and store in state for all agents."""
    req = state["request"]
    logger.info(f"[Orchestrator] load_project_context: project={req.project_key}")

    # Fetch Jira data once
    try:
        jira = JiraService()
        jira_data = await jira.get_sprint_issues(req.project_key, req.sprint_id)
        logger.info(f"[Orchestrator] Fetched Jira data ({jira_data.get('total', 0)} issues)")
    except Exception as e:
        logger.info(f"[Orchestrator] Jira fetch failed: {e}. Using demo data.")
        jira_data = load_demo_jira_issues()

    # Fetch GitHub data once
    github_data = {}
    if req.github_repo:
        try:
            gh = GitHubService()
            github_data = {
                "open_prs": await gh.get_open_prs(req.github_repo),
                "issues": await gh.get_repo_issues(req.github_repo),
            }
            logger.info("[Orchestrator] Fetched GitHub data")
        except Exception as e:
            logger.info(f"[Orchestrator] GitHub fetch failed: {e}. Using demo data.")
            github_data = load_demo_github_prs()

    # Fetch Teams data once
    teams_data = []
    if req.teams_channel:
        try:
            teams = TeamsService()
            teams_data = await teams.get_channel_messages(req.teams_channel, limit=30)
            logger.info("[Orchestrator] Fetched Teams data")
        except Exception as e:
            logger.info(f"[Orchestrator] Teams fetch failed: {e}. Using demo data.")
            teams_data = load_demo_teams_messages()

    return {
        "jira_data": jira_data,
        "github_data": github_data,
        "teams_data": teams_data,
        "agent_trace": [_trace(f"Loaded project context for {req.project_key} (data fetched once)")],
    }


async def analyze_sprint(state: ProjectState) -> dict:
    """Run Sprint Analysis Agent with pre-fetched data."""
    req = state["request"]
    logger.info("[Orchestrator] analyze_sprint: Running Sprint Analysis Agent")
    try:
        result = await run_sprint_agent(req.project_key, req.sprint_id, jira_data=state.get("jira_data"))
    except Exception as e:
        logger.error(f"[Orchestrator] Sprint agent failed: {e}")
        result = None

    status = "completed" if result else "failed"
    logger.info(f"[Orchestrator] analyze_sprint: {status}")
    return {
        "sprint_analysis": result,
        "agent_trace": [_trace(f"Sprint Agent {status}")],
    }


async def detect_risks(state: ProjectState) -> dict:
    """Run Risk Detection Agent with pre-fetched data."""
    req = state["request"]
    logger.info("[Orchestrator] detect_risks: Running Risk Detection Agent")
    try:
        result = await run_risk_agent(
            req.project_key, req.github_repo, req.teams_channel,
            jira_data=state.get("jira_data"),
            github_data=state.get("github_data"),
            teams_data=state.get("teams_data"),
        )
    except Exception as e:
        logger.error(f"[Orchestrator] Risk agent failed: {e}")
        result = None

    status = "completed" if result else "failed"
    logger.info(f"[Orchestrator] detect_risks: {status}")
    return {
        "risk_analysis": result,
        "agent_trace": [_trace(f"Risk Agent {status}")],
    }


async def track_dependencies(state: ProjectState) -> dict:
    """Run Dependency Tracking Agent with pre-fetched data."""
    req = state["request"]
    logger.info("[Orchestrator] track_dependencies: Running Dependency Tracking Agent")
    try:
        result = await run_dependency_agent(
            req.project_key, req.github_repo,
            jira_data=state.get("jira_data"),
            github_data=state.get("github_data"),
        )
    except Exception as e:
        logger.error(f"[Orchestrator] Dependency agent failed: {e}")
        result = None

    status = "completed" if result else "failed"
    logger.info(f"[Orchestrator] track_dependencies: {status}")
    return {
        "dependency_analysis": result,
        "agent_trace": [_trace(f"Dependency Agent {status}")],
    }


async def forecast_delivery(state: ProjectState) -> dict:
    """Run Delivery Forecasting Agent with pre-fetched data."""
    req = state["request"]
    if not req.include_forecasting:
        return {
            "delivery_forecast": None,
            "agent_trace": [_trace("Forecast Agent skipped (disabled)")],
        }

    logger.info("[Orchestrator] forecast_delivery: Running Delivery Forecasting Agent")
    try:
        result = await run_forecasting_agent(
            req.project_key,
            sprint_analysis=state.get("sprint_analysis"),
            jira_data=state.get("jira_data"),
        )
    except Exception as e:
        logger.error(f"[Orchestrator] Forecasting agent failed: {e}")
        result = None

    status = "completed" if result else "failed"
    logger.info(f"[Orchestrator] forecast_delivery: {status}")
    return {
        "delivery_forecast": result,
        "agent_trace": [_trace(f"Forecast Agent {status}")],
    }


async def generate_report(state: ProjectState) -> dict:
    """Run Stakeholder Reporting Agent."""
    logger.info("[Orchestrator] generate_report: Running Stakeholder Reporting Agent")
    try:
        result = await run_reporting_agent(
            sprint=state.get("sprint_analysis"),
            risks=state.get("risk_analysis"),
            dependencies=state.get("dependency_analysis"),
        )
    except Exception as e:
        logger.error(f"[Orchestrator] Reporting agent failed: {e}")
        result = None

    status = "completed" if result else "failed"
    logger.info(f"[Orchestrator] generate_report: {status}")
    return {
        "stakeholder_report": result,
        "agent_trace": [_trace(f"Reporting Agent {status}")],
    }


# ── Conditional Edge: Escalation Check ──


def should_escalate(state: ProjectState) -> str:
    """Determine whether escalation is needed based on risk, dependencies, and sprint status."""
    risk = state.get("risk_analysis")
    deps = state.get("dependency_analysis")
    sprint = state.get("sprint_analysis")

    if risk and risk.overall_risk_level in (RiskSeverity.HIGH, RiskSeverity.CRITICAL):
        return "escalation_node"
    if deps and len(deps.conflicts) > 0:
        return "escalation_node"
    if sprint and sprint.status == SprintStatus.OFF_TRACK:
        return "escalation_node"

    return "merge_results"


async def escalation_node(state: ProjectState) -> dict:
    """Generate escalation recommendations when critical issues are detected."""
    logger.info("[Orchestrator] escalation_node: Generating escalation recommendations")

    reasons: list[str] = []
    recommendations: list[str] = []

    risk = state.get("risk_analysis")
    if risk and risk.overall_risk_level in (RiskSeverity.HIGH, RiskSeverity.CRITICAL):
        reasons.append(f"Overall risk level is {risk.overall_risk_level.value}")
        for r in risk.risks:
            if r.severity in (RiskSeverity.HIGH, RiskSeverity.CRITICAL):
                recommendations.append(r.recommendation)

    deps = state.get("dependency_analysis")
    if deps and deps.conflicts:
        reasons.append(f"{len(deps.conflicts)} dependency conflict(s) detected")
        recommendations.append("Resolve dependency conflicts before sprint completion")

    sprint = state.get("sprint_analysis")
    if sprint and sprint.status == SprintStatus.OFF_TRACK:
        reasons.append("Sprint is OFF_TRACK")
        recommendations.append("Consider scope reduction or sprint extension")

    if not recommendations:
        recommendations.append("Review flagged items with engineering leads")

    logger.info(f"[Orchestrator] escalation_node: {len(reasons)} reason(s), {len(recommendations)} recommendation(s)")
    return {
        "escalation_recommendations": recommendations,
        "agent_trace": [_trace(f"Escalation triggered — reasons: {'; '.join(reasons)}")],
    }


# ── Health Score Computation ──


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


# ── Final Merge Node ──


async def merge_results(state: ProjectState) -> dict:
    """Merge all agent outputs into the final ProjectHealthReport."""
    logger.info("[Orchestrator] merge_results: Building final health report")
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

    # Include escalation recommendations in evidence if present
    escalation_recs = state.get("escalation_recommendations")
    if escalation_recs:
        evidence.append(f"Escalation: {'; '.join(escalation_recs)}")

    report = ProjectHealthReport(
        project_key=req.project_key,
        health_score=_compute_health_score(state),
        sprint_analysis=state.get("sprint_analysis"),
        risk_analysis=state.get("risk_analysis"),
        dependency_analysis=state.get("dependency_analysis"),
        stakeholder_report=state.get("stakeholder_report"),
        delivery_forecast=state.get("delivery_forecast"),
        evidence_summary=evidence,
        agent_trace=state.get("agent_trace", []),
    )

    logger.info(f"[Orchestrator] merge_results: Health score = {report.health_score}")
    return {
        "health_report": report,
        "agent_trace": [_trace("Health report generated")],
    }


# ── Build LangGraph Workflow ──


def build_workflow() -> StateGraph:
    """Construct the AI Project Manager LangGraph with parallel fan-out execution."""
    workflow = StateGraph(ProjectState)

    # Register all nodes
    workflow.add_node("load_project_context", load_project_context)
    workflow.add_node("analyze_sprint", analyze_sprint)
    workflow.add_node("detect_risks", detect_risks)
    workflow.add_node("track_dependencies", track_dependencies)
    workflow.add_node("forecast_delivery", forecast_delivery)
    workflow.add_node("generate_report", generate_report)
    workflow.add_node("escalation_node", escalation_node)
    workflow.add_node("merge_results", merge_results)

    # Entry point: fetch all data once
    workflow.set_entry_point("load_project_context")

    # Fan-out: sprint, risk, dependency run in PARALLEL
    workflow.add_edge("load_project_context", "analyze_sprint")
    workflow.add_edge("load_project_context", "detect_risks")
    workflow.add_edge("load_project_context", "track_dependencies")

    # Fan-in: forecast and report run in PARALLEL after first 3 complete
    workflow.add_edge("analyze_sprint", "forecast_delivery")
    workflow.add_edge("analyze_sprint", "generate_report")
    workflow.add_edge("detect_risks", "generate_report")
    workflow.add_edge("track_dependencies", "generate_report")
    workflow.add_edge("detect_risks", "forecast_delivery")
    workflow.add_edge("track_dependencies", "forecast_delivery")

    # Conditional edge: escalate if critical issues found
    workflow.add_conditional_edges(
        "generate_report",
        should_escalate,
        {"escalation_node": "escalation_node", "merge_results": "merge_results"},
    )

    workflow.add_edge("forecast_delivery", "merge_results")
    workflow.add_edge("escalation_node", "merge_results")
    workflow.add_edge("merge_results", END)

    return workflow


async def run_project_analysis(request: ProjectUpdateRequest) -> ProjectHealthReport:
    """Entry point: run the full LangGraph workflow and return the health report."""
    logger.info(f"[Orchestrator] Starting analysis for project {request.project_key}")

    workflow = build_workflow()
    app = workflow.compile()

    initial_state: ProjectState = {"request": request, "agent_trace": []}
    final_state = await app.ainvoke(initial_state)

    report = final_state["health_report"]
    logger.info(f"[Orchestrator] Analysis complete. Health score: {report.health_score}")
    return report
