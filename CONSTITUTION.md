# 📜 PERSONAL AI EMPLOYEE - CONSTITUTION

**Version:** 2.0
**Adopted:** 2026-02-24
**Status:** Supreme Law of the AI Employee System

> **Note:** For complete technical specifications, see [SPECIFICATIONS.md](./SPECIFICATIONS.md)

---

## ✔ PREAMBLE

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

- API credentials stored in `.env` file only (never committed)
- OAuth tokens stored in `.system/` (never synced)
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

- Every action logged to Logs/YYYY-MM-DD.jsonl
- Task history persisted in .system/state/task_history.jsonl
- Audit trail includes: timestamp, actor, action, result
- Gold tier+: hash chain for tamper evidence

---

## ⚖️ ARTICLE II - KEY RULES

### Section 2.1: Autonomy Levels

| Level | Symbol | Description | Examples |
|-------|--------|-------------|----------|
| **Auto-Approve** | 🟢 | AI executes without human intervention | File organization, data entry (local), archiving |
| **Notify-Only** | 🟡 | AI executes but notifies human | Email replies to known contacts (<1000 chars) |
| **HITL Required** | 🔴 | Human approval mandatory before execution | All WhatsApp, payments, unknown senders, deletions |

### Section 2.2: HITL Thresholds

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

### Section 2.3: Approval Workflow

```
Pending_Approval/APPROVAL_{id}.md
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
Done/
```

**File Format:** Markdown with frontmatter (YAML)
**Human Action:** Move file to Approved/ or Rejected/ folder
**Orchestrator:** Detects file move, executes or archives

### Section 2.4: Secret Management

```
.env  (chmod 600, gitignored)

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

## 🚫 ARTICLE III - NON-NEGOTIABLES

### Section 3.1: Mandatory Requirements

These requirements **CANNOT** be compromised:

1. **✔ Qwen/Claude Code as Primary Engine**
   - AI reasoning must use Qwen CLI or Claude Code
   - No custom ML models as replacement
   - Ralph Loop pattern mandatory

2. **✔ Obsidian as Dashboard**
   - Vault structure as specified
   - Company_Handbook.md at root
   - Business_Goals.md at root

3. **✔ Qwen Code Skills**
   - Skills in `.qwen/skills/{skill}/SKILL.md` (project-level, git-shareable)
   - YAML frontmatter with name and description
   - Model-triggered based on keyword matching
   - Input/output schemas, decision rules, examples

4. **✔ Ralph Wiggum Loop Pattern**
   - External orchestrator (not built-in)
   - Iterative execution until completion
   - Completion signals as specified
   - No-progress detection (3 iterations)

5. **✔ File-Based HITL Workflow**
   - Approval via file move (Pending_Approval → Approved/Rejected)
   - No web UI required (Bronze/Silver)
   - Audit trail for all approvals

### Section 3.2: Amendment Process

This Constitution can be amended with:
- 100% builder consensus
- Documented rationale
- Version bump
- Change log entry

---

## ✔ ARTICLE IV - INTERPRETATION & ENFORCEMENT

### Section 4.1: Authority

- **Final Interpreter:** Lead architect
- **Dispute Resolution:** Team consensus
- **Emergency Powers:** Lead developer can override for security

### Section 4.2: Compliance

- All code must comply with this Constitution
- Code review checklist includes constitutional compliance
- Security audit verifies adherence

### Section 4.3: Effective Date

This Constitution is effective immediately upon adoption (2026-02-24).

---

## ✔ APPENDIX A - GLOSSARY

| Term | Definition |
|------|------------|
| **HITL** | Human-in-the-Loop: requires human approval before execution |
| **MCP** | Model Context Protocol: standardized interface for AI actions |
| **Ralph Loop** | Ralph Wiggum Loop: iterative AI execution pattern |
| **Vault** | Obsidian vault: file-based knowledge/state storage |
| **Watcher** | Python script monitoring external sources (Gmail, WhatsApp, etc.) |
| **Orchestrator** | Main event loop coordinating all components |
| **Circuit Breaker** | Error handling pattern: pause after repeated failures |
| **Dead Letter Queue** | Failed/: failed tasks for manual review |

---

## ✔ APPENDIX B - REFERENCES

- [SPECIFICATIONS.md](./SPECIFICATIONS.md) - Complete technical requirements
- [Ralph Loop Pattern](https://github.com/georgehuntley/ralph-wiggum-loop)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Obsidian Documentation](https://help.obsidian.md/)
- [Google Gmail API](https://developers.google.com/gmail/api)
- [Playwright Documentation](https://playwright.dev/)

---

**END OF CONSTITUTION**

*"Local-first, Privacy-first, Human-in-the-Loop, Always Transparent"*
