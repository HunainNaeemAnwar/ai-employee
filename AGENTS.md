# AGENTS.md - AI Agent Working Guide

**Version:** 2.1
**Audience:** AI Coding Agents (Qwen, Claude Code, etc.)
**Purpose:** README for AI agents working on Personal AI Employee project

> **Note:** For complete requirements, see [SPECIFICATIONS.md](./SPECIFICATIONS.md)

---

## Writing Rules

### Emoji Usage

**Allowed (Only These 4):**
- ⚡ (lightning) - For speed, power, energy, quick actions
- ✔ (check mark) - For completed items, success, correct
- ✖ (cross mark) - For failed items, errors, incorrect
- ⚠️ (warning) - For warnings, cautions, important notices

**Not Allowed:**
- No other emojis in documentation
- Use text labels instead: [SUCCESS], [ERROR], ⚠️, etc.

**Examples:**
```markdown
✔ Complete
✖ Failed
⚠️ Review required
⚡ Fast processing
```

---

## TABLE OF CONTENTS

1. [Quick Start](#quick-start)
2. [Ralph Loop Workflow](#ralph-loop-workflow)
3. [Project Structure](#project-structure)
4. [Development Commands](#development-commands)
5. [AI-Specific Guidance](#ai-specific-guidance)
6. [Common Workflows](#common-workflows)
7. [Known Pitfalls](#known-pitfalls)

---

## QUICK START

### Before Starting Work

1. **Read CONSTITUTION.md** - Governing principles (NON-NEGOTIABLE)
2. **Read SPECIFICATIONS.md** - Complete technical requirements
3. **Check current state** - `.system/state/current_task.json`
4. **Review progress** - `progress.txt` (if using Ralph Loop)

### File Priority Order

When starting a task, read in this order:

```
1. CONSTITUTION.md              (rules you must follow)
2. SPECIFICATIONS.md            (requirements to implement)
3. AGENTS.md                    (this file - working instructions)
4. .system/state/current_task.json  (current task state)
5. Needs_Action/{task}.json  (task details)
```

### Current Phase Check

```bash
# Check which phase we're in
cat progress.txt | grep "PHASE:"

# Check current task
cat .system/state/current_task.json
```

---

## RALPH LOOP WORKFLOW

### What is Ralph Loop?

The **Ralph Wiggum Loop** is an iterative execution pattern where:
1. AI reads state from files
2. AI takes ONE concrete action
3. AI updates state files
4. Loop repeats until completion

### Your Role in Ralph Loop

```
Iteration Start:
  |
  v
1. Read .system/state/current_task.json
2. Read task from Needs_Action/{task_id}.json or In_Progress/{task_id}.json
3. Understand what previous iteration did
4. Take ONE concrete action (not planning, DOING)
5. Update state file with what you did
6. Check if task complete
  |
  v
If Complete:
  -> Output: <status>TASK_COMPLETE</status>
  -> OR move task to Done/
If Not Complete:
  -> Next iteration continues
```

### Completion Signals

| Signal | How |
|--------|-----|
| **stdout** | Output `<status>TASK_COMPLETE</status>` |
| **stdout (alt)** | Output `<promise>COMPLETE</promise>` |
| **file** | Create `.system/state/complete.flag` |

### No-Progress Detection

**WARNING:** If state file doesn't change for 3 consecutive iterations, loop exits with error.

**To avoid:**
- Always update state after taking action
- Document what you did in `context.last_action`
- Update `iteration` counter

### State Update Format

```json
{
  "task_id": "uuid",
  "status": "in_progress",
  "iteration": 3,
  "last_iteration_at": "2026-02-17T10:40:00Z",
  "context": {
    "last_action": "drafted_reply_email",
    "next_step": "request_approval",
    "notes": "Reply drafted, awaiting HITL approval"
  },
  "history": [
    {"iteration": 1, "action": "read_email", "timestamp": "..."},
    {"iteration": 2, "action": "check_client_history", "timestamp": "..."},
    {"iteration": 3, "action": "draft_reply", "timestamp": "..."}
  ]
}
```

---

## PROJECT STRUCTURE

### Root Level

```
personal_assistant/
├── SPECIFICATIONS.md          <- Complete requirements (READ FIRST)
├── CONSTITUTION.md            <- Governing principles
├── AGENTS.md                  <- This file (working instructions)
├── BRONZE_TIER.md             <- Phase 1 completion report
├── README.md                  <- Project overview
└── AI_Employee_Vault/         <- Obsidian vault
```

### Vault Structure

```
AI_Employee_Vault/
├── Company_Handbook.md    <- AI behavior rules (ROOT)
├── Business_Goals.md      <- KPIs, targets (ROOT)
├── Dashboard.md           <- Real-time status (ROOT)
│
├── Inbox/
│   ├── Gmail/               <- Gmail Watcher drops here
│   ├── WhatsApp/            <- WhatsApp Watcher drops here
│   ├── Banking/             <- Finance Watcher drops here
│   └── Files/               <- File system drops here
│
├── Needs_Action/
├── Plans/
├── Done/
│
├── Pending_Approval/     <- HITL queue (sensitive actions)
├── Approved/             <- Human-approved, ready to execute
├── Rejected/             <- Human-rejected
│
├── Knowledge/
│   ├── Contexts/            <- Client profiles, history
│   └── Procedures/          <- Reusable SOPs
│
├── .env                  <- API keys (NEVER COMMIT)
├── Logs/                 <- Action logs (YYYY-MM-DD.jsonl)
│
└── .system/
    ├── state/               <- Current task states
    └── config/              <- Watcher configurations
```

---

## DEVELOPMENT COMMANDS

### Running the System

```bash
# Start orchestrator (main loop - watches for emails, runs Ralph Loop automatically)
python main.py start

# Run Ralph Loop manually (bash script)
./scripts/ralph-loop.sh "Process all files in Needs_Action" --vault ~/AI_Employee_Vault

# Run Ralph Loop with completion promise
./scripts/ralph-loop.sh "Process emails" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10 \
  --vault ~/AI_Employee_Vault

# Run Ralph Loop using direct bash pattern
echo "Process pending tasks" > PROMPT.md && while :; do cat PROMPT.md | qwen -i -o text; done

# Test individual watcher
python watchers/gmail_watcher.py --vault ~/AI_Employee_Vault --test

# Validate state files
python scripts/validate_state.py --vault ~/AI_Employee_Vault
```

### State Management

```bash
# Claim next pending task
python scripts/state_manager.py claim --vault ~/AI_Employee_Vault

# Check approval status
python scripts/state_manager.py check-approval --task <task_id>

# Move task to completed
python scripts/state_manager.py complete --task <task_id>
```

### Audit & Logs

```bash
# View today's audit log
cat Logs/$(date +%Y-%m-%d).jsonl

# View error log
cat Logs/error.log

# View task history
cat .system/state/task_history.jsonl | jq .
```

---

## AI-SPECIFIC GUIDANCE

### How to Request HITL Approval

When task requires human approval:

```python
# Use StateManager.request_approval()
approval_id = state_manager.request_approval(
    task=task,
    reason="Payment-related email requires approval"
)

# This creates file in Pending_Approval/
# Human moves to Approved/ or Rejected/
# Check status with state_manager.check_approval_status(task_id)
```

**File created:**
```
Pending_Approval/APPROVAL_{approval_id}.md
```

**Human action:**
```
Move to: Approved/  -> Execute action
Move to: Rejected/  -> Archive as rejected
```

### How to Update State Between Iterations

```python
# Read current state
state = read_json(".system/state/current_task.json")

# Update with your action
state["iteration"] += 1
state["last_iteration_at"] = datetime.now().isoformat()
state["context"]["last_action"] = "drafted_reply_email"
state["context"]["next_step"] = "request_approval"
state["history"].append({
    "iteration": state["iteration"],
    "action": "draft_reply",
    "timestamp": datetime.now().isoformat()
})

# Write atomically
write_atomic(".system/state/current_task.json", json.dumps(state, indent=2))
```

### Rate Limits

| Action | Limit | Window |
|--------|-------|--------|
| Email sending | 10 emails | Per hour |
| WhatsApp messages | 20 messages | Per hour |
| Payment attempts | 3 attempts | Per hour |
| API calls (Gmail) | 100 calls | Per minute |

**Enforcement:** Check before executing in MCP server

### Secrets Handling

```python
# CORRECT: Load from .env
from dotenv import load_dotenv
load_dotenv(".env")
api_key = os.getenv("GMAIL_CLIENT_ID")

# WRONG: Never hardcode or log secrets
api_key = "actual_key_here"  # NEVER
print(f"Using key: {api_key}")  # NEVER
```

**Rules:**
- Secrets in `.env` only
- Never commit `.env` to Git
- Never log secret values
- Never sync secrets to cloud

---

## COMMON WORKFLOWS

### Workflow 1: Processing a New Email Task

```
1. GmailWatcher detects new email
   |
   v
2. Creates action file in Inbox/Gmail/
   |
   v
3. Orchestrator moves to Needs_Action/
   |
   v
4. You claim task (StateManager.claim_next_pending())
   |
   v
5. Ralph Loop starts:
   Iteration 1: Read email, analyze intent
   Iteration 2: Check client history
   Iteration 3: Draft reply
   Iteration 4: Request approval (if HITL required)
   |
   v
6. Human approves (moves file to Approved/)
   |
   v
7. EmailMCP executes (sends email)
   |
   v
8. Task moved to Done/
   |
   v
9. Audit log updated
```

### Workflow 2: Drafting Reply with HITL

```python
# Iteration: Draft reply
task = read_json("Needs_Action/{task_id}.json")

draft_content = f"""
Subject: Re: {task['data']['subject']}

Dear {task['data']['from'].split('@')[0]},

[Your reply here]

Best regards,
AI Employee
"""

# Update state
state = read_json(".system/state/current_task.json")
state["context"]["last_action"] = "drafted_reply"
state["context"]["draft_content"] = draft_content
write_atomic(".system/state/current_task.json", json.dumps(state, indent=2))

# Request approval
approval_id = state_manager.request_approval(
    task=task,
    reason="Email reply requires approval (company policy)"
)

# Signal completion
print("<status>TASK_COMPLETE</status>")
```

### Workflow 3: Archiving Completed Tasks

```python
# After MCP execution succeeds
def archive_task(task_id: str):
    in_progress = f"In_Progress/{task_id}.json"
    completed = f"Done/{task_id}.json"

    task = read_json(in_progress)
    task["status"] = "completed"
    task["completed_at"] = datetime.now().isoformat()

    write_atomic(completed, json.dumps(task, indent=2))
    os.unlink(in_progress)

    # Append to history
    with open(".system/state/task_history.jsonl", "a") as f:
        f.write(json.dumps(task) + "\n")
```

---

## KNOWN PITFALLS

### Critical Mistakes to Avoid

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| **WhatsApp without HITL** | Privacy violation | ALWAYS check `hitl_required: true` |
| **Secrets in vault** | Security breach | Only in `.env` |
| **No completion signal** | Loop runs forever | Always output `<status>TASK_COMPLETE</status>` |
| **Concurrent task claims** | State corruption | Claim one task at a time |
| **Not updating state** | No-progress exit | Update state after EVERY action |
| **Hardcoding credentials** | Security breach | Use environment variables |
| **Committing .env** | Secrets exposed | `.gitignore` already configured |

### WhatsApp Rules

```
[CRITICAL] ALWAYS requires HITL approval
[CRITICAL] NEVER auto-send
[CRITICAL] Session stored locally only (never sync)
[CRITICAL] Playwright browser must be visible (headless=False)
```

### Email Rules

```
[INFO] Auto-approve: Known contact, <1000 chars, no links
[CRITICAL] HITL required: Unknown sender, >1000 chars, contains links
⚠️ Rate limit: 10 emails/hour maximum
```

### State Management Rules

```
[REQUIRED] Use atomic writes (temp file + rename)
[REQUIRED] Update state after every iteration
[REQUIRED] Document what you did in context.last_action
[REQUIRED] Increment iteration counter
[FORBIDDEN] Don't modify other tasks' state
[FORBIDDEN] Don't skip state updates
```

---

## FILE RELATIONSHIPS

| File | Audience | Purpose | When to Read |
|------|----------|---------|--------------|
| `CONSTITUTION.md` | **Humans + AI** | Governing principles, non-negotiables | First, before any work |
| `SPECIFICATIONS.md` | **Humans + AI** | Complete requirements | When implementing features |
| `AGENTS.md` | **AI Agents** | Working instructions, quick reference | Every iteration |
| `progress.txt` | **AI + Humans** | Ralph Loop progress tracking | Each iteration |
| `.system/state/current_task.json` | **AI** | Current task state | Every iteration |
| `.qwen/skills/{skill}/SKILL.md` | **AI** | Qwen Code Skills (auto-loaded) | When executing skill |

---

## QUICK LINKS

- [CONSTITUTION.md](./CONSTITUTION.md) - Governing principles
- [SPECIFICATIONS.md](./SPECIFICATIONS.md) - Complete requirements
- [BRONZE_TIER.md](./BRONZE_TIER.md) - Phase 1 completion report
- [Ralph Loop Pattern](https://github.com/georgehuntley/ralph-wiggum-loop)

---

## GETTING HELP

If you're stuck as an AI agent:

1. **Check state file** - What was the last action?
2. **Read SPECIFICATIONS.md** - What's the designed approach?
3. **Check CONSTITUTION.md** - Are there rules you're missing?
4. **Log error** - Write to `Logs/error.log`
5. **Request human help** - Move task to `Failed/`

---

**Last Updated:** 2026-02-25
**Version:** 2.1
**Current Phase:** Bronze (Gmail MVP)

*"Local-first, Privacy-first, Human-in-the-Loop, Always Transparent"*
