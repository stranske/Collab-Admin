"""Validate friction log CSV files."""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"
REQUIRED = [
    "date",
    "repo",
    "context",
    "minutes_lost",
    "what_broke",
    "what_was_confusing",
    "what_fixed_it",
    "pr_or_issue",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate friction log CSV files.")
    parser.add_argument("path", help="Path to the friction log CSV file.")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-row validation status.",
    )
    return parser.parse_args(argv)


def validate_date(value: str) -> str | None:
    try:
        datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        return f"Invalid date '{value}' (expected {DATE_FORMAT})"
    return None


def validate_row(row: dict[str, str | None]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED:
        if not (row.get(field) or "").strip():
            errors.append(f"Missing value for '{field}'")

    date_value = (row.get("date") or "").strip()
    date_error = validate_date(date_value)
    if date_error:
        errors.append(date_error)

    minutes_value = (row.get("minutes_lost") or "").strip()
    try:
        float(minutes_value)
    except ValueError:
        errors.append(f"Invalid minutes_lost '{minutes_value}'")

    return errors


def validate_friction_log(path: str, *, verbose: bool = False) -> list[str]:
    errors: list[str] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        missing = [c for c in REQUIRED if c not in fieldnames]
        if missing:
            return [f"Missing columns: {missing}"]
        for row_num, row in enumerate(reader, start=2):
            row_errors = validate_row(row)
            if row_errors:
                errors.extend([f"Row {row_num}: {err}" for err in row_errors])
            if verbose:
                if row_errors:
                    print(f"Row {row_num}: " + "; ".join(row_errors))
                else:
                    print(f"Row {row_num}: OK")
    return errors


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    errors = validate_friction_log(args.path, verbose=args.verbose)
    if errors:
        raise SystemExit("\n".join(errors))
    print("OK")


if __name__ == "__main__":
    main(sys.argv[1:])
