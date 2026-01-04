#!/usr/bin/env python3
"""Validate time log template CSV format."""

import csv
import sys
from pathlib import Path


def main() -> int:
    """Validate the time log template file."""
    if len(sys.argv) < 2:
        print("Usage: validate_time_log_template.py <template.csv>", file=sys.stderr)
        return 1

    template_path = Path(sys.argv[1])
    if not template_path.exists():
        print(f"ERROR: Template file does not exist: {template_path}", file=sys.stderr)
        return 1

    expected_header = [
        "date",
        "hours",
        "repo",
        "issue_or_pr",
        "category",
        "description",
        "artifact_link",
    ]

    with open(template_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("ERROR: Template file is empty", file=sys.stderr)
            return 1

    if header != expected_header:
        print("ERROR: Template header mismatch", file=sys.stderr)
        print(f"  Expected: {expected_header}", file=sys.stderr)
        print(f"  Got: {header}", file=sys.stderr)
        return 1

    print("✓ Time log template format is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
