"""Tests for config validation script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run_validator(
    project_path: Path, dashboard_path: Path
) -> subprocess.CompletedProcess[str]:
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


def _run_single_file_validator(
    file_path: Path, config_type: str
) -> subprocess.CompletedProcess[str]:
    """Run validator in single-file mode with --type argument."""
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "validate_config.py"
    command = [
        sys.executable,
        str(script_path),
        str(file_path),
        "--type",
        config_type,
    ]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def _run_validator_raw(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run validator with raw arguments."""
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "validate_config.py"
    command = [sys.executable, str(script_path)] + args
    return subprocess.run(command, capture_output=True, text=True, check=False)


def _write_project(path: Path, proposal_date: str = "2025-01-01") -> None:
    path.write_text(
        "\n".join(
            [
                "project:",
                '  name: "Demo"',
                f'  proposal_version_date: "{proposal_date}"',
                "  automation_ecosystem:",
                '    workflows_repo: "org/Workflows"',
                '    integration_tests_repo: "org/Workflows-Integration-Tests"',
                '    reference_consumer_repo: "org/Ref"',
                '    template_repo: "org/Template"',
                "  constraints:",
                "    hours_per_week_cap: 40",
                "    no_banking: true",
                "    forks_only_month_1: true",
                "    trend_no_ai_assistance: false",
                "  workstreams:",
                "    - id: ws1",
                '      name: "Stream"',
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
    assert "Config validation passed" in result.stdout


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
    _write_dashboard(dashboard_path, numeric='"yes"')

    result = _run_validator(project_path, dashboard_path)

    assert result.returncode != 0
    assert "dashboard.show_numeric_scoring must be a boolean" in (
        result.stderr + result.stdout
    )


# Tests for single-file validation mode (--type argument)


def test_single_file_project_ok(tmp_path: Path) -> None:
    """Single-file mode validates a project config correctly."""
    project_path = tmp_path / "project.yml"
    _write_project(project_path)

    result = _run_single_file_validator(project_path, "project")

    assert result.returncode == 0
    assert "Config validation passed" in result.stdout


def test_single_file_dashboard_ok(tmp_path: Path) -> None:
    """Single-file mode validates a dashboard config correctly."""
    dashboard_path = tmp_path / "dashboard.yml"
    _write_dashboard(dashboard_path)

    result = _run_single_file_validator(dashboard_path, "dashboard")

    assert result.returncode == 0
    assert "Config validation passed" in result.stdout


def test_single_file_project_rejects_invalid(tmp_path: Path) -> None:
    """Single-file mode rejects invalid project config."""
    project_path = tmp_path / "project.yml"
    project_path.write_text("project:\n  name: demo\n", encoding="utf-8")

    result = _run_single_file_validator(project_path, "project")

    assert result.returncode != 0
    assert "missing required project fields" in (result.stderr + result.stdout)


def test_single_file_nonexistent_file(tmp_path: Path) -> None:
    """Single-file mode reports error for nonexistent file."""
    missing_path = tmp_path / "nonexistent.yml"

    result = _run_single_file_validator(missing_path, "project")

    assert result.returncode != 0
    assert "does not exist" in (result.stderr + result.stdout)


def test_type_without_file_fails() -> None:
    """Providing --type without a file argument fails."""
    result = _run_validator_raw(["--type", "project"])

    assert result.returncode != 0
    assert "file argument is required" in (result.stderr + result.stdout)


def test_file_without_type_fails(tmp_path: Path) -> None:
    """Providing a file without --type fails."""
    project_path = tmp_path / "project.yml"
    _write_project(project_path)

    result = _run_validator_raw([str(project_path)])

    assert result.returncode != 0
    assert "--type is required" in (result.stderr + result.stdout)
