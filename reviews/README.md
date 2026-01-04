# Review Records

Review records capture rubric-based feedback for each PR. Store each record under
`reviews/YYYY-MM/` with one YAML file per PR.

## File naming

Use the format:

```
reviews/YYYY-MM/pr-<PR_NUMBER>.yml
```

Example:

```
reviews/2025-01/pr-123.yml
```

## Record format

Start from `templates/review_record.yml`. The required top-level fields are:

- `pr_number`: PR number as an integer
- `reviewer`: Reviewer name or handle
- `date`: Review date in `YYYY-MM-DD`
- `workstream`: Workstream name
- `rubric_used`: Rubric identifier (see `rubrics/`)
- `dimension_ratings`: List of rubric dimension ratings
- `feedback`: Summary feedback sections
- `follow_up_issues`: Required follow-up items

## Workflow

1. Generate a stub record with:
   `scripts/create_review_record.py <PR_NUMBER> --reviewer <name> --workstream <name> --rubric <rubric>`
2. Fill in `dimension_ratings`, `feedback`, and `follow_up_issues`.
3. Commit the new review record.
