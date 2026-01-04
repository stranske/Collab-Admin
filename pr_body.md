<!-- pr-preamble:start -->
> **Source:** Issue #16

<!-- pr-preamble:end -->

<!-- auto-status-summary:start -->
## Automated Status Summary
#### Scope
The `.github/workflows/ci_admin.yml` is a stub workflow. It needs jobs to validate Collab-Admin specific files like rubrics, review records, and time logs.

#### Tasks
- [x] Add job to validate all YAML files in `rubrics/` are parseable
- [x] Add job to validate rubric files have required structure (rubric_id, title, levels, dimensions)
- [ ] Add job to validate `config/project.yml` and `config/dashboard_public.yml` schemas
- [ ] Add job to lint markdown files in `docs/` for broken links
- [ ] Add job to validate time log template format if `logs/time_log_template.csv` exists
- [ ] Ensure all validation jobs report clear error messages

#### Acceptance criteria
- [ ] ci_admin.yml runs on pull_request events
- [x] YAML validation job catches malformed rubric files
- [ ] Config validation job ensures required fields exist
- [ ] Markdown lint job reports broken internal links
- [ ] All jobs use appropriate Python version and dependencies
- [ ] Workflow passes when all files are valid

<!-- auto-status-summary:end -->
