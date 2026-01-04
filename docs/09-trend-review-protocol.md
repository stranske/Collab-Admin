# Trend Review Protocol (No AI)

This protocol applies only to Trend_Model_Project “understanding” deliverables.

## Non-negotiable

No AI assistance for these write-ups.

## Evidence standard

Each memo includes a `References` section using the format:

```
path/to/file.py#L120-L188 — function_or_class_name — why it matters
```

Minimum expectations per subsystem brief:
- entrypoints (2+)
- core call path traces (2+)
- error/edge paths (2+)
- data boundaries/config/parsing (2+)
- change hotspots (“what I’d fix first”) (2+)

## Walkthrough enforcement

Expect live interruption checks:
- “Show me where that’s called”
- “What breaks if we remove this”
- “Which inputs hit this branch”