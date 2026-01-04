"""Validate core configuration YAML files for required fields and types."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import yaml

PROJECT_REQUIRED_FIELDS = (
    "name",
    "proposal_version_date",
    "automation_ecosystem",
    "constraints",
    "workstreams",
)
AUTOMATION_REQUIRED_FIELDS = (
    "workflows_repo",
    "integration_tests_repo",
    "reference_consumer_repo",
    "template_repo",
)
CONSTRAINT_BOOL_FIELDS = (
    "no_banking",
    "forks_only_month_1",
    "trend_no_ai_assistance",
)
CONSTRAINT_INT_FIELDS = ("hours_per_week_cap",)
WORKSTREAM_REQUIRED_FIELDS = ("id", "name")
DASHBOARD_REQUIRED_FIELDS = (
    "mode",
    "show_numeric_scoring",
    "show_level_counts",
    "show_level_distributions",
)


def _load_yaml(path: Path) -> tuple[object | None, str | None]:
    try:
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as exc:
        return None, f"{path}: YAML parse error: {exc}"
    return data, None


def _validate_non_empty_str(path: Path, key_path: str, value: object) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return [f"{path}: {key_path} must be a non-empty string."]
    return []


def _validate_project(path: Path, data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{path}: expected a mapping at the document root."]

    project = data.get("project")
    if not isinstance(project, dict):
        return [f"{path}: project must be a mapping."]

    missing = [field for field in PROJECT_REQUIRED_FIELDS if field not in project]
    if missing:
        errors.append(f"{path}: missing required project fields: {', '.join(missing)}.")
        return errors

    errors.extend(_validate_non_empty_str(path, "project.name", project["name"]))

    proposal_date = project.get("proposal_version_date")
    if not isinstance(proposal_date, str) or not proposal_date.strip():
        errors.append(
            f"{path}: project.proposal_version_date must be a non-empty string."
        )
    else:
        try:
            date.fromisoformat(proposal_date)
        except ValueError:
            errors.append(
                f"{path}: project.proposal_version_date must be YYYY-MM-DD format."
            )

    automation = project.get("automation_ecosystem")
    if not isinstance(automation, dict):
        errors.append(f"{path}: project.automation_ecosystem must be a mapping.")
    else:
        missing = [
            field for field in AUTOMATION_REQUIRED_FIELDS if field not in automation
        ]
        if missing:
            errors.append(
                f"{path}: project.automation_ecosystem missing fields: {', '.join(missing)}."
            )
        for field in AUTOMATION_REQUIRED_FIELDS:
            if field in automation:
                errors.extend(
                    _validate_non_empty_str(
                        path, f"project.automation_ecosystem.{field}", automation[field]
                    )
                )

    constraints = project.get("constraints")
    if not isinstance(constraints, dict):
        errors.append(f"{path}: project.constraints must be a mapping.")
    else:
        missing = [
            field
            for field in (*CONSTRAINT_BOOL_FIELDS, *CONSTRAINT_INT_FIELDS)
            if field not in constraints
        ]
        if missing:
            errors.append(
                f"{path}: project.constraints missing fields: {', '.join(missing)}."
            )
        for field in CONSTRAINT_BOOL_FIELDS:
            if field in constraints and not isinstance(constraints[field], bool):
                errors.append(f"{path}: project.constraints.{field} must be a boolean.")
        for field in CONSTRAINT_INT_FIELDS:
            if field in constraints:
                value = constraints[field]
                if not isinstance(value, int) or value <= 0:
                    errors.append(
                        f"{path}: project.constraints.{field} must be a positive integer."
                    )

    workstreams = project.get("workstreams")
    if not isinstance(workstreams, list) or not workstreams:
        errors.append(f"{path}: project.workstreams must be a non-empty list.")
    else:
        for idx, stream in enumerate(workstreams, start=1):
            if not isinstance(stream, dict):
                errors.append(f"{path}: project.workstreams[{idx}] must be a mapping.")
                continue
            missing = [
                field for field in WORKSTREAM_REQUIRED_FIELDS if field not in stream
            ]
            if missing:
                errors.append(
                    f"{path}: project.workstreams[{idx}] missing fields: {', '.join(missing)}."
                )
                continue
            errors.extend(
                _validate_non_empty_str(
                    path, f"project.workstreams[{idx}].id", stream["id"]
                )
            )
            errors.extend(
                _validate_non_empty_str(
                    path, f"project.workstreams[{idx}].name", stream["name"]
                )
            )

    return errors


def _validate_dashboard(path: Path, data: object) -> list[str]:
    if not isinstance(data, dict):
        return [f"{path}: expected a mapping at the document root."]

    dashboard = data.get("dashboard")
    if not isinstance(dashboard, dict):
        return [f"{path}: dashboard must be a mapping."]

    missing = [field for field in DASHBOARD_REQUIRED_FIELDS if field not in dashboard]
    if missing:
        return [f"{path}: missing required dashboard fields: {', '.join(missing)}."]

    errors: list[str] = []
    errors.extend(_validate_non_empty_str(path, "dashboard.mode", dashboard["mode"]))
    for field in DASHBOARD_REQUIRED_FIELDS:
        if field == "mode":
            continue
        if not isinstance(dashboard[field], bool):
            errors.append(f"{path}: dashboard.{field} must be a boolean.")

    return errors


def validate_configs(project_path: Path, dashboard_path: Path) -> list[str]:
    errors: list[str] = []
    if not project_path.exists():
        errors.append(f"{project_path}: file does not exist.")
    if not dashboard_path.exists():
        errors.append(f"{dashboard_path}: file does not exist.")
    if errors:
        return errors

    project_data, project_error = _load_yaml(project_path)
    if project_error:
        errors.append(project_error)
    else:
        errors.extend(_validate_project(project_path, project_data))

    dashboard_data, dashboard_error = _load_yaml(dashboard_path)
    if dashboard_error:
        errors.append(dashboard_error)
    else:
        errors.extend(_validate_dashboard(dashboard_path, dashboard_data))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate configuration YAML files.")
    parser.add_argument(
        "--project-path",
        default="config/project.yml",
        help="Path to the project config (default: config/project.yml).",
    )
    parser.add_argument(
        "--dashboard-path",
        default="config/dashboard_public.yml",
        help="Path to the dashboard config (default: config/dashboard_public.yml).",
    )
    args = parser.parse_args(argv)

    errors = validate_configs(Path(args.project_path), Path(args.dashboard_path))
    if errors:
        message = "Config validation failed:\n" + "\n".join(
            f"- {error}" for error in errors
        )
        raise SystemExit(message)

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
