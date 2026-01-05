"""Tests for workflow templates."""

from pathlib import Path

import yaml


def test_auto_revision_workflow_template_triggers_review_paths() -> None:
    """Workflow template should target review file changes."""
    repo_root = Path(__file__).resolve().parents[1]
    template = repo_root / "templates" / "auto-revision-issues.yml"
    content = template.read_text(encoding="utf-8")
    payload = yaml.safe_load(content)
    on_block = payload.get("on")
    if on_block is None and True in payload:
        on_block = payload[True]
    assert isinstance(on_block, dict)

    push = on_block.get("push")
    pull_request = on_block.get("pull_request")
    assert isinstance(push, dict)
    assert isinstance(pull_request, dict)

    push_paths = push.get("paths")
    pr_paths = pull_request.get("paths")
    assert "reviews/**/*.yml" in push_paths
    assert "reviews/**/*.yaml" in push_paths
    assert "reviews/**/*.yml" in pr_paths
    assert "reviews/**/*.yaml" in pr_paths

    pr_types = pull_request.get("types")
    assert "ready_for_review" in pr_types


def test_auto_revision_workflow_template_notes_manual_copy() -> None:
    """Template should document the manual workflow copy step."""
    repo_root = Path(__file__).resolve().parents[1]
    template = repo_root / "templates" / "auto-revision-issues.yml"
    content = template.read_text(encoding="utf-8")

    assert "needs-human" in content
