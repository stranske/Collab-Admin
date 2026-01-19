#!/usr/bin/env python
"""Create a review record stub from the review template."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

_TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "templates" / "review_record.yml"
_REVIEWS_ROOT = Path(__file__).resolve().parents[1] / "reviews"


def _parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid --date (expected YYYY-MM-DD): {value!r}") from exc


def _load_template(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"Template not found: {path}")
    return path.read_text(encoding="utf-8")


def _render_template(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    return template


def _output_path(pr_number: int, review_date: dt.date) -> Path:
    month_dir = _REVIEWS_ROOT / review_date.strftime("%Y-%m")
    return month_dir / f"pr-{pr_number}.yml"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pr_number", type=int, help="Pull request number")
    parser.add_argument("--reviewer", default="TBD", help="Reviewer name or handle")
    parser.add_argument("--workstream", default="TBD", help="Workstream name")
    parser.add_argument("--rubric", default="TBD", help="Rubric identifier")
    parser.add_argument(
        "--date",
        default=None,
        help="Review date in YYYY-MM-DD (defaults to today)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path to override the default location",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.pr_number <= 0:
        raise SystemExit("pr_number must be a positive integer")

    review_date = _parse_date(args.date) if args.date else dt.date.today()
    output_path = args.output or _output_path(args.pr_number, review_date)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        raise SystemExit(f"Review record already exists: {output_path}")

    template = _load_template(_TEMPLATE_PATH)
    rendered = _render_template(
        template,
        {
            "pr_number": str(args.pr_number),
            "reviewer": args.reviewer,
            "date": review_date.isoformat(),
            "workstream": args.workstream,
            "rubric_used": args.rubric,
        },
    )
    output_path.write_text(rendered, encoding="utf-8")

    print(f"Created review record: {output_path}")


if __name__ == "__main__":
    main()
