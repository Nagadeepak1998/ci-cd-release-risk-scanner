from __future__ import annotations

from pathlib import PurePosixPath

from release_risk_scanner.models import DeployContext, RiskFinding, RiskReport


def scan_release(context: DeployContext) -> RiskReport:
    findings = [
        *_test_findings(context),
        *_change_findings(context),
        *_operational_findings(context),
        *_approval_findings(context),
    ]
    score = min(100, sum(finding.points for finding in findings))
    decision = _decision(score)
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
        required_actions=_required_actions(decision, findings),
    )


def render_markdown(report: RiskReport) -> str:
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


def _required_actions(decision: str, findings: list[RiskFinding]) -> list[str]:
    if decision == "approve":
        return ["Proceed through the normal deployment path and monitor release metrics."]
    actions = ["Attach this report to the release ticket."]
    if any(finding.rule_id == "failed-tests" for finding in findings):
        actions.append("Fix or explicitly waive failing tests before deployment.")
    if any(finding.rule_id == "database-migration" for finding in findings):
        actions.append("Confirm migration rollback and backup plan.")
    if any(finding.rule_id == "missing-production-approval" for finding in findings):
        actions.append("Collect the required production approvals.")
    if decision == "block":
        actions.append("Do not deploy until critical findings are resolved or approved by release owner.")
    return actions

