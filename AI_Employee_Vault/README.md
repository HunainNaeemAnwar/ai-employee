# AI Employee Vault

**Purpose:** Obsidian vault for Personal AI Employee system

**Structure:**
```
AI_Employee_Vault/
├── Company_Handbook.md       # AI behavior rules (ROOT)
├── Business_Goals.md         # KPIs, targets (ROOT)
├── Dashboard.md              # Real-time status (ROOT)
├── Inbox/                    # Watcher drop zone (Gmail/, WhatsApp/, etc.)
├── Needs_Action/             # Tasks waiting to be processed
├── Plans/                    # Execution plans
├── Done/                     # Completed tasks
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Ready to execute
├── Rejected/                 # Discarded
├── Knowledge/                # Contexts, procedures
├── Logs/                     # Audit logs
└── .system/                  # State, config (hidden)
```

## Qwen Code Skills

Skills are stored in `.qwen/skills/` (project-level) or `~/.qwen/skills/` (personal):

- `email-triage` - Categorize and prioritize emails
- `email-reply-draft` - Draft email replies  
- `client-lookup` - Check if sender is known client

## Getting Started

1. **Setup Credentials:**
   ```bash
   cp AI_Employee_Vault/SECURITY/.env.example AI_Employee_Vault/SECURITY/.env
   # Edit .env with your Gmail API credentials
   ```

2. **Start Orchestrator:**
   ```bash
   python scripts/orchestrator.py
   ```

3. **Check Status:**
   ```bash
   cat AI_Employee_Vault/SYSTEM/state/current_task.json
   ```

## Current Phase: Bronze (Gmail MVP)

**Success Criteria:**
- New email → Watcher detects → Qwen drafts → HITL → Email sent

---

**Last Updated:** 2026-02-17
