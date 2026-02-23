# 🤖 AGENTS.md - AI Agent Working Guide

**Version:** 1.0  
**Audience:** AI Coding Agents (Qwen, Claude Code, etc.)  
**Purpose:** README for AI agents working on Personal AI Employee project

---

## 📋 TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [Phase-Wise Development](#phase-wise-development)
3. [Quick Start for AI Agents](#quick-start-for-ai-agents)
4. [Ralph Loop Workflow](#ralph-loop-workflow)
5. [Project Structure](#project-structure)
6. [Development Commands](#development-commands)
7. [AI-Specific Guidance](#ai-specific-guidance)
8. [Common Workflows](#common-workflows)
9. [Known Pitfalls](#known-pitfalls)
10. [File Relati``onships](#file-relationships)

---

## 🎯 PROJECT OVERVIEW

### What We're Building

**Personal AI Employee** - A Digital FTE (Full-Time Equivalent) that autonomously manages personal and business tasks 24/7:

- ✉️ Email triage and responses (Gmail)
- 💬 WhatsApp message monitoring and replies
- 🏦 Bank transaction tracking and accounting
- 📱 Social media management (LinkedIn, Twitter/X, Instagram)
- 📊 Weekly business audits and CEO briefings

### Core Philosophy

| Principle | Description |
|-----------|-------------|
| **Local-First** | Data stays on your machine, not cloud |
| **Privacy-First** | Secrets never leave your device |
| **Human-in-the-Loop** | AI suggests, human approves critical actions |
| **Transparent** | All decisions logged, auditable |

### AI Engine

- **Primary:** Qwen CLI (`qwen --file prompt.md --cwd <vault>`)
- **Pattern:** Ralph Wiggum Loop (iterative execution until completion)
- **State:** JSON files in Obsidian vault
- **Actions:** MCP servers (Email, Browser, WhatsApp, Odoo)

---

## 📊 PHASE-WISE DEVELOPMENT

**We build incrementally, phase by phase. Complete each phase before starting the next.**

### Phase 1: Bronze (Week 1)

```
Goal: Working MVP with Gmail automation
```

**Must Have:**
- [ ] Gmail Watcher (poll every 2 min)
- [ ] Ralph Wiggum Loop (external orchestrator)
- [ ] Email MCP (Gmail API)
- [ ] HITL approval workflow (file-based)
- [ ] Obsidian vault with root-level handbook
- [ ] State persistence (JSON files)
- [ ] Audit logging (JSONL)

**Success Criteria:**
```
New email → Watcher detects → Qwen drafts → HITL approval → Email sent
```

### Phase 2: Silver (Week 2)

```
Goal: Multi-channel automation with scheduling
```

**Must Have (all Bronze +):**
- [ ] WhatsApp Watcher (Playwright, 30 sec poll)
- [ ] WhatsApp MCP (LOCAL ONLY, HITL always)
- [ ] LinkedIn MCP (auto-posting)
- [ ] Scheduled jobs (CEO Briefing @ Mon 7 AM)
- [ ] Circuit breakers (error recovery)
- [ ] Rate limiting (10 emails/hour)

**Success Criteria:**
```
WhatsApp message → Always requires approval
CEO Briefing generates automatically Monday 7 AM
```

### Phase 3: Gold (Week 3-4)

```
Goal: Full cross-domain integration
```

**Must Have (all Silver +):**
- [ ] Finance Watcher (bank CSV/API, daily sync)
- [ ] Odoo MCP (invoice generation, accounting)
- [ ] Twitter/X MCP
- [ ] Instagram MCP
- [ ] CEO Briefing Generator (comprehensive report)
- [ ] Hash chain audit logs (tamper-evident)
- [ ] SQLite migration (concurrent access)

**Success Criteria:**
```
Bank transactions synced daily
Invoices auto-generated from completed tasks
Tamper-evident audit trail
```

### Phase 4: Platinum (Week 5-6)

```
Goal: Production 24/7 deployment
```

**Must Have (all Gold +):**
- [ ] Cloud deployment (Oracle Cloud Free Tier)
- [ ] Cloud/Local split (cloud drafts, local approves)
- [ ] Git-based vault sync (secrets excluded)
- [ ] 24/7 operation with health monitoring
- [ ] Prometheus + Grafana dashboard
- [ ] Alerting (PagerDuty/Slack)
- [ ] Automated backups

**Success Criteria:**
```
Cloud agent can draft, local must approve
Vault syncs without conflicts
Health dashboard shows system status
```

### Phase Rules

1. ✅ Complete each phase before starting next
2. ✅ Each phase must be independently testable
3. ✅ Documentation updated per phase
4. ✅ No phase skipped or partially implemented

---

## 🚀 QUICK START FOR AI AGENTS

### Environment Setup

**Virtual Environment:** Already created and activated in project root using `uv`.

```bash
# The venv is located at: /home/hunain/personal_assistant/.venv
# It should already be activated in your current session
```

### Before Starting Work

1. **Read CONSTITUTION.md** - Governing principles (NON-NEGOTIABLE)
2. **Read ARCHITECTURE.md** - Technical design specification
3. **Check current state** - `SYSTEM/state/current_task.json`
4. **Review progress** - `progress.txt` (if using Ralph Loop)
5. **Check Qwen Skills** - `.qwen/skills/` (auto-loaded by Qwen Code)

### File Priority Order

When starting a task, read in this order:

```
1. CONSTITUTION.md       (rules you must follow)
2. ARCHITECTURE.md       (design you must implement)
3. AGENTS.md             (this file - working instructions)
4. SYSTEM/state/current_task.json  (current task state)
5. PROCESSING/In_Progress/{task}.json  (task details)
```

**Qwen Code Skills** are auto-loaded from `.qwen/skills/` when you use Qwen CLI.

### Current Phase Check

```bash
# Check which phase we're in
cat progress.txt | grep "PHASE:"

# Check current task
cat SYSTEM/state/current_task.json
```

---

## 🤖 MCP SERVER USAGE GUIDE

### Overview

MCP (Model Context Protocol) servers are Python modules that execute actions validated by the orchestrator.

### MCP Framework Pattern

```python
from mcp_servers.base_mcp import BaseMCP, ValidationResult, ExecutionResult

class EmailMCP(BaseMCP):
    def validate(self, action: dict) -> ValidationResult:
        # Check rate limits, HITL approval, parameters
        return ValidationResult(success=True)
    
    def execute(self, action: dict) -> ExecutionResult:
        # Perform the action
        return ExecutionResult(success=True, output="Email sent")
```

### Using MCPs in Orchestrator

```python
from mcp_servers.email_mcp import EmailMCP

# Initialize MCP
email_mcp = EmailMCP(vault_path="/path/to/vault")

# Validate action
action = {"to": "client@example.com", "subject": "Update", "body": "..."}
result = email_mcp.validate(action)

if result.success:
    # Execute action
    result = email_mcp.execute(action)
    
    # Audit log
    log_entry = email_mcp.audit_log(action, result)
```

### HITL Approval with MCPs

```python
# Check if HITL required
if mcp._requires_hitl(action):
    if not action.get('hitl_approved'):
        # Create approval request
        approval_id = state_manager.request_approval(task, reason="...")
        # Wait for user to move file to Approved/
```

### Rate Limiting

Each MCP enforces rate limits:

| MCP | Rate Limit |
|-----|------------|
| EmailMCP | 10 emails/hour |
| BrowserMCP | 60 actions/hour |
| WhatsAppMCP | 20 messages/hour |
| OdooMCP | 50 API calls/hour |
| SocialMCP | 5 posts/hour/platform |

### Available MCPs by Tier

| Tier | MCPs |
|------|------|
| **Bronze** | StateMCP, EmailMCP |
| **Silver** | + BrowserMCP, WhatsAppMCP |
| **Gold** | + OdooMCP, SocialMCP |
| **Platinum** | + SyncMCP |

---

## 🔄 RALPH LOOP WORKFLOW

### What is Ralph Loop?

The **Ralph Wiggum Loop** is an iterative execution pattern where:
1. AI reads state from files
2. AI takes ONE concrete action
3. AI updates state files
4. Loop repeats until completion

### Your Role in Ralph Loop

```
Iteration Start:
  ↓
1. Read SYSTEM/state/current_task.json
2. Read task from PROCESSING/In_Progress/{task_id}.json
3. Understand what previous iteration did
4. Take ONE concrete action (not planning, DOING)
5. Update state file with what you did
6. Check if task complete
  ↓
If Complete:
  → Output: <status>TASK_COMPLETE</status>
  → OR create: SYSTEM/state/complete.flag
If Not Complete:
  → Next iteration continues
```

### Completion Signals

You MUST signal completion ONE of these ways:

| Signal | How |
|--------|-----|
| **stdout** | Output `<status>TASK_COMPLETE</status>` |
| **stdout (alt)** | Output `<promise>COMPLETE</promise>` |
| **file** | Create `SYSTEM/state/complete.flag` |

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

## 📁 PROJECT STRUCTURE

### Root Level

```
personal_assistant/
├── AGENTS.md              ← This file (AI working instructions)
├── CONSTITUTION.md        ← Governing principles (READ FIRST)
├── ARCHITECTURE.md        ← Technical design spec
├── progress.txt           ← Ralph Loop progress tracking
└── AI_Employee_Vault/     ← Obsidian vault
```

### Vault Structure

```
AI_Employee_Vault/
├── 📋 Company_Handbook.md    ← AI behavior rules (ROOT)
├── 📋 Business_Goals.md      ← KPIs, targets (ROOT)
│
├── 📥 INPUT_QUEUES/
│   ├── Gmail/               ← Gmail Watcher drops here
│   ├── WhatsApp/            ← WhatsApp Watcher drops here
│   ├── Banking/             ← Finance Watcher drops here
│   └── Files/               ← File system drops here
│
├── 🔄 PROCESSING/
│   ├── Pending/             ← Tasks waiting to be claimed
│   ├── In_Progress/         ← Currently working on
│   ├── Plans/               ← Generated execution plans
│   ├── Pending_Approval/    ← HITL queue (sensitive actions)
│   ├── Approved/            ← Human-approved, ready to execute
│   ├── Rejected/            ← Human-rejected
│   └── Failed/              ← Dead Letter Queue
│
├── ✅ OUTPUT/
│   ├── Completed/           ← Finished tasks
│   ├── Reports/             ← CEO Briefings, audits
│   └── Archive/             ← Monthly archival
│
├── 🧠 KNOWLEDGE/
│   ├── Contexts/            ← Client profiles, history
│   └── Procedures/          ← Reusable SOPs
│
├── 🤖 QWEN SKILLS/ (auto-loaded by Qwen Code)
│   ├── .qwen/skills/        ← Project skills (git-shareable)
│   │   ├── email-triage/
│   │   ├── email-reply-draft/
│   │   └── client-lookup/
│   └── ~/.qwen/skills/      ← Personal skills (global)
│
├── 🛡️ SECURITY/
│   ├── .env                 ← API keys (NEVER COMMIT)
│   └── audit_logs/          ← Action logs (YYYY-MM-DD.jsonl)
│
└── ⚙️ SYSTEM/
    ├── state/               ← Current task states
    │   ├── current_task.json
    │   ├── task_history.jsonl
    │   └── complete.flag    ← Completion signal
    ├── config/              ← Watcher configurations
    └── logs/                ← Error & performance logs
```

---

## ⌨️ DEVELOPMENT COMMANDS

### Running the System

```bash
# Start orchestrator (main loop)
python scripts/orchestrator.py --vault ~/AI_Employee_Vault

# Run Ralph Loop manually
python scripts/ralph_loop.py --vault ~/AI_Employee_Vault --task <task_id>

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
cat SECURITY/audit_logs/$(date +%Y-%m-%d).jsonl

# View error log
tail -50 SYSTEM/logs/error.log

# View task history
cat SYSTEM/state/task_history.jsonl | jq .
```

---

## 🎯 AI-SPECIFIC GUIDANCE

### How to Request HITL Approval

When task requires human approval:

```python
# Use StateManager.request_approval()
approval_id = state_manager.request_approval(
    task=task,
    reason="Payment-related email requires approval"
)

# This creates file in PROCESSING/Pending_Approval/
# Human moves to Approved/ or Rejected/
# Check status with state_manager.check_approval_status(task_id)
```

**File created:**
```
PROCESSING/Pending_Approval/APPROVAL_{approval_id}.md
```

**Human action:**
```
Move to: PROCESSING/Approved/  → Execute action
Move to: PROCESSING/Rejected/  → Archive as rejected
```

### How to Update State Between Iterations

```python
# Read current state
state = read_json("SYSTEM/state/current_task.json")

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
write_atomic("SYSTEM/state/current_task.json", json.dumps(state, indent=2))
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
# ✅ CORRECT: Load from .env
from dotenv import load_dotenv
load_dotenv("SECURITY/.env")
api_key = os.getenv("GMAIL_CLIENT_ID")

# ❌ WRONG: Never hardcode or log secrets
api_key = "actual_key_here"  # NEVER
print(f"Using key: {api_key}")  # NEVER
```

**Rules:**
- Secrets in `SECURITY/.env` only
- Never commit `.env` to Git
- Never log secret values
- Never sync secrets to cloud

---

## 📋 COMMON WORKFLOWS

### Workflow 1: Processing a New Email Task

```
1. GmailWatcher detects new email
   ↓
2. Creates action file in INPUT_QUEUES/Gmail/
   ↓
3. Orchestrator moves to PROCESSING/Pending/
   ↓
4. You claim task (StateManager.claim_next_pending())
   ↓
5. Ralph Loop starts:
   Iteration 1: Read email, analyze intent
   Iteration 2: Check client history
   Iteration 3: Draft reply
   Iteration 4: Request approval (if HITL required)
   ↓
6. Human approves (moves file to Approved/)
   ↓
7. EmailMCP executes (sends email)
   ↓
8. Task moved to OUTPUT/Completed/
   ↓
9. Audit log updated
```

### Workflow 2: Drafting Reply with HITL

```python
# Iteration: Draft reply
task = read_json("PROCESSING/In_Progress/{task_id}.json")

draft_content = f"""
Subject: Re: {task['data']['subject']}

Dear {task['data']['from'].split('@')[0]},

[Your reply here]

Best regards,
AI Employee
"""

# Update state
state = read_json("SYSTEM/state/current_task.json")
state["context"]["last_action"] = "drafted_reply"
state["context"]["draft_content"] = draft_content
write_atomic("SYSTEM/state/current_task.json", json.dumps(state, indent=2))

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
    in_progress = f"PROCESSING/In_Progress/{task_id}.json"
    completed = f"OUTPUT/Completed/{task_id}.json"
    
    task = read_json(in_progress)
    task["status"] = "completed"
    task["completed_at"] = datetime.now().isoformat()
    
    write_atomic(completed, json.dumps(task, indent=2))
    os.unlink(in_progress)
    
    # Append to history
    with open("SYSTEM/state/task_history.jsonl", "a") as f:
        f.write(json.dumps(task) + "\n")
```

---

## ⚠️ KNOWN PITFALLS

### Critical Mistakes to Avoid

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| **WhatsApp without HITL** | Privacy violation | ALWAYS check `hitl_required: true` |
| **Secrets in vault** | Security breach | Only in `SECURITY/.env` |
| **No completion signal** | Loop runs forever | Always output `<status>TASK_COMPLETE</status>` |
| **Concurrent task claims** | State corruption | Claim one task at a time |
| **Not updating state** | No-progress exit | Update state after EVERY action |
| **Hardcoding credentials** | Security breach | Use environment variables |
| **Committing .env** | Secrets exposed | `.gitignore` already configured |

### WhatsApp Rules

```
🔴 ALWAYS requires HITL approval
🔴 NEVER auto-send
🔴 Session stored locally only (never sync)
🔴 Playwright browser must be visible (headless=False)
```

### Email Rules

```
🟢 Auto-approve: Known contact, <1000 chars, no links
🔴 HITL required: Unknown sender, >1000 chars, contains links
⚠️ Rate limit: 10 emails/hour maximum
```

### State Management Rules

```
✅ Use atomic writes (temp file + rename)
✅ Update state after every iteration
✅ Document what you did in context.last_action
✅ Increment iteration counter
❌ Don't modify other tasks' state
❌ Don't skip state updates
```

---

## 📎 FILE RELATIONSHIPS

| File | Audience | Purpose | When to Read |
|------|----------|---------|--------------|
| `CONSTITUTION.md` | **Humans + AI** | Governing principles, non-negotiables | First, before any work |
| `ARCHITECTURE.md` | **Humans + AI** | Technical design, component specs | When implementing features |
| `AGENTS.md` | **AI Agents** | Working instructions, quick reference | Every iteration |
| `progress.txt` | **AI + Humans** | Ralph Loop progress tracking | Each iteration |
| `SYSTEM/state/current_task.json` | **AI** | Current task state | Every iteration |
| `.qwen/skills/{skill}/SKILL.md` | **AI** | Qwen Code Skills (auto-loaded) | When executing skill |

---

## 🔗 QUICK LINKS

- [CONSTITUTION.md](./CONSTITUTION.md) - Governing principles
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Technical design
- [Ralph Loop Pattern](https://github.com/georgehuntley/ralph-wiggum-loop) - Original documentation
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification

---

## 📞 GETTING HELP

If you're stuck as an AI agent:

1. **Check state file** - What was the last action?
2. **Review Skill Library** - Is there a skill for this?
3. **Read Architecture** - What's the designed approach?
4. **Check Constitution** - Are there rules you're missing?
5. **Log error** - Write to `SYSTEM/logs/error.log`
6. **Request human help** - Move task to `PROCESSING/Failed/`

---

**Last Updated:** 2026-02-17  
**Version:** 1.0  
**Current Phase:** Bronze (Gmail MVP)

*"Local-first, Privacy-first, Human-in-the-Loop, Always Transparent"*
