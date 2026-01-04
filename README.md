# Collab-Admin

Control plane for the stranske collaboration project. This repository defines policies, protocols, rubrics, submission templates, review workflows, time/expense tracking, dashboards, and validation scripts for the collaboration.

## Purpose

Collab-Admin serves as the **single source of truth** for:
- Operating model and governance ([docs/01-operating-model.md](docs/01-operating-model.md))
- Security boundaries and access control ([docs/02-security-boundaries.md](docs/02-security-boundaries.md))
- Submission standards and review rubrics ([rubrics/](rubrics/))
- Time tracking and compensation protocols ([docs/04-time-tracking-policy.md](docs/04-time-tracking-policy.md))
- Public-facing dashboards ([dashboards/public/](dashboards/public/))
- Validation and quality assurance scripts ([scripts/](scripts/))

This repo was initialized by layering the [Collab-Admin starter kit](collab-admin-starter-kit-v4.zip) onto the [stranske/Template](https://github.com/stranske/Template) structure to leverage shared automation from [stranske/Workflows](https://github.com/stranske/Workflows).

## Repository Structure

```
Collab-Admin/
├── config/
│   ├── project.yml              # Project configuration
│   └── dashboard_public.yml     # Public dashboard config
├── docs/                        # Policy and protocol documentation
│   ├── 00-charter.md           # Project charter and goals
│   ├── 01-operating-model.md   # Work processes and constraints
│   ├── 02-security-boundaries.md # Access control and secrets
│   ├── 03-ai-policy.md         # AI usage guidelines
│   ├── 04-time-tracking-policy.md # Time logging requirements
│   ├── 05-definition-of-done.md # Completion criteria
│   ├── 06-review-workflow.md   # PR review process
│   ├── 07-compensation-expenses.md # Payment protocols
│   ├── 08-month-end-settlement.md # Monthly reconciliation
│   ├── 09-trend-review-protocol.md # Trend model analysis
│   ├── 10-agent-integration-protocol.md # Claude Code integration
│   ├── 11-consumer-usability-protocol.md # Usability validation
│   ├── 12-marketplace-plan-protocol.md # Marketplace research
│   ├── 13-project-instrumentation-roadmap.md # Observability
│   └── 14-workflows-ecosystem.md # Automation architecture
├── rubrics/
│   ├── rubric_index.yml        # Index of all rubrics
│   └── writing_quality.yml     # Writing quality rubric
├── templates/
│   └── submission_packet.md    # Standard submission format
├── scripts/
│   └── validate_time_log.py    # Time log validation script
├── streamlit_app/
│   └── app.py                  # Dashboard application
├── dashboards/
│   └── public/                 # Public-facing dashboards
│       └── README.md           # Dashboard documentation
├── reviews/                    # Review records (git-tracked)
├── logs/                       # Time and expense logs (.gitignored)
└── .github/workflows/          # CI and automation workflows
    ├── ci_admin.yml           # Admin validation CI
    └── build_dashboard.yml    # Dashboard build workflow
```

## Workstreams

The collaboration has four workstreams, each with specific deliverables and rubrics:

1. **Trend Model Clarity** ([docs/09-trend-review-protocol.md](docs/09-trend-review-protocol.md))
   - Analyze existing trend model implementation
   - Document findings and recommendations
   - No AI tools allowed for this workstream

2. **Agent Integration** ([docs/10-agent-integration-protocol.md](docs/10-agent-integration-protocol.md))
   - Integrate Claude Code as next agent
   - Implement 3rd agent integration
   - Test multi-agent workflows

3. **Consumer Usability** ([docs/11-consumer-usability-protocol.md](docs/11-consumer-usability-protocol.md))
   - Validate setup documentation
   - Test consumer repo creation process
   - Improve onboarding experience

4. **Marketplace Plan** ([docs/12-marketplace-plan-protocol.md](docs/12-marketplace-plan-protocol.md))
   - Research GitHub marketplace requirements
   - Create implementation roadmap
   - Document API integration patterns

## Submission Process

All work must be submitted via GitHub PR with a completed [submission packet](templates/submission_packet.md) that includes:
- Work summary and time tracking
- Deliverable links and evidence
- Self-assessment against rubrics
- Open questions or blockers

See [docs/06-review-workflow.md](docs/06-review-workflow.md) for complete review process.

## Automation

This repository uses [stranske/Workflows](https://github.com/stranske/Workflows) for:
- **Gate CI**: PR validation with Python linting, type checking, and tests
- **Keepalive Automation**: CLI Codex agent for automated implementation
- **Autofix**: Automatic code formatting and lint fixes
- **Dashboard Builds**: Automated dashboard generation from review data

### Key Workflows

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| **ci_admin.yml** | Validate docs, rubrics, time logs | Pull request |
| **build_dashboard.yml** | Generate public dashboards | Push to main |
| **Gate** | Standard CI validation | Pull request |
| **Keepalive Loop** | Agent automation | Gate pass + labels |

## Development

```bash
# Clone repository
git clone https://github.com/stranske/Collab-Admin.git
cd Collab-Admin

# Install dependencies
pip install -e ".[dev]"

# Run validation scripts
python scripts/validate_time_log.py logs/time_log.csv

# Run tests
pytest

# Check code quality
ruff check src/ tests/ scripts/
mypy src/ tests/ scripts/
```

## Configuration

### Required Secrets

| Secret | Purpose |
|--------|---------|
| `CODEX_AUTH_JSON` | Codex CLI authentication |
| `WORKFLOWS_APP_ID` | GitHub App ID for token minting |
| `WORKFLOWS_APP_PRIVATE_KEY` | GitHub App private key |
| `SERVICE_BOT_PAT` | Bot PAT for automation |
| `OWNER_PR_PAT` | Owner PAT for PR operations |

### Repository Variables

| Variable | Purpose | Value |
|----------|---------|-------|
| `ALLOWED_KEEPALIVE_LOGINS` | Users who can trigger keepalive | `stranske` |

## Documentation

- [Charter](docs/00-charter.md) - Project goals and scope
- [Operating Model](docs/01-operating-model.md) - How work flows through GitHub
- [Security Boundaries](docs/02-security-boundaries.md) - Access control and secrets
- [Workflows Ecosystem](docs/14-workflows-ecosystem.md) - Complete automation architecture

## License

MIT License - see [LICENSE](LICENSE) for details.
