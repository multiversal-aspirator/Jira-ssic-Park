from dotenv import load_dotenv
load_dotenv()  # Load .env into os.environ (needed by langsmith SDK)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.project_routes import router as project_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered autonomous project management for engineering teams",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000","http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(project_router)


@app.get("/")
async def root():
    return {
        "message": "AI Project Manager API",
        "docs": "/docs",
    }
