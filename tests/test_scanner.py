from pathlib import Path

from release_risk_scanner.io import (
    load_change_advisory_review,
    load_context,
    load_evidence_bundle,
    load_supply_chain_review,
)
from release_risk_scanner.scanner import (
    evaluate_change_advisory,
    evaluate_release_evidence,
    evaluate_supply_chain,
    render_markdown,
    scan_release,
)


def test_risky_release_blocks_deploy() -> None:
    report = scan_release(load_context(Path("tests/fixtures/risky_release.json")))

    assert report.decision == "block"
    assert report.score == 100
    assert any(finding.rule_id == "failed-tests" for finding in report.findings)
    assert any(finding.rule_id == "missing-rollback-plan" for finding in report.findings)
    assert any(finding.rule_id == "off-hours-without-canary" for finding in report.findings)
    assert any(check.status == "fail" for check in report.readiness_checks)
    assert any("Do not deploy" in action for action in report.required_actions)


def test_safe_release_approves_deploy() -> None:
    report = scan_release(load_context(Path("tests/fixtures/safe_release.json")))

    assert report.decision == "approve"
    assert report.score == 0
    assert len(report.findings) == 0
    assert all(check.status == "pass" for check in report.readiness_checks)


def test_markdown_report_contains_gate_context() -> None:
    report = scan_release(load_context(Path("tests/fixtures/risky_release.json")))
    markdown = render_markdown(report)

    assert "# Release Risk Report: checkout-api" in markdown
    assert "Decision: `block`" in markdown
    assert "## Deployment Readiness" in markdown
    assert "rollback_plan" in markdown
    assert "failed-tests" in markdown


def test_healthy_evidence_promotes_release() -> None:
    report = evaluate_release_evidence(load_evidence_bundle(Path("tests/fixtures/healthy_evidence.json")))

    assert report.decision == "promote"
    assert report.evidence_score == 0


def test_rollback_evidence_stops_release() -> None:
    report = evaluate_release_evidence(load_evidence_bundle(Path("tests/fixtures/rollback_evidence.json")))

    assert report.decision == "rollback"
    assert report.evidence_score == 100
    assert any(finding.rule_id == "error-budget-burn" for finding in report.findings)


def test_evidence_markdown_contains_post_deploy_decision() -> None:
    report = evaluate_release_evidence(load_evidence_bundle(Path("tests/fixtures/rollback_evidence.json")))
    markdown = render_markdown(report)

    assert "# Release Evidence Report: checkout-api" in markdown
    assert "Decision: `rollback`" in markdown
    assert "error-budget-burn" in markdown


def test_verified_supply_chain_approves_artifact() -> None:
    review = load_supply_chain_review(Path("tests/fixtures/supply_chain_safe.json"))
    report = evaluate_supply_chain(review)

    assert report.decision == "approve"
    assert report.score == 0


def test_unsafe_supply_chain_blocks_artifact() -> None:
    review = load_supply_chain_review(Path("tests/fixtures/supply_chain_blocked.json"))
    report = evaluate_supply_chain(review)

    assert report.decision == "block"
    assert report.score == 100
    assert any(finding.rule_id == "unverified-signature" for finding in report.findings)
    assert any(finding.rule_id == "critical-vulnerabilities" for finding in report.findings)
    assert "# Supply Chain Review: checkout-api" in render_markdown(report)


def test_safe_change_advisory_approves_change() -> None:
    review = load_change_advisory_review(Path("tests/fixtures/change_advisory_safe.json"))
    report = evaluate_change_advisory(review)

    assert report.decision == "approve"
    assert report.score == 0


def test_blocked_change_advisory_stops_freeze_window_release() -> None:
    review = load_change_advisory_review(Path("tests/fixtures/change_advisory_blocked.json"))
    report = evaluate_change_advisory(review)

    assert report.decision == "block"
    assert report.score == 100
    assert any(finding.rule_id == "freeze-window-active" for finding in report.findings)
    assert any(finding.rule_id == "missing-support-coverage" for finding in report.findings)
    assert "# Change Advisory Review: checkout-api" in render_markdown(report)
