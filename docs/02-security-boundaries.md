# Security Boundaries

This collaboration is deliberately “small and private,” but the automation stack can still do dumb things at high speed.

## Non-negotiables

- No shared PATs or long-lived secrets in chat/email.
- Secrets live only in GitHub Actions secrets (repo settings).
- Month 1 uses forks-only for collaborator work.

## Tokens used by the Workflows ecosystem

If you enable the keepalive/autofix/agent system in `collab-admin`, the shared automation expects these secrets/variables to exist (they are referenced throughout the Workflows consumer templates and setup docs):

### Secrets

- `SERVICE_BOT_PAT` (classic PAT) – bot pushes branches and posts comments.
- `ACTIONS_BOT_PAT` – workflow dispatch + cross-repo triggers.
- `OWNER_PR_PAT` – creates PRs / branch operations when elevated permissions are needed.
- `CODEX_AUTH_JSON` – Codex CLI auth blob for workflows that run Codex.
- Optional preferred auth: `WORKFLOWS_APP_ID` + `WORKFLOWS_APP_PRIVATE_KEY` (GitHub App token minting).

### Variables

- `ALLOWED_KEEPALIVE_LOGINS` – comma-separated allowlist for who can trigger keepalive.

Month 1 note: fork PRs generally cannot access these secrets. Plan accordingly.

## Fork PR safety posture

Do not create workflows that check out and execute fork code using secrets. If you must use `pull_request_target`, the workflow should:

- only run “metadata operations” (labels/comments)
- avoid `actions/checkout` of fork head
- treat all fork-supplied text as untrusted input

The Workflows ecosystem already uses guardrails and allowlists around keepalive triggers and dispatch payloads. Keep those intact.
