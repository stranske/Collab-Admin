# Agent Integration Protocol

This workstream is about integrating additional agents into the existing automation ecosystem.

The current ecosystem is anchored in `stranske/Workflows` and its consumer repos.

## Required deliverables

- Claude Code integrated as the next agent
- A third agent integrated (Aider / Continue / approved alt)
- A stable “outputs contract” for agent runs so keepalive/verifier does not require per-agent special cases
- Documentation that enables a future agent to be added by following the docs (docs-first test)

## Ground truth file references (Workflows)

- Agent control plane catalog and topology: `../.workflows-lib/docs/ci/WORKFLOWS.md` in Workflows
- Orchestrator entry point: `.github/workflows/agents-70-orchestrator.yml`
- PR keepalive detection: consumer `.github/workflows/agents-pr-meta.yml` calling Workflows `reusable-20-pr-meta.yml`

## Contract expectations

Any agent integration should:

1. Emit a machine-readable result object (pass/fail + summary + artifacts)
2. Produce stable filenames for prompt/output artifacts
3. Respect the “no secrets in logs” rule

If it’s not testable in Workflows-Integration-Tests, it’s not integrated.
