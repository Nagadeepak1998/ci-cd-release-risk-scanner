from __future__ import annotations

from pydantic import BaseModel, Field


class TestSummary(BaseModel):
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    skipped: int = Field(default=0, ge=0)
    coverage_delta: float = 0.0


class DeployContext(BaseModel):
    service: str
    environment: str = "production"
    version: str
    changed_files: list[str] = Field(default_factory=list)
    test_summary: TestSummary
    dependency_updates: list[str] = Field(default_factory=list)
    incidents_last_7d: int = Field(default=0, ge=0)
    rollback_count_30d: int = Field(default=0, ge=0)
    changed_lines: int = Field(default=0, ge=0)
    approvers: list[str] = Field(default_factory=list)
    rollback_plan_url: str | None = None
    monitoring_dashboard_url: str | None = None
    canary_enabled: bool = False
    deployment_window: str = "business_hours"


class RiskFinding(BaseModel):
    rule_id: str
    severity: str
    points: int
    message: str
    evidence: list[str] = Field(default_factory=list)


class ReadinessCheck(BaseModel):
    name: str
    status: str
    evidence: str


class RiskReport(BaseModel):
    service: str
    environment: str
    version: str
    score: int
    decision: str
    summary: str
    findings: list[RiskFinding]
    readiness_checks: list[ReadinessCheck]
    required_actions: list[str]


class PostDeployEvidence(BaseModel):
    window_minutes: int = Field(default=30, ge=1)
    canary_weight_percent: int = Field(default=100, ge=0, le=100)
    error_budget_burn_rate: float = Field(default=0.0, ge=0)
    error_rate_percent: float = Field(default=0.0, ge=0)
    baseline_error_rate_percent: float = Field(default=0.0, ge=0)
    p95_latency_ms: float = Field(default=0.0, ge=0)
    baseline_p95_latency_ms: float = Field(default=0.0, ge=0)
    synthetic_checks_failed: int = Field(default=0, ge=0)
    rollback_events: int = Field(default=0, ge=0)
    alerts_firing: list[str] = Field(default_factory=list)
    release_owner_approved: bool = False


class ReleaseEvidenceBundle(BaseModel):
    release: DeployContext
    evidence: PostDeployEvidence


class EvidenceReport(BaseModel):
    service: str
    environment: str
    version: str
    pre_release_score: int
    pre_release_decision: str
    evidence_score: int
    decision: str
    summary: str
    findings: list[RiskFinding]
    readiness_checks: list[ReadinessCheck]
    required_actions: list[str]
