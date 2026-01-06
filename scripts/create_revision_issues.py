#!/usr/bin/env python3
"""Create GitHub issues for required follow-up items in review records."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class FollowUpIssue:
    issue_id: str
    description: str
    required: bool


@dataclass(frozen=True)
class ReviewRecord:
    pr_number: int
    reviewer: str
    date: str
    workstream: str
    rubric_used: str
    follow_up_issues: tuple[FollowUpIssue, ...]


@dataclass(frozen=True)
class IssueAction:
    issue_id: str
    status: str
    url: str | None


def _load_yaml(path: Path) -> dict[str, object]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Failed to read review file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"Review file must be a YAML mapping: {path}")
    return payload


def _require_field(
    payload: dict[str, object], name: str, field_type: type, source: Path
) -> object:
    value = payload.get(name)
    if not isinstance(value, field_type):
        raise SystemExit(
            f"Review file missing {name} ({field_type.__name__}) in {source}"
        )
    return value


def _parse_follow_up_items(
    raw_items: object, source: Path
) -> tuple[FollowUpIssue, ...]:
    if raw_items is None:
        return ()
    if not isinstance(raw_items, list):
        raise SystemExit(f"follow_up_issues must be a list in {source}")
    parsed: list[FollowUpIssue] = []
    for entry in raw_items:
        if not isinstance(entry, dict):
            raise SystemExit(f"follow_up_issues entries must be mappings in {source}")
        issue_id = entry.get("id")
        description = entry.get("description")
        required = entry.get("required", False)
        if not isinstance(issue_id, str) or not issue_id.strip():
            raise SystemExit(f"follow_up_issues entry missing id in {source}")
        if not isinstance(description, str) or not description.strip():
            raise SystemExit(f"follow_up_issues entry missing description in {source}")
        if not isinstance(required, bool):
            raise SystemExit(
                f"follow_up_issues entry required must be boolean in {source}"
            )
        parsed.append(
            FollowUpIssue(
                issue_id=issue_id.strip(),
                description=description.strip(),
                required=required,
            )
        )
    return tuple(parsed)


def load_review(path: Path) -> ReviewRecord:
    payload = _load_yaml(path)
    pr_number = _require_field(payload, "pr_number", int, path)
    reviewer = _require_field(payload, "reviewer", str, path)
    date = _require_field(payload, "date", str, path)
    workstream = _require_field(payload, "workstream", str, path)
    rubric_used = _require_field(payload, "rubric_used", str, path)
    follow_up_issues = _parse_follow_up_items(payload.get("follow_up_issues"), path)
    return ReviewRecord(
        pr_number=pr_number,
        reviewer=reviewer,
        date=date,
        workstream=workstream,
        rubric_used=rubric_used,
        follow_up_issues=follow_up_issues,
    )


def _review_reference(path: Path) -> str:
    repo_root = Path(__file__).resolve().parents[1]
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _pr_reference(pr_number: int, repo: str | None) -> str:
    if repo:
        return f"https://github.com/{repo}/pull/{pr_number}"
    return f"#{pr_number}"


def build_issue_title(review: ReviewRecord, follow_up: FollowUpIssue) -> str:
    return f"PR {review.pr_number} review follow-up: {follow_up.issue_id}"


def build_issue_body(
    review: ReviewRecord,
    follow_up: FollowUpIssue,
    review_reference: str,
    repo: str | None,
) -> str:
    pr_reference = _pr_reference(review.pr_number, repo)
    required_label = "yes" if follow_up.required else "no"
    return "\n".join(
        [
            f"Follow-up ID: {follow_up.issue_id}",
            f"Required: {required_label}",
            "",
            "Description:",
            follow_up.description,
            "",
            f"Source review: {review_reference}",
            f"PR: {pr_reference}",
        ]
    )


def _run_gh(
    args: list[str],
    runner: callable = subprocess.run,
) -> subprocess.CompletedProcess[str]:
    return runner(
        ["gh", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _ensure_gh_ok(result: subprocess.CompletedProcess[str], context: str) -> None:
    if result.returncode == 0:
        return
    detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
    raise SystemExit(f"gh {context} failed: {detail}")


def _issue_search_query(follow_up: FollowUpIssue, review_reference: str) -> str:
    return f'"Follow-up ID: {follow_up.issue_id}" "Source review: {review_reference}"'


def _issue_exists(
    follow_up: FollowUpIssue,
    review_reference: str,
    repo: str | None,
    runner: callable = subprocess.run,
) -> bool:
    args = [
        "issue",
        "list",
        "--search",
        _issue_search_query(follow_up, review_reference),
        "--json",
        "number,title,body",
        "--limit",
        "100",
    ]
    if repo:
        args.extend(["--repo", repo])
    result = _run_gh(args, runner=runner)
    _ensure_gh_ok(result, "issue list")
    try:
        issues = json.loads(result.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse gh issue list output: {exc}") from exc
    return bool(issues)


def _create_issue(
    title: str,
    body: str,
    label: str,
    repo: str | None,
    runner: callable = subprocess.run,
) -> str:
    args = ["issue", "create", "--title", title, "--body", body, "--label", label]
    if repo:
        args.extend(["--repo", repo])
    result = _run_gh(args, runner=runner)
    _ensure_gh_ok(result, "issue create")
    return result.stdout.strip()


def process_review(
    review_path: Path,
    repo: str | None,
    label: str,
    include_optional: bool,
    dry_run: bool,
    runner: callable = subprocess.run,
) -> list[IssueAction]:
    review = load_review(review_path)
    review_reference = _review_reference(review_path)
    actions: list[IssueAction] = []
    follow_ups = (
        issue for issue in review.follow_up_issues if issue.required or include_optional
    )
    for follow_up in follow_ups:
        title = build_issue_title(review, follow_up)
        body = build_issue_body(review, follow_up, review_reference, repo)
        if dry_run:
            actions.append(
                IssueAction(issue_id=follow_up.issue_id, status="dry-run", url=None)
            )
            continue
        if _issue_exists(follow_up, review_reference, repo, runner=runner):
            actions.append(
                IssueAction(issue_id=follow_up.issue_id, status="skipped", url=None)
            )
            continue
        url = _create_issue(title, body, label, repo, runner=runner)
        actions.append(
            IssueAction(issue_id=follow_up.issue_id, status="created", url=url)
        )
    return actions


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_paths", nargs="+", type=Path, help="Review YAML files.")
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY"),
        help="GitHub repo in owner/name form (defaults to GITHUB_REPOSITORY).",
    )
    parser.add_argument(
        "--label",
        default="revision-required",
        help="Label to apply to created issues.",
    )
    parser.add_argument(
        "--include-optional",
        action="store_true",
        help="Include non-required follow-up issues.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without calling gh.",
    )
    return parser


def _summarize_actions(actions: Iterable[IssueAction]) -> None:
    for action in actions:
        if action.status == "created":
            message = f"Created follow-up issue {action.issue_id}"
            if action.url:
                message = f"{message}: {action.url}"
            print(message)
        elif action.status == "skipped":
            print(f"Skipped follow-up issue {action.issue_id} (already exists)")
        else:
            print(f"Dry run: would create follow-up issue {action.issue_id}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    all_actions: list[IssueAction] = []
    for path in args.review_paths:
        if not path.exists():
            raise SystemExit(f"Review file not found: {path}")
        actions = process_review(
            path,
            repo=args.repo,
            label=args.label,
            include_optional=args.include_optional,
            dry_run=args.dry_run,
        )
        all_actions.extend(actions)
    _summarize_actions(all_actions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
