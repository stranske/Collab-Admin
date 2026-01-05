#!/usr/bin/env python3
"""Validate trend memo references in markdown files."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Reference:
    path: str
    start_line: int
    end_line: int
    description: str
    source: str
    source_line: int
    category: str | None


CATEGORY_ALIASES = {
    "entrypoints": ("entrypoints", "entry points", "entrypoint"),
    "call_paths": ("core call paths", "call paths", "call path"),
    "error_paths": ("error/edge paths", "error paths", "edge paths", "edge path"),
    "data_boundaries": (
        "data boundaries",
        "data boundary",
        "config",
        "configuration",
        "parsing",
    ),
    "hotspots": (
        "change hotspots",
        "hotspots",
        "hotspot",
        "what i'd fix first",
        "what i\u2019d fix first",
    ),
}

CATEGORY_LABELS = {
    "entrypoints": "entrypoints",
    "call_paths": "call paths",
    "error_paths": "error/edge paths",
    "data_boundaries": "data boundaries",
    "hotspots": "change hotspots",
}

CATEGORY_MINIMUMS = {
    "entrypoints": 2,
    "call_paths": 2,
    "error_paths": 2,
    "data_boundaries": 2,
    "hotspots": 2,
}

REFERENCE_RE = re.compile(
    r"(?P<path>[A-Za-z0-9_./-]+)"
    r"#L(?P<start>\d+)-L(?P<end>\d+)"
    r"\s*(?:\u2014|-)\s*(?P<desc>.+)"
)

REFERENCE_CORE_RE = re.compile(
    r"(?P<path>[A-Za-z0-9_./-]+)#L(?P<start>\d+)-L(?P<end>\d+)"
)

HEADING_RE = re.compile(r"^\s*(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*$")


def _normalize_category(text: str) -> str | None:
    lowered = text.lower()
    for key, aliases in CATEGORY_ALIASES.items():
        if any(alias in lowered for alias in aliases):
            return key
    return None


def _extract_category(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None

    if stripped.startswith("#"):
        heading = stripped.lstrip("#").strip()
        return _normalize_category(heading)

    is_label = stripped.endswith(":")
    is_bold = stripped.startswith("**") and stripped.endswith("**")
    if not (is_label or is_bold):
        return None

    text = stripped
    if is_label:
        text = text[:-1].strip()
    if is_bold:
        text = text[2:-2].strip()
    return _normalize_category(text)


def _resolve_reference_path(base_dir: Path, source_dir: Path, ref_path: str) -> Path | None:
    candidate = Path(ref_path)
    if candidate.is_absolute():
        return candidate

    for root in (source_dir, base_dir):
        resolved = (root / ref_path).resolve()
        if resolved.exists():
            return resolved
    return None


def _parse_references(
    markdown: str, source: str
) -> tuple[list[Reference], list[str], bool]:
    references: list[Reference] = []
    errors: list[str] = []
    current_category: str | None = None
    in_references = False
    references_heading_level: int | None = None
    found_references = False

    for line_number, line in enumerate(markdown.splitlines(), start=1):
        heading_match = HEADING_RE.match(line)
        if heading_match:
            title = heading_match.group("title").strip()
            level = len(heading_match.group("hashes"))
            if "references" in title.lower():
                in_references = True
                references_heading_level = level
                current_category = None
                found_references = True
                continue
            if (
                in_references
                and references_heading_level is not None
                and level <= references_heading_level
            ):
                in_references = False
                current_category = None

        if not in_references:
            continue

        category = _extract_category(line)
        if category:
            current_category = category
            continue

        matches = list(REFERENCE_RE.finditer(line))
        if matches:
            for match in matches:
                start = int(match.group("start"))
                end = int(match.group("end"))
                description = match.group("desc").strip()
                ref_category = current_category
                if not ref_category:
                    errors.append(
                        f"{source}:{line_number}: reference missing category heading."
                    )
                if end < start:
                    errors.append(
                        f"{source}:{line_number}: invalid line range L{start}-L{end}."
                    )
                if not description:
                    errors.append(
                        f"{source}:{line_number}: reference missing description."
                    )
                references.append(
                    Reference(
                        path=match.group("path"),
                        start_line=start,
                        end_line=end,
                        description=description,
                        source=source,
                        source_line=line_number,
                        category=ref_category,
                    )
                )
            continue

        if "#L" in line and REFERENCE_CORE_RE.search(line):
            errors.append(
                f"{source}:{line_number}: malformed reference, expected "
                "'path#Lx-Ly — description'."
            )
        elif "#L" in line:
            errors.append(f"{source}:{line_number}: malformed reference.")

    if not found_references:
        errors.append(f"{source}: missing References section.")

    return references, errors, found_references


def _check_reference_files(
    references: list[Reference], base_dir: Path, source_dir: Path
) -> list[str]:
    errors: list[str] = []
    for ref in references:
        resolved = _resolve_reference_path(base_dir, source_dir, ref.path)
        if resolved is None:
            errors.append(
                f"{ref.source}:{ref.source_line}: file not found for {ref.path}."
            )
            continue
        try:
            lines = resolved.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            errors.append(
                f"{ref.source}:{ref.source_line}: failed to read {resolved}: {exc}."
            )
            continue
        if ref.start_line < 1 or ref.end_line > len(lines):
            errors.append(
                f"{ref.source}:{ref.source_line}: line range L{ref.start_line}-"
                f"L{ref.end_line} is outside {resolved} (1-{len(lines)})."
            )
    return errors


def _check_category_minimums(references: list[Reference]) -> list[str]:
    counts = {key: 0 for key in CATEGORY_MINIMUMS}
    for ref in references:
        if ref.category in counts:
            counts[ref.category] += 1
    errors: list[str] = []
    for key, minimum in CATEGORY_MINIMUMS.items():
        if counts[key] < minimum:
            label = CATEGORY_LABELS.get(key, key)
            errors.append(
                f"Insufficient {label} references: {counts[key]} found, "
                f"{minimum}+ required."
            )
    return errors


def validate_trend_references_text(
    markdown: str,
    source: str = "stdin",
    check_files: bool = False,
    base_dir: Path | None = None,
) -> list[str]:
    base_dir = base_dir or Path.cwd()
    references, errors, _ = _parse_references(markdown, source)
    errors.extend(_check_category_minimums(references))
    if check_files:
        errors.extend(_check_reference_files(references, base_dir, base_dir))
    return errors


def validate_trend_references(path: Path, check_files: bool = False) -> list[str]:
    if not path.exists():
        return [f"{path}: file does not exist."]
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path}: failed to read file: {exc}"]

    references, errors, _ = _parse_references(content, str(path))
    errors.extend(_check_category_minimums(references))
    if check_files:
        errors.extend(
            _check_reference_files(references, Path.cwd(), path.parent.resolve())
        )
    return errors


def _collect_markdown_files(paths: list[Path]) -> list[Path]:
    markdown_files: list[Path] = []
    for path in paths:
        if path.is_dir():
            markdown_files.extend(sorted(path.rglob("*.md")))
        else:
            markdown_files.append(path)
    return markdown_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Trend memo references in markdown."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=[],
        help="Markdown files or directories to check.",
    )
    parser.add_argument(
        "--check-files",
        action="store_true",
        help="Verify referenced files exist and line ranges are valid.",
    )
    args = parser.parse_args(argv)

    if not args.paths:
        errors = ["No markdown paths provided."]
    else:
        errors = []
        for markdown_path in _collect_markdown_files([Path(p) for p in args.paths]):
            errors.extend(
                validate_trend_references(markdown_path, check_files=args.check_files)
            )

    if errors:
        message = "Trend reference validation failed:\n" + "\n".join(
            f"- {error}" for error in errors
        )
        raise SystemExit(message)

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
