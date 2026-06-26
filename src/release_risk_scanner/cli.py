from __future__ import annotations

import argparse
from pathlib import Path

from release_risk_scanner.io import load_context, write_report
from release_risk_scanner.scanner import scan_release


def main() -> int:
    parser = argparse.ArgumentParser(description="Score CI/CD release risk from deployment evidence.")
    parser.add_argument("context", type=Path, help="Release context JSON")
    parser.add_argument("--output", type=Path, default=Path("reports/release-risk.json"))
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--fail-on", choices=["manual_review", "block"], default="block")
    args = parser.parse_args()

    report = scan_release(load_context(args.context))
    write_report(args.output, report, args.format)
    print(f"{report.decision}: {report.service} score={report.score} findings={len(report.findings)}")

    if args.fail_on == "manual_review" and report.decision in {"manual_review", "block"}:
        return 2
    if args.fail_on == "block" and report.decision == "block":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

