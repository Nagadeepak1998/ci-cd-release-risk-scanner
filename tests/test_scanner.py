from pathlib import Path

from release_risk_scanner.io import load_context
from release_risk_scanner.scanner import render_markdown, scan_release


def test_risky_release_blocks_deploy() -> None:
    report = scan_release(load_context(Path("tests/fixtures/risky_release.json")))

    assert report.decision == "block"
    assert report.score == 100
    assert any(finding.rule_id == "failed-tests" for finding in report.findings)
    assert any("Do not deploy" in action for action in report.required_actions)


def test_safe_release_approves_deploy() -> None:
    report = scan_release(load_context(Path("tests/fixtures/safe_release.json")))

    assert report.decision == "approve"
    assert report.score == 0
    assert len(report.findings) == 0


def test_markdown_report_contains_gate_context() -> None:
    report = scan_release(load_context(Path("tests/fixtures/risky_release.json")))
    markdown = render_markdown(report)

    assert "# Release Risk Report: checkout-api" in markdown
    assert "Decision: `block`" in markdown
    assert "failed-tests" in markdown

