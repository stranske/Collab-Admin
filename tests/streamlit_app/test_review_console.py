"""Tests for Review Console module."""

from datetime import date
from pathlib import Path

from streamlit_app.review_console import (
    generate_review_yaml,
    load_rubric_dimensions,
    load_rubric_levels,
    load_rubric_options,
)


def test_load_rubric_options_from_directory(tmp_path: Path) -> None:
    """Load rubric IDs from directory."""
    (tmp_path / "writing_quality.yml").write_text("rubric_id: writing_quality")
    (tmp_path / "agent_integration.yml").write_text("rubric_id: agent_integration")
    (tmp_path / "rubric_index.yml").write_text("# index file")

    options = load_rubric_options(tmp_path)

    assert "writing_quality" in options
    assert "agent_integration" in options
    assert "rubric_index" not in options  # Index should be excluded


def test_load_rubric_options_missing_dir(tmp_path: Path) -> None:
    """Return empty list for missing directory."""
    missing = tmp_path / "nonexistent"

    options = load_rubric_options(missing)

    assert options == []


def test_load_rubric_dimensions(tmp_path: Path) -> None:
    """Load dimensions from rubric file."""
    rubric = tmp_path / "test.yml"
    rubric.write_text(
        """
rubric_id: test
dimensions:
  - id: dim1
    name: First Dimension
  - id: dim2
    name: Second Dimension
"""
    )

    dimensions = load_rubric_dimensions(rubric)

    assert len(dimensions) == 2
    assert dimensions[0]["id"] == "dim1"
    assert dimensions[1]["name"] == "Second Dimension"


def test_load_rubric_dimensions_missing_file(tmp_path: Path) -> None:
    """Return empty list for missing file."""
    missing = tmp_path / "nonexistent.yml"

    dimensions = load_rubric_dimensions(missing)

    assert dimensions == []


def test_load_rubric_levels(tmp_path: Path) -> None:
    """Load levels from rubric file."""
    rubric = tmp_path / "test.yml"
    rubric.write_text(
        """
rubric_id: test
levels: [Bad, OK, Good, Great]
"""
    )

    levels = load_rubric_levels(rubric)

    assert levels == ["Bad", "OK", "Good", "Great"]


def test_load_rubric_levels_default(tmp_path: Path) -> None:
    """Return default levels if not specified."""
    rubric = tmp_path / "test.yml"
    rubric.write_text("rubric_id: test")

    levels = load_rubric_levels(rubric)

    assert levels == ["Poor", "Mediocre", "High", "Excellent"]


def test_load_rubric_levels_missing_file(tmp_path: Path) -> None:
    """Return default levels for missing file."""
    missing = tmp_path / "nonexistent.yml"

    levels = load_rubric_levels(missing)

    assert levels == ["Poor", "Mediocre", "High", "Excellent"]


def test_generate_review_yaml_basic() -> None:
    """Generate basic review YAML."""
    yaml_content = generate_review_yaml(
        pr_number=42,
        reviewer="tester",
        review_date=date(2026, 1, 4),
        workstream="Test Workstream",
        rubric_used="writing_quality",
        dimension_ratings=[{"dimension": "rigor", "rating": "High"}],
        strengths=["Good analysis"],
        risks=["Minor concern"],
        notes=[],
        follow_ups=[],
    )

    assert "pr_number: 42" in yaml_content
    assert "reviewer: tester" in yaml_content
    assert "date: '2026-01-04'" in yaml_content or "date: 2026-01-04" in yaml_content
    assert "workstream: Test Workstream" in yaml_content
    assert "rubric_used: writing_quality" in yaml_content
    assert "rigor" in yaml_content
    assert "High" in yaml_content
    assert "Good analysis" in yaml_content
    assert "Minor concern" in yaml_content


def test_generate_review_yaml_with_follow_ups() -> None:
    """Generate review YAML with follow-up issues."""
    yaml_content = generate_review_yaml(
        pr_number=1,
        reviewer="admin",
        review_date=date(2026, 1, 4),
        workstream="WS1",
        rubric_used="test",
        dimension_ratings=[],
        strengths=[],
        risks=[],
        notes=[],
        follow_ups=[
            {"id": "FU-1", "description": "Fix the bug", "required": True},
            {"id": "FU-2", "description": "Update docs", "required": False},
        ],
    )

    assert "FU-1" in yaml_content
    assert "Fix the bug" in yaml_content
    assert "required: true" in yaml_content
    assert "FU-2" in yaml_content


def test_generate_review_yaml_empty_lists() -> None:
    """Generate review YAML handles empty lists."""
    yaml_content = generate_review_yaml(
        pr_number=1,
        reviewer="admin",
        review_date=date(2026, 1, 4),
        workstream="WS1",
        rubric_used="test",
        dimension_ratings=[],
        strengths=[],
        risks=[],
        notes=[],
        follow_ups=[],
    )

    assert "strengths: []" in yaml_content
    assert "risks: []" in yaml_content
    assert "notes: []" in yaml_content
    assert "follow_up_issues: []" in yaml_content
