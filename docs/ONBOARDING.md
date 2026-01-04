# Collaborator Onboarding Process

## Overview

Before starting work, all collaborators must:
1. Read and acknowledge all policy documents
2. Demonstrate understanding through written responses  
3. Receive owner approval

This process ensures alignment on expectations and prevents misunderstandings about scope, compensation, and workflow.

## For New Collaborators

### Step 1: Receive Invitation

You'll receive an email invitation to the Collab-Admin repository. Accept the invitation to gain read access.

### Step 2: Create Your Onboarding Issue

1. Go to **Issues** → **New Issue**
2. Select **"Collaborator Onboarding"** template
3. Replace `[NAME]` in the title with your name
4. The form will guide you through the process

### Step 3: Read Policy Documents

Work through each linked document carefully. These define:

| Document | Key Topics |
|----------|------------|
| [00-charter.md](00-charter.md) | Project goals, scope boundaries |
| [01-operating-model.md](01-operating-model.md) | GitHub-based workflow |
| [02-security-boundaries.md](02-security-boundaries.md) | Access control, secrets |
| [03-ai-policy.md](03-ai-policy.md) | AI usage rules by workstream |
| [04-time-tracking-policy.md](04-time-tracking-policy.md) | Logging requirements, caps |
| [05-definition-of-done.md](05-definition-of-done.md) | Completion criteria |
| [06-review-workflow.md](06-review-workflow.md) | PR and submission review |
| [07-compensation-expenses.md](07-compensation-expenses.md) | Payment protocols |

### Step 4: Acknowledge and Respond

- Check each acknowledgment box **after** reading that document
- Write thoughtful responses to each comprehension question
- Responses should be in your own words, not copied from docs
- Brief but complete answers are fine (1-3 paragraphs each)

### Step 5: Wait for Review

The project owner will review your responses for:
- Evidence that you read the documents
- Correct understanding of key policies
- Any misconceptions that need clarification

### Step 6: Approval or Follow-up

- **If approved**: Issue is closed with "onboarding-complete" label, you receive contributor access
- **If clarification needed**: Owner will comment with specific questions to address

## Comprehension Questions Explained

The onboarding form asks specific questions designed to reveal understanding (or misconceptions):

| Question | What It Reveals |
|----------|-----------------|
| **Q1: Scope** | Do you understand project boundaries? |
| **Q2: AI Policy** | Critical - some workstreams prohibit AI entirely |
| **Q3: Submission** | Will you follow the payment process correctly? |
| **Q4: Time Tracking** | Do you understand hours caps and logging format? |
| **Q5: Your Role** | Are you clear on your specific assignment? |
| **Q6: Clarifications** | What needs discussion before you start? |

## After Onboarding

Once approved:

1. **Access Upgrade**: You'll be upgraded from read to contributor access
2. **Workstream Assignment**: Issues for your workstream will be assigned to you
3. **Begin Work**: Follow the submission process for all deliverables
4. **Track Time**: Log hours per the time tracking policy
5. **Ask Questions**: Create issues for anything unclear

## Timeline

- **Expected completion**: 1-2 hours to read policies and complete responses
- **Review turnaround**: Within 48 hours of submission
- **Start date**: You may begin work immediately after approval

## E-Signature Alternative

For situations requiring a more formal acknowledgment record:

### Option A: Signed Git Commit

Create a GPG-signed commit with this exact message format:
```
I, [Full Name], acknowledge reading and understanding all Collab-Admin 
policies as of [YYYY-MM-DD]. GitHub: @[username]
```

This creates a cryptographically verifiable record of your acknowledgment.

### Option B: Markdown Signature Block

Add yourself to `COLLABORATORS.md` via PR with:
```markdown
## [Your Name]
- GitHub: @username
- Onboarded: YYYY-MM-DD
- Workstream: [Assigned Workstream]
- Acknowledgment: I have read and agree to all policies in docs/
```

## Getting Help

- **Policy questions**: Create an issue with the `question` label
- **Technical setup**: See [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)
- **Workflow issues**: See [KEEPALIVE_TROUBLESHOOTING.md](KEEPALIVE_TROUBLESHOOTING.md)

---

*Last updated: January 2026*
