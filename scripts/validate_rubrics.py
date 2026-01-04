"""Validate rubric YAML files for parseability and required structure."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REQUIRED_FIELDS = ("rubric_id", "title", "levels", "dimensions")


def _load_yaml(path: Path) -> tuple[object | None, str | None]:
    try:
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as exc:
        return None, f"{path}: YAML parse error: {exc}"
    return data, None


def _validate_structure(path: Path, data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{path}: expected a mapping at the document root."]

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        errors.append(f"{path}: missing required fields: {', '.join(missing)}.")
        return errors

    if not isinstance(data["rubric_id"], str) or not data["rubric_id"].strip():
        errors.append(f"{path}: rubric_id must be a non-empty string.")
    if not isinstance(data["title"], str) or not data["title"].strip():
        errors.append(f"{path}: title must be a non-empty string.")
    if not isinstance(data["levels"], list) or not data["levels"]:
        errors.append(f"{path}: levels must be a non-empty list.")
    if not isinstance(data["dimensions"], list) or not data["dimensions"]:
        errors.append(f"{path}: dimensions must be a non-empty list.")

    return errors


def validate_rubrics(rubrics_dir: Path, check_structure: bool) -> list[str]:
    errors: list[str] = []
    if not rubrics_dir.exists():
        return [f"{rubrics_dir}: directory does not exist."]

    yaml_files = sorted(rubrics_dir.glob("*.yml"))
    if not yaml_files:
        return [f"{rubrics_dir}: no rubric YAML files found."]

    for rubric_path in yaml_files:
        data, error = _load_yaml(rubric_path)
        if error:
            errors.append(error)
            continue
        if check_structure and rubric_path.name != "rubric_index.yml":
            errors.extend(_validate_structure(rubric_path, data))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate rubric YAML files.")
    parser.add_argument(
        "rubrics_dir",
        nargs="?",
        default="rubrics",
        help="Path to the rubrics directory (default: rubrics).",
    )
    parser.add_argument(
        "--check-structure",
        action="store_true",
        help="Validate required rubric fields and basic types.",
    )
    args = parser.parse_args(argv)

    errors = validate_rubrics(Path(args.rubrics_dir), args.check_structure)
    if errors:
        message = "Rubric validation failed:\n" + "\n".join(f"- {error}" for error in errors)
        raise SystemExit(message)

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
