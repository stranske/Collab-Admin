<!-- pr-preamble:start -->
> **Source:** Issue #14

<!-- pr-preamble:end -->

<!-- auto-status-summary:start -->
## Automated Status Summary
#### Scope
The streamlit_app/app.py is a placeholder. The collaboration needs a private dashboard to visualize review records, time tracking, and workstream progress.

#### Tasks
- [x] Add time log loading from `logs/time_log.csv` with weekly/monthly aggregations
- [x] Add review record loading from `reviews/` YAML files
- [ ] Create workstream progress overview showing completion by workstream
- [ ] Create time tracking summary with weekly caps visualization
- [ ] Add rubric dimension distribution charts (no numeric scores published)
- [ ] Add requirements.txt or update pyproject.toml with streamlit dependencies

#### Acceptance criteria
- [x] Dashboard loads without errors when `streamlit run streamlit_app/app.py` is executed
- [ ] Time tracking view shows hours by week with 40hr cap indicator
- [ ] Workstream view shows deliverable completion status
- [ ] Review records display feedback and follow-ups (not numeric scores)
- [x] App gracefully handles missing/empty data files

<!-- auto-status-summary:end -->
