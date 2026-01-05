#!/usr/bin/env python3
"""Validate submission packet markdown for required sections."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RequiredSection:
    name: str
    label_patterns: tuple[re.Pattern[str], ...]
    value_pattern: re.Pattern[str]


REQUIRED_SECTIONS = (
    RequiredSection(
        name="Issue",
        label_patterns=(re.compile(r"^issue\b", re.IGNORECASE),),
        value_pattern=re.compile(r"\d"),
    ),
    RequiredSection(
        name="Workstream",
        label_patterns=(re.compile(r"^workstream\b", re.IGNORECASE),),
        value_pattern=re.compile(r"[A-Za-z0-9]"),
    ),
    RequiredSection(
        name="Deliverables",
        label_patterns=(
            re.compile(r"^deliverables\b", re.IGNORECASE),
            re.compile(r"^deliverables included\b", re.IGNORECASE),
        ),
        value_pattern=re.compile(r"[A-Za-z0-9]"),
    ),
    RequiredSection(
        name="How to run/test",
        label_patterns=(
            re.compile(r"^how to run/test\b", re.IGNORECASE),
            re.compile(r"^how to run\b", re.IGNORECASE),
            re.compile(r"^how to test\b", re.IGNORECASE),
        ),
        value_pattern=re.compile(r"[A-Za-z0-9]"),
    ),
    RequiredSection(
        name="Evidence",
        label_patterns=(re.compile(r"^evidence\b", re.IGNORECASE),),
        value_pattern=re.compile(r"[A-Za-z0-9]"),
    ),
)

SECTION_LINE_RE = re.compile(r"^\s*[-*]\s+(?P<label>[^:]+):\s*(?P<value>.*)$")


def _extract_section_values(markdown: str) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {section.name: [] for section in REQUIRED_SECTIONS}
    for line in markdown.splitlines():
        match = SECTION_LINE_RE.match(line)
        if not match:
            continue
        label = match.group("label").strip()
        value = match.group("value").strip()
        for section in REQUIRED_SECTIONS:
            if any(pattern.search(label) for pattern in section.label_patterns):
                values[section.name].append(value)
                break
    return values


def _validate_sections(markdown: str, source: str) -> list[str]:
    values = _extract_section_values(markdown)
    errors: list[str] = []
    for section in REQUIRED_SECTIONS:
        entries = values.get(section.name, [])
        if not entries:
            errors.append(f"{source}: missing required section: {section.name}.")
            continue
        if not any(section.value_pattern.search(entry or "") for entry in entries):
            errors.append(f"{source}: {section.name} is missing a value.")
    return errors


def validate_submission_packet(path: Path) -> list[str]:
    if not path.exists():
        return [f"{path}: file does not exist."]
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path}: failed to read file: {exc}"]
    return _validate_sections(content, str(path))


def validate_submission_packet_text(text: str, source: str = "stdin") -> list[str]:
    return _validate_sections(text, source)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate submission packet markdown for required sections."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Path to submission packet markdown file.",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read submission packet markdown from stdin.",
    )
    args = parser.parse_args(argv)

    if args.stdin:
        content = sys.stdin.read()
        errors = validate_submission_packet_text(content)
    else:
        if args.path is None:
            errors = ["No submission packet path provided."]
        else:
            errors = validate_submission_packet(Path(args.path))

    if errors:
        message = "Submission packet validation failed:\n" + "\n".join(
            f"- {error}" for error in errors
        )
        raise SystemExit(message)

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
