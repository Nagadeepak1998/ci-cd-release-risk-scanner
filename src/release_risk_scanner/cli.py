from __future__ import annotations

import argparse
from pathlib import Path

from release_risk_scanner.io import load_context, load_evidence_bundle, write_report
from release_risk_scanner.scanner import evaluate_release_evidence, scan_release


def main() -> int:
    parser = argparse.ArgumentParser(description="Score CI/CD release risk from deployment evidence.")
    parser.add_argument("context", type=Path, nargs="?", help="Release context JSON")
    parser.add_argument("--evidence", type=Path, help="Release plus post-deploy evidence JSON")
    parser.add_argument("--output", type=Path, default=Path("reports/release-risk.json"))
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument(
        "--fail-on",
        choices=["manual_review", "block", "watch", "rollback"],
        default="block",
    )
    args = parser.parse_args()

    if args.evidence:
        report = evaluate_release_evidence(load_evidence_bundle(args.evidence))
    else:
        if args.context is None:
            parser.error("context is required unless --evidence is provided")
        report = scan_release(load_context(args.context))
    write_report(args.output, report, args.format)
    score = report.score if hasattr(report, "score") else report.evidence_score
    print(f"{report.decision}: {report.service} score={score} findings={len(report.findings)}")

    if args.fail_on == "manual_review" and report.decision in {"manual_review", "block"}:
        return 2
    if args.fail_on == "block" and report.decision == "block":
        return 2
    if args.fail_on == "watch" and report.decision in {"watch", "rollback"}:
        return 2
    if args.fail_on == "rollback" and report.decision == "rollback":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
