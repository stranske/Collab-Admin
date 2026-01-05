"""Tests for validate_trend_references script."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    script_path = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "validate_trend_references.py"
    )
    spec = importlib.util.spec_from_file_location(
        "validate_trend_references", script_path
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validate_trend_references = load_module()


def build_markdown(refs_by_category: dict[str, list[str]]) -> str:
    lines = ["# Trend Memo", "## References"]
    for category, refs in refs_by_category.items():
        lines.append(f"### {category}")
        for ref in refs:
            lines.append(f"- {ref} - rationale")
    return "\n".join(lines) + "\n"


def generate_refs(prefix: str, count: int, start_line: int = 1) -> list[str]:
    refs = []
    for i in range(count):
        start = start_line + i * 2
        end = start + 1
        refs.append(f"{prefix}#L{start}-L{end}")
    return refs


def test_valid_references_pass(tmp_path: Path) -> None:
    markdown = build_markdown(
        {
            "Entrypoints": generate_refs("src/app.py", 2, 1),
            "Core call paths": generate_refs("src/app.py", 2, 5),
            "Error/edge paths": generate_refs("src/app.py", 2, 9),
            "Data boundaries/config/parsing": generate_refs("src/app.py", 2, 13),
            "Change hotspots": generate_refs("src/app.py", 2, 17),
        }
    )

    errors = validate_trend_references.validate_trend_references_text(markdown)

    assert errors == []


def test_malformed_reference_reported() -> None:
    markdown = "\n".join(
        [
            "# Trend Memo",
            "## References",
            "### Entrypoints",
            "- src/app.py#L1-L2 missing desc",
            "### Core call paths",
            "- src/app.py#L3-L4 - ok",
            "- src/app.py#L5-L6 - ok",
            "### Error/edge paths",
            "- src/app.py#L7-L8 - ok",
            "- src/app.py#L9-L10 - ok",
            "### Data boundaries/config/parsing",
            "- src/app.py#L11-L12 - ok",
            "- src/app.py#L13-L14 - ok",
            "### Change hotspots",
            "- src/app.py#L15-L16 - ok",
            "- src/app.py#L17-L18 - ok",
        ]
    )

    errors = validate_trend_references.validate_trend_references_text(markdown)

    assert any("malformed reference" in err for err in errors)


def test_check_files_validates_line_ranges(tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    app_path = src_dir / "app.py"
    app_path.write_text("\n".join(f"line {i}" for i in range(1, 7)), encoding="utf-8")

    refs = {
        "Entrypoints": ["src/app.py#L1-L2", "src/app.py#L3-L4"],
        "Core call paths": ["src/app.py#L1-L2", "src/app.py#L3-L4"],
        "Error/edge paths": ["src/app.py#L1-L2", "src/app.py#L3-L4"],
        "Data boundaries/config/parsing": ["src/app.py#L1-L2", "src/app.py#L3-L4"],
        "Change hotspots": ["src/app.py#L1-L2", "src/app.py#L10-L12"],
    }
    markdown = build_markdown(refs)

    errors = validate_trend_references.validate_trend_references_text(
        markdown, check_files=True, base_dir=tmp_path
    )

    assert any("outside" in err for err in errors)


def test_category_minimums_enforced() -> None:
    markdown = build_markdown(
        {
            "Entrypoints": generate_refs("src/app.py", 1, 1),
            "Core call paths": generate_refs("src/app.py", 2, 5),
            "Error/edge paths": generate_refs("src/app.py", 2, 9),
            "Data boundaries/config/parsing": generate_refs("src/app.py", 2, 13),
            "Change hotspots": generate_refs("src/app.py", 2, 17),
        }
    )

    errors = validate_trend_references.validate_trend_references_text(markdown)

    assert any("Insufficient entrypoints references" in err for err in errors)
