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
