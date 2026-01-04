#!/usr/bin/env python
"""Build a static markdown dashboard from local review, time log, and CI data."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

TIME_LOG_FIELDS = (
    "date",
    "hours",
    "repo",
    "issue_or_pr",
    "category",
    "description",
    "artifact_link",
)

DEFAULT_TIME_LOG_DIR = Path("logs/time")
DEFAULT_REVIEWS_DIR = Path("reviews")
DEFAULT_CI_HISTORY = Path("logs/ci/metrics-history.ndjson")
DEFAULT_ISSUE_PR_METRICS = Path("logs/issue_pr_metrics.json")
DEFAULT_CONFIG_PATH = Path("config/dashboard_public.yml")
DEFAULT_OUTPUT_PATH = Path("dashboards/public/dashboard.md")
DEFAULT_RECENT_CI_RUNS = 10
DEFAULT_RECENT_ACTIVITY = 5


@dataclass(frozen=True)
class DashboardConfig:
    show_numeric_scoring: bool = False


@dataclass(frozen=True)
class TimeLogSummary:
    total_hours: float
    workstream_hours: dict[str, float]
    category_hours: dict[str, float]
    entries: int
    skipped_rows: int


@dataclass(frozen=True)
class ReviewSummary:
    total_reviews: int
    workstream_counts: dict[str, int]
    numeric_average: float | None
    numeric_average_by_workstream: dict[str, float]
    numeric_ratings_found: int


@dataclass(frozen=True)
class IssuePrSummary:
    issues_open: int | None
    issues_closed: int | None
    prs_open: int | None
    prs_closed: int | None
    recent_activity: list[str]


@dataclass(frozen=True)
class CiHealthSummary:
    total_runs: int
    recent_runs: int
    recent_passes: int
    pass_rate: float | None
    latest_status: str | None
    latest_timestamp: str | None
    latest_summary: dict[str, Any] | None


def _format_float(value: float) -> str:
    text = f"{value:.2f}"
    text = text.rstrip("0").rstrip(".")
    return text


def _load_yaml(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None
    if isinstance(data, dict):
        return data
    return None


def _load_dashboard_config(path: Path) -> DashboardConfig:
    data = _load_yaml(path)
    if not data:
        return DashboardConfig()
    dashboard = data.get("dashboard")
    if not isinstance(dashboard, dict):
        return DashboardConfig()
    show_numeric = dashboard.get("show_numeric_scoring", False)
    return DashboardConfig(show_numeric_scoring=bool(show_numeric))


def _parse_hours(raw: str | None) -> float | None:
    if raw is None:
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    if value < 0:
        return None
    return value


def _summarize_time_logs(time_log_dir: Path) -> TimeLogSummary:
    total_hours = 0.0
    workstream_hours: dict[str, float] = {}
    category_hours: dict[str, float] = {}
    entries = 0
    skipped_rows = 0

    if not time_log_dir.is_dir():
        return TimeLogSummary(
            total_hours=0.0,
            workstream_hours={},
            category_hours={},
            entries=0,
            skipped_rows=0,
        )

    for path in sorted(time_log_dir.glob("*.csv")):
        with path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not all(
                field in reader.fieldnames for field in TIME_LOG_FIELDS
            ):
                continue
            for row in reader:
                hours = _parse_hours(row.get("hours"))
                if hours is None:
                    skipped_rows += 1
                    continue
                workstream = (row.get("repo") or "Unknown").strip() or "Unknown"
                category = (
                    row.get("category") or "Uncategorized"
                ).strip() or "Uncategorized"
                total_hours += hours
                workstream_hours[workstream] = (
                    workstream_hours.get(workstream, 0.0) + hours
                )
                category_hours[category] = category_hours.get(category, 0.0) + hours
                entries += 1

    return TimeLogSummary(
        total_hours=total_hours,
        workstream_hours=workstream_hours,
        category_hours=category_hours,
        entries=entries,
        skipped_rows=skipped_rows,
    )


def _extract_numeric_rating(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _summarize_reviews(reviews_dir: Path) -> ReviewSummary:
    total_reviews = 0
    workstream_counts: dict[str, int] = {}
    numeric_ratings: list[float] = []
    numeric_by_workstream: dict[str, list[float]] = {}

    if not reviews_dir.is_dir():
        return ReviewSummary(
            total_reviews=0,
            workstream_counts={},
            numeric_average=None,
            numeric_average_by_workstream={},
            numeric_ratings_found=0,
        )

    review_paths = sorted(
        list(reviews_dir.rglob("*.yml")) + list(reviews_dir.rglob("*.yaml"))
    )

    for path in review_paths:
        data = _load_yaml(path)
        if not data:
            continue
        total_reviews += 1
        workstream = data.get("workstream") or "Unknown"
        if not isinstance(workstream, str):
            workstream = "Unknown"
        workstream = workstream.strip() or "Unknown"
        workstream_counts[workstream] = workstream_counts.get(workstream, 0) + 1

        ratings = data.get("dimension_ratings")
        if not isinstance(ratings, list):
            continue
        for entry in ratings:
            if not isinstance(entry, dict):
                continue
            rating_value = _extract_numeric_rating(entry.get("rating"))
            if rating_value is None:
                continue
            numeric_ratings.append(rating_value)
            numeric_by_workstream.setdefault(workstream, []).append(rating_value)

    numeric_average = (
        sum(numeric_ratings) / len(numeric_ratings) if numeric_ratings else None
    )
    numeric_average_by_workstream = {
        workstream: sum(values) / len(values)
        for workstream, values in numeric_by_workstream.items()
        if values
    }

    return ReviewSummary(
        total_reviews=total_reviews,
        workstream_counts=workstream_counts,
        numeric_average=numeric_average,
        numeric_average_by_workstream=numeric_average_by_workstream,
        numeric_ratings_found=len(numeric_ratings),
    )


def _load_issue_pr_metrics(path: Path) -> IssuePrSummary | None:
    if not path.is_file():
        return None
    raw: dict[str, Any] | None
    if path.suffix.lower() in {".yml", ".yaml"}:
        raw = _load_yaml(path)
    else:
        try:
            raw_data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        raw = raw_data if isinstance(raw_data, dict) else None
    if not raw:
        return None

    def _coerce_int(value: Any) -> int | None:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                return None
        return None

    issues = raw.get("issues", {})
    prs = raw.get("pull_requests", {})
    issues_open = _coerce_int(issues.get("open")) if isinstance(issues, dict) else None
    issues_closed = (
        _coerce_int(issues.get("closed")) if isinstance(issues, dict) else None
    )
    prs_open = _coerce_int(prs.get("open")) if isinstance(prs, dict) else None
    prs_closed = _coerce_int(prs.get("closed")) if isinstance(prs, dict) else None

    recent_activity: list[str] = []
    recent_list: list[dict[str, Any]] = []
    if isinstance(issues, dict):
        recent_list.extend(
            entry
            for entry in issues.get("recent_activity", issues.get("recent", [])) or []
            if isinstance(entry, dict)
        )
    if isinstance(prs, dict):
        recent_list.extend(
            entry
            for entry in prs.get("recent_activity", prs.get("recent", [])) or []
            if isinstance(entry, dict)
        )

    for entry in recent_list[:DEFAULT_RECENT_ACTIVITY]:
        item_type = entry.get("type") or entry.get("kind") or "Item"
        number = entry.get("number")
        title = entry.get("title") or entry.get("name") or "(untitled)"
        updated = entry.get("updated_at") or entry.get("updated") or entry.get("date")
        number_text = f"#{number}" if number is not None else ""
        updated_text = f" ({updated})" if updated else ""
        recent_activity.append(
            f"{item_type} {number_text} {title}{updated_text}".strip()
        )

    return IssuePrSummary(
        issues_open=issues_open,
        issues_closed=issues_closed,
        prs_open=prs_open,
        prs_closed=prs_closed,
        recent_activity=recent_activity,
    )


def _load_ci_history(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.is_file():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(entry, dict):
            records.append(entry)
    return records


def _summarize_ci_history(
    records: list[dict[str, Any]],
    *,
    recent_limit: int,
) -> CiHealthSummary:
    total_runs = len(records)
    if not records:
        return CiHealthSummary(
            total_runs=0,
            recent_runs=0,
            recent_passes=0,
            pass_rate=None,
            latest_status=None,
            latest_timestamp=None,
            latest_summary=None,
        )
    recent = records[-recent_limit:] if recent_limit > 0 else []
    recent_passes = 0
    for entry in recent:
        summary = entry.get("summary", {}) if isinstance(entry, dict) else {}
        failures = int(summary.get("failures", 0) or 0)
        errors = int(summary.get("errors", 0) or 0)
        if failures == 0 and errors == 0:
            recent_passes += 1

    pass_rate = (recent_passes / len(recent)) * 100 if recent else None
    latest = records[-1]
    latest_summary = latest.get("summary") if isinstance(latest, dict) else None
    latest_timestamp = latest.get("timestamp") if isinstance(latest, dict) else None
    latest_status = None
    if isinstance(latest_summary, dict):
        failures = int(latest_summary.get("failures", 0) or 0)
        errors = int(latest_summary.get("errors", 0) or 0)
        latest_status = "passed" if failures == 0 and errors == 0 else "failed"

    return CiHealthSummary(
        total_runs=total_runs,
        recent_runs=len(recent),
        recent_passes=recent_passes,
        pass_rate=pass_rate,
        latest_status=latest_status,
        latest_timestamp=latest_timestamp,
        latest_summary=latest_summary if isinstance(latest_summary, dict) else None,
    )


def _render_time_section(summary: TimeLogSummary) -> list[str]:
    lines = ["## Time Tracking Summary"]
    if summary.entries == 0:
        lines.append("No time logs found.")
        return lines
    lines.append(f"Total hours logged: {_format_float(summary.total_hours)}")
    lines.append("Hours by workstream:")
    for workstream, hours in sorted(
        summary.workstream_hours.items(), key=lambda item: (-item[1], item[0])
    ):
        lines.append(f"- {workstream}: {_format_float(hours)}")
    lines.append("Hours by category:")
    for category, hours in sorted(
        summary.category_hours.items(), key=lambda item: (-item[1], item[0])
    ):
        lines.append(f"- {category}: {_format_float(hours)}")
    if summary.skipped_rows:
        lines.append(f"Skipped {summary.skipped_rows} rows with invalid hours.")
    return lines


def _render_review_section(
    summary: ReviewSummary, config: DashboardConfig
) -> list[str]:
    lines = ["## Review Summary"]
    if summary.total_reviews == 0:
        lines.append("No reviews found.")
        return lines
    lines.append(f"Reviews logged: {summary.total_reviews}")
    lines.append("Reviews by workstream:")
    for workstream, count in sorted(summary.workstream_counts.items()):
        lines.append(f"- {workstream}: {count}")
    if summary.numeric_ratings_found == 0:
        return lines
    if config.show_numeric_scoring and summary.numeric_average is not None:
        lines.append(
            f"Average rating (numeric): {_format_float(summary.numeric_average)}"
        )
        if summary.numeric_average_by_workstream:
            lines.append("Average rating by workstream (numeric):")
            for workstream, average in sorted(
                summary.numeric_average_by_workstream.items()
            ):
                lines.append(f"- {workstream}: {_format_float(average)}")
    else:
        lines.append("Numeric ratings exist but are hidden by dashboard config.")
    return lines


def _render_issue_pr_section(summary: IssuePrSummary | None) -> list[str]:
    lines = ["### Issue & PR Metrics"]
    if summary is None:
        lines.append("No issue/PR metrics available.")
        return lines
    if summary.issues_open is not None or summary.issues_closed is not None:
        open_count = summary.issues_open if summary.issues_open is not None else "n/a"
        closed_count = (
            summary.issues_closed if summary.issues_closed is not None else "n/a"
        )
        lines.append(f"Issues: open {open_count} | closed {closed_count}")
    if summary.prs_open is not None or summary.prs_closed is not None:
        open_count = summary.prs_open if summary.prs_open is not None else "n/a"
        closed_count = summary.prs_closed if summary.prs_closed is not None else "n/a"
        lines.append(f"Pull requests: open {open_count} | closed {closed_count}")
    if summary.recent_activity:
        lines.append("Recent activity:")
        for entry in summary.recent_activity:
            lines.append(f"- {entry}")
    return lines


def _render_ci_section(summary: CiHealthSummary) -> list[str]:
    lines = ["### CI Health"]
    if summary.total_runs == 0:
        lines.append("No CI history available.")
        return lines
    if summary.pass_rate is not None and summary.recent_runs:
        pass_rate = _format_float(summary.pass_rate)
        lines.append(
            f"Recent pass rate (last {summary.recent_runs} runs): {pass_rate}% "
            f"({summary.recent_passes}/{summary.recent_runs})"
        )
    if summary.latest_status:
        timestamp = summary.latest_timestamp or "unknown time"
        detail = ""
        if summary.latest_summary:
            tests = summary.latest_summary.get("tests")
            failures = summary.latest_summary.get("failures")
            errors = summary.latest_summary.get("errors")
            detail = f" (tests: {tests}, failures: {failures}, errors: {errors})"
        lines.append(f"Latest run: {timestamp} - {summary.latest_status}{detail}")
    return lines


def build_dashboard(
    *,
    time_log_dir: Path,
    reviews_dir: Path,
    ci_history_path: Path,
    issue_pr_path: Path,
    config_path: Path,
    now: dt.datetime | None = None,
    recent_ci_runs: int = DEFAULT_RECENT_CI_RUNS,
) -> str:
    config = _load_dashboard_config(config_path)
    time_summary = _summarize_time_logs(time_log_dir)
    review_summary = _summarize_reviews(reviews_dir)
    issue_pr_summary = _load_issue_pr_metrics(issue_pr_path)
    ci_summary = _summarize_ci_history(
        _load_ci_history(ci_history_path), recent_limit=recent_ci_runs
    )

    timestamp = now or dt.datetime.now(dt.UTC)
    updated = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

    sections: list[str] = ["# Dashboard", f"Updated: {updated}", ""]
    sections.extend(_render_time_section(time_summary))
    sections.append("")
    sections.extend(_render_review_section(review_summary, config))
    sections.append("")
    sections.append("## Project Health Metrics")
    sections.extend(_render_issue_pr_section(issue_pr_summary))
    sections.append("")
    sections.extend(_render_ci_section(ci_summary))
    sections.append("")

    return "\n".join(sections).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a static dashboard markdown file from local data."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Destination markdown path.",
    )
    parser.add_argument(
        "--time-log-dir",
        type=Path,
        default=DEFAULT_TIME_LOG_DIR,
        help="Directory containing monthly time log CSV files.",
    )
    parser.add_argument(
        "--reviews-dir",
        type=Path,
        default=DEFAULT_REVIEWS_DIR,
        help="Directory containing review YAML files.",
    )
    parser.add_argument(
        "--ci-history",
        type=Path,
        default=DEFAULT_CI_HISTORY,
        help="NDJSON file containing CI history records.",
    )
    parser.add_argument(
        "--issue-pr-path",
        type=Path,
        default=DEFAULT_ISSUE_PR_METRICS,
        help="JSON/YAML file containing issue and PR metrics.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Dashboard config file path.",
    )
    parser.add_argument(
        "--recent-ci-runs",
        type=int,
        default=DEFAULT_RECENT_CI_RUNS,
        help="Number of recent CI runs to summarize.",
    )
    parser.add_argument(
        "--now",
        type=str,
        default=None,
        help="Override timestamp in ISO format (for testing).",
    )

    args = parser.parse_args(argv)
    now = None
    if args.now:
        try:
            now = dt.datetime.fromisoformat(args.now)
        except ValueError:
            print(f"Invalid --now value: {args.now}", file=sys.stderr)
            return 2
        if now.tzinfo is None:
            now = now.replace(tzinfo=dt.UTC)
        else:
            now = now.astimezone(dt.UTC)

    markdown = build_dashboard(
        time_log_dir=args.time_log_dir,
        reviews_dir=args.reviews_dir,
        ci_history_path=args.ci_history,
        issue_pr_path=args.issue_pr_path,
        config_path=args.config,
        now=now,
        recent_ci_runs=args.recent_ci_runs,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(f"Dashboard written to {args.output}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
