# 📜 PERSONAL AI EMPLOYEE HACKATHON - CONSTITUTION

**Version:** 1.0  
**Adopted:** 2026-02-17  
**Status:** Supreme Law of the AI Employee System

---

## 🎯 PREAMBLE

We, the builders of the Personal AI Employee system, in order to create a **Digital FTE (Full-Time Equivalent)** that autonomously manages personal and business tasks while preserving privacy, ensuring human oversight, and maintaining transparency, do ordain and establish this Constitution as the supreme governing document of our architecture.

---

## 🏛️ ARTICLE I - CORE PHILOSOPHY

### Section 1.1: Local-First Principle
> **Data stays on your machine, not cloud.**

- All processing occurs on local hardware (laptop/desktop)
- Cloud deployment (Platinum tier) is optional and only for drafting
- Sensitive actions ALWAYS require local execution
- No dependency on external servers for core functionality

### Section 1.2: Privacy-First Principle
> **Secrets never leave your device.**

- API credentials stored in `.env` files only (SECURITY/.env)
- WhatsApp sessions, banking credentials: LOCAL ONLY, never sync
- No telemetry, no analytics, no tracking
- User owns all data, no third-party access

### Section 1.3: Human-in-the-Loop Principle
> **AI suggests, human approves critical actions.**

- All sensitive actions require explicit human approval
- Approval workflow: file-based (move Pending_Approval → Approved/Rejected)
- Auto-approve only for low-risk, repetitive tasks
- Human can override any AI decision

### Section 1.4: Transparency Principle
> **All decisions logged, auditable.**

- Every action logged to SECURITY/audit_logs/YYYY-MM-DD.jsonl
- Task history persisted in SYSTEM/state/task_history.jsonl
- Audit trail includes: timestamp, actor, action, result
- Gold tier+: hash chain for tamper evidence

---

## 🏗️ ARTICLE II - SYSTEM ARCHITECTURE

### Section 2.1: Core Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                         │
│  Gmail API │ WhatsApp Web │ Bank CSV │ File System Drop    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              PERCEPTION LAYER (Watchers - Python)           │
│  - Gmail Watcher (2 min poll)                               │
│  - WhatsApp Watcher (30 sec poll)                           │
│  - File Watcher (realtime via watchdog)                     │
│  - Finance Watcher (daily 9 AM)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              KNOWLEDGE LAYER (Vault - Obsidian)             │
│  - Company_Handbook.md (root)                               │
│  - Business_Goals.md (root)                                 │
│  - PROCESSING/ (task state)                                 │
│  - SYSTEM/state/ (current state)                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BRAIN LAYER (Qwen CLI - Reasoning)             │
│  - Spawned as subprocess                                    │
│  - File-based prompts (--file prompt.md)                    │
│  - 5-minute timeout per iteration                           │
│  - Ralph Loop: iterate until completion                     │
│  - Qwen Code Skills auto-loaded from .qwen/skills/          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              ACTION LAYER (MCP Servers - Python)            │
│  - Email MCP (Gmail API / SMTP)                             │
│  - Browser MCP (Playwright)                                 │
│  - WhatsApp MCP (Playwright + WhatsApp Web)                 │
│  - Odoo MCP (JSON-RPC) - Gold tier                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              OUTPUT LAYER (Completed Tasks)                 │
│  - OUTPUT/Completed/                                        │
│  - OUTPUT/Reports/ (CEO Briefings)                          │
│  - OUTPUT/Archive/ (monthly)                                │
└─────────────────────────────────────────────────────────────┘
```

### Section 2.2: Ralph Wiggum Loop Pattern

```
while task not complete:
    1. Read state from SYSTEM/state/current_task.json
    2. Read task from PROCESSING/In_Progress/{task_id}.json
    3. Build prompt for Qwen
    4. Spawn Qwen subprocess
    5. Capture output, check for completion signal
    6. Update state file
    7. Check for no-progress (exit after 3 iterations)
    8. Repeat until completion or max iterations (50)
```

**Completion Signals** (any one):
- `<status>TASK_COMPLETE</status>` in stdout
- `<promise>COMPLETE</promise>` in stdout
- `SYSTEM/state/complete.flag` file created

### Section 2.3: Orchestrator Responsibilities

- Manage watcher lifecycle (start/stop/restart)
- Claim tasks from PROCESSING/Pending/ (priority-based)
- Execute Ralph Loop for each task
- Process approved actions (execute MCP calls)
- Run scheduled jobs (CEO Briefing @ Mon 7 AM)
- Handle errors with circuit breakers
- Log all actions to audit trail

---

## ⚖️ ARTICLE III - KEY RULES

### Section 3.1: Autonomy Levels

| Level | Symbol | Description | Examples |
|-------|--------|-------------|----------|
| **Auto-Approve** | 🟢 | AI executes without human intervention | File organization, data entry (local), archiving |
| **Notify-Only** | 🟡 | AI executes but notifies human | Email replies to known contacts (<1000 chars) |
| **HITL Required** | 🔴 | Human approval mandatory before execution | All WhatsApp, payments, unknown senders, deletions |

### Section 3.2: HITL Thresholds

| Action Type | Autonomy Level | Conditions |
|-------------|----------------|------------|
| Email reply | 🟢 Auto | Known contact, <1000 chars, no links |
| Email reply | 🔴 HITL | Unknown sender, >1000 chars, contains links |
| WhatsApp reply | 🔴 HITL | ALWAYS (privacy policy) |
| Payment | 🔴 HITL | ALWAYS (all payments) |
| New payee | 🔴 HITL | ALWAYS (all new payees) |
| File organization | 🟢 Auto | Local files only |
| Data entry (local) | 🟢 Auto | Odoo, spreadsheets |
| Social media post | 🟡 Notify | Draft only, publishing requires HITL |
| Data deletion | 🔴 HITL | ALWAYS |
| Contract signing | 🔴 HITL | ALWAYS |

### Section 3.3: State Storage

| Tier | Storage Method | Rationale |
|------|----------------|-----------|
| **Bronze** | JSON files in vault | Simple, human-readable, easy debugging |
| **Silver** | JSON files in vault | Same as Bronze (no change) |
| **Gold** | SQLite + JSON audit logs | Concurrent access, better querying |
| **Platinum** | SQLite + Git sync | Cloud/local split, conflict resolution |

### Section 3.4: Approval Workflow

```
PROCESSING/Pending_Approval/APPROVAL_{id}.md
         │
         │ (human reviews)
         │
    ┌────┴────┐
    │         │
    ▼         ▼
Approved/   Rejected/
    │         │
    │         └───→ Archive as rejected
    │
    ▼
Execute via MCP
    │
    ▼
OUTPUT/Completed/
```

**File Format:** Markdown with frontmatter (YAML)
**Human Action:** Move file to Approved/ or Rejected/ folder
**Orchestrator:** Detects file move, executes or archives

### Section 3.5: Completion Signals

| Signal | Type | Detection |
|--------|------|-----------|
| `<status>TASK_COMPLETE</status>` | stdout | String match in Qwen output |
| `<promise>COMPLETE</promise>` | stdout | String match in Qwen output |
| `complete.flag` | file | File exists in SYSTEM/state/ |

### Section 3.6: Secret Management

```
SECURITY/.env  (chmod 600, gitignored)

# NEVER in vault, NEVER synced to cloud
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
BANK_API_KEY=...
ODOO_PASSWORD=...
```

**Rules:**
- Load via `python-dotenv`
- Never log secrets (redact in audit logs)
- Never commit to Git
- Never sync to cloud (Platinum: separate local secrets)

---

## 📊 ARTICLE IV - TIER REQUIREMENTS

### Section 4.0: Phase-Wise Development Strategy

**We build incrementally, phase by phase. Complete each phase before starting the next.**

| Phase | Focus | Timeline | Success Metric |
|-------|-------|----------|----------------|
| **Bronze** | Core loop working | Week 1 | Email detected → Qwen processes → HITL → Sent |
| **Silver** | Multi-channel | Week 2 | WhatsApp + LinkedIn working with scheduling |
| **Gold** | Full integration | Week 3-4 | Odoo + CEO Briefing + all social platforms |
| **Platinum** | Production ready | Week 5-6 | 24/7 cloud deployment with monitoring |

**Rules:**

1. ✅ **Complete each phase before starting next** - No skipping phases
2. ✅ **Each phase must be independently testable** - Working demo per phase
3. ✅ **Documentation updated per phase** - AGENTS.md, ARCHITECTURE.md current
4. ✅ **No phase skipped or partially implemented** - All requirements must be met

**Phase Governance:**
- Phase completion verified against requirement checklist
- Demo recorded for each phase milestone
- Retrospective conducted before starting next phase

### Section 4.1: Bronze Tier (MVP)

**Must Have:**
- ✅ Gmail Watcher (poll every 2 min)
- ✅ Ralph Wiggum Loop (external orchestrator)
- ✅ MCP Server Framework (`mcp_servers/base_mcp.py`)
- ✅ StateMCP (Bronze) - Read/write vault state
- ✅ EmailMCP (Bronze) - Send emails via Gmail API
- ✅ HITL approval workflow (file-based)
- ✅ Obsidian vault with root-level handbook
- ✅ State persistence (JSON files)
- ✅ Audit logging (JSONL)
- ✅ Rate limiting (10 emails/hour)

**Success Criteria:**
- New email → Watcher detects → Qwen drafts → HITL approval → EmailMCP sends
- Ralph Loop handles multi-step tasks
- All actions logged via MCP audit_log()
- Rate limiting enforced

### Section 4.2: Silver Tier

**Must Have (all Bronze +):**
- ✅ WhatsApp Watcher (Playwright, 30 sec poll)
- ✅ BrowserMCP (Silver) - Browser automation
- ✅ WhatsAppMCP (Silver) - WhatsApp Web automation (LOCAL ONLY, HITL always)
- ✅ Scheduled jobs (CEO Briefing @ Mon 7 AM)
- ✅ Circuit breakers (error recovery)
- ✅ Rate limiting per MCP (10 emails/hour, 60 browser actions/hour, 20 WhatsApp msgs/hour)

**Success Criteria:**
- WhatsApp message → WhatsAppMCP detects → ALWAYS requires approval
- BrowserMCP automates web interactions with HITL for login/payment pages
- CEO Briefing generates automatically
- System recovers from transient errors
- Rate limits enforced per MCP

### Section 4.3: Gold Tier

**Must Have (all Silver +):**
- ✅ Finance Watcher (bank CSV/API, daily sync)
- ✅ OdooMCP (Gold) - Invoice generation, accounting (ALWAYS HITL for financial postings)
- ✅ SocialMCP (Gold) - LinkedIn, Twitter/X, Instagram posting
- ✅ CEO Briefing Generator (comprehensive report)
- ✅ Hash chain audit logs (tamper-evident)
- ✅ SQLite migration (concurrent access)
- ✅ Rate limiting (50 Odoo calls/hour, 5 social posts/hour/platform)

**Success Criteria:**
- Bank transactions synced daily
- Invoices auto-generated from tasks
- Tamper-evident audit trail

### Section 4.4: Platinum Tier

**Must Have (all Gold +):**
- ✅ Cloud deployment (Oracle Cloud Free Tier)
- ✅ Cloud/Local split (cloud drafts, local approves)
- ✅ Git-based vault sync (secrets excluded)
- ✅ 24/7 operation with health monitoring
- ✅ Prometheus + Grafana dashboard
- ✅ Alerting (PagerDuty/Slack)
- ✅ Automated backups

**Success Criteria:**
- Cloud agent can draft, local must approve
- Vault syncs without conflicts
- Health dashboard shows system status
- Alerts on critical failures

---

## 📦 ARTICLE V - DELIVERABLES

### Section 5.1: Required Submissions

1. **Working Code (GitHub Repository)**
   - Complete source code
   - Requirements.txt / dependencies
   - Setup instructions (README.md)
   - Architecture documentation (ARCHITECTURE.md)

2. **Demo Video (5-10 minutes)**
   - Show end-to-end workflow
   - Demonstrate HITL approval
   - Show Ralph Loop in action
   - Explain architecture decisions

3. **Architecture Document**
   - This document (ARCHITECTURE.md)
   - Component diagrams
   - Data contracts
   - State machine

4. **Security Disclosure**
   - Threat model
   - Mitigation strategies
   - Secret management approach
   - HITL justification

### Section 5.2: Phase-Based Delivery

**Deliverables are phase-gated:**

| Phase | Deliverable | Deadline |
|-------|-------------|----------|
| **Bronze** | Minimum viable demo | Week 1 |
| **Silver** | Feature-complete demo | Week 2 |
| **Gold** | Full submission package | Week 3-4 |
| **Platinum** | Optional production deployment | Week 5-6 |

**Phase Delivery Rules:**
- Each phase demo must be recordable and functional
- Gold phase = minimum for hackathon submission
- Platinum = optional enhancement (bonus points)

### Section 5.3: Optional Enhancements

- Live demo (if possible)
- Performance benchmarks
- Comparison with human baseline
- User testimonials (if tested)

---

## 🏆 ARTICLE VI - JUDGING CRITERIA

### Section 6.1: Evaluation Matrix

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Functionality** | 30% | Does it work? End-to-end flow? Handles edge cases? |
| **Innovation** | 25% | Novel use of AI? Creative architecture? Unique features? |
| **Practicality** | 20% | Real-world usable? Cost-effective? Maintainable? |
| **Security** | 15% | Privacy preserved? HITL enforced? Secrets protected? |
| **Documentation** | 10% | Clear README? Architecture explained? Setup easy? |

### Section 6.2: Scoring Guidelines

**Functionality (30%):**
- 25-30: Full end-to-end flow, handles errors gracefully
- 15-24: Core features work, some edge cases fail
- 0-14: Incomplete, major features broken

**Innovation (25%):**
- 20-25: Novel architecture, creative AI use, unique features
- 10-19: Standard approach, some creative elements
- 0-9: Generic implementation, no innovation

**Practicality (20%):**
- 16-20: Production-ready, cost-effective, maintainable
- 8-15: Usable with modifications, moderate cost
- 0-7: Not practical, too expensive, hard to maintain

**Security (15%):**
- 12-15: Strong security, HITL enforced, secrets protected
- 6-11: Basic security, some gaps
- 0-5: Security vulnerabilities, secrets exposed

**Documentation (10%):**
- 8-10: Comprehensive, clear, easy setup
- 4-7: Adequate, some gaps
- 0-3: Poor documentation, hard to understand

---

## 🚫 ARTICLE VII - NON-NEGOTIABLES

### Section 7.1: Mandatory Requirements

These requirements **CANNOT** be compromised:

1. **✅ Qwen/Claude Code as Primary Engine**
   - AI reasoning must use Qwen CLI or Claude Code
   - No custom ML models as replacement
   - Ralph Loop pattern mandatory

2. **✅ Obsidian as Dashboard**
   - Vault structure as specified
   - Company_Handbook.md at root
   - Business_Goals.md at root

3. **✅ Qwen Code Skills**
   - Skills in `.qwen/skills/{skill}/SKILL.md` (project-level, git-shareable)
   - YAML frontmatter with name and description
   - Model-triggered based on keyword matching
   - Input/output schemas, decision rules, examples

4. **✅ Ralph Wiggum Loop Pattern**
   - External orchestrator (not built-in)
   - Iterative execution until completion
   - Completion signals as specified
   - No-progress detection (3 iterations)

4. **✅ File-Based HITL Workflow**
   - Approval via file move (Pending_Approval → Approved/Rejected)
   - No web UI required (Bronze/Silver)
   - Audit trail for all approvals

5. **✅ Qwen Code Skills Format**
   - Skills in `.qwen/skills/{skill}/SKILL.md` (project-level, git-shareable)
   - YAML frontmatter with `name` and `description` fields
   - Model-triggered based on description keyword matching
   - Input/output schemas specified
   - Decision rules and examples provided

### Section 7.2: Amendment Process

This Constitution can be amended with:
- 100% builder consensus
- Documented rationale
- Version bump
- Change log entry

---

## 📝 ARTICLE VIII - INTERPRETATION & ENFORCEMENT

### Section 8.1: Authority

- **Final Interpreter:** Lead architect
- **Dispute Resolution:** Team consensus
- **Emergency Powers:** Lead developer can override for security

### Section 8.2: Compliance

- All code must comply with this Constitution
- Code review checklist includes constitutional compliance
- Security audit verifies adherence

### Section 8.3: Effective Date

This Constitution is effective immediately upon adoption (2026-02-17).

---

## ✍️ SIGNATURES

**Adopted by:**

| Name | Role | Date |
|------|------|------|
| [Builder Name] | Lead Architect | 2026-02-17 |
| [Builder Name] | Lead Developer | 2026-02-17 |

---

## 📎 APPENDIX A - GLOSSARY

| Term | Definition |
|------|------------|
| **HITL** | Human-in-the-Loop: requires human approval before execution |
| **MCP** | Model Context Protocol: standardized interface for AI actions |
| **Ralph Loop** | Ralph Wiggum Loop: iterative AI execution pattern |
| **Vault** | Obsidian vault: file-based knowledge/state storage |
| **Watcher** | Python script monitoring external sources (Gmail, WhatsApp, etc.) |
| **Orchestrator** | Main event loop coordinating all components |
| **Circuit Breaker** | Error handling pattern: pause after repeated failures |
| **Dead Letter Queue** | PROCESSING/Failed/: failed tasks for manual review |

---

## 📎 APPENDIX B - REFERENCES

1. [Ralph Loop Pattern by Geoffrey Huntley](https://github.com/georgehuntley/ralph-wiggum-loop)
2. [Model Context Protocol Specification](https://modelcontextprotocol.io/)
3. [Obsidian Documentation](https://help.obsidian.md/)
4. [Google Gmail API](https://developers.google.com/gmail/api)
5. [Playwright Documentation](https://playwright.dev/)

---

**END OF CONSTITUTION**

*"Local-first, Privacy-first, Human-in-the-Loop, Always Transparent"*
