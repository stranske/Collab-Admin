<!-- pr-preamble:start -->
> **Source:** Issue #9

<!-- pr-preamble:end -->

<!-- auto-status-summary:start -->
## Automated Status Summary
#### Scope
The Collab-Admin repository needs to be initialized as the control plane for the collaboration project. This repo will manage policies, protocols, rubrics, submission templates, review records, time/expense logs, dashboards, and validation scripts.

According to the starter kit README, this repo should be created by layering the starter kit files onto the stranske/Template structure (which is already in place) to leverage the shared automation library from stranske/Workflows for Gate CI, keepalive, autofix, etc.

#### Tasks
- [ ] Copy starter kit docs/ folder to repository root
- [ ] Copy rubrics/ folder with rubric_index.yml and writing_quality.yml
- [ ] Copy templates/ folder with submission_packet.md
- [ ] Set up streamlit_app/ directory with app.py
- [ ] Set up dashboards/public/ structure
- [ ] Copy scripts/ folder with validation scripts
- [ ] Integrate .github/workflows/ci_admin.yml and build_dashboard.yml
- [ ] Update repository README.md with Collab-Admin specific content
- [ ] Add config/ folder with project.yml and dashboard_public.yml
- [ ] Create placeholder directories: reviews/, logs/
- [ ] Update .gitignore for logs and review artifacts
- [ ] Verify all references in docs point to correct paths

#### Acceptance criteria
- [ ] - Repository contains all starter kit folders (docs/, rubrics/, templates/, scripts/, streamlit_app/, dashboards/, config/)
- [ ] - README.md clearly explains the Collab-Admin purpose and structure
- [ ] - All documentation files are accessible and properly formatted
- [ ] - Validation scripts are executable
- [ ] - Workflow files integrate with existing Gate/CI system
- [ ] - Charter (docs/00-charter.md) is present and accurate
- [ ] - Operating model (docs/01-operating-model.md) reflects the collaboration structure
- [ ] - Rubrics system is documented and ready for use
- [ ] - Submission packet template is ready for PR submissions

**Head SHA:** f27208ad84fb4e10f309e060693e9f60c2d38b83
**Latest Runs:** ⏳ queued — Gate
**Required:** gate: ⏳ queued

| Workflow / Job | Result | Logs |
|----------------|--------|------|
| Agents PR Meta | ❔ in progress | [View run](https://github.com/stranske/Collab-Admin/actions/runs/20689175197) |
| Autofix | ❔ in progress | [View run](https://github.com/stranske/Collab-Admin/actions/runs/20689175193) |
| CI | ❔ in progress | [View run](https://github.com/stranske/Collab-Admin/actions/runs/20689175209) |
| Copilot code review | ⏳ queued | [View run](https://github.com/stranske/Collab-Admin/actions/runs/20689175637) |
| Gate | ⏳ queued | [View run](https://github.com/stranske/Collab-Admin/actions/runs/20689175202) |
| Health 45 Agents Guard | ❔ in progress | [View run](https://github.com/stranske/Collab-Admin/actions/runs/20689175161) |
<!-- auto-status-summary:end -->
