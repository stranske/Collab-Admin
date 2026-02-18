#!/usr/bin/env python3
"""Validate time log template CSV format."""

import argparse
import csv
import sys
from pathlib import Path


def validate_template(template_path: Path) -> tuple[bool, str]:
    """Validate a time log template file.

    Args:
        template_path: Path to the template CSV file.

    Returns:
        Tuple of (success, message).
    """
    if not template_path.exists():
        return False, f"Template file does not exist: {template_path}"

    expected_header = [
        "date",
        "hours",
        "repo",
        "issue_or_pr",
        "category",
        "description",
        "artifact_link",
    ]

    try:
        with open(template_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                return False, "Template file is empty"
    except OSError as e:
        return False, f"Failed to read template file: {e}"

    if header != expected_header:
        return (
            False,
            f"Template header mismatch\n  Expected: {expected_header}\n  Got: {header}",
        )

    return True, "Time log template format is valid"


def main() -> int:
    """Validate the time log template file."""
    parser = argparse.ArgumentParser(description="Validate time log template CSV format.")
    parser.add_argument(
        "template",
        metavar="template.csv",
        help="Path to the time log template CSV file",
    )
    args = parser.parse_args()

    template_path = Path(args.template)
    success, message = validate_template(template_path)

    if success:
        print(f"✓ {message}")
        return 0
    else:
        print(f"ERROR: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
