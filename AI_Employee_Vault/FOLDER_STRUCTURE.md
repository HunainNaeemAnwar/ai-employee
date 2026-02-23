# 📁 AI Employee Vault - Folder Structure

**Version:** 2.0 (Cleaned & Professional)  
**Last Updated:** 2026-02-23  
**Purpose:** Clear, professional folder structure with no duplicates

---

## 🎯 DESIGN PRINCIPLES

1. **Every folder has a clear purpose** - No ambiguous names
2. **No duplicates** - Each type of file has one home
3. **Hackathon compatible** - Symlinks for `/Inbox`, `/Needs_Action`, `/Done`, `/Logs`
4. **Professional** - Clear hierarchy, easy to navigate
5. **Minimal** - Only folders that serve a functional role

---

## 📊 COMPLETE FOLDER STRUCTURE

```
AI_Employee_Vault/
│
├── 📋 Company_Handbook.md          # AI behavior rules (ROOT LEVEL)
├── 📋 Business_Goals.md            # KPIs, targets, metrics (ROOT LEVEL)
├── 📊 Dashboard.md                 # Real-time status (ROOT LEVEL)
│
├── 📥 INPUT_QUEUES/                # New items land here (Hackathon: /Inbox)
│   ├── Gmail/                      # Gmail Watcher drops action files
│   ├── WhatsApp/                   # WhatsApp Watcher drops action files
│   ├── Banking/                    # Finance Watcher drops transaction files
│   └── Files/                      # File system drop folder
│
├── 🔄 PROCESSING/                  # Active task workflow
│   ├── Pending/                    # Tasks waiting to be claimed (Hackathon: /Needs_Action)
│   ├── In_Progress/                # Currently being worked on
│   ├── Plans/                      # Plan.md progress tracking files
│   ├── Pending_Approval/           # Awaiting human approval
│   ├── Approved/                   # Human-approved, ready to execute
│   ├── Rejected/                   # Human-rejected tasks
│   └── Failed/                     # Dead Letter Queue (failed tasks)
│
├── ✅ OUTPUT/                      # Completed work
│   ├── Completed/                  # Finished tasks (Hackathon: /Done)
│   │   └── approvals/              # Processed approval files
│   ├── Reports/                    # CEO Briefings, audit reports
│   └── Archive/                    # Monthly archival (YYYY-MM/)
│
├── 🧠 KNOWLEDGE/                   # Reference information
│   ├── Contexts/                   # Client profiles, history, job alerts
│   └── Procedures/                 # Reusable SOPs, how-to guides
│
├── 🛡️ SECURITY/                    # Sensitive data (NEVER SYNC)
│   ├── .env                        # API credentials (NEVER COMMIT)
│   └── audit_logs/                 # Action audit logs (Hackathon: /Logs)
│
└── ⚙️ SYSTEM/                      # System state & config
    ├── state/                      # Current task state
    │   ├── current_task.json       # Current processing state
    │   └── task_history.jsonl      # Historical task log
    └── config/                     # System configurations
        ├── watchers.yaml           # Watcher configurations
        └── mcp_config.yaml         # MCP server configurations
```

---

## 📋 FOLDER PURPOSES

### Root Level Files

| File | Purpose | Edit Frequency |
|------|---------|----------------|
| `Company_Handbook.md` | AI behavior rules, autonomy levels | Monthly |
| `Business_Goals.md` | KPIs, targets, metrics | Weekly |
| `Dashboard.md` | Real-time system status | Auto-generated |

### INPUT_QUEUES/

**Purpose:** Entry point for all new items detected by Watchers.

| Subfolder | Source | Watcher |
|-----------|--------|---------|
| `Gmail/` | Gmail API | GmailWatcher (2 min poll) |
| `WhatsApp/` | WhatsApp Web | WhatsAppWatcher (30 sec poll) |
| `Banking/` | Bank CSV/API | FinanceWatcher (daily 9 AM) |
| `Files/` | Local file system | FileSystemWatcher (realtime) |

**Lifecycle:** Items moved to `PROCESSING/Pending/` within 10 seconds.

---

### PROCESSING/

**Purpose:** Active task workflow - where work happens.

| Subfolder | Purpose | Who Moves Here | Who Moves Out |
|-----------|---------|----------------|---------------|
| `Pending/` | Tasks waiting to be claimed | Orchestrator | Orchestrator (claim) |
| `In_Progress/` | Currently being worked on | Orchestrator | Orchestrator (complete) |
| `Plans/` | Plan.md progress tracking | Ralph Loop | Auto-archive |
| `Pending_Approval/` | Awaiting human approval | Ralph Loop | Human (approve/reject) |
| `Approved/` | Human-approved actions | Human | Orchestrator (execute) |
| `Rejected/` | Human-rejected actions | Human | Auto-archive |
| `Failed/` | Failed tasks (DLQ) | Orchestrator | Human (review) |

**Hackathon Names:**
- `Pending/` = `/Needs_Action`
- Symlink created for compatibility

---

### OUTPUT/

**Purpose:** Completed work and reports.

| Subfolder | Purpose | Retention |
|-----------|---------|-----------|
| `Completed/` | Finished tasks | 90 days |
| `Completed/approvals/` | Processed approval files | 90 days |
| `Reports/` | CEO Briefings, audit reports | 1 year |
| `Archive/` | Monthly archival | Indefinite |

**Hackathon Names:**
- `Completed/` = `/Done`
- Symlink created for compatibility

---

### KNOWLEDGE/

**Purpose:** Reference information for AI and humans.

| Subfolder | Content | Update Frequency |
|-----------|---------|------------------|
| `Contexts/` | Client profiles, history, job alerts | As needed |
| `Procedures/` | SOPs, how-to guides, best practices | Monthly |

**Example Files:**
- `Contexts/clients.md` - Known client database
- `Procedures/email_response.md` - Email response guidelines

---

### SECURITY/

**Purpose:** Sensitive data that should NEVER sync to cloud.

| File/Folder | Content | Git Status |
|-------------|---------|------------|
| `.env` | API credentials | ❌ Never commit |
| `audit_logs/` | Action audit logs (JSONL) | ❌ Never commit |

**Hackathon Names:**
- `audit_logs/` = `/Logs`
- Symlink created for compatibility

**Security Rules:**
1. Never commit `.env` to Git
2. Never sync to cloud (Platinum tier: separate local secrets)
3. chmod 600 on `.env`

---

### SYSTEM/

**Purpose:** System state and configuration.

| Subfolder | Content | Auto/Manual |
|-----------|---------|-------------|
| `state/` | Current task state | Auto-generated |
| `config/` | System configurations | Manual |

**Key Files:**
- `state/current_task.json` - Current processing state
- `state/task_history.jsonl` - Historical task log
- `config/watchers.yaml` - Watcher configurations
- `config/mcp_config.yaml` - MCP server configurations

---

## 🗑️ REMOVED FOLDERS (Cleanup)

The following folders were removed for being duplicates or unnecessary:

| Removed Folder | Reason | Consolidated Into |
|----------------|--------|-------------------|
| `PROCESSING/Processed/` | Empty, unclear purpose | N/A |
| `PROCESSING/Sending/` | Temporary folder, not needed | N/A |
| `SYSTEM/logs/` | Empty, unused | N/A |
| `SYSTEM/audit/` | Duplicate audit location | `SECURITY/audit_logs/` |
| `SYSTEM/audit_logs/` | Duplicate audit location | `SECURITY/audit_logs/` |
| `SYSTEM/audit_trail/` | Duplicate audit location | `SECURITY/audit_logs/` |
| `OUTPUT/Audit/` | Duplicate audit location | `SECURITY/audit_logs/` |
| `KNOWLEDGE/Job_Alerts/` | Low usage | `KNOWLEDGE/Contexts/` |

**Audit Log Consolidation:**
- All audit logs now in `SECURITY/audit_logs/`
- Audit reports (markdown) moved to `OUTPUT/Reports/`
- Single source of truth for audit trail

---

## 📊 FOLDER STATISTICS

| Category | Folder Count | File Count (avg) |
|----------|--------------|------------------|
| **Input** | 4 | 10-50 |
| **Processing** | 7 | 5-20 |
| **Output** | 3 | 50-200 |
| **Knowledge** | 2 | 10-50 |
| **Security** | 1 (+ files) | 30-100 |
| **System** | 2 | 5-10 |
| **TOTAL** | **19** | **110-330** |

---

## 🔄 FILE LIFECYCLE

```
1. Email arrives
   ↓
2. INPUT_QUEUES/Gmail/action_*.json created
   ↓
3. Moved to PROCESSING/Pending/
   ↓
4. Claimed → PROCESSING/In_Progress/
   ↓
5. Ralph Loop → PROCESSING/Plans/PLAN_*.md created
   ↓
6. Approval needed → PROCESSING/Pending_Approval/APPROVAL_*.md
   ↓
7. Human approves → Moved to PROCESSING/Approved/
   ↓
8. Email sent → Moved to OUTPUT/Completed/
   ↓
9. Audit logged → SECURITY/audit_logs/YYYY-MM-DD.jsonl
   ↓
10. Monthly → Moved to OUTPUT/Archive/YYYY-MM/
```

---

## 🎯 HACKATHON COMPLIANCE

| Hackathon Folder | Our Implementation | Symlink |
|------------------|-------------------|---------|
| `/Inbox` | `INPUT_QUEUES/` | ✅ Created |
| `/Needs_Action` | `PROCESSING/Pending/` | ✅ Created |
| `/Plans` | `PROCESSING/Plans/` | ✅ Direct match |
| `/Done` | `OUTPUT/Completed/` | ✅ Created |
| `/Pending_Approval` | `PROCESSING/Pending_Approval/` | ✅ Direct match |
| `/Approved` | `PROCESSING/Approved/` | ✅ Direct match |
| `/Rejected` | `PROCESSING/Rejected/` | ✅ Direct match |
| `/Logs` | `SECURITY/audit_logs/` | ✅ Created |

**All hackathon folder requirements met!** ✅

---

## 📝 MAINTENANCE

### Weekly
- Review `PROCESSING/Failed/` for recoverable tasks
- Archive old `OUTPUT/Completed/` files (> 30 days)

### Monthly
- Move `OUTPUT/Completed/` to `OUTPUT/Archive/YYYY-MM/`
- Review `SECURITY/audit_logs/` for patterns
- Update `KNOWLEDGE/Contexts/clients.md`

### Quarterly
- Review folder structure for optimization
- Archive old `SECURITY/audit_logs/` (> 90 days)
- Update `KNOWLEDGE/Procedures/` with lessons learned

---

**Last Cleanup:** 2026-02-23  
**Folders Removed:** 8 duplicate/empty folders  
**Files Consolidated:** Audit logs from 5 locations → 1  
**Status:** ✅ Clean, professional, no duplicates
