from __future__ import annotations

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.metrics import (
    CHANGE_ADVISORY_REVIEWS,
    EVIDENCE_REVIEWS,
    LATENCY,
    LATEST_CHANGE_ADVISORY_SCORE,
    LATEST_EVIDENCE_SCORE,
    LATEST_SCORE,
    SCANS,
    SUPPLY_CHAIN_REVIEWS,
)
from release_risk_scanner.models import (
    ChangeAdvisoryReport,
    ChangeAdvisoryReview,
    DeployContext,
    EvidenceReport,
    ReleaseEvidenceBundle,
    RiskReport,
    SupplyChainReport,
    SupplyChainReview,
)
from release_risk_scanner.scanner import (
    evaluate_change_advisory,
    evaluate_release_evidence,
    evaluate_supply_chain,
    scan_release,
)

app = FastAPI(
    title="CI/CD Release Risk Scanner",
    version="0.1.0",
    description="Scores release risk from CI/CD evidence and returns a deploy gate decision.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/scan", response_model=RiskReport)
def scan(context: DeployContext) -> RiskReport:
    with LATENCY.time():
        report = scan_release(context)
    SCANS.labels(decision=report.decision).inc()
    LATEST_SCORE.set(report.score)
    return report


@app.post("/evidence", response_model=EvidenceReport)
def evidence(bundle: ReleaseEvidenceBundle) -> EvidenceReport:
    with LATENCY.time():
        report = evaluate_release_evidence(bundle)
    EVIDENCE_REVIEWS.labels(decision=report.decision).inc()
    LATEST_EVIDENCE_SCORE.set(report.evidence_score)
    return report


@app.post("/supply-chain", response_model=SupplyChainReport)
def supply_chain(review: SupplyChainReview) -> SupplyChainReport:
    with LATENCY.time():
        report = evaluate_supply_chain(review)
    SUPPLY_CHAIN_REVIEWS.labels(decision=report.decision).inc()
    return report


@app.post("/change-advisory", response_model=ChangeAdvisoryReport)
def change_advisory(review: ChangeAdvisoryReview) -> ChangeAdvisoryReport:
    with LATENCY.time():
        report = evaluate_change_advisory(review)
    CHANGE_ADVISORY_REVIEWS.labels(decision=report.decision).inc()
    LATEST_CHANGE_ADVISORY_SCORE.set(report.score)
    return report


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
