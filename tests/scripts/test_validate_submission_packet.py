"""Tests for submission packet validation script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run_validator(path: Path | None, markdown: str | None = None) -> subprocess.CompletedProcess[str]:
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "validate_submission_packet.py"
    if markdown is None:
        command = [sys.executable, str(script_path), str(path)]
        return subprocess.run(command, capture_output=True, text=True, check=False)
    command = [sys.executable, str(script_path), "--stdin"]
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        input=markdown,
    )


def test_validate_submission_packet_ok(tmp_path: Path) -> None:
    packet = tmp_path / "submission_packet.md"
    packet.write_text(
        "\n".join(
            [
                "# Submission Packet",
                "- Issue: #123",
                "- Workstream: Core",
                "- Deliverables included (links/paths): scripts/validate_submission_packet.py",
                "- How to run/test (commands + expected result): pytest tests/ -m \"not slow\"",
                "- Evidence (links to CI runs, logs, screenshots as needed): logs/run.txt",
            ]
        ),
        encoding="utf-8",
    )

    result = _run_validator(packet)

    assert result.returncode == 0
    assert "OK" in result.stdout


def test_validate_submission_packet_missing_sections(tmp_path: Path) -> None:
    packet = tmp_path / "submission_packet.md"
    packet.write_text(
        "\n".join(
            [
                "# Submission Packet",
                "- Issue: #",
                "- Workstream: Core",
                "- Deliverables included (links/paths): scripts/validate_submission_packet.py",
                "- How to run/test (commands + expected result): pytest tests/ -m \"not slow\"",
            ]
        ),
        encoding="utf-8",
    )

    result = _run_validator(packet)

    assert result.returncode != 0
    combined = result.stderr + result.stdout
    assert "Issue is missing a value" in combined
    assert "missing required section: Evidence" in combined


def test_validate_submission_packet_stdin() -> None:
    markdown = "\n".join(
        [
            "- Issue: #77",
            "- Workstream: Ops",
            "- Deliverables: templates/submission_packet.md",
            "- How to run/test: pytest tests/scripts/test_validate_submission_packet.py -m \"not slow\"",
            "- Evidence: screenshots/ci.png",
        ]
    )

    result = _run_validator(None, markdown)

    assert result.returncode == 0
    assert "OK" in result.stdout
