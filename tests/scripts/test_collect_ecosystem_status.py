"""Tests for collect_ecosystem_status.py."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.collect_ecosystem_status import (
    EcosystemStatus,
    WorkflowReference,
    _collect_workflow_references,
    _parse_workflow_references,
    collect_ecosystem_status,
)


class TestParseWorkflowReferences:
    """Tests for _parse_workflow_references."""

    def test_extracts_reusable_workflow_reference(self, tmp_path: Path) -> None:
        """Test parsing a workflow file with reusable workflow references."""
        workflow = tmp_path / "test.yml"
        workflow.write_text(
            """
name: Test
on: push
jobs:
  python-ci:
    uses: stranske/Workflows/.github/workflows/reusable-10-ci-python.yml@main
  docker:
    uses: stranske/Workflows/.github/workflows/reusable-12-ci-docker.yml@v2.0.0
"""
        )
        refs = _parse_workflow_references(workflow)
        assert len(refs) == 2
        assert refs[0].referenced_repo == "stranske/Workflows"
        assert refs[0].referenced_workflow == "reusable-10-ci-python.yml"
        assert refs[0].ref == "main"
        assert refs[1].referenced_workflow == "reusable-12-ci-docker.yml"
        assert refs[1].ref == "v2.0.0"

    def test_no_reusable_workflows(self, tmp_path: Path) -> None:
        """Test parsing a workflow without reusable references."""
        workflow = tmp_path / "test.yml"
        workflow.write_text(
            """
name: Test
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
"""
        )
        refs = _parse_workflow_references(workflow)
        assert len(refs) == 0

    def test_invalid_yaml(self, tmp_path: Path) -> None:
        """Test handling invalid YAML."""
        workflow = tmp_path / "test.yml"
        workflow.write_text("invalid: yaml: content:")
        refs = _parse_workflow_references(workflow)
        assert len(refs) == 0

    def test_missing_file(self, tmp_path: Path) -> None:
        """Test handling missing file."""
        workflow = tmp_path / "nonexistent.yml"
        refs = _parse_workflow_references(workflow)
        assert len(refs) == 0


class TestCollectWorkflowReferences:
    """Tests for _collect_workflow_references."""

    def test_collects_from_directory(self, tmp_path: Path) -> None:
        """Test collecting references from multiple workflow files."""
        workflows_dir = tmp_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)

        (workflows_dir / "ci.yml").write_text(
            """
name: CI
on: push
jobs:
  test:
    uses: stranske/Workflows/.github/workflows/reusable-10-ci-python.yml@main
"""
        )
        (workflows_dir / "gate.yml").write_text(
            """
name: Gate
on: pull_request
jobs:
  gate:
    uses: stranske/Workflows/.github/workflows/reusable-gate.yml@main
"""
        )

        refs = _collect_workflow_references(workflows_dir)
        assert len(refs) == 2

    def test_missing_directory(self, tmp_path: Path) -> None:
        """Test handling missing directory."""
        refs = _collect_workflow_references(tmp_path / "nonexistent")
        assert len(refs) == 0


class TestCollectEcosystemStatus:
    """Tests for collect_ecosystem_status."""

    @patch("scripts.collect_ecosystem_status._get_agent_pr_status")
    @patch("scripts.collect_ecosystem_status._get_last_sync_commit")
    def test_collects_complete_status(
        self,
        mock_sync: MagicMock,
        mock_prs: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test collecting complete ecosystem status."""
        mock_prs.return_value = []
        mock_sync.return_value = "abc123 chore: sync from Workflows"

        workflows_dir = tmp_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)
        (workflows_dir / "test.yml").write_text(
            """
name: Test
on: push
jobs:
  test:
    uses: stranske/Workflows/.github/workflows/reusable-ci.yml@main
"""
        )

        status = collect_ecosystem_status(workflows_dir=workflows_dir)

        assert status.workflows_source == "stranske/Workflows"
        assert status.total_workflows == 1
        assert status.workflows_using_reusable == 1
        assert len(status.workflow_references) == 1
        assert status.last_sync_commit == "abc123 chore: sync from Workflows"

    @patch("scripts.collect_ecosystem_status._get_agent_pr_status")
    @patch("scripts.collect_ecosystem_status._get_last_sync_commit")
    def test_empty_workflows_directory(
        self,
        mock_sync: MagicMock,
        mock_prs: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test handling empty workflows directory."""
        mock_prs.return_value = []
        mock_sync.return_value = None

        workflows_dir = tmp_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)

        status = collect_ecosystem_status(workflows_dir=workflows_dir)

        assert status.total_workflows == 0
        assert status.workflows_using_reusable == 0
        assert len(status.workflow_references) == 0
