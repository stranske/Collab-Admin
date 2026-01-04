# Collab-Admin Setup Completion Checklist

This checklist tracks the remaining work to complete Collab-Admin setup after initial repository creation from Template.

## Status Summary

| Phase | Description | Status |
|-------|-------------|--------|
| Initial Setup | Repository from Template, starter kit files | ✅ Complete |
| Phase A | Configuration fixes | ✅ Complete |
| Phase B | Sync registration in Workflows | ✅ Complete |
| Phase C | Code work via GitHub Issues | ✅ Complete |
| Phase P0-P2 | Instrumentation roadmap (boot/rubrics/validators) | ✅ Complete |
| Phase P3 | Dashboard MVP | 🔵 In Progress |
| Phase P4 | Static dashboard + report PRs | ✅ Basic setup |
| Phase P5 | Tighten (auto-open revision issues) | ⏳ Not started |

---

## Phase A: Configuration Fixes ✅

- [x] **A.1** Update `.gitignore` - add `codex-prompt-*.md`, `codex-output-*.md`, `logs/*.csv`
- [x] **A.2** Update `pyproject.toml` - change "my-project" to "collab-admin", fix URLs
- [x] **A.3** Create `reviews/` directory with `.gitkeep`
- [x] **A.4** Create `logs/` directory with `.gitkeep`
- [x] **A.5** Configure branch protection on `main` (owner configured)

---

## Phase B: Sync Registration ✅

- [x] **B.1** Register in `REGISTERED_CONSUMER_REPOS` (maint-68-sync-consumer-repos.yml)

Note: B.2 (sync-manifest.yml) and B.3 (sync_consumer_repos.py) do not exist in Workflows - the sync uses maint-68 workflow directly.

---

## Phase C: Code Work (GitHub Issues) ✅

All issues completed:

| Issue | Title | Status |
|-------|-------|--------|
| [#12](https://github.com/stranske/Collab-Admin/issues/12) | Complete rubric YAML files | ✅ Closed |
| [#13](https://github.com/stranske/Collab-Admin/issues/13) | Create review record templates | ✅ Closed |
| [#14](https://github.com/stranske/Collab-Admin/issues/14) | Enhance Streamlit dashboard | ✅ Closed |
| [#15](https://github.com/stranske/Collab-Admin/issues/15) | Enhance time log validation | ✅ Closed |
| [#16](https://github.com/stranske/Collab-Admin/issues/16) | Enhance ci_admin.yml workflow | ✅ Closed |
| [#17](https://github.com/stranske/Collab-Admin/issues/17) | Update pyproject.toml and config | ✅ Closed |

---

## Project Instrumentation Roadmap

See [docs/13-project-instrumentation-roadmap.md](13-project-instrumentation-roadmap.md) for full details.

### Phase P0: Boot ✅
- [x] Repo skeleton exists
- [x] Policies + templates exist
- [x] Issue forms exist

### Phase P1: Rubrics v1 ✅
- [x] Descriptor rubrics for core deliverables (11 rubric files)
- [x] Writing quality rubric included

### Phase P2: Validators ✅
- [x] Time cap validator (`validate_time_log.py`)
- [x] Time log template validator (`validate_time_log_template.py`)
- [x] Config validator (`validate_config.py`)
- [x] Rubric validator (`validate_rubrics.py`)

### Phase P3: Dashboard MVP 🔵
- [x] Streamlit app exists (`streamlit_app/app.py`)
- [x] Reads time logs and displays charts
- [x] Reads review records
- [ ] **TODO:** Add GitHub metadata integration (Issues/PRs/CI status)
- [ ] **TODO:** Review Console for writing review YAML

### Phase P4: Static Dashboard ✅ (Basic)
- [x] `build_dashboard.yml` workflow exists
- [x] Opens PRs for dashboard updates (no direct pushes)
- [ ] **TODO:** Enhance static dashboard content beyond timestamp

### Phase P5: Tighten ⏳
- [ ] Auto-open revision issues
- [ ] Richer Workflows ecosystem linkage reporting

---

## Initial Setup (Completed)

### Repository Structure ✅
- [x] Created from stranske/Template
- [x] Starter kit files added (docs/, rubrics/, templates/, scripts/, config/)
- [x] README.md customized for Collab-Admin

### GitHub Workflows ✅
- [x] All agent workflows present
- [x] autofix-versions.env configured
- [x] ci_admin.yml and build_dashboard.yml added

### Scripts and Prompts ✅
- [x] `.github/scripts/` - JS/Python scripts
- [x] `.github/codex/AGENT_INSTRUCTIONS.md`
- [x] `.github/codex/prompts/keepalive_next_task.md`
- [x] `.github/templates/keepalive-instruction.md`

### Issue Templates ✅
- [x] `.github/ISSUE_TEMPLATE/agent_task.yml`
- [x] `.github/ISSUE_TEMPLATE/collaborator_onboarding.yml`
- [x] `.github/ISSUE_TEMPLATE/config.yml`

### Labels ✅
- [x] `agent:codex`, `agent:needs-attention`, `agents:keepalive`
- [x] `autofix`, `autofix:clean`, `autofix:applied`, `autofix:clean-only`
- [x] `onboarding`, `onboarding-complete`, `needs-review`

### Secrets ✅
- [x] `CODEX_AUTH_JSON`
- [x] `WORKFLOWS_APP_ID`, `WORKFLOWS_APP_PRIVATE_KEY`
- [x] `SERVICE_BOT_PAT`, `ACTIONS_BOT_PAT`, `OWNER_PR_PAT`

### Variables ✅
- [x] `ALLOWED_KEEPALIVE_LOGINS=stranske`

### GitHub App ✅
- [x] agents-workflows-bot installed on repository

---

## Version History

| Date | Changes |
|------|---------|
| 2026-01-04 | Updated with completed phases A, B, C and roadmap status |
| 2026-01-04 | Initial checklist created |
