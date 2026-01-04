# Collaborator Onboarding — Administrator Guide

This document provides the owner/administrator with a complete reference for managing the collaborator onboarding process.

## System Overview

### Purpose

The onboarding system accomplishes three goals:

1. **Policy Acknowledgment** — Creates an auditable record that collaborators have read all governing documents
2. **Comprehension Verification** — Reveals misunderstandings before work begins through paragraph responses
3. **Access Control** — Provides a gate for contributor access based on demonstrated understanding

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ONBOARDING WORKFLOW                          │
├─────────────────────────────────────────────────────────────────┤
│  1. Owner invites collaborator with READ access                 │
│  2. Collaborator creates issue from template                    │
│  3. Collaborator reads policies, checks boxes, writes responses │
│  4. Owner reviews responses for misconceptions                  │
│  5. Owner approves/requests clarification                       │
│  6. On approval: upgrade to WRITE access, assign work           │
└─────────────────────────────────────────────────────────────────┘
```

### Files Involved

| File | Purpose |
|------|---------|
| `.github/ISSUE_TEMPLATE/collaborator_onboarding.yml` | Issue form with checkboxes and questions |
| `docs/ONBOARDING.md` | Collaborator-facing instructions |
| `templates/onboarding_review.md` | Owner's review template |
| `docs/ONBOARDING_ADMIN_GUIDE.md` | This document |

---

## Onboarding a New Collaborator

### Step 1: Send Repository Invitation

```bash
# Via GitHub CLI
gh api -X PUT repos/stranske/Collab-Admin/collaborators/{username} \
  -f permission=pull

# Or via web:
# Settings → Collaborators → Add people → Select "Read" permission
```

**Important:** Start with READ access only. Write access is granted after onboarding approval.

### Step 2: Notify Collaborator

Send them this message:

```
Welcome to the collaboration!

Please complete onboarding:
1. Accept the repository invitation
2. Go to https://github.com/stranske/Collab-Admin/issues/new/choose
3. Select "Collaborator Onboarding"
4. Read all linked policy docs and complete the form

I'll review your responses within 48 hours. Questions? Reply to this message.
```

### Step 3: Monitor for Submission

Watch for issues with the `onboarding` label:

```bash
gh issue list --repo stranske/Collab-Admin --label onboarding
```

### Step 4: Review Submission

1. Open the onboarding issue
2. Copy `templates/onboarding_review.md` content
3. Paste into a local file or your notes app
4. Work through each assessment section
5. Make your decision (approve/clarify/reject)

### Step 5: Take Action

**If Approving:**

```bash
# Add label
gh issue edit {issue_number} --repo stranske/Collab-Admin \
  --add-label "onboarding-complete"

# Close issue
gh issue close {issue_number} --repo stranske/Collab-Admin \
  --comment "✅ Onboarding approved! Upgrading your access now."

# Upgrade access to write
gh api -X PUT repos/stranske/Collab-Admin/collaborators/{username} \
  -f permission=push

# Assign first issue
gh issue edit {first_issue_number} --repo stranske/Collab-Admin \
  --add-assignee {username}
```

**If Requesting Clarification:**

```bash
gh issue comment {issue_number} --repo stranske/Collab-Admin --body "
Please clarify the following before we proceed:

1. In Q2 (AI Policy), you mentioned using AI for trend analysis, but the 
   Trend Model Clarity workstream prohibits AI tools entirely. Please 
   confirm you understand this restriction.

2. In Q4 (Time Tracking), you didn't mention the weekly cap. What is 
   the maximum hours per week?

Once you've replied, I'll complete the review.
"
```

**If Rejecting:**

```bash
gh issue comment {issue_number} --repo stranske/Collab-Admin --body "
Thank you for completing the form. I've identified some fundamental 
misunderstandings that we need to address:

1. [Specific issue]

Please re-read [specific document] carefully, then update your responses 
to Q{X} and Q{Y}. If you have questions about the policies, please ask 
them in a comment here.
"
```

---

## What to Look For in Responses

### Red Flags (Likely Problems)

| Signal | Concern | Action |
|--------|---------|--------|
| Copied text from docs | Didn't actually internalize | Ask to rephrase |
| Very short responses | May not have read carefully | Ask for detail |
| Generic responses | Could apply to any project | Ask specifics |
| Scope creep | Expects to do more than defined | Clarify boundaries |
| AI policy misunderstanding | Critical for some workstreams | Clarify restrictions |
| Payment assumptions | May not follow process | Ensure understanding |

### Green Flags (Good Signs)

| Signal | Indicates |
|--------|-----------|
| Own words, not copied | Actually processed information |
| Specific examples | Deep understanding |
| Mentions workstream constraints | Read workstream-specific docs |
| Asks clarifying questions | Thoughtful engagement |
| Accurate on caps/limits | Read policy details |

### Critical Items to Verify

1. **AI Policy by Workstream**
   - Trend Model Clarity: NO AI allowed
   - Agent Integration: AI is the focus
   - Consumer Usability: AI allowed with disclosure
   - Marketplace Plan: AI allowed with disclosure

2. **Time Tracking Requirements**
   - Format: CSV with specific columns
   - Cap: 40 hours/week maximum
   - No banking: Can't carry over unused hours

3. **Submission Process**
   - All work via PR with submission packet
   - Review required before payment
   - Must link time entries to artifacts

---

## Managing Labels

Create these labels if they don't exist:

```bash
# Onboarding labels
gh label create "onboarding" --repo stranske/Collab-Admin \
  --color "0E8A16" --description "Collaborator onboarding in progress"

gh label create "onboarding-complete" --repo stranske/Collab-Admin \
  --color "5319E7" --description "Collaborator onboarding approved"

gh label create "needs-review" --repo stranske/Collab-Admin \
  --color "FBCA04" --description "Awaiting owner review"
```

---

## Audit Trail

The onboarding system creates these records:

1. **Issue History** — Full text of acknowledgments and responses
2. **Timestamp** — When they completed onboarding
3. **Review Decision** — Your approval comment
4. **Access Log** — GitHub audit log shows permission changes

For compliance or disputes, the onboarding issue provides evidence that:
- Collaborator was shown all policies (checkboxes linked to docs)
- Collaborator affirmed reading them (required checkboxes)
- Collaborator demonstrated understanding (paragraph responses)
- Owner verified understanding (review + approval)

---

## E-Sign Alternatives

If you need a more formal acknowledgment:

### GPG-Signed Commit

Have collaborator create a signed commit:

```bash
# Collaborator runs:
git commit --allow-empty --gpg-sign -m \
  "I, [Full Name], acknowledge reading all Collab-Admin policies as of [DATE]. GitHub: @[username]"
git push
```

This creates cryptographic proof tied to their GPG key.

### COLLABORATORS.md Registry

Create `COLLABORATORS.md` and have each person add themselves via PR:

```markdown
# Registered Collaborators

## Jane Doe
- GitHub: @janedoe
- Onboarded: 2026-01-04
- Workstream: Consumer Usability
- Acknowledgment: I have read and agree to all policies in docs/
```

The PR history + their commit = acknowledgment record.

---

## Troubleshooting

### Collaborator Can't Create Issue

**Cause:** They may not have accepted the invitation yet, or invitation expired.

**Fix:** Re-send invitation:
```bash
gh api -X PUT repos/stranske/Collab-Admin/collaborators/{username} -f permission=pull
```

### Issue Template Not Showing

**Cause:** Template file syntax error or wrong location.

**Fix:** Validate YAML:
```bash
python -c "import yaml; yaml.safe_load(open('.github/ISSUE_TEMPLATE/collaborator_onboarding.yml'))"
```

### Collaborator Accidentally Submitted Incomplete

**Options:**
1. Have them edit the issue to complete it
2. Close and have them create a new one
3. Ask follow-up questions in comments

---

## Metrics

Track onboarding effectiveness:

| Metric | How to Measure |
|--------|----------------|
| Time to complete | Issue creation → submission |
| Clarification rate | % needing follow-up questions |
| Rejection rate | % not approved on first try |
| Common misconceptions | Tally by question |

Review these quarterly to improve policy clarity.

---

## Quick Reference

### Approve Collaborator (Full Command Sequence)

```bash
USER="{username}"
ISSUE="{issue_number}"

# Label and close
gh issue edit $ISSUE --repo stranske/Collab-Admin --add-label "onboarding-complete"
gh issue close $ISSUE --repo stranske/Collab-Admin --comment "✅ Onboarding approved!"

# Upgrade access
gh api -X PUT repos/stranske/Collab-Admin/collaborators/$USER -f permission=push

echo "✅ $USER is now onboarded with write access"
```

### Check Pending Onboardings

```bash
gh issue list --repo stranske/Collab-Admin --label "onboarding" --label "needs-review"
```

---

*Document version: 1.0 — January 2026*
