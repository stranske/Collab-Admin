<!-- pr-preamble:start -->
> **Source:** Issue #9

<!-- pr-preamble:end -->

<!-- auto-status-summary:start -->
## Automated Status Summary
#### Scope
The Collab-Admin repository needs to be initialized as the control plane for the collaboration project. This repo will manage policies, protocols, rubrics, submission templates, review records, time/expense logs, dashboards, and validation scripts.

According to the starter kit README, this repo should be created by layering the starter kit files onto the stranske/Template structure (which is already in place) to leverage the shared automation library from stranske/Workflows for Gate CI, keepalive, autofix, etc.

#### Tasks
- [x] Copy starter kit docs/ folder to repository root
- [x] Copy rubrics/ folder with rubric_index.yml and writing_quality.yml
- [x] Copy templates/ folder with submission_packet.md
- [x] Set up streamlit_app/ directory with app.py
- [x] Set up dashboards/public/ structure
- [x] Copy scripts/ folder with validation scripts
- [x] Integrate .github/workflows/ci_admin.yml and build_dashboard.yml
- [x] Update repository README.md with Collab-Admin specific content
- [x] Add config/ folder with project.yml and dashboard_public.yml
- [x] Create placeholder directories: reviews/, logs/
- [x] Update .gitignore for logs and review artifacts
- [x] Verify all references in docs point to correct paths

#### Acceptance criteria
- [x] - Repository contains all starter kit folders (docs/, rubrics/, templates/, scripts/, streamlit_app/, dashboards/, config/)
- [x] - README.md clearly explains the Collab-Admin purpose and structure
- [ ] - All documentation files are accessible and properly formatted
- [x] - Validation scripts are executable
- [ ] - Workflow files integrate with existing Gate/CI system
- [x] - Charter (docs/00-charter.md) is present and accurate
- [x] - Operating model (docs/01-operating-model.md) reflects the collaboration structure
- [x] - Rubrics system is documented and ready for use
- [x] - Submission packet template is ready for PR submissions

<!-- auto-status-summary:end -->
