"""Tests for build_static_dashboard script."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml


def load_module():
    script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "build_static_dashboard.py"
    )
    spec = importlib.util.spec_from_file_location("build_static_dashboard", script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


build_static_dashboard = load_module()


def write_time_log(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=build_static_dashboard.TIME_LOG_FIELDS
        )
        writer.writeheader()
        writer.writerows(rows)


def write_review(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


def write_ci_history(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(record, sort_keys=True) for record in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_issue_pr_metrics(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def write_config(path: Path, show_numeric: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"dashboard": {"show_numeric_scoring": show_numeric}}
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")


def test_build_dashboard_with_data(tmp_path: Path) -> None:
    time_log = tmp_path / "logs" / "time" / "2025-01.csv"
    write_time_log(
        time_log,
        [
            {
                "date": "2025-01-02",
                "hours": "2.0",
                "repo": "Collab-Admin",
                "issue_or_pr": "PR-10",
                "category": "build",
                "description": "Work",
                "artifact_link": "https://github.com/org/repo/pull/10",
            },
            {
                "date": "2025-01-03",
                "hours": "1.5",
                "repo": "Collab-Admin",
                "issue_or_pr": "PR-11",
                "category": "review",
                "description": "Review",
                "artifact_link": "https://github.com/org/repo/pull/11",
            },
        ],
    )

    review_path = tmp_path / "reviews" / "2025-01" / "review.yml"
    write_review(
        review_path,
        {
            "workstream": "Instrumentation",
            "dimension_ratings": [
                {"dimension": "quality", "rating": "4"},
                {"dimension": "clarity", "rating": "3"},
            ],
        },
    )
    review_path_two = tmp_path / "reviews" / "2025-01" / "review-two.yml"
    write_review(
        review_path_two,
        {
            "workstream": "Ops",
            "dimension_ratings": [{"dimension": "quality", "rating": "Excellent"}],
        },
    )

    ci_history = tmp_path / "logs" / "ci" / "metrics-history.ndjson"
    write_ci_history(
        ci_history,
        [
            {"timestamp": "2025-01-01T00:00:00Z", "summary": {"tests": 10}},
            {
                "timestamp": "2025-01-02T00:00:00Z",
                "summary": {"tests": 10, "failures": 0, "errors": 0},
            },
            {
                "timestamp": "2025-01-03T00:00:00Z",
                "summary": {"tests": 10, "failures": 1, "errors": 0},
            },
        ],
    )

    issue_pr_path = tmp_path / "logs" / "issue_pr_metrics.json"
    write_issue_pr_metrics(
        issue_pr_path,
        {
            "issues": {
                "open": 2,
                "closed": 5,
                "recent_activity": [
                    {
                        "type": "Issue",
                        "number": 12,
                        "title": "Fix login",
                        "updated_at": "2025-01-01",
                    }
                ],
            },
            "pull_requests": {
                "open": 1,
                "closed": 3,
                "recent_activity": [
                    {
                        "type": "PR",
                        "number": 34,
                        "title": "Add feature",
                        "updated_at": "2025-01-02",
                    }
                ],
            },
        },
    )

    config_path = tmp_path / "config" / "dashboard_public.yml"
    write_config(config_path, show_numeric=False)

    dashboard = build_static_dashboard.build_dashboard(
        time_log_dir=time_log.parent,
        reviews_dir=review_path.parents[1],
        ci_history_path=ci_history,
        issue_pr_path=issue_pr_path,
        config_path=config_path,
        now=datetime(2025, 1, 5, 12, 0, 0, tzinfo=UTC),
        recent_ci_runs=3,
    )

    assert "## Time Tracking Summary" in dashboard
    assert "Total hours logged: 3.5" in dashboard
    assert "- Collab-Admin: 3.5" in dashboard
    assert "- build: 2" in dashboard
    assert "- review: 1.5" in dashboard
    assert "## Review Summary" in dashboard
    assert "Reviews logged: 2" in dashboard
    assert "Numeric ratings exist but are hidden by dashboard config." in dashboard
    assert "## Project Health Metrics" in dashboard
    assert "Issues: open 2 | closed 5" in dashboard
    assert "Pull requests: open 1 | closed 3" in dashboard
    assert "Issue #12 Fix login (2025-01-01)" in dashboard
    assert "PR #34 Add feature (2025-01-02)" in dashboard
    assert "Recent pass rate (last 3 runs): 66.67% (2/3)" in dashboard
    assert (
        "Latest run: 2025-01-03T00:00:00Z - failed (tests: 10, failures: 1, errors: 0)"
        in dashboard
    )


def test_build_dashboard_shows_numeric_average_when_enabled(tmp_path: Path) -> None:
    review_path = tmp_path / "reviews" / "2025-02" / "review.yml"
    write_review(
        review_path,
        {
            "workstream": "Instrumentation",
            "dimension_ratings": [{"dimension": "quality", "rating": 4}],
        },
    )
    config_path = tmp_path / "config" / "dashboard_public.yml"
    write_config(config_path, show_numeric=True)

    dashboard = build_static_dashboard.build_dashboard(
        time_log_dir=tmp_path / "logs" / "time",
        reviews_dir=review_path.parents[1],
        ci_history_path=tmp_path / "logs" / "ci" / "metrics-history.ndjson",
        issue_pr_path=tmp_path / "logs" / "issue_pr_metrics.json",
        config_path=config_path,
        now=datetime(2025, 2, 1, 12, 0, 0, tzinfo=UTC),
        recent_ci_runs=3,
    )

    assert "Average rating (numeric): 4" in dashboard


def test_build_dashboard_handles_missing_data(tmp_path: Path) -> None:
    dashboard = build_static_dashboard.build_dashboard(
        time_log_dir=tmp_path / "logs" / "time",
        reviews_dir=tmp_path / "reviews",
        ci_history_path=tmp_path / "logs" / "ci" / "metrics-history.ndjson",
        issue_pr_path=tmp_path / "logs" / "issue_pr_metrics.json",
        config_path=tmp_path / "config" / "dashboard_public.yml",
        now=datetime(2025, 3, 1, 12, 0, 0, tzinfo=UTC),
        recent_ci_runs=3,
    )

    assert "No time logs found." in dashboard
    assert "No reviews found." in dashboard
    assert "No issue/PR metrics available." in dashboard
    assert "No CI history available." in dashboard
