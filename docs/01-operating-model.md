# Operating Model

This document turns the collaboration proposal constraints into an actual working system.

## 1) Work moves through GitHub

**Unit of work:** an Issue → a PR → a reviewed artifact.

Every PR should include a filled-out `templates/submission_packet.md` (or a link to it) so review never becomes an archaeology project.

## 2) Month 1: forks-only

The collaborator works in a fork. All changes land via PR to the upstream repo.

Practical consequences:

- secrets are **not** available to fork PR workflows (unless you deliberately use `pull_request_target`, which we do *sparingly*)
- “agent automation that needs tokens” is expected to be limited in month 1

## 3) PR-only, Tim merges

- Tim is the sole merger.
- “Drive-by pushes” to `main` are treated as a bug, not a feature.

## 4) Workstreams

The collaboration has four workstreams:

1. Trend model understanding (no AI)
2. Agent integration (Claude Code next, then a 3rd agent)
3. Consumer usability validation
4. Marketplace plan

Each workstream has:

- required deliverables
- a rubric pack
- a submission packet standard
