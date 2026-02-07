"""Tests for log templates and directory layout."""

from pathlib import Path


def test_log_directories_exist() -> None:
    """Log directories should exist for each log type."""
    repo_root = Path(__file__).resolve().parents[1]
    for path in (
        repo_root / "logs" / "time",
        repo_root / "logs" / "expenses",
        repo_root / "logs" / "friction",
        repo_root / "logs" / "month_end",
    ):
        assert path.is_dir()


def test_csv_templates_match_policy_headers() -> None:
    """CSV templates should match policy-defined headers."""
    repo_root = Path(__file__).resolve().parents[1]
    templates = {
        repo_root
        / "logs"
        / "expenses"
        / "expense_template.csv": (
            "date,amount,currency,category,description,receipt_link,issue_or_pr,preapproval_link"
        ),
        repo_root
        / "logs"
        / "friction"
        / "friction_template.csv": (
            "date,repo,context,minutes_lost,what_broke,what_was_confusing,what_fixed_it,pr_or_issue"
        ),
        repo_root
        / "logs"
        / "time_log_template.csv": (
            "date,hours,repo,issue_or_pr,category,description,artifact_link"
        ),
    }
    for path, expected_header in templates.items():
        header = path.read_text(encoding="utf-8").splitlines()[0]
        assert header == expected_header


def test_month_end_template_sections() -> None:
    """Month-end template should include required sections."""
    repo_root = Path(__file__).resolve().parents[1]
    template = repo_root / "logs" / "month_end" / "template.md"
    content = template.read_text(encoding="utf-8")
    for section in (
        "## Hours Summary",
        "## Deliverables",
        "## Reviews",
        "## Expenses",
    ):
        assert section in content
