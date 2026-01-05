"""Generate month-end settlement memo from logs and reviews."""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

MONTH_FORMAT = "%Y-%m"
PR_LINK_RE = re.compile(r"^https://github.com/[^/]+/[^/]+/pulls?/\d+/?$")


@dataclass(frozen=True)
class ReviewRecord:
    pr_number: str
    reviewer: str
    date: str
    workstream: str
    rubric_used: str
    follow_up_required: int


@dataclass(frozen=True)
class ExpenseEntry:
    date: str
    amount: float
    currency: str
    category: str
    description: str
    receipt_link: str
    issue_or_pr: str


def _parse_month(value: str) -> str:
    try:
        parsed = datetime.strptime(value, MONTH_FORMAT)
    except ValueError as exc:
        raise SystemExit(f"Invalid --month (expected YYYY-MM): {value!r}") from exc
    return parsed.strftime(MONTH_FORMAT)


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [row for row in reader]


def _parse_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _collect_pr_links(rows: Iterable[dict[str, str]]) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()
    for row in rows:
        link = (row.get("artifact_link") or "").strip()
        if link and PR_LINK_RE.match(link) and link not in seen:
            seen.add(link)
            links.append(link)
    return links


def _summarize_hours(rows: Iterable[dict[str, str]]) -> tuple[str, list[str]]:
    total_hours = 0.0
    by_category: defaultdict[str, float] = defaultdict(float)
    by_repo: defaultdict[str, float] = defaultdict(float)
    warnings: list[str] = []

    for row in rows:
        hours_value = row.get("hours") or ""
        hours = _parse_float(hours_value)
        if hours is None:
            warnings.append(f"Skipped row with invalid hours: {hours_value!r}")
            continue
        total_hours += hours
        category = (row.get("category") or "unspecified").strip() or "unspecified"
        repo = (row.get("repo") or "unspecified").strip() or "unspecified"
        by_category[category] += hours
        by_repo[repo] += hours

    lines = [f"Total hours: {total_hours:.2f}"]
    if by_category:
        lines.append("By category:")
        for category, hours in sorted(by_category.items()):
            lines.append(f"- {category}: {hours:.2f}")
    if by_repo:
        lines.append("By repo:")
        for repo, hours in sorted(by_repo.items()):
            lines.append(f"- {repo}: {hours:.2f}")
    return "\n".join(lines), warnings


def _load_reviews(review_dir: Path) -> list[ReviewRecord]:
    if not review_dir.is_dir():
        return []
    records: list[ReviewRecord] = []
    for path in sorted(review_dir.glob("*.yml")) + sorted(review_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        follow_ups = data.get("follow_up_issues") or []
        required = sum(1 for item in follow_ups if item.get("required") is True)
        records.append(
            ReviewRecord(
                pr_number=str(data.get("pr_number", "unknown")),
                reviewer=str(data.get("reviewer", "unknown")),
                date=str(data.get("date", "unknown")),
                workstream=str(data.get("workstream", "unknown")),
                rubric_used=str(data.get("rubric_used", "unknown")),
                follow_up_required=required,
            )
        )
    return records


def _summarize_reviews(records: Iterable[ReviewRecord]) -> str:
    records = list(records)
    lines = [f"Total reviews: {len(records)}"]
    for record in records:
        lines.append(
            " - ".join(
                [
                    f"PR #{record.pr_number}",
                    f"Reviewer: {record.reviewer}",
                    f"Date: {record.date}",
                    f"Workstream: {record.workstream}",
                    f"Rubric: {record.rubric_used}",
                    f"Follow-ups required: {record.follow_up_required}",
                ]
            )
        )
    return "\n".join(lines)


def _load_expenses(path: Path) -> list[ExpenseEntry]:
    rows = _read_csv_rows(path)
    expenses: list[ExpenseEntry] = []
    for row in rows:
        amount = _parse_float(row.get("amount") or "")
        if amount is None:
            continue
        expenses.append(
            ExpenseEntry(
                date=(row.get("date") or "").strip(),
                amount=amount,
                currency=(row.get("currency") or "unknown").strip() or "unknown",
                category=(row.get("category") or "unspecified").strip()
                or "unspecified",
                description=(row.get("description") or "").strip(),
                receipt_link=(row.get("receipt_link") or "").strip(),
                issue_or_pr=(row.get("issue_or_pr") or "").strip(),
            )
        )
    return expenses


def _summarize_expenses(expenses: Iterable[ExpenseEntry]) -> str:
    expenses = list(expenses)
    totals: defaultdict[str, float] = defaultdict(float)
    for entry in expenses:
        totals[entry.currency] += entry.amount
    lines: list[str] = []
    if totals:
        lines.append("Total expenses:")
        for currency, amount in sorted(totals.items()):
            lines.append(f"- {currency}: {amount:.2f}")
    if expenses:
        lines.append("Entries:")
        for entry in expenses:
            details = (
                f"{entry.date} | {entry.amount:.2f} {entry.currency} | "
                f"{entry.category} | {entry.description}"
            )
            if entry.receipt_link:
                details += f" | {entry.receipt_link}"
            if entry.issue_or_pr:
                details += f" | {entry.issue_or_pr}"
            lines.append(f"- {details}")
    return "\n".join(lines)


def generate_month_end(month: str, root: Path) -> Path:
    month = _parse_month(month)
    time_log = root / "logs" / "time" / f"{month}.csv"
    expenses_log = root / "logs" / "expenses" / f"{month}.csv"
    reviews_dir = root / "reviews" / month
    output_dir = root / "logs" / "month_end"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{month}.md"

    time_rows = _read_csv_rows(time_log)
    expense_entries = _load_expenses(expenses_log)
    review_records = _load_reviews(reviews_dir)

    hours_summary = ""
    hours_warnings: list[str] = []
    if time_rows:
        hours_summary, hours_warnings = _summarize_hours(time_rows)

    pr_links = _collect_pr_links(time_rows)

    lines = [
        "# Month-End Memo",
        "",
        f"Month: {month}",
        "",
        "## Hours Summary",
    ]
    if time_rows:
        lines.append(hours_summary)
    else:
        lines.append(f"No time logs found for {month}.")
    if hours_warnings:
        lines.append("Warnings:")
        lines.extend([f"- {warning}" for warning in hours_warnings])

    lines.extend(["", "## Deliverables"])
    if pr_links:
        lines.extend([f"- {link}" for link in pr_links])
    else:
        lines.append("No deliverables recorded.")

    lines.extend(["", "## Reviews"])
    if review_records:
        lines.append(_summarize_reviews(review_records))
    else:
        lines.append("No reviews recorded.")

    lines.extend(["", "## Expenses"])
    if expense_entries:
        lines.append(_summarize_expenses(expense_entries))
    else:
        lines.append("No expenses recorded.")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", required=True, help="Month to summarize (YYYY-MM)")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Optional repo root override (for testing)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    output_path = generate_month_end(args.month, args.root)
    print(f"Generated month-end memo: {output_path}")


if __name__ == "__main__":
    main()
