"""Tests for rubric validation script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run_validator(rubrics_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "validate_rubrics.py"
    command = [sys.executable, str(script_path), str(rubrics_dir), *args]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def test_validate_rubrics_ok(tmp_path: Path) -> None:
    rubrics_dir = tmp_path / "rubrics"
    rubrics_dir.mkdir()

    (rubrics_dir / "sample.yml").write_text(
        "\n".join(
            [
                "rubric_id: sample",
                "title: Sample Rubric",
                "levels: [Poor, Good]",
                "dimensions:",
                "  - id: scope",
                "    name: Scope",
                "    descriptors:",
                "      Poor: Missing scope",
                "      Good: Adequate scope",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (rubrics_dir / "rubric_index.yml").write_text(
        "rubrics:\n  - sample.yml\n", encoding="utf-8"
    )

    result = _run_validator(rubrics_dir, "--check-structure")

    assert result.returncode == 0
    assert "OK" in result.stdout


def test_validate_rubrics_rejects_invalid_yaml(tmp_path: Path) -> None:
    rubrics_dir = tmp_path / "rubrics"
    rubrics_dir.mkdir()
    (rubrics_dir / "bad.yml").write_text("rubric_id: [unclosed\n", encoding="utf-8")

    result = _run_validator(rubrics_dir)

    assert result.returncode != 0
    assert "bad.yml" in (result.stderr + result.stdout)


def test_validate_rubrics_missing_required_fields(tmp_path: Path) -> None:
    rubrics_dir = tmp_path / "rubrics"
    rubrics_dir.mkdir()
    (rubrics_dir / "missing.yml").write_text(
        "\n".join(
            [
                "rubric_id: missing",
                "levels: [Poor, Good]",
                "dimensions: []",
            ]
        ),
        encoding="utf-8",
    )

    result = _run_validator(rubrics_dir, "--check-structure")

    assert result.returncode != 0
    assert "missing required fields" in (result.stderr + result.stdout)
