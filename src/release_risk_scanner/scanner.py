from __future__ import annotations

from pathlib import PurePosixPath

from release_risk_scanner.models import (
    DeployContext,
    EvidenceReport,
    PostDeployEvidence,
    ReadinessCheck,
    ReleaseEvidenceBundle,
    RiskFinding,
    RiskReport,
    SupplyChainEvidence,
    SupplyChainReport,
    SupplyChainReview,
)


def scan_release(context: DeployContext) -> RiskReport:
    findings = [
        *_test_findings(context),
        *_change_findings(context),
        *_operational_findings(context),
        *_approval_findings(context),
        *_readiness_findings(context),
    ]
    score = min(100, sum(finding.points for finding in findings))
    decision = _decision(score)
    readiness_checks = _readiness_checks(context)
    return RiskReport(
        service=context.service,
        environment=context.environment,
        version=context.version,
        score=score,
        decision=decision,
        summary=(
            f"{context.service} {context.version} is {decision} for {context.environment} "
            f"with release risk score {score}."
        ),
        findings=findings,
        readiness_checks=readiness_checks,
        required_actions=_required_actions(decision, findings, readiness_checks),
    )


def evaluate_release_evidence(bundle: ReleaseEvidenceBundle) -> EvidenceReport:
    pre_release = scan_release(bundle.release)
    findings = [
        *_pre_release_evidence_findings(pre_release),
        *_post_deploy_findings(bundle.evidence),
    ]
    score = min(100, sum(finding.points for finding in findings))
    decision = _evidence_decision(pre_release, bundle.evidence, score)
    return EvidenceReport(
        service=bundle.release.service,
        environment=bundle.release.environment,
        version=bundle.release.version,
        pre_release_score=pre_release.score,
        pre_release_decision=pre_release.decision,
        evidence_score=score,
        decision=decision,
        summary=(
            f"{bundle.release.service} {bundle.release.version} post-deploy evidence is "
            f"{decision} after {bundle.evidence.window_minutes} minutes with evidence score {score}."
        ),
        findings=findings,
        readiness_checks=pre_release.readiness_checks,
        required_actions=_evidence_actions(decision, findings),
    )


def evaluate_supply_chain(review: SupplyChainReview) -> SupplyChainReport:
    findings = _supply_chain_findings(review.evidence)
    score = min(100, sum(finding.points for finding in findings))
    decision = _decision(score)
    if review.evidence.critical_vulnerabilities or not review.evidence.signature_verified:
        decision = "block"
    return SupplyChainReport(
        service=review.release.service,
        environment=review.release.environment,
        version=review.release.version,
        artifact_digest=review.evidence.artifact_digest,
        score=score,
        decision=decision,
        summary=(
            f"{review.release.service} {review.release.version} supply-chain evidence is "
            f"{decision} with policy score {score}."
        ),
        findings=findings,
        required_actions=_supply_chain_actions(decision, findings),
    )


def render_markdown(report: RiskReport | EvidenceReport | SupplyChainReport) -> str:
    if isinstance(report, SupplyChainReport):
        return _render_supply_chain_markdown(report)
    if isinstance(report, EvidenceReport):
        return _render_evidence_markdown(report)

    lines = [
        f"# Release Risk Report: {report.service}",
        "",
        f"- Environment: `{report.environment}`",
        f"- Version: `{report.version}`",
        f"- Score: `{report.score}`",
        f"- Decision: `{report.decision}`",
        "",
        "## Summary",
        "",
        report.summary,
        "",
        "## Findings",
        "",
    ]
    for finding in report.findings:
        evidence = "; ".join(finding.evidence) if finding.evidence else "no extra evidence"
        lines.append(
            f"- **{finding.rule_id}** ({finding.severity}, +{finding.points}): "
            f"{finding.message} Evidence: {evidence}."
        )
    lines.extend(["", "## Deployment Readiness", ""])
    for check in report.readiness_checks:
        lines.append(f"- **{check.name}**: `{check.status}` - {check.evidence}")
    lines.extend(["", "## Required Actions", ""])
    lines.extend(f"1. {action}" for action in report.required_actions)
    lines.append("")
    return "\n".join(lines)


def _render_supply_chain_markdown(report: SupplyChainReport) -> str:
    lines = [
        f"# Supply Chain Review: {report.service}",
        "",
        f"- Environment: `{report.environment}`",
        f"- Version: `{report.version}`",
        f"- Artifact: `{report.artifact_digest}`",
        f"- Score: `{report.score}`",
        f"- Decision: `{report.decision}`",
        "",
        "## Findings",
        "",
    ]
    for finding in report.findings:
        evidence = "; ".join(finding.evidence) if finding.evidence else "no extra evidence"
        lines.append(
            f"- **{finding.rule_id}** ({finding.severity}, +{finding.points}): "
            f"{finding.message} Evidence: {evidence}."
        )
    lines.extend(["", "## Required Actions", ""])
    lines.extend(f"1. {action}" for action in report.required_actions)
    lines.append("")
    return "\n".join(lines)


def _supply_chain_findings(evidence: SupplyChainEvidence) -> list[RiskFinding]:
    checks = [
        (not evidence.sbom_present, "missing-sbom", "high", 20, "Artifact has no SBOM."),
        (
            not evidence.provenance_present,
            "missing-provenance",
            "high",
            20,
            "Artifact has no build provenance attestation.",
        ),
        (
            not evidence.signature_verified,
            "unverified-signature",
            "critical",
            40,
            "Artifact signature was not verified.",
        ),
    ]
    findings = [
        RiskFinding(rule_id=rule, severity=severity, points=points, message=message)
        for failed, rule, severity, points, message in checks
        if failed
    ]
    if evidence.critical_vulnerabilities:
        findings.append(
            RiskFinding(
                rule_id="critical-vulnerabilities",
                severity="critical",
                points=50,
                message="Artifact contains critical vulnerabilities.",
                evidence=[f"critical={evidence.critical_vulnerabilities}"],
            )
        )
    if evidence.high_vulnerabilities:
        findings.append(
            RiskFinding(
                rule_id="high-vulnerabilities",
                severity="high",
                points=min(30, evidence.high_vulnerabilities * 10),
                message="Artifact contains high-severity vulnerabilities.",
                evidence=[f"high={evidence.high_vulnerabilities}"],
            )
        )
    if evidence.licenses_denied:
        findings.append(
            RiskFinding(
                rule_id="denied-licenses",
                severity="high",
                points=30,
                message="SBOM contains dependencies with denied licenses.",
                evidence=evidence.licenses_denied[:5],
            )
        )
    return findings


def _supply_chain_actions(decision: str, findings: list[RiskFinding]) -> list[str]:
    if decision == "approve":
        return ["Attach the verified SBOM, provenance, and signature evidence to the release."]
    actions = ["Do not promote this artifact until blocking supply-chain findings are resolved."]
    if any(f.rule_id == "unverified-signature" for f in findings):
        actions.append("Sign the artifact and verify the signature against the trusted identity policy.")
    if any(f.rule_id == "critical-vulnerabilities" for f in findings):
        actions.append("Rebuild with patched dependencies and rerun the vulnerability scan.")
    return actions


def _render_evidence_markdown(report: EvidenceReport) -> str:
    lines = [
        f"# Release Evidence Report: {report.service}",
        "",
        f"- Environment: `{report.environment}`",
        f"- Version: `{report.version}`",
        f"- Pre-release score: `{report.pre_release_score}`",
        f"- Pre-release decision: `{report.pre_release_decision}`",
        f"- Evidence score: `{report.evidence_score}`",
        f"- Decision: `{report.decision}`",
        "",
        "## Summary",
        "",
        report.summary,
        "",
        "## Findings",
        "",
    ]
    for finding in report.findings:
        evidence = "; ".join(finding.evidence) if finding.evidence else "no extra evidence"
        lines.append(
            f"- **{finding.rule_id}** ({finding.severity}, +{finding.points}): "
            f"{finding.message} Evidence: {evidence}."
        )
    lines.extend(["", "## Deployment Readiness", ""])
    for check in report.readiness_checks:
        lines.append(f"- **{check.name}**: `{check.status}` - {check.evidence}")
    lines.extend(["", "## Required Actions", ""])
    lines.extend(f"1. {action}" for action in report.required_actions)
    lines.append("")
    return "\n".join(lines)


def _test_findings(context: DeployContext) -> list[RiskFinding]:
    summary = context.test_summary
    findings: list[RiskFinding] = []
    if summary.failed:
        findings.append(
            RiskFinding(
                rule_id="failed-tests",
                severity="critical",
                points=40,
                message="Release has failing tests.",
                evidence=[f"failed={summary.failed}", f"passed={summary.passed}"],
            )
        )
    if summary.coverage_delta <= -3:
        findings.append(
            RiskFinding(
                rule_id="coverage-drop",
                severity="medium",
                points=12,
                message="Test coverage dropped beyond the release threshold.",
                evidence=[f"coverage_delta={summary.coverage_delta}"],
            )
        )
    return findings


def _change_findings(context: DeployContext) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    risky_files = [path for path in context.changed_files if _is_risky_path(path)]
    migration_files = [path for path in context.changed_files if "migration" in path.lower()]
    infra_files = [path for path in context.changed_files if path.startswith(("infra/", "terraform/"))]

    if risky_files:
        findings.append(
            RiskFinding(
                rule_id="security-or-config-change",
                severity="high",
                points=20,
                message="Release changes security, auth, secrets, or production config paths.",
                evidence=risky_files[:5],
            )
        )
    if migration_files:
        findings.append(
            RiskFinding(
                rule_id="database-migration",
                severity="high",
                points=18,
                message="Release includes database migration files.",
                evidence=migration_files[:5],
            )
        )
    if infra_files:
        findings.append(
            RiskFinding(
                rule_id="infra-change",
                severity="medium",
                points=10,
                message="Release includes infrastructure changes.",
                evidence=infra_files[:5],
            )
        )
    if context.changed_lines >= 800:
        findings.append(
            RiskFinding(
                rule_id="large-change-set",
                severity="medium",
                points=12,
                message="Release changes a large number of lines.",
                evidence=[f"changed_lines={context.changed_lines}"],
            )
        )
    if context.dependency_updates:
        findings.append(
            RiskFinding(
                rule_id="dependency-update",
                severity="medium",
                points=min(15, 5 * len(context.dependency_updates)),
                message="Release updates runtime dependencies.",
                evidence=context.dependency_updates[:5],
            )
        )
    return findings


def _operational_findings(context: DeployContext) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    if context.incidents_last_7d >= 2:
        findings.append(
            RiskFinding(
                rule_id="recent-incidents",
                severity="high",
                points=18,
                message="Service had multiple recent incidents.",
                evidence=[f"incidents_last_7d={context.incidents_last_7d}"],
            )
        )
    if context.rollback_count_30d:
        findings.append(
            RiskFinding(
                rule_id="rollback-history",
                severity="medium",
                points=min(18, 9 * context.rollback_count_30d),
                message="Service has recent rollback history.",
                evidence=[f"rollback_count_30d={context.rollback_count_30d}"],
            )
        )
    return findings


def _approval_findings(context: DeployContext) -> list[RiskFinding]:
    if context.environment == "production" and len(context.approvers) < 2:
        return [
            RiskFinding(
                rule_id="missing-production-approval",
                severity="high",
                points=16,
                message="Production releases require at least two approvers.",
                evidence=[f"approvers={len(context.approvers)}"],
            )
        ]
    return []


def _readiness_findings(context: DeployContext) -> list[RiskFinding]:
    if context.environment != "production":
        return []

    findings: list[RiskFinding] = []
    if not context.rollback_plan_url:
        findings.append(
            RiskFinding(
                rule_id="missing-rollback-plan",
                severity="high",
                points=16,
                message="Production release is missing a rollback plan reference.",
                evidence=["rollback_plan_url=missing"],
            )
        )
    if not context.monitoring_dashboard_url:
        findings.append(
            RiskFinding(
                rule_id="missing-monitoring-dashboard",
                severity="medium",
                points=8,
                message="Production release is missing a monitoring dashboard reference.",
                evidence=["monitoring_dashboard_url=missing"],
            )
        )
    if context.deployment_window == "off_hours" and not context.canary_enabled:
        findings.append(
            RiskFinding(
                rule_id="off-hours-without-canary",
                severity="medium",
                points=12,
                message="Off-hours production release does not use a canary rollout.",
                evidence=["deployment_window=off_hours", "canary_enabled=false"],
            )
        )
    return findings


def _readiness_checks(context: DeployContext) -> list[ReadinessCheck]:
    canary_status = "pass"
    canary_evidence = "canary rollout enabled"
    if context.deployment_window == "off_hours" and not context.canary_enabled:
        canary_status = "fail"
        canary_evidence = "off-hours release without canary rollout"
    elif not context.canary_enabled:
        canary_status = "warn"
        canary_evidence = "standard rollout; canary not enabled"

    return [
        ReadinessCheck(
            name="rollback_plan",
            status="pass" if context.rollback_plan_url else "fail",
            evidence=context.rollback_plan_url or "missing rollback plan URL",
        ),
        ReadinessCheck(
            name="monitoring_dashboard",
            status="pass" if context.monitoring_dashboard_url else "fail",
            evidence=context.monitoring_dashboard_url or "missing dashboard URL",
        ),
        ReadinessCheck(
            name="canary_rollout",
            status=canary_status,
            evidence=canary_evidence,
        ),
    ]


def _pre_release_evidence_findings(report: RiskReport) -> list[RiskFinding]:
    if report.decision == "block":
        return [
            RiskFinding(
                rule_id="pre-release-blocked",
                severity="critical",
                points=30,
                message="Release was already blocked before post-deploy evidence was attached.",
                evidence=[f"pre_release_score={report.score}"],
            )
        ]
    if report.decision == "manual_review":
        return [
            RiskFinding(
                rule_id="pre-release-manual-review",
                severity="medium",
                points=10,
                message="Release entered deploy evidence review with manual-review risk.",
                evidence=[f"pre_release_score={report.score}"],
            )
        ]
    return []


def _post_deploy_findings(evidence: PostDeployEvidence) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    if evidence.error_budget_burn_rate >= 8:
        findings.append(
            RiskFinding(
                rule_id="error-budget-burn",
                severity="critical",
                points=35,
                message="Post-deploy error budget burn rate is above rollback threshold.",
                evidence=[f"burn_rate={evidence.error_budget_burn_rate}"],
            )
        )
    if evidence.error_rate_percent >= max(2.0, evidence.baseline_error_rate_percent * 3):
        findings.append(
            RiskFinding(
                rule_id="error-rate-regression",
                severity="high",
                points=22,
                message="Post-deploy error rate regressed against baseline.",
                evidence=[
                    f"error_rate={evidence.error_rate_percent}",
                    f"baseline={evidence.baseline_error_rate_percent}",
                ],
            )
        )
    if evidence.baseline_p95_latency_ms and evidence.p95_latency_ms >= evidence.baseline_p95_latency_ms * 1.5:
        findings.append(
            RiskFinding(
                rule_id="latency-regression",
                severity="high",
                points=18,
                message="Post-deploy p95 latency regressed against baseline.",
                evidence=[
                    f"p95_ms={evidence.p95_latency_ms}",
                    f"baseline_p95_ms={evidence.baseline_p95_latency_ms}",
                ],
            )
        )
    if evidence.synthetic_checks_failed:
        findings.append(
            RiskFinding(
                rule_id="synthetic-check-failure",
                severity="high",
                points=min(25, evidence.synthetic_checks_failed * 10),
                message="Post-deploy synthetic checks failed.",
                evidence=[f"failed={evidence.synthetic_checks_failed}"],
            )
        )
    if evidence.rollback_events:
        findings.append(
            RiskFinding(
                rule_id="rollback-event",
                severity="critical",
                points=40,
                message="Rollback automation or manual rollback event was observed.",
                evidence=[f"rollback_events={evidence.rollback_events}"],
            )
        )
    if evidence.alerts_firing:
        findings.append(
            RiskFinding(
                rule_id="alerts-firing",
                severity="high",
                points=min(24, len(evidence.alerts_firing) * 8),
                message="Post-deploy production alerts are firing.",
                evidence=evidence.alerts_firing[:5],
            )
        )
    if evidence.canary_weight_percent < 100 and not evidence.release_owner_approved:
        findings.append(
            RiskFinding(
                rule_id="canary-promotion-unapproved",
                severity="medium",
                points=10,
                message="Canary has not reached full traffic and lacks release-owner approval.",
                evidence=[f"canary_weight_percent={evidence.canary_weight_percent}"],
            )
        )
    return findings


def _is_risky_path(path: str) -> bool:
    parts = [part.lower() for part in PurePosixPath(path).parts]
    joined = "/".join(parts)
    risky_terms = ("auth", "secret", "permission", "rbac", "config", "prod", "policy")
    return any(term in joined for term in risky_terms)


def _decision(score: int) -> str:
    if score >= 70:
        return "block"
    if score >= 35:
        return "manual_review"
    return "approve"


def _required_actions(
    decision: str, findings: list[RiskFinding], readiness_checks: list[ReadinessCheck]
) -> list[str]:
    if decision == "approve":
        return ["Proceed through the normal deployment path and monitor release metrics."]
    actions = ["Attach this report to the release ticket."]
    if any(finding.rule_id == "failed-tests" for finding in findings):
        actions.append("Fix or explicitly waive failing tests before deployment.")
    if any(finding.rule_id == "database-migration" for finding in findings):
        actions.append("Confirm migration rollback and backup plan.")
    if any(finding.rule_id == "missing-production-approval" for finding in findings):
        actions.append("Collect the required production approvals.")
    if any(check.status == "fail" for check in readiness_checks):
        actions.append("Complete failed deployment readiness checks before production rollout.")
    if decision == "block":
        actions.append("Do not deploy until critical findings are resolved or approved by release owner.")
    return actions


def _evidence_decision(report: RiskReport, evidence: PostDeployEvidence, score: int) -> str:
    if evidence.rollback_events or score >= 70:
        return "rollback"
    if report.decision == "block":
        return "rollback"
    if score >= 35:
        return "watch"
    return "promote"


def _evidence_actions(decision: str, findings: list[RiskFinding]) -> list[str]:
    if decision == "promote":
        return ["Promote the release and keep normal post-deploy monitoring active."]
    actions = ["Attach this evidence report to the release ticket."]
    if any(finding.rule_id == "error-budget-burn" for finding in findings):
        actions.append("Page the release owner and start rollback review.")
    if any(finding.rule_id == "rollback-event" for finding in findings):
        actions.append("Confirm rollback completion and open an incident follow-up.")
    if decision == "rollback":
        actions.append("Stop promotion and roll back or keep traffic pinned to the last healthy version.")
    else:
        actions.append("Hold promotion until the next evidence window is healthy.")
    return actions
