"""Tests for validate_time_log script."""

from __future__ import annotations

import csv
import importlib.util
from datetime import date, timedelta
from pathlib import Path

import pytest


def load_module():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "validate_time_log.py"
    spec = importlib.util.spec_from_file_location("validate_time_log", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validate_time_log = load_module()


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=validate_time_log.REQUIRED)
        writer.writeheader()
        writer.writerows(rows)


def base_row(row_date: str | None = None) -> dict[str, str]:
    if row_date is None:
        row_date = (date.today() - timedelta(days=7)).isoformat()
    return {
        "date": row_date,
        "hours": "2.5",
        "repo": "Collab-Admin",
        "issue_or_pr": "PR-123",
        "category": "feature",
        "description": "Implement validation",
        "artifact_link": "https://github.com/org/repo/pull/123",
    }


def test_valid_log_passes(tmp_path: Path) -> None:
    path = tmp_path / "log.csv"
    write_csv(path, [base_row("2024-01-08")])

    errors = validate_time_log.validate_time_log(path, today=date(2024, 1, 10))

    assert errors == []


def test_invalid_category_fails(tmp_path: Path) -> None:
    path = tmp_path / "log.csv"
    row = base_row("2024-01-08")
    row["category"] = "ops"
    write_csv(path, [row])

    errors = validate_time_log.validate_time_log(path, today=date(2024, 1, 10))

    assert any("Invalid category" in err for err in errors)


def test_invalid_artifact_link_fails(tmp_path: Path) -> None:
    path = tmp_path / "log.csv"
    row = base_row("2024-01-08")
    row["artifact_link"] = "https://example.com/not-github"
    write_csv(path, [row])

    errors = validate_time_log.validate_time_log(path, today=date(2024, 1, 10))

    assert any("Invalid artifact_link" in err for err in errors)


def test_invalid_date_format_fails(tmp_path: Path) -> None:
    path = tmp_path / "log.csv"
    row = base_row("2024-01-08")
    row["date"] = "2024/01/08"
    write_csv(path, [row])

    errors = validate_time_log.validate_time_log(path, today=date(2024, 1, 10))

    assert any("Invalid date" in err for err in errors)


def test_date_range_checks(tmp_path: Path) -> None:
    path = tmp_path / "log.csv"
    today = date(2024, 1, 10)
    row_future = base_row("2024-01-08")
    row_future["date"] = "2024-01-12"
    row_old = base_row("2024-01-08")
    too_old = today - timedelta(days=validate_time_log.MAX_PAST_DAYS + 1)
    row_old["date"] = too_old.strftime(validate_time_log.DATE_FORMAT)
    write_csv(path, [row_future, row_old])

    errors = validate_time_log.validate_time_log(path, today=today)

    assert any("future" in err for err in errors)
    assert any("too old" in err for err in errors)


def test_verbose_output_in_main(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "log.csv"
    write_csv(path, [base_row()])

    validate_time_log.main(["--verbose", str(path)])
    out = capsys.readouterr().out

    assert "Row 2: OK" in out
    assert "OK" in out


def test_src_smoke() -> None:
    from my_project import __version__, add, greet

    assert __version__ == "0.1.0"
    assert greet("Team") == "Hello, Team!"
    assert add(1, 2) == 3
