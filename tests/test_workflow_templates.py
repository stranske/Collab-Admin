"""Tests for workflow templates."""

from pathlib import Path


def test_auto_revision_workflow_template_triggers_review_paths() -> None:
    """Workflow template should target review file changes."""
    repo_root = Path(__file__).resolve().parents[1]
    template = repo_root / "templates" / "auto-revision-issues.yml"
    content = template.read_text(encoding="utf-8")

    assert "push:" in content
    assert "pull_request:" in content
    assert "reviews/**/*.yml" in content
    assert "reviews/**/*.yaml" in content


def test_auto_revision_workflow_template_notes_manual_copy() -> None:
    """Template should document the manual workflow copy step."""
    repo_root = Path(__file__).resolve().parents[1]
    template = repo_root / "templates" / "auto-revision-issues.yml"
    content = template.read_text(encoding="utf-8")

    assert "needs-human" in content
