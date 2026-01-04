# Time Tracking Policy

Hard constraint: **40 hours/week cap** and **no banking**.

## Logging format

Time logs live in `logs/time/YYYY-MM.csv` and use the headers:

```
date,hours,repo,issue_or_pr,category,description,artifact_link
```

### Category guidance

- `build` – coding/config changes
- `review` – reading + review memos
- `ops` – debugging workflows/CI
- `research` – scoping + exploration

## What “no banking” means

If someone works 55 hours this week, next week is not “earned vacation.” Weekly cap violations should be visible and treated as a process failure.
