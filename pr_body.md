<!-- pr-preamble:start -->
> **Source:** Issue #17

<!-- pr-preamble:end -->

<!-- auto-status-summary:start -->
## Automated Status Summary
#### Scope
The `pyproject.toml` contains template placeholder values (name="my-project", generic URLs). It needs to be updated with Collab-Admin specific configuration.

#### Tasks
- [x] Update `pyproject.toml` project name from "my-project" to "collab-admin"
- [x] Update `pyproject.toml` description to match Collab-Admin purpose
- [x] Update `pyproject.toml` homepage and repository URLs to stranske/Collab-Admin
- [x] Update `pyproject.toml` known-first-party from "my_project" to "collab_admin"
- [x] Add PR-specific codex patterns to .gitignore: `codex-prompt-*.md`, `codex-output-*.md`
- [x] Add `logs/` directory pattern to .gitignore (keep time logs private)
- [x] Add streamlit dependency to pyproject.toml optional-dependencies

#### Acceptance criteria
- [x] `pyproject.toml` name field is "collab-admin"
- [x] `pyproject.toml` URLs point to stranske/Collab-Admin
- [x] `.gitignore` includes PR-specific codex patterns
- [x] `.gitignore` includes `logs/*.csv` or `logs/` pattern (excluding template)
- [ ] `pip install -e ".[dev]"` succeeds without errors

<!-- auto-status-summary:end -->
