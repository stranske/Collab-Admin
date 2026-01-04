<!-- pr-preamble:start -->
> **Source:** Issue #15

<!-- pr-preamble:end -->

<!-- auto-status-summary:start -->
## Automated Status Summary
#### Scope
The `scripts/validate_time_log.py` script exists but needs enhancements for better validation, and sample data files are needed for testing.

#### Tasks
- [x] Create `logs/.gitkeep` to ensure directory exists
- [x] Add `logs/` to .gitignore (time logs are private)
- [x] Create `logs/time_log_template.csv` with header and example row (tracked)
- [x] Enhance `scripts/validate_time_log.py` to validate category values against allowed list
- [x] Add validation for artifact_link format (GitHub URL pattern)
- [x] Add validation for date format and reasonable date range
- [x] Add --verbose flag for detailed output
- [x] Add unit tests in `tests/scripts/test_validate_time_log.py`

#### Acceptance criteria
- [x] `logs/` directory exists with .gitkeep
- [x] `logs/time_log_template.csv` provides clear header and format example
- [x] Script validates category values (setup, feature, fix, review, meeting, admin)
- [x] Script validates artifact_link is a valid GitHub URL or empty
- [x] Script validates dates are reasonable (not in future, not too old)
- [x] All tests pass with `pytest tests/scripts/`
- [x] Script passes `ruff check` and `mypy`

<!-- auto-status-summary:end -->
