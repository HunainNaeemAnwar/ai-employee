# ✔ Personal AI Employee - Complete Specifications

**Version:** 2.0
**Last Updated:** 2026-02-24
**Status:** Ready for Implementation

---

## ✔ PROJECT OVERVIEW

### What We're Building

A **Digital FTE (Full-Time Equivalent)** - an AI agent that autonomously manages personal and business tasks 24/7:

- ✉️ **Email Management**: Gmail triage, auto-categorization, draft replies
- 💬 **WhatsApp Monitoring**: Keyword detection, reply drafting (HITL required)
- 🏦 **Finance Tracking**: Bank transaction sync, invoice generation via Odoo
- ✔ **Social Media**: LinkedIn, Twitter/X, Instagram posting
- ✔ **Weekly Audits**: CEO Briefing every Monday 7 AM

### Core Philosophy

| Principle | Description |
|-----------|-------------|
| **Local-First** | Data stays on your machine, not cloud (Bronze/Silver) |
| **Privacy-First** | Secrets never leave your device |
| **Human-in-the-Loop** | AI suggests, human approves critical actions |
| **Transparent** | All decisions logged, auditable |

### AI Engine

- **Primary:** Claude Code (or Qwen CLI via router)
- **Pattern:** Ralph Wiggum Loop (iterative execution until completion)
- **State:** JSON/Markdown files in Obsidian vault
- **Actions:** MCP servers (Email, Browser, WhatsApp, Odoo, Social)

---

## ✔ PROJECT TIER REQUIREMENTS

### Bronze Tier: Foundation (Minimum Viable Deliverable)

**Estimated Time:** 8-12 hours

**Requirements:**
- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md` at root
- [ ] One working Watcher script (Gmail OR file system monitoring)
- [ ] Claude Code successfully reading from and writing to the vault
- [ ] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [ ] All AI functionality implemented as [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

**Success Criteria:**
```
New email → Watcher detects → Claude drafts → Human approves → Email sent
```

---

### Silver Tier: Functional Assistant

**Estimated Time:** 20-30 hours

**Requirements (All Bronze +):**
- [ ] Two or more Watcher scripts (Gmail + WhatsApp + LinkedIn)
- [ ] Auto-post on LinkedIn about business to generate sales
- [ ] Claude reasoning loop that creates `Plan.md` files
- [ ] One working MCP server for external action (e.g., sending emails)
- [ ] Human-in-the-loop approval workflow for sensitive actions
- [ ] Basic scheduling via cron or Task Scheduler
- [ ] All AI functionality implemented as Agent Skills

**Success Criteria:**
```
WhatsApp message → Always requires approval
CEO Briefing generates automatically Monday 7 AM
```

---

### Gold Tier: Autonomous Employee

**Estimated Time:** 40+ hours

**Requirements (All Silver +):**
- [ ] Full cross-domain integration (Personal + Business)
- [ ] Create accounting system in Odoo Community (self-hosted, local)
- [ ] Integrate Odoo via MCP server using JSON-RPC APIs (Odoo 19+)
- [ ] Integrate Facebook and Instagram - post messages and generate summary
- [ ] Integrate Twitter (X) - post messages and generate summary
- [ ] Multiple MCP servers for different action types
- [ ] Weekly Business and Accounting Audit with CEO Briefing generation
- [ ] Error recovery and graceful degradation
- [ ] Comprehensive audit logging
- [ ] Ralph Wiggum loop for autonomous multi-step task completion
- [ ] Documentation of architecture and lessons learned
- [ ] All AI functionality implemented as Agent Skills

**Success Criteria:**
```
Bank transactions synced daily
Invoices auto-generated from completed tasks
Tamper-evident audit trail
```

---

### Platinum Tier: Always-On Cloud + Local Executive

**Estimated Time:** 60+ hours

**Requirements (All Gold +):**
- [ ] Run AI Employee on Cloud 24/7 (always-on watchers + orchestrator + health monitoring)
- [ ] Deploy Cloud VM (Oracle/AWS/etc.)
- [ ] **Work-Zone Specialization:**
  - **Cloud owns:** Email triage + draft replies + social post drafts/scheduling (draft-only; requires Local approval before send/post)
  - **Local owns:** approvals, WhatsApp session, payments/banking, final "send/post" actions
- [ ] **Delegation via Synced Vault:**
  - Agents communicate by writing files into: `/Needs_Action/<domain>/`, `/Plans/<domain>/`, `/Pending_Approval/<domain>/`
  - Prevent double-work using: `/In_Progress/<agent>/` claim-by-move rule, single-writer rule for `Dashboard.md`
  - Cloud writes updates to `/Updates/` (or `/Signals/`), Local merges into `Dashboard.md`
  - For Vault sync (Phase 1) use Git (recommended) or Syncthing
  - **Claim-by-move rule:** first agent to move item from `/Needs_Action` to `/In_Progress/<agent>/` owns it; other agents ignore
- [ ] **Security rule:** Vault sync includes only markdown/state. Secrets never sync (.env, tokens, WhatsApp sessions, banking creds)
- [ ] Deploy Odoo Community on Cloud VM (24/7) with HTTPS, backups, health monitoring
- [ ] Integrate Cloud Agent with Odoo via MCP for draft-only accounting actions
- [ ] Local approval required for posting invoices/payments
- [ ] Optional A2A Upgrade (Phase 2): Replace some file handoffs with direct A2A messages, keeping vault as audit record

**Platinum Demo (Minimum Passing Gate):**
```
Email arrives while Local is offline → Cloud drafts reply + writes approval file → 
when Local returns, user approves → Local executes send via MCP → logs → moves task to /Done
```

---

## ✔ FOLDER STRUCTURE

### Required Folder Names

| Folder | Purpose |
|--------|---------|
| `/Inbox` | New items land here (Watcher output) |
| `/Needs_Action` | Tasks waiting to be processed |
| `/Plans` | Generated execution plans (Plan.md files) |
| `/Done` | Finished tasks |
| `/Pending_Approval` | HITL queue (sensitive actions) |
| `/Approved` | Human-approved actions ready to execute |
| `/Rejected` | Human-rejected actions |
| `/Logs` | Audit logs |

### Complete Structure

```
AI_Employee_Vault/
├── ✔ Company_Handbook.md          # AI behavior rules (ROOT LEVEL)
├── ✔ Business_Goals.md            # KPIs, targets (ROOT LEVEL)
├── ✔ Dashboard.md                 # Real-time status (ROOT LEVEL)
│
├── 📥 Inbox/
│   ├── Gmail/                      # Gmail Watcher drops here
│   ├── WhatsApp/                   # WhatsApp Watcher drops here
│   ├── Banking/                    # Finance Watcher drops here
│   └── Files/                      # File system drops here
│
├── ✔ Needs_Action/
├── ✔ Plans/
├── ✔ Done/
│
├── ✔ Pending_Approval/            # HITL queue
├── ✔ Approved/                    # Human-approved
├── ✖ Rejected/                    # Human-rejected
│
├── 🧠 Knowledge/
│   ├── Contexts/                   # Client profiles, history
│   └── Procedures/                 # Reusable SOPs
│
├── 📰 Logs/
│   └── YYYY-MM-DD.jsonl            # Daily audit logs
│
└── 📰 Accounting/
    └── Current_Month.md            # Bank transactions
```

---

## ✔ SYSTEM ARCHITECTURE

### Architecture Layers

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
│  - WhatsApp Watcher (30 sec poll, Playwright)               │
│  - File Watcher (realtime via watchdog)                     │
│  - Finance Watcher (daily 9 AM)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              KNOWLEDGE LAYER (Vault - Obsidian)             │
│  - Company_Handbook.md (root)                               │
│  - Business_Goals.md (root)                                 │
│  - Dashboard.md (root)                                      │
│  - Inbox/, Needs_Action/, Plans/, Done/                     │
│  - Pending_Approval/, Approved/, Rejected/                  │
│  - Logs/ (audit trail)                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BRAIN LAYER (Claude Code - Reasoning)          │
│  - Spawned as subprocess                                    │
│  - File-based prompts (--file prompt.md)                    │
│  - 5-minute timeout per iteration                           │
│  - Ralph Loop: iterate until completion (max 50)            │
│  - Agent Skills auto-loaded from .claude/skills/            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              ACTION LAYER (MCP Servers - Python/Node)       │
│  - Email MCP (Gmail API)                                    │
│  - Browser MCP (Playwright)                                 │
│  - WhatsApp MCP (Playwright + WhatsApp Web)                 │
│  - Odoo MCP (JSON-RPC) - Gold tier                          │
│  - Social MCP (LinkedIn, Twitter, Instagram)                │
│  - Sync MCP (Git-based vault sync) - Platinum               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              OUTPUT LAYER (Completed Tasks)                 │
│  - Done/                                                    │
│  - Reports/ (CEO Briefings)                                 │
│  - Archive/ (monthly)                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## ✔ RALPH WIGGUM LOOP PATTERN

### Overview

The **Ralph Wiggum Loop** is an autonomous AI execution pattern that uses a **Stop Hook** to intercept the AI's exit and re-inject the prompt until the task is complete.

**Core Pattern (Bash):**
```bash
while :; do cat PROMPT.md | qwen; done
```

**Key Characteristics:**
- Fresh context per iteration (new subprocess each time)
- State persists via filesystem and git history
- Stop hook intercepts exit and re-injects prompt
- Completion detection via configurable signals

### How It Works

```
1. User invokes Ralph Loop with a prompt
2. Qwen CLI works on the task (fresh context)
3. Qwen tries to exit
4. Stop Hook intercepts exit:
   - Checks output for completion signal
   - If found → Allow exit (complete)
   - If NOT found → Continue loop, re-inject prompt
5. Qwen sees previous work via:
   - File system changes
   - Git history
   - State files
6. Loop continues until completion or max iterations
```

### Completion Signals

| Signal | Type | Detection |
|--------|------|-----------|
| `<promise>COMPLETE</promise>` | stdout | String match in output |
| `<promise>TASK_COMPLETE</promise>` | stdout | String match in output |
| `<status>TASK_COMPLETE</status>` | stdout | String match in output |
| `DONE` | stdout | String match in output |
| Custom promise | stdout | User-defined string |

### Usage

**Option 1: Bash Script (Recommended)**
```bash
# Basic usage
./scripts/ralph-loop.sh "Process all files in Needs_Action"

# With completion promise
./scripts/ralph-loop.sh "Migrate tests to pytest" \
  --completion-promise "All tests migrated" \
  --max-iterations 10

# With custom vault
./scripts/ralph-loop.sh "Add type hints" \
  --vault ~/AI_Employee_Vault \
  --max-iterations 20

# Using environment variables
MAX_ITERATIONS=20 ./scripts/ralph-loop.sh "Add docs"
```

**Option 2: Direct Bash Loop (Original Pattern)**
```bash
# Write prompt to file
echo "Process all pending tasks" > PROMPT.md

# Run the original Ralph Wiggum pattern
while :; do cat PROMPT.md | qwen -i -o text; done
```

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max-iterations` | 50 | Maximum loop iterations |
| `--completion-promise` | Standard signals | Custom completion string |
| `--vault` | Current dir | Path to Obsidian vault |
| `--timeout` | 300s | Timeout per iteration |

**Environment Variables:**
- `MAX_ITERATIONS` - Override max iterations
- `COMPLETION_SIGNAL` - Custom completion signal
- `LOG_DIR` - Directory for iteration logs (default: `.ralph-logs`)

### Safety Mechanisms

| Mechanism | Purpose |
|-----------|---------|
| Max iterations | Prevents infinite loops |
| No-progress detection | Exits after 3 iterations with no changes |
| Timeout per iteration | Prevents hanging on slow operations |
| Logging | All iterations logged to `.ralph-logs/` |
| Ctrl+C trap | Graceful interruption |

### When to Use

| ✔ Use For | ✖ Avoid For |
|------------|--------------|
| Large refactors | Ambiguous requirements |
| Batch operations (email triage, docs) | Architectural decisions |
| Test coverage | Security-sensitive code |
| Greenfield scaffolding | Exploration/learning |

**Key requirement:** You must be able to define "done" precisely.

### File Structure

| File | Purpose |
|------|---------|
| `PROMPT.md` | Task specification fed to each iteration |
| `progress.txt` | Tracks completed iterations |
| `.ralph-logs/iteration-N.txt` | Output logs for each iteration |
| `.system/state/current_task.json` | State tracking for progress detection |

---

##  AGENT SKILLS FRAMEWORK

### Overview

All AI functionality must be implemented as **Agent Skills** - reusable, modular capabilities that Claude Code can invoke.

### Skill Structure

```
.qwen/skills/
└── {skill-name}/
    └── SKILL.md
```

### SKILL.md Format

```markdown
---
name: skill-name
description: What this skill does
---

## Input Schema
{
  "type": "object",
  "properties": {
    "field": {"type": "string"}
  }
}

## Output Schema
{
  "type": "object",
  "properties": {
    "result": {"type": "string"}
  }
}

## Decision Rules
- When to use this skill
- Conditions for execution

## Examples
- Example 1
- Example 2
```

### Required Skills by Tier

| Tier | Skills |
|------|--------|
| **Bronze** | email-triage, email-reply-draft, client-lookup |
| **Silver** | whatsapp-monitor, linkedin-post, plan-creation |
| **Gold** | invoice-generation, social-post, ceo-briefing |
| **Platinum** | vault-sync, cloud-delegate |

---

## 📦 MCP SERVER SPECIFICATIONS

### Overview

**MCP (Model Context Protocol) Servers** are Python/Node.js modules that provide validated action execution.

### Base Pattern

```python
from base_mcp import BaseMCP, ValidationResult, ExecutionResult

class MyMCP(BaseMCP):
    def validate(self, action: dict) -> ValidationResult:
        # Check rate limits, HITL approval, parameters
        return ValidationResult(success=True)

    def execute(self, action: dict) -> ExecutionResult:
        # Perform the action
        return ExecutionResult(success=True, output="result")

    def audit_log(self, action: dict, result: ExecutionResult) -> dict:
        # Generate audit log entry
        return {...}
```

### MCP Servers by Tier

| Tier | MCP | Purpose | Rate Limit |
|------|-----|---------|------------|
| **Bronze** | StateMCP | Read/write vault state | N/A |
| **Bronze** | EmailMCP | Send emails via Gmail API | 10/hour |
| **Silver** | BrowserMCP | Browser automation (Playwright) | 60/hour |
| **Silver** | WhatsAppMCP | WhatsApp Web automation | 20/hour |
| **Gold** | OdooMCP | Invoice generation, accounting | 50/hour |
| **Gold** | SocialMCP | LinkedIn, Twitter, Instagram | 5/hour/platform |
| **Platinum** | SyncMCP | Cloud/local vault sync | N/A |

---

## 👁️ WATCHER SPECIFICATIONS

### Base Pattern

```python
from base_watcher import BaseWatcher

class MyWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        '''Main watch loop'''
        while True:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            time.sleep(self.check_interval)
```

### Watchers by Tier

| Tier | Watcher | Poll Interval | Purpose |
|------|---------|---------------|---------|
| **Bronze** | Gmail Watcher | 2 min | Monitor Gmail for unread/important |
| **Silver** | WhatsApp Watcher | 30 sec | Monitor WhatsApp for keywords |
| **Silver** | LinkedIn Watcher | 5 min | Monitor LinkedIn messages |
| **Gold** | Finance Watcher | Daily 9 AM | Sync bank transactions |
| **Gold** | Social Watcher | 10 min | Monitor social mentions |

---

## ✔ SECURITY REQUIREMENTS

### 6.1 Credential Management

**NEVER:**
- Store credentials in plain text
- Commit `.env` files to Git
- Log secret values
- Sync secrets to cloud

**ALWAYS:**
- Use environment variables: `export GMAIL_API_KEY="your-key"`
- Store in `.env` file (add to `.gitignore` immediately)
- Use secrets manager for banking (macOS Keychain, Windows Credential Manager, 1Password CLI)
- Rotate credentials monthly

**Example `.env`:**
```bash
# .env - NEVER commit this file
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
BANK_API_TOKEN=your_token
WHATSAPP_SESSION_PATH=/secure/path/session
```

---

### 6.2 Sandboxing & Isolation

**Development Mode:**
- Create `DEV_MODE` flag that prevents real external actions
- All action scripts support `--dry-run` flag
- Use test/sandbox accounts during development

**Example:**
```python
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'

def send_email(to, subject, body):
    if DRY_RUN:
        logger.info(f'[DRY RUN] Would send email to {to}')
        return
    # Actual send logic
```

---

### 6.3 Audit Logging

**Required Log Format:**
```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "action_type": "email_send",
  "actor": "claude_code",
  "target": "client@example.com",
  "parameters": {"subject": "Invoice #123"},
  "approval_status": "approved",
  "approved_by": "human",
  "result": "success"
}
```

**Requirements:**
- Store logs in `/Vault/Logs/YYYY-MM-DD.json`
- Retain minimum 90 days
- Log every action (success or failure)

---

### 6.4 Permission Boundaries

| Action Category | Auto-Approve Threshold | Always Require Approval |
|-----------------|------------------------|-------------------------|
| Email replies | To known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move outside vault |
| WhatsApp messages | NEVER | ALWAYS (privacy policy) |
| Invoice generation | Draft only | Sending to client |

---

## ✔ HUMAN-IN-THE-LOOP (HITL) WORKFLOW

### Approval Pattern

```
Needs_Action → Claude drafts → Pending_Approval → Human reviews → 
  ├─→ Approved → Execute via MCP → Done
  └─→ Rejected → Archive
```

### Approval File Format

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
reason: Invoice #1234 payment
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
---

## Payment Details
- Amount: $500.00
- To: Client A (Bank: XXXX1234)
- Reference: Invoice #1234

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

### Human Action

```
Move to: /Approved/  → Execute action
Move to: /Rejected/  → Archive as rejected
```

---

## ✔ BUSINESS HANDOVER: CEO BRIEFING

### Trigger

Scheduled task runs every Monday 7 AM

### Process

1. Read `Business_Goals.md`
2. Check `Done/` folder for completed tasks
3. Check bank transactions
4. Generate briefing

### CEO Briefing Template

```markdown
---
generated: 2026-01-06T07:00:00Z
period: 2025-12-30 to 2026-01-05
---

# Monday Morning CEO Briefing

## Executive Summary
Strong week with revenue ahead of target. One bottleneck identified.

## Revenue
- **This Week**: $2,450
- **MTD**: $4,500 (45% of $10,000 target)
- **Trend**: On track

## Completed Tasks
- [x] Client A invoice sent and paid
- [x] Project Alpha milestone 2 delivered
- [x] Weekly social media posts scheduled

## Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| Client B proposal | 2 days | 5 days | +3 days |

## Proactive Suggestions

### Cost Optimization
- **Notion**: No team activity in 45 days. Cost: $15/month.
  - [ACTION] Cancel subscription? Move to /Pending_Approval

### Upcoming Deadlines
- Project Alpha final delivery: Jan 15 (8 days)
- Quarterly tax prep: Jan 31 (25 days)

---
*Generated by AI Employee v0.1*
```

---

## ⚠️ ERROR HANDLING & RECOVERY

### Error Categories

| Category | Examples | Recovery Strategy |
|----------|----------|-------------------|
| Transient | Network timeout, API rate limit | Exponential backoff retry |
| Authentication | Expired token, revoked access | Alert human, pause operations |
| Logic | Claude misinterprets message | Human review queue |
| Data | Corrupted file, missing field | Quarantine + alert |
| System | Orchestrator crash, disk full | Watchdog + auto-restart |

### Retry Logic

```python
def with_retry(max_attempts=3, base_delay=1, max_delay=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except TransientError as e:
                    if attempt == max_attempts - 1:
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f'Attempt {attempt+1} failed, retrying in {delay}s')
                    time.sleep(delay)
        return wrapper
    return decorator
```

### Graceful Degradation

- **Gmail API down:** Queue outgoing emails locally, process when restored
- **Banking API timeout:** Never retry payments automatically, always require fresh approval
- **Claude Code unavailable:** Watchers continue collecting, queue grows for later processing
- **Obsidian vault locked:** Write to temporary folder, sync when available

### Watchdog Process

```python
# watchdog.py - Monitor and restart critical processes
PROCESSES = {
    'orchestrator': 'python orchestrator.py',
    'gmail_watcher': 'python gmail_watcher.py',
    'file_watcher': 'python filesystem_watcher.py'
}

def check_and_restart():
    for name, cmd in PROCESSES.items():
        if not is_process_running(pid_file):
            logger.warning(f'{name} not running, restarting...')
            proc = subprocess.Popen(cmd.split())
            pid_file.write_text(str(proc.pid))
            notify_human(f'{name} was restarted')

while True:
    check_and_restart()
    time.sleep(60)
```

---

## ✔ TECH STACK

### Required Software

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Latest | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts & orchestration |
| Node.js | v24+ LTS | MCP servers & automation |
| GitHub Desktop | Latest | Version control |

### Hardware Requirements

- **Minimum:** 8GB RAM, 4-core CPU, 20GB free disk
- **Recommended:** 16GB RAM, 8-core CPU, SSD
- **For 24/7:** Dedicated mini-PC or cloud VM (Oracle/AWS)

### Python Dependencies

```toml
[dependencies]
google-api-python-client = ">=2.0.0"
google-auth-httplib2 = ">=0.1.0"
google-auth-oauthlib = ">=1.0.0"
python-dotenv = ">=1.0.0"
pyyaml = ">=6.0"
playwright = ">=1.40.0"  # Silver tier
watchdog = ">=3.0.0"
requests = ">=2.31.0"
```

---

## ✔ DEVELOPMENT COMMANDS

### Running the System

```bash
# Start orchestrator (main loop - watches for emails, runs Ralph Loop automatically)
python main.py start

# Run Ralph Loop manually on next pending task
python scripts/ralph_loop.py --vault ~/AI_Employee_Vault

# Run Ralph Loop on specific task by ID
python scripts/ralph_loop.py --vault ~/AI_Employee_Vault --task <task_id>

# Run Ralph Loop on first task in folder
python scripts/ralph_loop.py --vault ~/AI_Employee_Vault --folder Needs_Action

# Test individual watcher
python watchers/gmail_watcher.py --vault ~/AI_Employee_Vault --test
```

### Ralph Loop Usage (For AI Agents)

The Ralph Loop is implemented in `agents/ralph.py` and can be used two ways:

**1. Command Line (Recommended):**
```bash
# Process next pending task
python scripts/ralph_loop.py --vault ~/AI_Employee_Vault

# Process specific task
python scripts/ralph_loop.py --vault ~/AI_Employee_Vault --task email_12345

# Process first task in folder
python scripts/ralph_loop.py --vault ~/AI_Employee_Vault --folder Needs_Action
```

**2. Python Import (For Code Integration):**
```python
from agents.ralph import RalphLoop

# Initialize
ralph = RalphLoop(vault_path="/path/to/vault")

# Run on a task
result = ralph.run(task)

# Check result
if result.success:
    print(f"Completed in {result.iterations} iterations")
else:
    print(f"Failed: {result.error}")
```

### Process Management (PM2)

```bash
# Install PM2
npm install -g pm2

# Start watchers with auto-restart
pm2 start gmail_watcher.py --interpreter python3
pm2 start whatsapp_watcher.py --interpreter python3
pm2 start orchestrator.py --interpreter python3

# Save process list for reboot
pm2 save
pm2 startup
```

### Audit & Logs

```bash
# View today's audit log
cat Logs/$(date +%Y-%m-%d).jsonl

# View error log
tail -50 Logs/error.log

# View task history
cat Logs/task_history.jsonl | jq .
```

---

## ✔ TESTING CHECKLIST

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_config.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Integration Tests

```bash
# Test Gmail → Ralph Loop → Email send
python scripts/test_end_to_end.py

# Test approval workflow
python scripts/test_approval_workflow.py

# Test CEO Briefing generation
python scripts/test_ceo_briefing.py
```

### Manual Testing

- [ ] Send test email to Gmail account
- [ ] Verify Gmail Watcher detects it
- [ ] Verify Ralph Loop creates draft
- [ ] Verify approval file created
- [ ] Move approval to Approved/
- [ ] Verify email sent
- [ ] Verify email marked as read
- [ ] Verify audit log updated

---

## ✔ PROJECT DELIVERABLES

### GitHub Repository

- [ ] Public repository
- [ ] `README.md` with setup instructions
- [ ] `SPECIFICATIONS.md` with system design
- [ ] `LICENSE` file (MIT recommended)
- [ ] `.gitignore` (never commit secrets!)

### Documentation

- [ ] README.md includes:
  - Project overview
  - Setup instructions
  - Architecture diagram
  - Usage examples
  - Tier declaration

- [ ] Security disclosure:
  - How credentials are handled
  - HITL thresholds implemented
  - Rate limiting implemented

### Demo Video (5-10 minutes)

**Script Outline:**

1. **Introduction (1 min)**
   - Project name and tier
   - Problem being solved
   - Key features

2. **Architecture Overview (2 min)**
   - Show folder structure
   - Explain Watchers → Ralph Loop → MCP flow
   - Show HITL workflow

3. **Live Demo (4 min)**
   - Send test email
   - Show Gmail Watcher detection
   - Show Ralph Loop processing
   - Show approval creation
   - Approve and send email
   - Show audit log

4. **Conclusion (1 min)**
   - Lessons learned
   - Future enhancements
   - Thank you

---

## ✔ EVALUATION CRITERIA

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Functionality** | 30% | Does it work? End-to-end flow? Handles edge cases? |
| **Innovation** | 25% | Novel use of AI? Creative architecture? Unique features? |
| **Practicality** | 20% | Real-world usable? Cost-effective? Maintainable? |
| **Security** | 15% | Privacy preserved? HITL enforced? Secrets protected? |
| **Documentation** | 10% | Clear README? Architecture explained? Setup easy? |

### Scoring Guidelines

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

## ✔ GETTING HELP

### Wednesday Research Meetings

- **When:** Every Wednesday at 10:00 PM PKT
- **Where:** [Zoom Link](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **Meeting ID:** 871 8870 7642
- **Passcode:** 744832

### Learning Resources

**Prerequisites:**
- [Claude Code Fundamentals](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
- [Obsidian Help](https://help.obsidian.md/Getting+started)
- [MCP Introduction](https://modelcontextprotocol.io/introduction)
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

**Core Learning:**
- [Claude + Obsidian Integration](https://www.youtube.com/watch?v=sCIS05Qt79Y)
- [Building MCP Servers](https://modelcontextprotocol.io/quickstart)
- [Gmail API Setup](https://developers.google.com/gmail/api/quickstart)
- [Playwright Automation](https://playwright.dev/python/docs/intro)

**Deep Dives:**
- [MCP Server Reference](https://github.com/anthropics/mcp-servers)
- [Ralph Wiggum Loop](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [Odoo JSON-RPC API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)

---

## ❓ TROUBLESHOOTING FAQ

### Setup Issues

**Q: Claude Code says "command not found"**

A: Ensure Claude Code is installed globally: `npm install -g @anthropic/claude-code`, then restart terminal.

**Q: Obsidian vault isn't being read by Claude**

A: Check that you're running Claude Code from the vault directory, or using the `--cwd` flag. Verify file permissions.

**Q: Gmail API returns 403 Forbidden**

A: Your OAuth consent screen may need verification, or you haven't enabled Gmail API in Google Cloud Console.

### Runtime Issues

**Q: Watcher scripts stop running overnight**

A: Use PM2 or supervisord to keep them alive. Implement Watchdog pattern from Section 7.

**Q: Claude is making incorrect decisions**

A: Review `Company_Handbook.md` rules. Add more specific examples. Lower autonomy thresholds.

**Q: MCP server won't connect**

A: Check server process is running. Verify path in mcp.json is absolute. Check Claude Code logs.

### Security Concerns

**Q: How do I know my credentials are safe?**

A: Never commit `.env` files. Use environment variables. Rotate credentials. Implement audit logging.

**Q: What if Claude tries to pay the wrong person?**

A: That's why HITL is critical for payments. Any payment creates approval file first. Never auto-approve new recipients.

---

## ✔ APPENDIX A - EXAMPLE END-TO-END FLOW

### Scenario: Client Requests Invoice via WhatsApp

**Step 1: Detection (WhatsApp Watcher)**
```
Detected: "Hey, can you send me the invoice for January?"
Watcher creates: /Vault/Needs_Action/WHATSAPP_client_a_2026-01-07.md
```

**Step 2: Reasoning (Claude Code)**
```
Claude reads file and creates: /Vault/Plans/PLAN_invoice_client_a.md

## Objective
Generate and send January invoice to Client A

## Steps
- [x] Identify client: Client A (client_a@email.com)
- [x] Calculate amount: $1,500 (from /Accounting/Rates.md)
- [ ] Generate invoice PDF
- [ ] Send via email (REQUIRES APPROVAL)
- [ ] Log transaction
```

**Step 3: Approval (HITL)**
```
Claude creates: /Vault/Pending_Approval/EMAIL_invoice_client_a.md

Human reviews and moves to /Approved/
```

**Step 4: Action (Email MCP)**
```python
await email_mcp.send_email({
  to: 'client_a@email.com',
  subject: 'January 2026 Invoice - $1,500',
  body: 'Please find attached your invoice.',
  attachment: '/Vault/Invoices/2026-01_Client_A.pdf'
})
```

**Step 5: Completion**
```
Dashboard.md updated:
## Recent Activity
- [2026-01-07 10:45] Invoice sent to Client A ($1,500)

Files moved to Done/
Audit log updated
```

---

## ✔ APPENDIX B - ETHICS & RESPONSIBLE AUTOMATION

### When AI Should NOT Act Autonomously

- **Emotional contexts:** Condolence messages, conflict resolution
- **Legal matters:** Contract signing, legal advice, regulatory filings
- **Medical decisions:** Health-related actions
- **Financial edge cases:** Unusual transactions, new recipients, large amounts
- **Irreversible actions:** Anything that cannot be easily undone

### Transparency Principles

- Disclose AI involvement when sending emails
- Maintain audit trails for all actions
- Allow opt-out for contacts requesting human-only communication
- Schedule weekly reviews of AI decisions

### Oversight Schedule

1. **Daily:** 2-minute dashboard check
2. **Weekly:** 15-minute action log review
3. **Monthly:** 1-hour comprehensive audit
4. **Quarterly:** Full security and access review

### The Human Remains Accountable

**You are responsible for your AI Employee's actions.** Regular oversight is essential.

---

**"Local-first, Privacy-first, Human-in-the-Loop, Always Transparent"**
