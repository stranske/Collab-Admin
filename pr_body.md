<!-- pr-preamble:start -->
> **Source:** Issue #43

<!-- pr-preamble:end -->

<!-- auto-status-summary:start -->
## Automated Status Summary
#### Scope
Per docs/13-project-instrumentation-roadmap.md Phase P4, the static dashboard should generate meaningful content from reviews, time logs, and CI data. Currently `dashboards/public/dashboard.md` only contains a timestamp.

#### Tasks
- [ ] Create `scripts/build_static_dashboard.py` that generates markdown from data sources
- [ ] Include time log summary (total hours, hours by workstream, hours by category)
- [ ] Include review outcomes summary (count by workstream, average ratings if available)
- [ ] Include issue/PR metrics (open/closed counts, recent activity)
- [ ] Include CI health summary (recent pass/fail rates)
- [ ] Update `build_dashboard.yml` to call the new script
- [ ] Add unit tests for the dashboard builder

#### Acceptance criteria
- [ ] Generated `dashboard.md` includes time tracking summary section
- [ ] Generated `dashboard.md` includes review summary section
- [ ] Generated `dashboard.md` includes project health metrics
- [ ] Dashboard updates via PR (no direct push to main)
- [ ] Script handles missing data gracefully (empty logs, no reviews)
- [ ] All tests pass

<!-- auto-status-summary:end -->
