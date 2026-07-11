from __future__ import annotations

import json
from pathlib import Path

from release_risk_scanner.models import (
    DeployContext,
    EvidenceReport,
    ReleaseEvidenceBundle,
    RiskReport,
    SupplyChainReport,
    SupplyChainReview,
)
from release_risk_scanner.scanner import render_markdown


def load_context(path: Path) -> DeployContext:
    return DeployContext.model_validate_json(path.read_text(encoding="utf-8"))


def load_evidence_bundle(path: Path) -> ReleaseEvidenceBundle:
    return ReleaseEvidenceBundle.model_validate_json(path.read_text(encoding="utf-8"))


def load_supply_chain_review(path: Path) -> SupplyChainReview:
    return SupplyChainReview.model_validate_json(path.read_text(encoding="utf-8"))


def write_report(
    path: Path, report: RiskReport | EvidenceReport | SupplyChainReport, output_format: str
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "markdown":
        path.write_text(render_markdown(report), encoding="utf-8")
    else:
        path.write_text(json.dumps(report.model_dump(), indent=2, sort_keys=True) + "\n")
