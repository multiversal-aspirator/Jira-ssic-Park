from dotenv import load_dotenv
load_dotenv()  # Load .env into os.environ (needed by langsmith SDK)

import logging
import sys

# Configure root logger so ALL app logs print to terminal
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
    force=True,
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.project_routes import router as project_router
from app.api.webhook_routes import router as webhook_router
from app.api.intelligence_routes import router as intelligence_router
from app.api.team_routes import router as team_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered autonomous project management for engineering teams",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000","http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(project_router)
app.include_router(webhook_router)
app.include_router(intelligence_router)
app.include_router(team_router)


@app.get("/")
async def root():
    return {
        "message": "AI Project Manager API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "analyze": "/api/project/analyze",
            "webhooks": "/api/webhooks/status",
            "intelligence": "/api/intelligence/ask",
            "team": "/api/team/overview",
            "search": "/api/intelligence/search",
        },
    }
