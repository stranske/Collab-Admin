"""Tests for validate_friction_log script."""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


def load_module():
    script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "validate_friction_log.py"
    )
    spec = importlib.util.spec_from_file_location("validate_friction_log", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validate_friction_log = load_module()


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=validate_friction_log.REQUIRED)
        writer.writeheader()
        writer.writerows(rows)


def base_row() -> dict[str, str]:
    return {
        "date": "2024-01-08",
        "repo": "Collab-Admin",
        "context": "build",
        "minutes_lost": "45",
        "what_broke": "Broken link",
        "what_was_confusing": "Unclear steps",
        "what_fixed_it": "Updated docs",
        "pr_or_issue": "PR-456",
    }


def test_valid_log_passes(tmp_path: Path) -> None:
    path = tmp_path / "friction.csv"
    write_csv(path, [base_row()])

    errors = validate_friction_log.validate_friction_log(str(path))

    assert errors == []


def test_missing_columns_fails(tmp_path: Path) -> None:
    path = tmp_path / "friction.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "repo", "minutes_lost"])
        writer.writerow(["2024-01-08", "Collab-Admin", "15"])

    errors = validate_friction_log.validate_friction_log(str(path))

    assert any("Missing columns" in err for err in errors)


def test_invalid_date_format_fails(tmp_path: Path) -> None:
    path = tmp_path / "friction.csv"
    row = base_row()
    row["date"] = "2024/01/08"
    write_csv(path, [row])

    errors = validate_friction_log.validate_friction_log(str(path))

    assert any("Invalid date" in err for err in errors)


def test_invalid_minutes_lost_fails(tmp_path: Path) -> None:
    path = tmp_path / "friction.csv"
    row = base_row()
    row["minutes_lost"] = "forty"
    write_csv(path, [row])

    errors = validate_friction_log.validate_friction_log(str(path))

    assert any("Invalid minutes_lost" in err for err in errors)


def test_missing_required_value_fails(tmp_path: Path) -> None:
    path = tmp_path / "friction.csv"
    row = base_row()
    row["what_fixed_it"] = ""
    write_csv(path, [row])

    errors = validate_friction_log.validate_friction_log(str(path))

    assert any("Missing value for 'what_fixed_it'" in err for err in errors)
