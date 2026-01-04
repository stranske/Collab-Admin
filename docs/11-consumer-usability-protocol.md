# Consumer Usability Protocol

This workstream tests that the Workflows automation is actually usable by someone building a medium-sized project.

## Constraints

- Choose a “medium build” project with multiple modules and a CLI/UI surface.
- Integrate with `stranske/Workflows` using the thin-caller pattern.

## Required artifact: friction log

Friction logs live in `logs/friction/YYYY-MM.csv` and record:

```
date,repo,context,minutes_lost,what_broke,what_was_confusing,what_fixed_it,pr_or_issue
```

## Minimum bar

- at least two PRs that reduce friction (not just documentation bloat)
- evidence that Workflows-level fixes were made in the source repo when appropriate