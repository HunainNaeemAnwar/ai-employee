# Human Input Request Feature

## Overview

The AI Employee can now **ask questions to the human** when it needs more context to proceed.

---

## How It Works

### 1. AI Needs Context

When processing an email, if Qwen determines it needs more information, it outputs:

```
HUMAN INPUT REQUIRED

Questions:
1. What was the previous conversation about?
2. What is your relationship with the sender?
3. What timeline should be committed to?
```

### 2. System Creates Input Request

The Ralph Loop detects this and creates a file:

```
PROCESSING/Pending_Approval/INPUT_<uuid>.md
```

### 3. File Format

```markdown
---
input_id: abc123
task_id: email_12345
type: human_input_request
status: awaiting_response
---

# Human Input Required

The AI needs context from you to proceed.

## Email Context
- **From:** sender@example.com
- **Subject:** Quick Follow-Up
- **Received:** 2026-02-18

## Questions

### Q1: What was the previous conversation about?
**Your Answer:** 
```

```

### Q2: What is your relationship with the sender?
**Your Answer:** 
```

```

### Q3: What timeline should be committed to?
**Your Answer:** 
```

```

## Instructions

1. **Edit this file** - Fill in your answers in the code blocks above
2. **Change status** - Update `status: awaiting_response` to `status: responded`
3. **Save the file** - The orchestrator will pick it up automatically
```

---

## User Workflow

### Step 1: Open Obsidian

Navigate to: `PROCESSING/Pending_Approval/`

### Step 2: Find Input Request

Look for files named: `INPUT_<uuid>.md`

### Step 3: Fill In Answers

Edit the file and add your answers in the code blocks:

```markdown
### Q1: What was the previous conversation about?
**Your Answer:** 
```
It was about the Q1 project timeline and deliverables.
```
```

### Step 4: Change Status

Update the frontmatter:

```yaml
status: responded  # Changed from "awaiting_response"
```

### Step 5: Save

Save the file in Obsidian.

### Step 6: Wait

Within 10-20 seconds, the orchestrator will:
- Detect your response
- Process the answers
- Create approval request with draft email
- Move to next step

---

## System Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Email arrives → Ralph Loop processes                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Qwen determines: "Need more context"                    │
│     Outputs: HUMAN INPUT REQUIRED + Questions               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Ralph Loop creates: INPUT_<uuid>.md                     │
│     In: PROCESSING/Pending_Approval/                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  4. User opens Obsidian → Finds INPUT_<uuid>.md             │
│     Fills in answers → Changes status → Saves               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Orchestrator detects (within 10 seconds)                │
│     Reads answers → Creates approval with draft             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  6. User approves → Email sent → Task completed             │
└─────────────────────────────────────────────────────────────┘
```

---

## Example Scenario

### Email Received:
```
From: john@client.com
Subject: Quick Follow-Up
Body: Hi, just checking in on our discussion from last week...
```

### Qwen Output:
```
HUMAN INPUT REQUIRED

Questions:
1. What was discussed last week?
2. What is the current status?
3. What commitment can we make?
```

### Input File Created:
```
PROCESSING/Pending_Approval/INPUT_abc123.md
```

### User Fills In:
```markdown
### Q1: What was discussed last week?
**Your Answer:** 
```
We discussed the Q2 roadmap and potential integration timeline.
```

### Q2: What is the current status?
**Your Answer:** 
```
Still in planning phase, waiting for budget approval.
```

### Q3: What commitment can we make?
**Your Answer:** 
```
Can provide detailed proposal by end of next week.
```
```

### Status Changed:
```yaml
status: responded
```

### System Creates Approval:
```
PROCESSING/Pending_Approval/APPROVAL_xyz789.md

## Draft Content
```
Dear John,

Thank you for following up on our Q2 roadmap discussion.

We're still in the planning phase and waiting for budget approval. 
I can provide you with a detailed proposal by end of next week.

Best regards,
AI Employee
```
```

---

## Benefits

| Benefit | Description |
|---------|-------------|
| **Context Preservation** | Human provides context AI doesn't have |
| **Better Replies** | AI drafts based on accurate information |
| **Human Control** | You decide what information to share |
| **Audit Trail** | All Q&A logged for future reference |
| **Flexible** | Works for any type of question |

---

## Files Location

| File Type | Location |
|-----------|----------|
| Input Requests | `PROCESSING/Pending_Approval/INPUT_*.md` |
| Approvals | `PROCESSING/Pending_Approval/APPROVAL_*.md` |
| Completed | `OUTPUT/Completed/` |
| Audit Logs | `SECURITY/audit_logs/YYYY-MM-DD.jsonl` |

---

## Commands

```bash
# Check pending input requests
ls -la AI_Employee_Vault/PROCESSING/Pending_Approval/INPUT_*.md

# View an input request
cat AI_Employee_Vault/PROCESSING/Pending_Approval/INPUT_<uuid>.md

# Check status
python3 scripts/orchestrator.py status
```

---

## Tips

1. **Be Specific** - Provide detailed answers for better drafts
2. **Respond Quickly** - AI waits for your input before proceeding
3. **Check Daily** - New input requests appear in Pending_Approval/
4. **Use Obsidian** - Easiest way to edit and save files

---

**Last Updated:** 2026-02-18  
**Feature Version:** 1.0
