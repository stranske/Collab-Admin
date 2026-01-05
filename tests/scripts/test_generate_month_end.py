"""Tests for generate_month_end script."""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path


def load_module():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "generate_month_end.py"
    spec = importlib.util.spec_from_file_location("generate_month_end", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


generate_month_end = load_module()


def write_time_log(path: Path, rows: list[dict[str, str]]) -> None:
    headers = [
        "date",
        "hours",
        "repo",
        "issue_or_pr",
        "category",
        "description",
        "artifact_link",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def write_expenses(path: Path, rows: list[dict[str, str]]) -> None:
    headers = [
        "date",
        "amount",
        "currency",
        "category",
        "description",
        "receipt_link",
        "issue_or_pr",
        "preapproval_link",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def test_generate_month_end_with_data(tmp_path: Path) -> None:
    (tmp_path / "logs" / "time").mkdir(parents=True)
    (tmp_path / "logs" / "expenses").mkdir(parents=True)
    (tmp_path / "reviews" / "2024-01").mkdir(parents=True)

    write_time_log(
        tmp_path / "logs" / "time" / "2024-01.csv",
        [
            {
                "date": "2024-01-08",
                "hours": "2.5",
                "repo": "Collab-Admin",
                "issue_or_pr": "PR-123",
                "category": "feature",
                "description": "Implement memo generator",
                "artifact_link": "https://github.com/org/repo/pull/123",
            },
            {
                "date": "2024-01-09",
                "hours": "1.5",
                "repo": "Collab-Admin",
                "issue_or_pr": "PR-124",
                "category": "review",
                "description": "Review changes",
                "artifact_link": "https://github.com/org/repo/pull/124",
            },
        ],
    )

    write_expenses(
        tmp_path / "logs" / "expenses" / "2024-01.csv",
        [
            {
                "date": "2024-01-15",
                "amount": "100.00",
                "currency": "USD",
                "category": "travel",
                "description": "Taxi to client site",
                "receipt_link": "https://example.com/receipt",
                "issue_or_pr": "PR-123",
                "preapproval_link": "",
            }
        ],
    )

    review_path = tmp_path / "reviews" / "2024-01" / "pr-123.yml"
    review_path.write_text(
        "\n".join(
            [
                "pr_number: 123",
                "reviewer: Alex",
                "date: 2024-01-20",
                "workstream: Core",
                "rubric_used: R1",
                "follow_up_issues:",
                "  - id: 1",
                "    description: Follow up",
                "    required: true",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    output_path = generate_month_end.generate_month_end("2024-01", tmp_path)

    content = output_path.read_text(encoding="utf-8")
    assert "Month: 2024-01" in content
    assert "Total hours: 4.00" in content
    assert "- feature: 2.50" in content
    assert "- review: 1.50" in content
    assert "https://github.com/org/repo/pull/123" in content
    assert "Total reviews: 1" in content
    assert "PR #123" in content
    assert "USD: 100.00" in content
    assert "Taxi to client site" in content


def test_generate_month_end_with_missing_data(tmp_path: Path) -> None:
    (tmp_path / "logs" / "month_end").mkdir(parents=True)

    output_path = generate_month_end.generate_month_end("2024-02", tmp_path)

    content = output_path.read_text(encoding="utf-8")
    assert "No time logs found for 2024-02." in content
    assert "No deliverables recorded." in content
    assert "No reviews recorded." in content
    assert "No expenses recorded." in content
