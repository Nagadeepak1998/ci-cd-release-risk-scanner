import os
import subprocess
import sys
from pathlib import Path


def test_cli_writes_report_and_blocks(tmp_path: Path) -> None:
    output = tmp_path / "risk.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "release_risk_scanner.cli",
            "tests/fixtures/risky_release.json",
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        env={**os.environ, "PYTHONPATH": "src"},
        text=True,
    )

    assert result.returncode == 2
    assert "block: checkout-api" in result.stdout
    assert output.exists()


def test_cli_writes_evidence_report_and_rolls_back(tmp_path: Path) -> None:
    output = tmp_path / "evidence.md"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "release_risk_scanner.cli",
            "--evidence",
            "tests/fixtures/rollback_evidence.json",
            "--format",
            "markdown",
            "--output",
            str(output),
            "--fail-on",
            "rollback",
        ],
        check=False,
        capture_output=True,
        env={**os.environ, "PYTHONPATH": "src"},
        text=True,
    )

    assert result.returncode == 2
    assert "rollback: checkout-api" in result.stdout
    assert "Release Evidence Report" in output.read_text()


def test_cli_writes_supply_chain_report_and_blocks(tmp_path: Path) -> None:
    output = tmp_path / "supply-chain.md"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "release_risk_scanner.cli",
            "--supply-chain",
            "tests/fixtures/supply_chain_blocked.json",
            "--format",
            "markdown",
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        env={**os.environ, "PYTHONPATH": "src"},
        text=True,
    )

    assert result.returncode == 2
    assert "block: checkout-api" in result.stdout
    assert "Supply Chain Review" in output.read_text()
