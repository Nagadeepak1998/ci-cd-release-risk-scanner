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


class RiskFinding(BaseModel):
    rule_id: str
    severity: str
    points: int
    message: str
    evidence: list[str] = Field(default_factory=list)


class RiskReport(BaseModel):
    service: str
    environment: str
    version: str
    score: int
    decision: str
    summary: str
    findings: list[RiskFinding]
    required_actions: list[str]

