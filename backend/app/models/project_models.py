from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SprintStatus(str, Enum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    OFF_TRACK = "off_track"


# ── Request Models ──


class ProjectUpdateRequest(BaseModel):
    project_key: str = Field(..., description="Jira project key or identifier")
    sprint_id: Optional[str] = Field(None, description="Specific sprint to analyze")
    github_repo: Optional[str] = Field(None, description="GitHub repo in owner/repo format")
    teams_channel: Optional[str] = Field(None, description="Microsoft Teams channel for context")
    include_forecasting: bool = Field(True, description="Whether to run delivery forecasting")


# ── Agent Output Models ──


class SprintAnalysis(BaseModel):
    sprint_name: str
    total_issues: int
    completed: int
    in_progress: int
    blocked: int
    completion_percentage: float
    velocity: float
    status: SprintStatus
    summary: str


class Risk(BaseModel):
    title: str
    severity: RiskSeverity
    evidence: str
    impact: str
    recommendation: str
    source: str


class RiskAnalysis(BaseModel):
    risks: list[Risk]
    overall_risk_level: RiskSeverity
    summary: str


class Dependency(BaseModel):
    source_issue: str
    target_issue: str
    dependency_type: str
    status: str
    is_blocking: bool


class DependencyAnalysis(BaseModel):
    dependencies: list[Dependency]
    conflicts: list[str]
    critical_path: list[str]
    summary: str


class StakeholderReport(BaseModel):
    executive_summary: str
    key_metrics: dict
    highlights: list[str]
    concerns: list[str]
    next_steps: list[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class DeliveryForecast(BaseModel):
    predicted_completion_date: Optional[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    completion_likelihood: str
    historical_velocity: list[float]
    trend: str
    factors: list[str]
    summary: str


# ── Unified Report ──


class ProjectHealthReport(BaseModel):
    project_key: str
    health_score: float = Field(ge=0.0, le=100.0)
    sprint_analysis: Optional[SprintAnalysis] = None
    risk_analysis: Optional[RiskAnalysis] = None
    dependency_analysis: Optional[DependencyAnalysis] = None
    stakeholder_report: Optional[StakeholderReport] = None
    delivery_forecast: Optional[DeliveryForecast] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    evidence_summary: list[str] = Field(default_factory=list)
