# Workflows Ecosystem Reference (Workflows + Integration-Tests + Consumers)

This is the missing “explicit repo detail” section.

The collaboration system assumes:

- `stranske/Workflows` is the **source of truth** for reusable CI + agent automation.
- `stranske/Workflows-Integration-Tests` validates the system from an external consumer POV.
- Consumer repos (Template, Travel-Plan-Permission, etc.) use **thin callers** that `uses:` workflows from Workflows.

If you ignore this architecture, you’ll end up with a beautiful garden of duplicated YAML and heartbreak.

---

## 1) The core CI topology

**Gate is the centerpiece.** In Workflows, the canonical merge gate is:

- `.github/workflows/pr-00-gate.yml` (display name: “Gate”)

Gate fans out to:

- `reusable-10-ci-python.yml` (Python lint/type/tests/coverage)
- `reusable-12-ci-docker.yml` (Docker smoke)

and then publishes the required commit status (the one branch protection cares about) out of the Gate `summary` job.

Consumer repos copy a Gate template (`.github/workflows/pr-00-gate.yml`) that calls Workflows’ reusable CI and then posts the commit status `Gate / gate`.

Example caller shape:

- `python-ci` job: `uses: stranske/Workflows/.github/workflows/reusable-10-ci-python.yml@main`
- `summary` job: computes state and posts the `Gate / gate` commit status

**Hard requirement for keepalive:** the Gate workflow must publish the `Gate / gate` commit status.

---

## 2) The agent/keepalive control plane

### 2.1 Consumer “PR meta” workflow

Consumer repos include `.github/workflows/agents-pr-meta.yml` (thin caller):

- triggers on `issue_comment.created` (keepalive commands)
- re-runs on `workflow_run` of `Gate` (to avoid race conditions)
- base64-encodes the comment body and calls `stranske/Workflows/.github/workflows/reusable-20-pr-meta.yml@main`

This is the mechanism that detects keepalive activation and dispatches the orchestrator.

Repo variable used here:

- `ALLOWED_KEEPALIVE_LOGINS` (passed as `allowed_keepalive_logins`)

### 2.2 Workflows reusable PR meta (`reusable-20-pr-meta.yml`)

The reusable PR meta workflow uses a dual-checkout pattern:

- checkout **consumer repo** for context
- checkout **Workflows repo** for scripts (`scripts/` and `.github/scripts/`)

This keeps consumer repos thin while centralizing the logic.

### 2.3 Orchestrator

In Workflows, `.github/workflows/agents-70-orchestrator.yml` is the “one entry point” that:

- runs on a schedule (`*/30 * * * *`)
- triggers on `workflow_run` completion of Gate
- can be pinged via `repository_dispatch`

It delegates to reusable init/main workflows and uses bot/app auth when available.

---

## 3) Sync: Workflows → consumers

The Workflows repo syncs consumer-facing files via:

- **Maint 68 Sync Consumer Repos** (`.github/workflows/maint-68-sync-consumer-repos.yml`)
- a **manifest** (`.github/sync-manifest.yml`) that declares exactly what gets synced

### 3.1 Manifest-driven categories

The sync manifest (`.github/sync-manifest.yml`) includes, at minimum:

- thin caller workflows (Gate, agent workflows, autofix)
- codex prompts
- scripts needed by workflows
- documentation that should exist in consumer repos

The manifest also uses `sync_mode: create_only` for consumer-owned files (e.g., Gate tuning and `.github/workflows/autofix-versions.env`) so repo-specific customization survives sync.

The manifest’s “workflows” section explicitly lists (among others):

- `.github/workflows/pr-00-gate.yml` (create_only)
- `.github/workflows/ci.yml` (create_only)
- `.github/workflows/autofix.yml`
- `.github/workflows/agents-orchestrator.yml` (consumer orchestrator thin caller)
- `.github/workflows/agents-pr-meta.yml`
- `.github/workflows/agents-issue-intake.yml` (legacy name)
- `.github/workflows/agents-keepalive-loop.yml`
- `.github/workflows/agents-autofix-loop.yml`
- `.github/workflows/agents-verifier.yml`
- `.github/workflows/agents-bot-comment-handler.yml`
- `.github/workflows/agents-guard.yml`
- `.github/workflows/maint-coverage-guard.yml`

Migration note: some repos also carry numbered variants (e.g., `agents-70-orchestrator.yml`, `agents-63-issue-intake.yml`) alongside the legacy names during transitions.

### 3.2 Registered consumer repos

The `maint-68` workflow maintains a list of registered consumers in `REGISTERED_CONSUMER_REPOS`.

If/when `collab-admin` becomes a consumer, it should be added there.

---

## 4) Integration tests: Workflows ↔ Workflows-Integration-Tests

The integration test repo uses a multi-job workflow (`.github/workflows/ci.yml`) that calls the reusable CI workflow in several configurations.

Template job names and required artifact prefixes:

- `basic` → `artifact-prefix: basic-`
- `full-coverage` → `artifact-prefix: full-`
- `typecheck-only` → `artifact-prefix: typecheck-`
- `lint-only` → `artifact-prefix: lint-`

Key rules enforced:

- Multi-job CI must use distinct `artifact-prefix` values per job to avoid conflicts.
- Avoid invalid input names (e.g., use `typecheck`, not `enable-mypy`).

The integration repo also includes `.github/workflows/notify-workflows.yml` that dispatches a `repository_dispatch` event back to the Workflows repo when integration config changes.

On the Workflows side:

- `health-67-integration-sync-check.yml` validates the integration repo matches the templates.
- `maint-69-sync-integration-repo.yml` pushes template updates into Workflows-Integration-Tests.

---

## 5) Known GitHub Actions sharp edges (codified in the repos)

- Mixing reusable-workflow jobs (`uses:`) and normal jobs (`runs-on:`) in the same workflow file has caused `startup_failure` in consumer experiments. Keep reusable calls isolated to their own workflow file.
- Consumer thin-caller `ci.yml` files warn against adding a top-level `permissions:` block because it can trigger `startup_failure` when calling reusable workflows.

---

## 6) Bootstrapping Collab-Admin (recommended path)

1. Clone `stranske/Template` to create `collab-admin`.
2. Layer this starter kit’s `docs/`, `rubrics/`, `templates/`, and `scripts/` on top.
3. Decide whether collab-admin is a “full consumer”:
   - If YES: ensure Workflows secrets/vars exist and register the repo for sync.
   - If NO (month 1): keep agent secrets unset and treat automation as optional.

This keeps the admin repo aligned with the same automation reality the collaborator will be working inside.
