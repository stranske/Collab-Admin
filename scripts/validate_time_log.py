"""Validate time logs:
- CSV schema
- category and artifact link validation
- date format and reasonable range
- weekly sum <= 40 hours
- no banking enforced (policy; this script flags >40 only)
"""

import argparse
import csv
import re
import sys
from collections import defaultdict
from datetime import date, datetime

REQUIRED = [
    "date",
    "hours",
    "repo",
    "issue_or_pr",
    "category",
    "description",
    "artifact_link",
]

ALLOWED_CATEGORIES = {"setup", "feature", "fix", "review", "meeting", "admin"}
GITHUB_URL_RE = re.compile(r"^https://github.com/[^/]+/[^/]+(?:/.*)?$")
MAX_PAST_DAYS = 365 * 2
DATE_FORMAT = "%Y-%m-%d"


def week_key(dt: date) -> str:
    # ISO week
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate time log CSV files.")
    parser.add_argument("path", help="Path to the time log CSV file.")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-row validation status and summaries.",
    )
    return parser.parse_args(argv)


def validate_date(value: str, today: date) -> tuple[date | None, str | None]:
    try:
        dt = datetime.strptime(value, DATE_FORMAT).date()
    except ValueError:
        return None, f"Invalid date '{value}' (expected {DATE_FORMAT})"
    if dt > today:
        return None, f"Date '{value}' is in the future"
    if (today - dt).days > MAX_PAST_DAYS:
        return None, f"Date '{value}' is too old (>{MAX_PAST_DAYS} days)"
    return dt, None


def validate_row(
    row: dict[str, str | None], today: date
) -> tuple[date | None, float | None, list[str]]:
    errors = []
    dt, date_error = validate_date(row.get("date") or "", today)
    if date_error:
        errors.append(date_error)

    hours_value = row.get("hours") or ""
    hours = None
    try:
        hours = float(hours_value)
    except ValueError:
        errors.append(f"Invalid hours '{hours_value}'")

    category = row.get("category") or ""
    if category not in ALLOWED_CATEGORIES:
        allowed = ", ".join(sorted(ALLOWED_CATEGORIES))
        errors.append(f"Invalid category '{category}' (allowed: {allowed})")

    artifact_link = (row.get("artifact_link") or "").strip()
    if artifact_link and not GITHUB_URL_RE.match(artifact_link):
        errors.append("Invalid artifact_link (expected GitHub URL or empty)")

    return dt, hours, errors


def validate_time_log(path: str, *, verbose: bool = False, today: date | None = None) -> list[str]:
    today = today or date.today()
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        fieldnames = r.fieldnames or []
        missing = [c for c in REQUIRED if c not in fieldnames]
        if missing:
            return [f"Missing columns: {missing}"]
        totals: defaultdict[str, float] = defaultdict(float)
        errors: list[str] = []
        for row_num, row in enumerate(r, start=2):
            dt, hrs, row_errors = validate_row(row, today)
            if row_errors:
                errors.extend([f"Row {row_num}: {err}" for err in row_errors])
            if verbose:
                if row_errors:
                    print(f"Row {row_num}: " + "; ".join(row_errors))
                else:
                    print(f"Row {row_num}: OK")
            if dt is not None and hrs is not None:
                totals[week_key(dt)] += hrs
        bad = {k: v for k, v in totals.items() if v > 40.0 + 1e-9}
        if bad:
            errors.append(f"Weekly cap exceeded: {bad}")
            if verbose:
                print(f"Weekly cap exceeded: {bad}")
    return errors


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    errors = validate_time_log(args.path, verbose=args.verbose)
    if errors:
        raise SystemExit("\n".join(errors))
    print("OK")


if __name__ == "__main__":
    main(sys.argv[1:])
