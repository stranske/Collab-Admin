"""Keep disposable root dependencies out of git without hiding vendored scripts."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def test_generated_dirs_untracked_and_vendored_preserved() -> None:
    assert not git("ls-files", "node_modules").stdout.strip()
    assert git("ls-files", ".github/scripts/node_modules").stdout.strip()
    assert git("check-ignore", "--no-index", "-q", "node_modules/probe.js").returncode == 0
    assert (
        git(
            "check-ignore",
            "--no-index",
            "-q",
            ".github/scripts/node_modules/minimatch/package.json",
        ).returncode
        == 1
    )
