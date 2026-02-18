#!/usr/bin/env python
"""Collect Workflows ecosystem linkage status for the dashboard.

This script gathers information about:
- Workflow sync status (last sync date, source repo)
- Reusable workflow references and versions
- Agent automation status (keepalive enabled PRs)
- Sync manifest compliance
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

DEFAULT_WORKFLOWS_DIR = Path(".github/workflows")
DEFAULT_OUTPUT_PATH = Path("logs/ecosystem_status.json")
WORKFLOWS_REPO = "stranske/Workflows"


@dataclass(frozen=True)
class WorkflowReference:
    """A reference to an external reusable workflow."""

    workflow_file: str
    referenced_repo: str
    referenced_workflow: str
    ref: str  # branch/tag/sha


@dataclass(frozen=True)
class AgentPrStatus:
    """Status of agent automation on a PR."""

    pr_number: int
    title: str
    has_keepalive: bool
    has_agent_codex: bool
    state: str


@dataclass(frozen=True)
class EcosystemStatus:
    """Complete ecosystem linkage status."""

    collected_at: str
    workflows_source: str
    workflow_references: list[WorkflowReference]
    total_workflows: int
    workflows_using_reusable: int
    agent_prs: list[AgentPrStatus]
    keepalive_enabled_count: int
    last_sync_commit: str | None
    sync_workflow_exists: bool


def _parse_workflow_references(workflow_path: Path) -> list[WorkflowReference]:
    """Extract reusable workflow references from a workflow file."""
    references: list[WorkflowReference] = []

    try:
        content = workflow_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
    except (OSError, yaml.YAMLError):
        return references

    if not isinstance(data, dict):
        return references

    jobs = data.get("jobs", {})
    if not isinstance(jobs, dict):
        return references

    # Pattern: owner/repo/.github/workflows/file.yml@ref
    uses_pattern = re.compile(r"^([^/]+/[^/]+)/\.github/workflows/([^@]+)@(.+)$")

    for _job_name, job_config in jobs.items():
        if not isinstance(job_config, dict):
            continue
        uses = job_config.get("uses")
        if not isinstance(uses, str):
            continue

        match = uses_pattern.match(uses)
        if match:
            repo, workflow, ref = match.groups()
            references.append(
                WorkflowReference(
                    workflow_file=workflow_path.name,
                    referenced_repo=repo,
                    referenced_workflow=workflow,
                    ref=ref,
                )
            )

    return references


def _collect_workflow_references(workflows_dir: Path) -> list[WorkflowReference]:
    """Collect all reusable workflow references from local workflows."""
    all_references: list[WorkflowReference] = []

    if not workflows_dir.is_dir():
        return all_references

    for workflow_path in sorted(workflows_dir.glob("*.yml")):
        refs = _parse_workflow_references(workflow_path)
        all_references.extend(refs)

    for workflow_path in sorted(workflows_dir.glob("*.yaml")):
        refs = _parse_workflow_references(workflow_path)
        all_references.extend(refs)

    return all_references


def _get_agent_pr_status() -> list[AgentPrStatus]:
    """Get status of PRs with agent labels using gh CLI."""
    statuses: list[AgentPrStatus] = []

    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--state",
                "open",
                "--json",
                "number,title,labels",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return statuses

        prs = json.loads(result.stdout)
        for pr in prs:
            labels = [lbl.get("name", "") for lbl in pr.get("labels", [])]
            has_keepalive = "agents:keepalive" in labels
            has_agent_codex = "agent:codex" in labels

            if has_keepalive or has_agent_codex:
                statuses.append(
                    AgentPrStatus(
                        pr_number=pr.get("number", 0),
                        title=pr.get("title", ""),
                        has_keepalive=has_keepalive,
                        has_agent_codex=has_agent_codex,
                        state="open",
                    )
                )
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass

    return statuses


def _get_last_sync_commit() -> str | None:
    """Get the last commit that was a sync from Workflows."""
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--oneline",
                "--grep=sync",
                "-i",
                "-n",
                "1",
                "--format=%h %s",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def collect_ecosystem_status(
    workflows_dir: Path = DEFAULT_WORKFLOWS_DIR,
) -> EcosystemStatus:
    """Collect complete ecosystem linkage status."""
    references = _collect_workflow_references(workflows_dir)
    agent_prs = _get_agent_pr_status()
    last_sync = _get_last_sync_commit()

    # Count workflows
    total_workflows = 0
    if workflows_dir.is_dir():
        total_workflows = len(list(workflows_dir.glob("*.yml"))) + len(
            list(workflows_dir.glob("*.yaml"))
        )

    # Count workflows using reusable workflows
    workflows_using = len({ref.workflow_file for ref in references})

    # Check if sync-related workflow exists
    sync_workflow_exists = (
        workflows_dir / "maint-68-sync-consumer-repos.yml"
    ).exists() or any("sync" in f.name.lower() for f in workflows_dir.glob("*.yml"))

    return EcosystemStatus(
        collected_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
        workflows_source=WORKFLOWS_REPO,
        workflow_references=[
            WorkflowReference(
                workflow_file=r.workflow_file,
                referenced_repo=r.referenced_repo,
                referenced_workflow=r.referenced_workflow,
                ref=r.ref,
            )
            for r in references
        ],
        total_workflows=total_workflows,
        workflows_using_reusable=workflows_using,
        agent_prs=[
            AgentPrStatus(
                pr_number=p.pr_number,
                title=p.title,
                has_keepalive=p.has_keepalive,
                has_agent_codex=p.has_agent_codex,
                state=p.state,
            )
            for p in agent_prs
        ],
        keepalive_enabled_count=sum(1 for p in agent_prs if p.has_keepalive),
        last_sync_commit=last_sync,
        sync_workflow_exists=sync_workflow_exists,
    )


def _dataclass_to_dict(obj: Any) -> Any:
    """Convert dataclass to dict recursively."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _dataclass_to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [_dataclass_to_dict(item) for item in obj]
    return obj


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Collect Workflows ecosystem linkage status."
    )
    parser.add_argument(
        "--workflows-dir",
        type=Path,
        default=DEFAULT_WORKFLOWS_DIR,
        help="Directory containing workflow files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output JSON file path.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print to stdout instead of file.",
    )

    args = parser.parse_args(argv)

    status = collect_ecosystem_status(workflows_dir=args.workflows_dir)
    data = _dataclass_to_dict(status)

    if args.stdout:
        print(json.dumps(data, indent=2))
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Ecosystem status written to {args.output}")

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
