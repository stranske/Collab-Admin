<!-- pr-preamble:start -->
> **Source:** Issue #17

<!-- pr-preamble:end -->

<!-- auto-status-summary:start -->
## Automated Status Summary
#### Scope
The `pyproject.toml` contains template placeholder values (name="my-project", generic URLs). It needs to be updated with Collab-Admin specific configuration.

#### Tasks
- [ ] Update `pyproject.toml` project name from "my-project" to "collab-admin"
- [ ] Update `pyproject.toml` description to match Collab-Admin purpose
- [ ] Update `pyproject.toml` homepage and repository URLs to stranske/Collab-Admin
- [ ] Update `pyproject.toml` known-first-party from "my_project" to "collab_admin"
- [ ] Add PR-specific codex patterns to .gitignore: `codex-prompt-*.md`, `codex-output-*.md`
- [ ] Add `logs/` directory pattern to .gitignore (keep time logs private)
- [ ] Add streamlit dependency to pyproject.toml optional-dependencies

#### Acceptance criteria
- [ ] `pyproject.toml` name field is "collab-admin"
- [ ] `pyproject.toml` URLs point to stranske/Collab-Admin
- [ ] `.gitignore` includes PR-specific codex patterns
- [ ] `.gitignore` includes `logs/*.csv` or `logs/` pattern (excluding template)
- [ ] `pip install -e ".[dev]"` succeeds without errors

<!-- auto-status-summary:end -->
