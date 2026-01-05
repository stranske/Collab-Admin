"""Tests for create_revision_issues script."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

from scripts.create_revision_issues import (
    FollowUpIssue,
    ReviewRecord,
    build_issue_body,
    load_review,
    process_review,
)


class FakeGhRunner:
    def __init__(self, list_payload: list[dict[str, object]] | None = None) -> None:
        self.calls: list[list[str]] = []
        self.list_payload = list_payload

    def __call__(
        self,
        args: list[str],
        capture_output: bool = True,
        text: bool = True,
        check: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        self.calls.append(args)
        if args[1:3] == ["issue", "list"]:
            payload = json.dumps(self.list_payload or [])
            return subprocess.CompletedProcess(args, 0, stdout=payload, stderr="")
        if args[1:3] == ["issue", "create"]:
            return subprocess.CompletedProcess(
                args, 0, stdout="https://github.com/org/repo/issues/99\n", stderr=""
            )
        return subprocess.CompletedProcess(args, 1, stdout="", stderr="unexpected")


def _write_review(path: Path, follow_up_issues: list[dict[str, object]]) -> None:
    data = {
        "pr_number": 123,
        "reviewer": "alice",
        "date": "2025-01-01",
        "workstream": "core",
        "rubric_used": "v1",
        "follow_up_issues": follow_up_issues,
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def test_load_review_parses_follow_up_issues(tmp_path: Path) -> None:
    review_path = tmp_path / "pr-123.yml"
    _write_review(
        review_path,
        [
            {"id": "F1", "description": "Fix flaky test", "required": True},
            {"id": "F2", "description": "Refactor docs", "required": False},
        ],
    )

    review = load_review(review_path)

    assert review.pr_number == 123
    assert len(review.follow_up_issues) == 2
    assert review.follow_up_issues[0].issue_id == "F1"
    assert review.follow_up_issues[1].required is False


def test_build_issue_body_links_review_and_pr() -> None:
    review = ReviewRecord(
        pr_number=77,
        reviewer="alice",
        date="2025-01-01",
        workstream="core",
        rubric_used="v1",
        follow_up_issues=(),
    )
    follow_up = FollowUpIssue(issue_id="R1", description="Fix bug", required=True)

    body = build_issue_body(
        review,
        follow_up,
        "reviews/2025-01/pr-77.yml",
        "org/repo",
    )

    assert "Source review: reviews/2025-01/pr-77.yml" in body
    assert "PR: https://github.com/org/repo/pull/77" in body
    assert "Follow-up ID: R1" in body


def test_process_review_skips_existing_issue(tmp_path: Path) -> None:
    review_path = tmp_path / "pr-123.yml"
    _write_review(
        review_path,
        [{"id": "F1", "description": "Fix flaky test", "required": True}],
    )
    runner = FakeGhRunner(list_payload=[{"number": 1}])

    actions = process_review(
        review_path,
        repo="org/repo",
        label="revision-required",
        include_optional=False,
        dry_run=False,
        runner=runner,
    )

    assert actions[0].status == "skipped"
    assert any(args[1:3] == ["issue", "list"] for args in runner.calls)
    assert not any(args[1:3] == ["issue", "create"] for args in runner.calls)


def test_process_review_creates_missing_issue(tmp_path: Path) -> None:
    review_path = tmp_path / "pr-123.yml"
    _write_review(
        review_path,
        [{"id": "F1", "description": "Fix flaky test", "required": True}],
    )
    runner = FakeGhRunner(list_payload=[])

    actions = process_review(
        review_path,
        repo="org/repo",
        label="revision-required",
        include_optional=False,
        dry_run=False,
        runner=runner,
    )

    assert actions[0].status == "created"
    create_calls = [args for args in runner.calls if args[1:3] == ["issue", "create"]]
    assert create_calls
    create_args = create_calls[0]
    assert "--label" in create_args
    assert "revision-required" in create_args
    body_index = create_args.index("--body") + 1
    assert "Source review:" in create_args[body_index]
    assert "PR: https://github.com/org/repo/pull/123" in create_args[body_index]
