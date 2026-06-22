from fastapi import APIRouter, HTTPException
from app.models.project_models import ProjectUpdateRequest, ProjectHealthReport
from app.orchestrator.workflow import run_project_analysis
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/project", tags=["project"])


@router.post("/analyze", response_model=ProjectHealthReport)
async def analyze_project(request: ProjectUpdateRequest):
    try:
        logger.info(f"Received analysis request for project: {request.project_key}")
        report = await run_project_analysis(request)
        return report
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-project-manager"}


@router.get("/health-report")
async def health_report():
    return {
        "project_name": "AI Project Manager",
        "sprint": "Sprint 21",
        "health_score": 78,
        "status": "At Risk",
        "summary": "Sprint is progressing, but backend dependencies and unresolved blockers may delay delivery.",
        "agents": {
            "sprint_analysis_agent": {
                "progress": "72%",
                "completed_tasks": 18,
                "total_tasks": 25
            },
            "risk_detection_agent": {
                "risk_level": "Medium",
                "risks": [
                    "Authentication API delayed",
                    "Two high-priority bugs still open"
                ]
            },
            "dependency_tracking_agent": {
                "blockers": [
                    "Frontend waiting for backend auth endpoint",
                    "QA waiting for stable deployment"
                ]
            },
            "delivery_forecasting_agent": {
                "completion_likelihood": "68%",
                "forecast": "Sprint may slip by 2 days"
            }
        },
        "recommendations": [
            "Assign one more backend developer to authentication API",
            "Prioritize bug fixes before adding new stories",
            "Run daily blocker review until sprint closure"
        ]
    }
