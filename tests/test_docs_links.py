"""Validate that local documentation links resolve to existing files."""

from __future__ import annotations

import re
from pathlib import Path

LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")


def _collect_missing_doc_links(repo_root: Path) -> list[tuple[Path, str]]:
    docs_dir = repo_root / "docs"
    missing: list[tuple[Path, str]] = []

    for doc_path in docs_dir.rglob("*.md"):
        content = doc_path.read_text(encoding="utf-8")
        for raw_link in LINK_PATTERN.findall(content):
            link = raw_link.strip()
            if not link or link.startswith("#") or link.startswith("mailto:"):
                continue
            if "://" in link:
                continue

            link_path = link.split("#", 1)[0]
            if not link_path:
                continue

            if link_path.startswith("/"):
                target = repo_root / link_path.lstrip("/")
            else:
                target = (doc_path.parent / link_path).resolve()

            if not target.exists():
                missing.append((doc_path, link))

    return missing


def test_docs_links_are_resolvable() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    missing = _collect_missing_doc_links(repo_root)

    assert not missing, "Missing doc links:\n" + "\n".join(
        f"- {path.relative_to(repo_root)} -> {link}" for path, link in missing
    )
