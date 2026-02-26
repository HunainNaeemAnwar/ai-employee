# Task Lifecycle Flow

**Document Purpose:** Complete flow of how tasks move through the AI Employee system

**Last Updated:** 2026-02-26

---

## 🔄 Complete Task Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMAIL PROCESSING FLOW                         │
└─────────────────────────────────────────────────────────────────┘

1. Inbox/Gmail/
   │
   │ Gmail Watcher detects new email
   │ Creates: action_{timestamp}_{id}.json
   │
   ▼
2. Needs_Action/
   │
   │ Orchestrator claims task (every 10 seconds)
   │ Moves file → In_Progress/
   │
   ▼
3. In_Progress/  ← Tasks are processed here
   │
   ├─→ Is promotional/no-reply?
   │   │
   │   └─→ Auto-skip → Done/  ✅
   │
   ├─→ Normal email?
   │   │
   │   └─→ Ralph Loop processes
   │       │
   │       ├─→ Draft created?
   │       │   │
   │       │   └─→ Create approval request
   │       │       │
   │       │       ├─→ Create: Pending_Approval/APPROVAL_{id}.md
   │       │       │
   │       │       └─→ Move: In_Progress/{task}.json → Pending_Approval/{task}.json
   │       │           │
   │       │           ▼
   │       │       Pending_Approval/  ← Waiting for human
   │       │           │
   │       │           │ Human moves file:
   │       │           ├─→ Approved/  → Send email → Done/ ✅
   │       │           └─→ Rejected/  → Discard → Rejected/ ✖
   │       │
   │       └─→ No draft (categorization only)?
   │           │
   │           └─→ Move: In_Progress/ → Done/ ✅
   │
   └─→ Ralph Loop error?
       │
       └─→ Move: In_Progress/ → Failed/ ✖

```

---

## 📁 Folder Descriptions

| Folder | Purpose | Who Moves Here |
|--------|---------|----------------|
| **Inbox/Gmail/** | Gmail Watcher drop zone | Gmail Watcher |
| **Needs_Action/** | Queue waiting to be processed | Gmail Watcher → Orchestrator |
| **In_Progress/** | Currently being worked on | Orchestrator (claim) |
| **Pending_Approval/** | Awaiting human approval | Orchestrator (after Ralph Loop) |
| **Approved/** | Human approved, ready to execute | Human (manual move) |
| **Rejected/** | Human rejected | Human (manual move) |
| **Done/** | Completed tasks | Orchestrator (auto-skip or after send) |
| **Failed/** | Failed tasks | Orchestrator (error handling) |

---

## 🔍 Task File States

### State 1: New Email Detected
```
Location: Inbox/Gmail/action_{timestamp}_{id}.json
Status: "new"
```

### State 2: Waiting to be Processed
```
Location: Needs_Action/action_{timestamp}_{id}.json
Status: "pending"
```

### State 3: Being Processed
```
Location: In_Progress/action_{timestamp}_{id}.json
Status: "in_progress"
```

### State 4a: Auto-Skipped (Promotional/No-Reply)
```
Location: Done/action_{timestamp}_{id}.json
Status: "completed"
Reason: "Auto-skipped (promotional)"
```

### State 4b: Awaiting Approval
```
Location: Pending_Approval/action_{timestamp}_{id}.json
        + Pending_Approval/APPROVAL_{approval_id}.md
Status: "pending_approval"
```

### State 5a: Approved and Sent
```
Location: Done/approvals/APPROVAL_{approval_id}.md
Status: "completed"
Result: Email sent via Gmail API
```

### State 5b: Rejected
```
Location: Rejected/APPROVAL_{approval_id}.md
Status: "rejected"
Result: Discarded
```

---

## ⚡ Auto-Skip Rules

Tasks that skip human approval:

| Type | Condition | Action |
|------|-----------|--------|
| **Promotional** | `type == "promotional"` | Move to Done/ |
| **No-Reply** | Sender contains: no-reply, noreply, newsletter, notifications | Move to Done/ |
| **Marketing** | Sender domain: mail.*, notifications.*, etc. | Move to Done/ |

---

## 🎯 Ralph Loop Outcomes

| Outcome | Action | File Movement |
|---------|--------|---------------|
| **Draft created** | Create approval request | In_Progress/ → Pending_Approval/ |
| **No draft needed** | Mark as categorized | In_Progress/ → Done/ |
| **Error occurred** | Log error | In_Progress/ → Failed/ |

---

## 📊 Dashboard Integration

Dashboard.md shows real-time counts:

```markdown
## 📥 Task Queue Status

| Folder | Count | Description |
|--------|-------|-------------|
| Inbox/Gmail/ | 0 | New emails detected |
| Needs_Action/ | 5 | Tasks waiting to be claimed |
| In_Progress/ | 0 | Currently being worked on |
| Pending_Approval/ | 2 | Awaiting human approval |
| Done/ | 10 | Tasks completed today |
```

**Update Frequency:** Every 10 seconds (when orchestrator running)

---

## 🛠️ Troubleshooting

### In_Progress/ Has Stuck Tasks

**Symptom:** Tasks stay in In_Progress/ but don't move forward

**Cause:** Orchestrator not running or Ralph Loop not completing

**Fix:**
```bash
# Run cleanup script
python scripts/cleanup_in_progress.py

# Start orchestrator
python main.py start
```

### Tasks Not Being Claimed

**Symptom:** Tasks stay in Needs_Action/ forever

**Cause:** Orchestrator not running

**Fix:**
```bash
# Check if orchestrator is running
python main.py status

# Start orchestrator
python main.py start
```

### Approval Files Not Moving

**Symptom:** Approval files stay in Pending_Approval/

**Cause:** Human hasn't moved file to Approved/ or Rejected/

**Fix:**
```bash
# List pending approvals
ls AI_Employee_Vault/Pending_Approval/

# Read approval content
cat AI_Employee_Vault/Pending_Approval/APPROVAL_*.md

# Move to Approved/ to send
mv AI_Employee_Vault/Pending_Approval/APPROVAL_*.md \
   AI_Employee_Vault/Approved/

# Or move to Rejected/ to discard
mv AI_Employee_Vault/Pending_Approval/APPROVAL_*.md \
   AI_Employee_Vault/Rejected/
```

---

## 📈 Metrics Tracked

| Metric | Where Logged |
|--------|--------------|
| Email detected | Logs/YYYY-MM-DD.jsonl |
| Task claimed | Logs/YYYY-MM-DD.jsonl |
| Ralph Loop iterations | .system/state/current_task.json |
| Approval requested | Logs/YYYY-MM-DD.jsonl |
| Email sent | Logs/YYYY-MM-DD.jsonl |
| Task completed | Logs/YYYY-MM-DD.jsonl + .system/state/task_history.jsonl |

---

**Related Documents:**
- [BRONZE_TIER.md](./BRONZE_TIER.md) - Phase 1 completion report
- [SPECIFICATIONS.md](./SPECIFICATIONS.md) - Complete technical specs
- [AGENTS.md](./AGENTS.md) - AI agent working guide
