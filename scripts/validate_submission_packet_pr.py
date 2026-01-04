#!/usr/bin/env python3
"""Validate submission packets from PR descriptions or linked files."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_submission_packet import (
    REQUIRED_SECTIONS,
    SECTION_LINE_RE,
    validate_submission_packet,
    validate_submission_packet_text,
)


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
PATH_RE = re.compile(r"(?P<path>[\w./-]*submission_packet\.md)", re.IGNORECASE)


def _body_has_section_labels(body: str) -> bool:
    for line in body.splitlines():
        match = SECTION_LINE_RE.match(line)
        if not match:
            continue
        label = match.group("label").strip()
        if any(
            pattern.search(label)
            for section in REQUIRED_SECTIONS
            for pattern in section.label_patterns
        ):
            return True
    return False


def _find_candidate_paths(body: str) -> list[str]:
    candidates: list[str] = []
    for match in LINK_RE.finditer(body):
        link_text = match.group(1).lower()
        link_target = match.group(2)
        if link_target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if "submission" not in link_text and "submission" not in link_target.lower():
            continue
        candidates.append(link_target)
    for match in PATH_RE.finditer(body):
        candidates.append(match.group("path"))
    seen: set[str] = set()
    unique: list[str] = []
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        unique.append(candidate)
    return unique


def _resolve_repo_path(candidate: str, repo_root: Path) -> Path | None:
    path_part = candidate.split("#", 1)[0].strip()
    if not path_part:
        return None
    raw_path = Path(path_part)
    resolved = raw_path if raw_path.is_absolute() else (repo_root / raw_path).resolve()
    repo_root = repo_root.resolve()
    if resolved == repo_root or repo_root in resolved.parents:
        return resolved
    return None


def _load_pr_body(event_path: Path) -> tuple[str | None, list[str]]:
    try:
        payload = json.loads(event_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, [f"{event_path}: failed to read event payload: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"{event_path}: invalid JSON payload: {exc}"]
    pr = payload.get("pull_request") or {}
    body = pr.get("body") or ""
    if not body.strip():
        return None, ["PR description is empty."]
    return body, []


def validate_pr_submission_packet(body: str, repo_root: Path) -> list[str]:
    errors: list[str] = []
    if _body_has_section_labels(body):
        errors.extend(
            validate_submission_packet_text(body, source="PR description")
        )
        if not errors:
            return []
    candidates = _find_candidate_paths(body)
    if not candidates:
        if errors:
            return errors
        return ["PR description does not include a submission packet or link."]
    for candidate in candidates:
        resolved = _resolve_repo_path(candidate, repo_root)
        if resolved is None:
            errors.append(f"{candidate}: linked path is outside the repository.")
            continue
        file_errors = validate_submission_packet(resolved)
        if not file_errors:
            return []
        errors.extend(file_errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate submission packet from PR description or linked files."
    )
    parser.add_argument(
        "--event-path",
        default=os.environ.get("GITHUB_EVENT_PATH"),
        help="Path to the GitHub event JSON payload.",
    )
    parser.add_argument(
        "--repo-root",
        default=os.environ.get("GITHUB_WORKSPACE", "."),
        help="Repository root for resolving linked files.",
    )
    parser.add_argument(
        "--body",
        help="PR description body (overrides --event-path).",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read PR description body from stdin.",
    )
    args = parser.parse_args(argv)

    if args.body is not None:
        body = args.body
        load_errors: list[str] = []
    elif args.stdin:
        body = sys.stdin.read()
        load_errors = []
    elif args.event_path:
        body, load_errors = _load_pr_body(Path(args.event_path))
        if body is None:
            body = ""
    else:
        body = ""
        load_errors = ["No PR description source provided."]

    errors = load_errors
    if not errors:
        errors = validate_pr_submission_packet(body, Path(args.repo_root))

    if errors:
        message = "Submission packet validation failed:\n" + "\n".join(
            f"- {error}" for error in errors
        )
        raise SystemExit(message)

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
