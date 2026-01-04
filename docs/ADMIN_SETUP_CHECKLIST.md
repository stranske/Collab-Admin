# Collab-Admin Setup Completion Checklist

This checklist tracks the remaining work to complete Collab-Admin setup after initial repository creation from Template.

## Status Summary

| Phase | Description | Status |
|-------|-------------|--------|
| Initial Setup | Repository from Template, starter kit files | ✅ Complete |
| Phase A | Configuration fixes | 🔵 In Progress |
| Phase B | Sync registration in Workflows | ⏸️ Pending |
| Phase C | Code work via GitHub Issues | 🔵 In Progress |

---

## Phase A: Configuration Fixes (Quick/Manual)

- [ ] **A.1** Update `.gitignore` - add `codex-prompt-*.md`, `codex-output-*.md`, `logs/*.csv`
- [ ] **A.2** Update `pyproject.toml` - change "my-project" to "collab-admin", fix URLs
- [ ] **A.3** Create `reviews/` directory with `.gitkeep`
- [ ] **A.4** Create `logs/` directory with `.gitkeep`
- [ ] **A.5** Configure branch protection on `main` (require `Gate / gate`)

---

## Phase B: Sync Registration (Workflows repo)

Register Collab-Admin as a consumer repo to receive automatic workflow updates.

- [ ] **B.1** Register in `REGISTERED_CONSUMER_REPOS` (maint-68-sync-consumer-repos.yml)
- [ ] **B.2** Register in `.github/sync-manifest.yml`
- [ ] **B.3** Register in `scripts/sync_consumer_repos.py`

---

## Phase C: Code Work (GitHub Issues)

These issues were created following the AGENT_ISSUE_FORMAT and can be assigned to agents.

| Issue | Title | Purpose | Status |
|-------|-------|---------|--------|
| [#12](https://github.com/stranske/Collab-Admin/issues/12) | Complete rubric YAML files | Create 9 missing rubric files for all workstreams | Open |
| [#13](https://github.com/stranske/Collab-Admin/issues/13) | Create review record templates | Set up `reviews/` directory structure and scripts | Open |
| [#14](https://github.com/stranske/Collab-Admin/issues/14) | Enhance Streamlit dashboard | Build out dashboard with review metrics visualization | Open |
| [#15](https://github.com/stranske/Collab-Admin/issues/15) | Enhance time log validation | Improve validation script and create `logs/` structure | Open |
| [#16](https://github.com/stranske/Collab-Admin/issues/16) | Enhance ci_admin.yml workflow | Add validation jobs for rubrics, configs, docs | Open |
| [#17](https://github.com/stranske/Collab-Admin/issues/17) | Update pyproject.toml and config | Fix placeholder values, update .gitignore | Open |

---

## Initial Setup (Completed)

The following was completed during initial repository setup:

### Repository Structure ✅
- [x] Created from stranske/Template
- [x] Starter kit files added (docs/, rubrics/, templates/, scripts/, config/)
- [x] README.md customized for Collab-Admin

### GitHub Workflows ✅
- [x] All agent workflows present (19 workflow files)
- [x] autofix-versions.env configured
- [x] ci_admin.yml and build_dashboard.yml added

### Scripts and Prompts ✅
- [x] `.github/scripts/` - 14 JS/Python scripts
- [x] `.github/codex/AGENT_INSTRUCTIONS.md`
- [x] `.github/codex/prompts/keepalive_next_task.md`
- [x] `.github/templates/keepalive-instruction.md`

### Issue Templates ✅
- [x] `.github/ISSUE_TEMPLATE/agent_task.yml`
- [x] `.github/ISSUE_TEMPLATE/config.yml`

### Labels ✅
- [x] `agent:codex`
- [x] `agent:needs-attention`
- [x] `agents:keepalive`
- [x] `autofix`
- [x] `autofix:clean`
- [x] `autofix:applied`
- [x] `autofix:clean-only`

### Secrets ✅
- [x] `CODEX_AUTH_JSON`
- [x] `WORKFLOWS_APP_ID`
- [x] `WORKFLOWS_APP_PRIVATE_KEY`
- [x] `SERVICE_BOT_PAT`
- [x] `ACTIONS_BOT_PAT`
- [x] `OWNER_PR_PAT`

### Variables ✅
- [x] `ALLOWED_KEEPALIVE_LOGINS=stranske`

### GitHub App ✅
- [x] agents-workflows-bot installed on repository

---

## Version History

| Date | Changes |
|------|---------|
| 2026-01-04 | Initial checklist created |
