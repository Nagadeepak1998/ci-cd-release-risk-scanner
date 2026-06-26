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
        text=True,
    )

    assert result.returncode == 2
    assert "block: checkout-api" in result.stdout
    assert output.exists()
