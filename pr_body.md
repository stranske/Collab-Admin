<!-- pr-preamble:start -->
> **Source:** Issue #13

<!-- pr-preamble:end -->

<!-- auto-status-summary:start -->
## Automated Status Summary
#### Scope
The review workflow (docs/06-review-workflow.md) specifies review records should be stored in `reviews/YYYY-MM/...yaml`. The directory structure and template files need to be created.

#### Tasks
- [ ] Create `reviews/.gitkeep` to ensure directory exists
- [ ] Create `reviews/README.md` explaining review record format
- [ ] Create `templates/review_record.yml` - Template for individual review records
- [ ] Create `scripts/create_review_record.py` - Script to generate review record stubs from PR data

#### Acceptance criteria
- [ ] `reviews/` directory exists and is tracked in git
- [ ] Review record template includes: pr_number, reviewer, date, workstream, rubric_used, dimension_ratings, feedback, follow_up_issues
- [ ] Script can generate a review record stub given a PR number
- [ ] README documents the review record format and workflow
- [ ] Script is executable and passes lint checks

<!-- auto-status-summary:end -->
