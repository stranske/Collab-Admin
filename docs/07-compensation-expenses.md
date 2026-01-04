# Compensation and Expenses

This repo keeps evidence for month-end settlement (hours, deliverables shipped, approved expenses).

## Expense logging

Expenses live in `logs/expenses/YYYY-MM.csv` and should include preapproval + receipt links.

CSV headers:

```
date,amount,currency,category,description,receipt_link,issue_or_pr,preapproval_link
```

If it’s not logged, it doesn’t exist.
