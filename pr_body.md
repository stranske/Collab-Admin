<!-- pr-preamble:start -->
> **Source:** Issue #15

<!-- pr-preamble:end -->

<!-- auto-status-summary:start -->
## Automated Status Summary
#### Scope
The `scripts/validate_time_log.py` script exists but needs enhancements for better validation, and sample data files are needed for testing.

#### Tasks
- [ ] Create `logs/.gitkeep` to ensure directory exists
- [ ] Add `logs/` to .gitignore (time logs are private)
- [ ] Create `logs/time_log_template.csv` with header and example row (tracked)
- [ ] Enhance `scripts/validate_time_log.py` to validate category values against allowed list
- [ ] Add validation for artifact_link format (GitHub URL pattern)
- [ ] Add validation for date format and reasonable date range
- [ ] Add --verbose flag for detailed output
- [ ] Add unit tests in `tests/scripts/test_validate_time_log.py`

#### Acceptance criteria
- [ ] `logs/` directory exists with .gitkeep
- [ ] `logs/time_log_template.csv` provides clear header and format example
- [ ] Script validates category values (setup, feature, fix, review, meeting, admin)
- [ ] Script validates artifact_link is a valid GitHub URL or empty
- [ ] Script validates dates are reasonable (not in future, not too old)
- [ ] All tests pass with `pytest tests/scripts/`
- [ ] Script passes `ruff check` and `mypy`

<!-- auto-status-summary:end -->
