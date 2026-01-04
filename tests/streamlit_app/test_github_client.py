"""Tests for GitHub client module."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from streamlit_app.github_client import (
    GitHubData,
    Issue,
    WorkflowRun,
    _parse_datetime,
    fetch_all_github_data,
    fetch_issues,
    fetch_pull_requests,
    fetch_workflow_runs,
)


def test_parse_datetime_zulu() -> None:
    """Parse ISO datetime with Z suffix."""
    result = _parse_datetime("2026-01-04T12:00:00Z")
    assert result.year == 2026
    assert result.month == 1
    assert result.day == 4
    assert result.hour == 12


def test_parse_datetime_offset() -> None:
    """Parse ISO datetime with offset."""
    result = _parse_datetime("2026-01-04T12:00:00+00:00")
    assert result.year == 2026


def test_issue_dataclass() -> None:
    """Issue dataclass stores all fields."""
    issue = Issue(
        number=1,
        title="Test",
        state="open",
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
        labels=["bug"],
        author="test-user",
        is_pr=False,
        url="https://github.com/test/repo/issues/1",
    )
    assert issue.number == 1
    assert issue.state == "open"
    assert not issue.is_pr


def test_workflow_run_dataclass() -> None:
    """WorkflowRun dataclass stores all fields."""
    run = WorkflowRun(
        name="CI",
        status="completed",
        conclusion="success",
        created_at=datetime.now(tz=UTC),
        head_branch="main",
        url="https://github.com/test/repo/actions/runs/1",
    )
    assert run.name == "CI"
    assert run.conclusion == "success"


def test_github_data_with_error() -> None:
    """GitHubData can store error message."""
    data = GitHubData(issues=[], pull_requests=[], workflow_runs=[], error="API error")
    assert data.error == "API error"


@patch("streamlit_app.github_client._make_request")
def test_fetch_issues_filters_prs(mock_request: MagicMock) -> None:
    """fetch_issues excludes pull requests."""
    mock_request.return_value = [
        {
            "number": 1,
            "title": "Issue",
            "state": "open",
            "created_at": "2026-01-04T12:00:00Z",
            "updated_at": "2026-01-04T12:00:00Z",
            "labels": [],
            "user": {"login": "user1"},
            "html_url": "https://github.com/test/repo/issues/1",
        },
        {
            "number": 2,
            "title": "PR",
            "state": "open",
            "created_at": "2026-01-04T12:00:00Z",
            "updated_at": "2026-01-04T12:00:00Z",
            "labels": [],
            "user": {"login": "user2"},
            "html_url": "https://github.com/test/repo/pull/2",
            "pull_request": {"url": "..."},
        },
    ]

    issues = fetch_issues("test/repo")

    assert len(issues) == 1
    assert issues[0].number == 1
    assert issues[0].title == "Issue"


@patch("streamlit_app.github_client._make_request")
def test_fetch_issues_handles_none(mock_request: MagicMock) -> None:
    """fetch_issues returns empty list on API failure."""
    mock_request.return_value = None

    issues = fetch_issues("test/repo")

    assert issues == []


@patch("streamlit_app.github_client._make_request")
def test_fetch_pull_requests(mock_request: MagicMock) -> None:
    """fetch_pull_requests parses PR data."""
    mock_request.return_value = [
        {
            "number": 10,
            "title": "Add feature",
            "state": "open",
            "created_at": "2026-01-04T10:00:00Z",
            "updated_at": "2026-01-04T11:00:00Z",
            "labels": [{"name": "enhancement"}],
            "user": {"login": "contributor"},
            "html_url": "https://github.com/test/repo/pull/10",
        },
    ]

    prs = fetch_pull_requests("test/repo")

    assert len(prs) == 1
    assert prs[0].number == 10
    assert prs[0].is_pr is True
    assert "enhancement" in prs[0].labels


@patch("streamlit_app.github_client._make_request")
def test_fetch_workflow_runs(mock_request: MagicMock) -> None:
    """fetch_workflow_runs parses workflow data."""
    mock_request.return_value = {
        "workflow_runs": [
            {
                "name": "CI",
                "status": "completed",
                "conclusion": "success",
                "created_at": "2026-01-04T12:00:00Z",
                "head_branch": "main",
                "html_url": "https://github.com/test/repo/actions/runs/1",
            },
        ]
    }

    runs = fetch_workflow_runs("test/repo")

    assert len(runs) == 1
    assert runs[0].name == "CI"
    assert runs[0].conclusion == "success"


@patch("streamlit_app.github_client._make_request")
def test_fetch_workflow_runs_handles_none(mock_request: MagicMock) -> None:
    """fetch_workflow_runs returns empty on API failure."""
    mock_request.return_value = None

    runs = fetch_workflow_runs("test/repo")

    assert runs == []


@patch("streamlit_app.github_client.fetch_issues")
@patch("streamlit_app.github_client.fetch_pull_requests")
@patch("streamlit_app.github_client.fetch_workflow_runs")
def test_fetch_all_github_data(
    mock_runs: MagicMock,
    mock_prs: MagicMock,
    mock_issues: MagicMock,
) -> None:
    """fetch_all_github_data aggregates all data."""
    mock_issues.return_value = [
        Issue(
            1,
            "Issue",
            "open",
            datetime.now(tz=UTC),
            datetime.now(tz=UTC),
            [],
            "user",
            False,
            "url",
        )
    ]
    mock_prs.return_value = []
    mock_runs.return_value = []

    data = fetch_all_github_data("test/repo")

    assert len(data.issues) == 1
    assert data.error is None
