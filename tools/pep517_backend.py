"""Minimal PEP 517 backend to support editable installs without network access."""

from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path
import re
import tempfile
import tomllib
import zipfile


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _project_metadata() -> tuple[str, str, str, str, list[str], dict[str, list[str]]]:
    pyproject_path = _project_root() / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = data.get("project", {})
    name = project["name"]
    version = project["version"]
    description = project.get("description", "")
    requires_python = project.get("requires-python", "")
    dependencies = project.get("dependencies", [])
    optional_deps = project.get("optional-dependencies", {})
    return name, version, description, requires_python, dependencies, optional_deps


def _normalize_dist_name(name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return normalized.replace("-", "_")


def _dist_info_name(name: str, version: str) -> str:
    return f"{_normalize_dist_name(name)}-{version}.dist-info"


def _write_metadata(
    dist_info_dir: Path,
    name: str,
    version: str,
    description: str,
    requires_python: str,
    dependencies: list[str],
    optional_deps: dict[str, list[str]],
) -> None:
    dist_info_dir.mkdir(parents=True, exist_ok=True)
    metadata_lines = [
        "Metadata-Version: 2.1",
        f"Name: {name}",
        f"Version: {version}",
    ]
    if description:
        metadata_lines.append(f"Summary: {description}")
    if requires_python:
        metadata_lines.append(f"Requires-Python: {requires_python}")
    for dependency in dependencies:
        metadata_lines.append(f"Requires-Dist: {dependency}")
    for extra, requirements in optional_deps.items():
        metadata_lines.append(f"Provides-Extra: {extra}")
        for requirement in requirements:
            metadata_lines.append(f'Requires-Dist: {requirement}; extra == "{extra}"')
    (dist_info_dir / "METADATA").write_text("\n".join(metadata_lines) + "\n", encoding="utf-8")
    (dist_info_dir / "WHEEL").write_text(
        "\n".join(
            [
                "Wheel-Version: 1.0",
                "Generator: collab-admin-pep517-backend",
                "Root-Is-Purelib: true",
                "Tag: py3-none-any",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _hash_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256(path.read_bytes()).digest()
    encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"sha256={encoded}", path.stat().st_size


def _collect_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for filename in filenames:
            if filename.endswith(".pyc"):
                continue
            paths.append(Path(dirpath) / filename)
    return paths


def _build_wheel(wheel_directory: str, *, editable: bool) -> str:
    name, version, description, requires_python, dependencies, optional_deps = _project_metadata()
    dist = _normalize_dist_name(name)
    wheel_name = f"{dist}-{version}-py3-none-any.whl"
    wheel_dir = Path(wheel_directory)
    wheel_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        dist_info_dir = tmp_path / _dist_info_name(name, version)
        _write_metadata(
            dist_info_dir, name, version, description, requires_python, dependencies, optional_deps
        )

        records: list[tuple[str, str, int]] = []

        if editable:
            pth_name = f"{dist}.pth"
            (tmp_path / pth_name).write_text(
                str(_project_root() / "src") + "\n", encoding="utf-8"
            )
            records.append((pth_name, *_hash_file(tmp_path / pth_name)))
        else:
            src_root = _project_root() / "src"
            for path in _collect_paths(src_root):
                rel_path = path.relative_to(src_root)
                dest_path = tmp_path / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                dest_path.write_bytes(path.read_bytes())
                records.append((rel_path.as_posix(), *_hash_file(dest_path)))

        for path in _collect_paths(dist_info_dir):
            rel_path = path.relative_to(tmp_path)
            records.append((rel_path.as_posix(), *_hash_file(path)))

        record_path = dist_info_dir / "RECORD"
        with record_path.open("w", encoding="utf-8") as record_file:
            for record in records:
                record_file.write(f"{record[0]},{record[1]},{record[2]}\n")
            record_file.write(f"{record_path.relative_to(tmp_path).as_posix()},,\n")

        wheel_path = wheel_dir / wheel_name
        with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in _collect_paths(tmp_path):
                zf.write(path, path.relative_to(tmp_path))

    return wheel_name


def _prepare_metadata(metadata_directory: str) -> str:
    name, version, description, requires_python, dependencies, optional_deps = _project_metadata()
    dist_info_name = _dist_info_name(name, version)
    dist_info_dir = Path(metadata_directory) / dist_info_name
    _write_metadata(
        dist_info_dir, name, version, description, requires_python, dependencies, optional_deps
    )
    record_path = dist_info_dir / "RECORD"
    record_path.write_text("", encoding="utf-8")
    return dist_info_name


def _supported_features() -> dict[str, bool]:
    return {"build_editable": True}


def get_requires_for_build_wheel(config_settings: dict | None = None) -> list[str]:
    return []


def get_requires_for_build_editable(config_settings: dict | None = None) -> list[str]:
    return []


def prepare_metadata_for_build_wheel(
    metadata_directory: str, config_settings: dict | None = None
) -> str:
    return _prepare_metadata(metadata_directory)


def prepare_metadata_for_build_editable(
    metadata_directory: str, config_settings: dict | None = None
) -> str:
    return _prepare_metadata(metadata_directory)


def build_wheel(
    wheel_directory: str, config_settings: dict | None = None, metadata_directory: str | None = None
) -> str:
    return _build_wheel(wheel_directory, editable=False)


def build_editable(
    wheel_directory: str, config_settings: dict | None = None, metadata_directory: str | None = None
) -> str:
    return _build_wheel(wheel_directory, editable=True)
