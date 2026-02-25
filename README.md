#  Personal AI Employee

**A Digital FTE (Full-Time Equivalent)** - An AI agent that autonomously manages personal and business tasks 24/7.

---

## ✔ What We're Building

A **Digital FTE** that autonomously manages:

- ✉️ **Email Management**: Gmail triage, auto-categorization, draft replies
- 💬 **WhatsApp Monitoring**: Keyword detection, reply drafting (HITL required)
- 🏦 **Finance Tracking**: Bank transaction sync, invoice generation via Odoo
- ✔ **Social Media**: LinkedIn, Twitter/X, Instagram posting
- ✔ **Weekly Audits**: CEO Briefing every Monday 7 AM

---

## 🏛️ Core Philosophy

| Principle | Description |
|-----------|-------------|
| **Local-First** | Data stays on your machine, not cloud |
| **Privacy-First** | Secrets never leave your device |
| **Human-in-the-Loop** | AI suggests, human approves critical actions |
| **Transparent** | All decisions logged, auditable |

---

## ✔ Quick Start

### Prerequisites

- Python 3.13+
- Node.js v24+ LTS
- Qwen CLI (or Claude Code)
- Obsidian v1.10.6+

### Installation

```bash
# Navigate to project directory
cd personal_assistant

# Activate virtual environment
source .venv/bin/activate

# Verify installation
python main.py status
```

### Start the System

```bash
# Start the orchestrator (main loop)
python main.py start
```

### Obsidian Vault Setup

```bash
# Vault location
cd AI_Employee_Vault

# Open in Obsidian:
# File → Open Vault → Select AI_Employee_Vault folder

# Folder structure (Hackathon Spec):
# - Inbox/           - New items from watchers
# - Needs_Action/    - Tasks waiting to be processed
# - Plans/           - Execution plans
# - Done/            - Completed tasks
# - Pending_Approval/- Awaiting human approval
# - Approved/        - Ready to execute
# - Rejected/        - Discarded tasks
# - Logs/            - Audit logs
```

### Gmail Authentication (Required for Email)

```bash
# Step 1: Get Gmail API credentials
# 1. Go to: https://console.cloud.google.com/
# 2. Create new project or select existing
# 3. Enable Gmail API
# 4. Create OAuth 2.0 credentials
# 5. Download credentials.json

# Step 2: Save credentials
cp credentials.json AI_Employee_Vault/.system/

# Step 3: Authenticate
python scripts/gmail_auth.py

# Step 4: Test authentication
python scripts/gmail_auth.py --test
```

---

## ✔ Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Vault path (optional, defaults to ./AI_Employee_Vault)
VAULT_PATH=/path/to/your/AI_Employee_Vault

# Gmail polling interval in seconds (default: 120)
GMAIL_POLL_INTERVAL=120

# Ralph Loop settings
MAX_ITERATIONS=10
ITERATION_TIMEOUT=120
NO_PROGRESS_THRESHOLD=2

# Email rate limiting
MAX_EMAILS_PER_HOUR=10
```

### Vault Path

By default, the vault is located at `./AI_Employee_Vault` (relative to project root).

To use a custom vault location:

```bash
# Option 1: Environment variable
export VAULT_PATH=/path/to/your/vault
python main.py start

# Option 2: .env file
echo "VAULT_PATH=/path/to/your/vault" >> .env
```

---

## ✔ Architecture Overview

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
│  - File Watcher (realtime)                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              KNOWLEDGE LAYER (Vault - Obsidian)             │
│  - Company_Handbook.md, Business_Goals.md, Dashboard.md     │
│  - Inbox/, Needs_Action/, Plans/, Done/                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BRAIN LAYER (Qwen CLI)                         │
│  - Ralph Wiggum Loop: iterate until completion              │
│  - Agent Skills auto-loaded                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              ACTION LAYER (MCP Servers - Python)            │
│  - Email MCP, Browser MCP, WhatsApp MCP, Odoo MCP, etc.     │
└─────────────────────────────────────────────────────────────┘
```

---

## ✔ Project Tiers

| Tier | Focus | Features |
|------|-------|----------|
| **Bronze** | Foundation | Gmail Watcher, Email MCP, HITL workflow |
| **Silver** | Multi-channel | WhatsApp, LinkedIn, scheduling |
| **Gold** | Full integration | Odoo, Social Media, CEO Briefing |
| **Platinum** | Production | Cloud deployment, 24/7 operation |

---

## ✔ Testing

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

### Manual Testing Checklist

- [ ] Send test email to Gmail account
- [ ] Verify Gmail Watcher detects it
- [ ] Verify Ralph Loop creates draft
- [ ] Verify approval file created
- [ ] Move approval to Approved/
- [ ] Verify email sent
- [ ] Verify email marked as read
- [ ] Verify audit log updated

---

## ✔ Folder Structure

```
personal_assistant/
├── SPECIFICATIONS.md          # Complete requirements
├── CONSTITUTION.md            # Governing principles
├── AGENTS.md                  # AI agent guide
├── README.md                  # This file - overview & quick start
├── main.py                    # Entry point
├── agents/                    # Ralph Loop, skills
├── mcp_servers/               # MCP implementations
├── watchers/                  # Gmail, WhatsApp, File watchers
├── core/                      # State, task management
├── cli/                       # CLI commands
├── config/                    # Settings, paths
├── utils/                     # Utilities
├── tests/                     # Test suite
└── AI_Employee_Vault/         # Obsidian vault
    ├── Company_Handbook.md
    ├── Business_Goals.md
    ├── Dashboard.md
    ├── Inbox/                 # New items (Gmail/, WhatsApp/, etc.)
    ├── Needs_Action/          # Tasks waiting to be processed
    ├── Plans/                 # Execution plans
    ├── Done/                  # Completed tasks
    ├── Pending_Approval/      # Awaiting approval
    ├── Approved/              # Ready to execute
    ├── Rejected/              # Discarded
    ├── Logs/                  # Audit logs
    ├── Knowledge/             # Reference info
    └── Accounting/            # Bank transactions
```

---

## ✔ Tech Stack

- **Language:** Python 3.13+
- **AI Engine:** Qwen CLI (or Claude Code)
- **Dashboard:** Obsidian Vault
- **Email:** Gmail API
- **Browser Automation:** Playwright
- **Accounting:** Odoo (JSON-RPC)
- **Package Manager:** UV

---

## ✔ Security

- Credentials stored in `.env` (never committed)
- All actions logged to `Logs/`
- HITL required for sensitive actions (payments, WhatsApp, unknown senders)
- Rate limiting per MCP server

---

## ❓ Troubleshooting

### Setup Issues

**Q: Qwen CLI says "command not found"**

A: Install Qwen CLI: `npm install -g @anthropic/claude-code`, then restart terminal.

**Q: Obsidian vault isn't being read**

A: Check that you're running from the vault directory, or using `--cwd` flag. Verify file permissions.

**Q: Gmail API returns 403 Forbidden**

A: Your OAuth consent screen may need verification, or you haven't enabled Gmail API in Google Cloud Console.

### Runtime Issues

**Q: Watcher scripts stop running overnight**

A: Use PM2 to keep them alive:
```bash
npm install -g pm2
pm2 start gmail_watcher.py --interpreter python3
pm2 save
pm2 startup
```

**Q: AI is making incorrect decisions**

A: Review `Company_Handbook.md` rules. Add more specific examples. Lower autonomy thresholds.

**Q: MCP server won't connect**

A: Check server process is running. Verify path in mcp.json is absolute. Check logs.

### Security Concerns

**Q: How do I know my credentials are safe?**

A: Never commit `.env` files. Use environment variables. Rotate credentials. Implement audit logging.

**Q: What if AI tries to pay the wrong person?**

A: That's why HITL is critical for payments. Any payment creates approval file first. Never auto-approve new recipients.

---

## ✔ Getting Help

### Wednesday Research Meetings

- **When:** Every Wednesday at 10:00 PM PKT
- **Where:** [Zoom Link](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **Meeting ID:** 871 8870 7642
- **Passcode:** 744832

### Learning Resources

- [Qwen/Claude Code Fundamentals](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
- [Obsidian Help](https://help.obsidian.md/Getting+started)
- [MCP Introduction](https://modelcontextprotocol.io/introduction)
- [Ralph Loop Pattern](https://github.com/georgehuntley/ralph-wiggum-loop)

---

## ✔ License

MIT License - see LICENSE file for details.

---

*"Local-first, Privacy-first, Human-in-the-Loop, Always Transparent"*
