"""Tests for PR submission packet validation."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run_validator(body: str, repo_root: Path) -> subprocess.CompletedProcess[str]:
    repo_base = Path(__file__).resolve().parents[2]
    script_path = repo_base / "scripts" / "validate_submission_packet_pr.py"
    command = [
        sys.executable,
        str(script_path),
        "--repo-root",
        str(repo_root),
        "--body",
        body,
    ]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def test_validate_pr_body_packet_ok(tmp_path: Path) -> None:
    body = "\n".join(
        [
            "# PR Title",
            "",
            "## Submission Packet",
            "- Issue: #42",
            "- Workstream: Admin",
            "- Deliverables included (links/paths): scripts/validate_submission_packet.py",
            '- How to run/test: pytest tests/scripts/test_validate_submission_packet.py -m "not slow"',
            "- Evidence: logs/run.txt",
        ]
    )

    result = _run_validator(body, tmp_path)

    assert result.returncode == 0
    assert "OK" in result.stdout


def test_validate_pr_body_linked_packet_ok(tmp_path: Path) -> None:
    packet = tmp_path / "submission_packet.md"
    packet.write_text(
        "\n".join(
            [
                "# Submission Packet",
                "- Issue: #99",
                "- Workstream: Infra",
                "- Deliverables: templates/submission_packet.md",
                '- How to run/test: pytest tests/scripts/test_validate_submission_packet.py -m "not slow"',
                "- Evidence: logs/ci.txt",
            ]
        ),
        encoding="utf-8",
    )
    body = "Submission packet: [packet](submission_packet.md)"

    result = _run_validator(body, tmp_path)

    assert result.returncode == 0
    assert "OK" in result.stdout


def test_validate_pr_body_linked_packet_missing_sections(tmp_path: Path) -> None:
    packet = tmp_path / "submission_packet.md"
    packet.write_text(
        "\n".join(
            [
                "# Submission Packet",
                "- Issue: #",
                "- Workstream: Admin",
                "- Deliverables: templates/submission_packet.md",
                '- How to run/test: pytest tests/scripts/test_validate_submission_packet.py -m "not slow"',
            ]
        ),
        encoding="utf-8",
    )
    body = "Submission packet: [packet](submission_packet.md)"

    result = _run_validator(body, tmp_path)

    assert result.returncode != 0
    combined = result.stderr + result.stdout
    assert "Issue is missing a value" in combined
    assert "missing required section: Evidence" in combined
