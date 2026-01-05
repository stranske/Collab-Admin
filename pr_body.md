<!-- pr-preamble:start -->
> **Source:** Issue #41

<!-- pr-preamble:end -->

<!-- auto-status-summary:start -->
## Automated Status Summary
#### Scope
Per docs/05-definition-of-done.md, every PR must include a completed submission packet (templates/submission_packet.md). Currently there is no automated validation that submission packets are complete.

#### Tasks
- [x] Create `scripts/validate_submission_packet.py` that parses markdown and checks required sections
- [x] Validator should check for: Issue number, Workstream, Deliverables, How to run/test, Evidence
- [x] Add submission packet validation to `ci_admin.yml` for PRs
- [x] Add unit tests for the validator

#### Acceptance criteria
- [x] Validator detects missing required sections
- [x] Validator accepts well-formed submission packets
- [x] Clear error messages indicate which sections are missing
- [ ] CI can run validation on PR descriptions or linked files
- [x] All tests pass

<!-- auto-status-summary:end -->
