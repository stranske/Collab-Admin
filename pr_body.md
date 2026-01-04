<!-- pr-preamble:start -->
> **Source:** Issue #39

<!-- pr-preamble:end -->

<!-- auto-status-summary:start -->
## Automated Status Summary
#### Scope
The collaboration policies define several log types that need directory infrastructure:
- Time logs: `logs/time/YYYY-MM.csv` (per docs/04-time-tracking-policy.md)
- Expense logs: `logs/expenses/YYYY-MM.csv` (per docs/07-compensation-expenses.md)
- Friction logs: `logs/friction/YYYY-MM.csv` (per docs/11-consumer-usability-protocol.md)
- Month-end memos: `logs/month_end/YYYY-MM.md` (per docs/08-month-end-settlement.md)

Currently only `logs/` exists with a time log template. The other directories and templates are missing.

#### Tasks
- [x] Create `logs/expenses/` directory with `.gitkeep`
- [x] Create `logs/expenses/expense_template.csv` with headers: `date,amount,currency,category,description,receipt_link,issue_or_pr,preapproval_link`
- [x] Create `logs/friction/` directory with `.gitkeep`
- [x] Create `logs/friction/friction_template.csv` with headers: `date,repo,context,minutes_lost,what_broke,what_was_confusing,what_fixed_it,pr_or_issue`
- [x] Create `logs/month_end/` directory with `.gitkeep`
- [x] Create `logs/month_end/template.md` with sections for hours summary, deliverables, reviews, expenses
- [x] Update `.gitignore` to exclude actual log files but not templates

#### Acceptance criteria
- [x] All four log directories exist: `logs/time/`, `logs/expenses/`, `logs/friction/`, `logs/month_end/`
- [x] Each directory has appropriate template file(s)
- [x] Templates match the CSV headers defined in policy docs
- [ ] CI passes

<!-- auto-status-summary:end -->
