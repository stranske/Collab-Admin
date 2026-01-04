"""Tests for validate_time_log_template.py."""

from pathlib import Path

from scripts.validate_time_log_template import validate_template

VALID_HEADER = "date,hours,repo,issue_or_pr,category,description,artifact_link"


def test_validate_template_valid(tmp_path: Path) -> None:
    """Valid template with correct header passes."""
    template = tmp_path / "template.csv"
    template.write_text(
        f"{VALID_HEADER}\n2024-01-08,2.5,Repo,PR-1,feature,desc,link\n",
        encoding="utf-8",
    )

    success, message = validate_template(template)

    assert success is True
    assert "valid" in message.lower()


def test_validate_template_header_only(tmp_path: Path) -> None:
    """Template with only header (no data rows) is valid."""
    template = tmp_path / "template.csv"
    template.write_text(f"{VALID_HEADER}\n", encoding="utf-8")

    success, message = validate_template(template)

    assert success is True


def test_validate_template_missing_file(tmp_path: Path) -> None:
    """Missing template file reports error."""
    missing = tmp_path / "nonexistent.csv"

    success, message = validate_template(missing)

    assert success is False
    assert "does not exist" in message


def test_validate_template_empty_file(tmp_path: Path) -> None:
    """Empty template file reports error."""
    template = tmp_path / "empty.csv"
    template.write_text("", encoding="utf-8")

    success, message = validate_template(template)

    assert success is False
    assert "empty" in message.lower()


def test_validate_template_wrong_header(tmp_path: Path) -> None:
    """Template with wrong header reports mismatch."""
    template = tmp_path / "bad.csv"
    template.write_text("wrong,header,columns\n", encoding="utf-8")

    success, message = validate_template(template)

    assert success is False
    assert "mismatch" in message.lower()


def test_validate_template_missing_column(tmp_path: Path) -> None:
    """Template missing a column reports mismatch."""
    template = tmp_path / "partial.csv"
    # Missing artifact_link column
    template.write_text(
        "date,hours,repo,issue_or_pr,category,description\n",
        encoding="utf-8",
    )

    success, message = validate_template(template)

    assert success is False
    assert "mismatch" in message.lower()


def test_validate_template_extra_column(tmp_path: Path) -> None:
    """Template with extra column reports mismatch."""
    template = tmp_path / "extra.csv"
    template.write_text(
        f"{VALID_HEADER},extra_col\n",
        encoding="utf-8",
    )

    success, message = validate_template(template)

    assert success is False
    assert "mismatch" in message.lower()
