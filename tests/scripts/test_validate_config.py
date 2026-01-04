"""Tests for config validation script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run_validator(project_path: Path, dashboard_path: Path) -> subprocess.CompletedProcess[str]:
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "validate_config.py"
    command = [
        sys.executable,
        str(script_path),
        "--project-path",
        str(project_path),
        "--dashboard-path",
        str(dashboard_path),
    ]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def _write_project(path: Path, proposal_date: str = "2025-01-01") -> None:
    path.write_text(
        "\n".join(
            [
                "project:",
                "  name: \"Demo\"",
                f"  proposal_version_date: \"{proposal_date}\"",
                "  automation_ecosystem:",
                "    workflows_repo: \"org/Workflows\"",
                "    integration_tests_repo: \"org/Workflows-Integration-Tests\"",
                "    reference_consumer_repo: \"org/Ref\"",
                "    template_repo: \"org/Template\"",
                "  constraints:",
                "    hours_per_week_cap: 40",
                "    no_banking: true",
                "    forks_only_month_1: true",
                "    trend_no_ai_assistance: false",
                "  workstreams:",
                "    - id: ws1",
                "      name: \"Stream\"",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_dashboard(path: Path, numeric: str = "false") -> None:
    path.write_text(
        "\n".join(
            [
                "dashboard:",
                "  mode: public",
                f"  show_numeric_scoring: {numeric}",
                "  show_level_counts: true",
                "  show_level_distributions: true",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_validate_config_ok(tmp_path: Path) -> None:
    project_path = tmp_path / "project.yml"
    dashboard_path = tmp_path / "dashboard.yml"
    _write_project(project_path)
    _write_dashboard(dashboard_path)

    result = _run_validator(project_path, dashboard_path)

    assert result.returncode == 0
    assert "OK" in result.stdout


def test_validate_config_missing_required_fields(tmp_path: Path) -> None:
    project_path = tmp_path / "project.yml"
    dashboard_path = tmp_path / "dashboard.yml"
    project_path.write_text("project:\n  name: demo\n", encoding="utf-8")
    _write_dashboard(dashboard_path)

    result = _run_validator(project_path, dashboard_path)

    assert result.returncode != 0
    assert "missing required project fields" in (result.stderr + result.stdout)


def test_validate_config_rejects_invalid_date(tmp_path: Path) -> None:
    project_path = tmp_path / "project.yml"
    dashboard_path = tmp_path / "dashboard.yml"
    _write_project(project_path, proposal_date="2025-13-99")
    _write_dashboard(dashboard_path)

    result = _run_validator(project_path, dashboard_path)

    assert result.returncode != 0
    assert "proposal_version_date" in (result.stderr + result.stdout)


def test_validate_config_rejects_invalid_dashboard_types(tmp_path: Path) -> None:
    project_path = tmp_path / "project.yml"
    dashboard_path = tmp_path / "dashboard.yml"
    _write_project(project_path)
    _write_dashboard(dashboard_path, numeric="\"yes\"")

    result = _run_validator(project_path, dashboard_path)

    assert result.returncode != 0
    assert "dashboard.show_numeric_scoring must be a boolean" in (
        result.stderr + result.stdout
    )
