"""GitHub API client for dashboard integration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests

GITHUB_API = "https://api.github.com"
DEFAULT_REPO = "stranske/Collab-Admin"


@dataclass
class Issue:
    """GitHub issue/PR data."""

    number: int
    title: str
    state: str
    created_at: datetime
    updated_at: datetime
    labels: list[str]
    author: str
    is_pr: bool
    url: str


@dataclass
class WorkflowRun:
    """GitHub Actions workflow run data."""

    name: str
    status: str
    conclusion: str | None
    created_at: datetime
    head_branch: str
    url: str


@dataclass
class GitHubData:
    """Container for all GitHub data."""

    issues: list[Issue]
    pull_requests: list[Issue]
    workflow_runs: list[WorkflowRun]
    error: str | None = None


def get_github_token() -> str | None:
    """Get GitHub token from environment."""
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def _parse_datetime(dt_str: str) -> datetime:
    """Parse ISO datetime string."""
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


def _make_request(
    endpoint: str, token: str | None = None
) -> dict[str, Any] | list[Any] | None:
    """Make authenticated request to GitHub API."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(f"{GITHUB_API}{endpoint}", headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def fetch_issues(repo: str = DEFAULT_REPO, token: str | None = None) -> list[Issue]:
    """Fetch open issues (not PRs) from repository."""
    data = _make_request(f"/repos/{repo}/issues?state=all&per_page=50", token)
    if not data or not isinstance(data, list):
        return []

    issues = []
    for item in data:
        # Skip PRs (they appear in issues endpoint too)
        if "pull_request" in item:
            continue
        issues.append(
            Issue(
                number=item["number"],
                title=item["title"],
                state=item["state"],
                created_at=_parse_datetime(item["created_at"]),
                updated_at=_parse_datetime(item["updated_at"]),
                labels=[label["name"] for label in item.get("labels", [])],
                author=item["user"]["login"],
                is_pr=False,
                url=item["html_url"],
            )
        )
    return issues


def fetch_pull_requests(
    repo: str = DEFAULT_REPO, token: str | None = None
) -> list[Issue]:
    """Fetch pull requests from repository."""
    data = _make_request(f"/repos/{repo}/pulls?state=all&per_page=30", token)
    if not data or not isinstance(data, list):
        return []

    prs = []
    for item in data:
        prs.append(
            Issue(
                number=item["number"],
                title=item["title"],
                state=item["state"],
                created_at=_parse_datetime(item["created_at"]),
                updated_at=_parse_datetime(item["updated_at"]),
                labels=[label["name"] for label in item.get("labels", [])],
                author=item["user"]["login"],
                is_pr=True,
                url=item["html_url"],
            )
        )
    return prs


def fetch_workflow_runs(
    repo: str = DEFAULT_REPO, token: str | None = None
) -> list[WorkflowRun]:
    """Fetch recent workflow runs from repository."""
    data = _make_request(f"/repos/{repo}/actions/runs?per_page=20", token)
    if not data or not isinstance(data, dict):
        return []

    runs = []
    for item in data.get("workflow_runs", []):
        runs.append(
            WorkflowRun(
                name=item["name"],
                status=item["status"],
                conclusion=item.get("conclusion"),
                created_at=_parse_datetime(item["created_at"]),
                head_branch=item["head_branch"],
                url=item["html_url"],
            )
        )
    return runs


def fetch_all_github_data(repo: str = DEFAULT_REPO) -> GitHubData:
    """Fetch all GitHub data for dashboard."""
    token = get_github_token()

    try:
        issues = fetch_issues(repo, token)
        prs = fetch_pull_requests(repo, token)
        runs = fetch_workflow_runs(repo, token)
        return GitHubData(issues=issues, pull_requests=prs, workflow_runs=runs)
    except Exception as e:
        return GitHubData(
            issues=[],
            pull_requests=[],
            workflow_runs=[],
            error=f"Failed to fetch GitHub data: {e}",
        )
