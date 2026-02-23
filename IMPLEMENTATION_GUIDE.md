# 🚀 PERSONAL AI EMPLOYEE - IMPLEMENTATION GUIDE

**Version:** 1.0  
**Last Updated:** 2026-02-23  
**Status:** Ready for Hackathon Implementation

---

## 📋 TABLE OF CONTENTS

1. [Getting Started](#getting-started)
2. [Hackathon Tier Roadmap](#hackathon-tier-roadmap)
3. [Bronze Tier Implementation](#bronze-tier-implementation)
4. [Silver Tier Implementation](#silver-tier-implementation)
5. [Gold Tier Implementation](#gold-tier-implementation)
6. [Platinum Tier Implementation](#platinum-tier-implementation)
7. [Testing Checklist](#testing-checklist)
8. [Submission Requirements](#submission-requirements)
9. [Demo Video Script](#demo-video-script)

---

## 🎯 GETTING STARTED

### Prerequisites Checklist

- [ ] Python 3.13+ installed
- [ ] Node.js v24+ LTS installed
- [ ] Claude Code subscription active
- [ ] Obsidian v1.10.6+ installed
- [ ] GitHub Desktop installed
- [ ] UV Python package manager installed

### Setup Commands

```bash
# Clone repository
git clone <your-repo-url>
cd personal_assistant

# Create virtual environment with UV
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Verify installation
python main.py status
```

### Obsidian Vault Setup

```bash
# Vault already created at:
AI_Employee_Vault/

# Open in Obsidian:
# File → Open Vault → Select AI_Employee_Vault folder
```

---

## 🏆 HACKATHON TIER ROADMAP

### Choose Your Target Tier

| Tier | Time Required | Complexity | Recommended For |
|------|---------------|------------|-----------------|
| **Bronze** | 8-12 hours | ⭐⭐ | First-time builders |
| **Silver** | 20-30 hours | ⭐⭐⭐ | Intermediate developers |
| **Gold** | 40+ hours | ⭐⭐⭐⭐ | Advanced developers |
| **Platinum** | 60+ hours | ⭐⭐⭐⭐⭐ | Production teams |

### Recommended Path

**Week 1:** Complete Bronze Tier  
**Week 2:** Add Silver Tier features  
**Week 3-4:** Implement Gold Tier  
**Week 5-6:** Optional Platinum deployment

---

## 🥉 BRONZE TIER IMPLEMENTATION

### Required Features

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [ ] Gmail Watcher script (polls every 2 min)
- [ ] Claude Code reading/writing to vault
- [x] Folder structure: INPUT_QUEUES, PROCESSING, OUTPUT
- [x] All AI functionality as Qwen Code Skills
- [x] Ralph Wiggum Loop for multi-step tasks
- [x] HITL approval workflow

### Step-by-Step Implementation

#### Step 1: Verify Vault Structure ✅

```bash
# Check folder structure
ls -la AI_Employee_Vault/

# Should see:
# - Company_Handbook.md
# - Business_Goals.md
# - Dashboard.md
# - INPUT_QUEUES/
# - PROCESSING/
# - OUTPUT/
# - SECURITY/
# - SYSTEM/
```

#### Step 2: Test Gmail Watcher

```bash
# Start orchestrator
python main.py start

# Expected output:
# ✅ Gmail Watcher authenticated
# 📧 Polling Gmail...
# 📬 Found X new emails
```

#### Step 3: Test Ralph Loop

```bash
# Move test email to Pending
cp test_files/invoice_email.json \
   AI_Employee_Vault/PROCESSING/Pending/

# Watch orchestrator process it
# Expected:
# 🧠 Running Ralph Loop...
# ✅ Ralph Loop completed in X iterations
```

#### Step 4: Test HITL Workflow

```bash
# Check for approval files
ls AI_Employee_Vault/PROCESSING/Pending_Approval/

# Move approval to Approved
mv AI_Employee_Vault/PROCESSING/Pending_Approval/APPROVAL_*.md \
   AI_Employee_Vault/PROCESSING/Approved/

# Watch email get sent
# Expected:
# 📧 Executing email send...
# ✅ Email sent successfully
```

### Bronze Tier Testing

```bash
# Run unit tests
pytest tests/ -v

# Expected: 19 tests passing
```

---

## 🥈 SILVER TIER IMPLEMENTATION

### Required Features (All Bronze +)

- [ ] WhatsApp Watcher script
- [ ] LinkedIn auto-posting (SocialMCP)
- [ ] Plan.md creation workflow
- [ ] Basic scheduling (cron jobs)
- [ ] 2+ Watcher scripts

### Step-by-Step Implementation

#### Step 1: Implement WhatsApp Watcher

```python
# watchers/whatsapp_watcher.py
from playwright.sync_api import sync_playwright
from watchers.base import BaseWatcher

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str):
        super().__init__(vault_path, check_interval=30)
        self.session_path = Path(session_path)
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help']
    
    def check_for_updates(self) -> list:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                self.session_path, headless=True
            )
            page = browser.pages[0]
            page.goto('https://web.whatsapp.com')
            page.wait_for_selector('[data-testid="chat-list"]')
            
            # Find unread messages with keywords
            unread = page.query_selector_all('[aria-label*="unread"]')
            messages = []
            for chat in unread:
                text = chat.inner_text().lower()
                if any(kw in text for kw in self.keywords):
                    messages.append({'text': text, 'chat': chat})
            browser.close()
            return messages
    
    def create_action_file(self, item) -> Path:
        content = f'''---
type: whatsapp
received: {datetime.now().isoformat()}
priority: high
---

## Message
{item['text']}
'''
        filepath = self.queue_folder / f'WHATSAPP_{uuid4().hex[:8]}.json'
        write_atomic(str(filepath), content)
        return filepath
```

#### Step 2: Implement Plan.md Workflow

```python
# In orchestrator, after Ralph Loop creates draft:
def create_plan_file(task: Task, draft: str) -> Path:
    plan_folder = Path(vault_path) / "PROCESSING" / "Plans"
    plan_file = plan_folder / f"PLAN_{task.id}.md"
    
    content = f'''---
task_id: {task.id}
created: {datetime.now().isoformat()}
status: pending_approval
objective: Process {task.type} from {task.sender}
---

## Objective
Process {task.type} email from {task.sender}

## Steps
- [x] Read email
- [x] Categorize email
- [x] Draft reply
- [ ] Send email (requires approval)
- [ ] Log transaction

## Approval Required
Email send requires human approval. See Pending_Approval/

## Notes
Draft created by Ralph Loop in {task.iteration} iterations
'''
    write_atomic(str(plan_file), content)
    return plan_file
```

#### Step 3: Add Scheduling

```bash
# Add cron job for CEO Briefing (Monday 7 AM)
crontab -e

# Add line:
0 7 * * 1 cd /home/hunain/personal_assistant && python scripts/ceo_briefing.py
```

### Silver Tier Testing

```bash
# Test WhatsApp Watcher
python watchers/whatsapp_watcher.py --test

# Test Plan.md creation
python scripts/test_plan_workflow.py

# Test scheduling
python scripts/test_scheduling.py
```

---

## 🥇 GOLD TIER IMPLEMENTATION

### Required Features (All Silver +)

- [ ] OdooMCP for accounting
- [ ] SocialMCP (Facebook, Instagram, Twitter/X)
- [ ] CEO Briefing generation (Monday 7 AM)
- [ ] Hash chain audit logs
- [ ] Error recovery & graceful degradation

### Step 1: Implement OdooMCP

```python
# mcp_servers/odoo_mcp.py
from mcp_servers.base_mcp import BaseMCP, ValidationResult, ExecutionResult
import requests

class OdooMCP(BaseMCP):
    def __init__(self, vault_path: str):
        super().__init__(vault_path)
        self.rate_limit = 50  # API calls per hour
        self.odoo_url = os.getenv('ODOO_URL')
        self.odoo_db = os.getenv('ODOO_DATABASE')
        self.odoo_user = os.getenv('ODOO_USERNAME')
        self.odoo_password = os.getenv('ODOO_PASSWORD')
    
    def _requires_hitl(self, action: dict) -> bool:
        # ALWAYS HITL for financial postings
        return True
    
    def execute(self, action: dict) -> ExecutionResult:
        try:
            action_type = action.get('action')
            
            if action_type == 'create_invoice':
                return self._create_invoice(action)
            elif action_type == 'record_payment':
                return self._record_payment(action)
            elif action_type == 'get_report':
                return self._get_report(action)
            else:
                return ExecutionResult(
                    success=False,
                    error=f"Unknown action: {action_type}"
                )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e)
            )
    
    def _create_invoice(self, action: dict) -> ExecutionResult:
        # JSON-RPC call to Odoo
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "account.move",
                "method": "create",
                "args": [{
                    "move_type": "out_invoice",
                    "partner_id": action['partner_id'],
                    "invoice_line_ids": action['lines']
                }]
            },
            "id": 1
        }
        
        response = requests.post(
            f"{self.odoo_url}/jsonrpc",
            json=payload,
            auth=(self.odoo_user, self.odoo_password)
        )
        
        invoice_id = response.json().get('result')
        return ExecutionResult(
            success=True,
            output=f"Invoice created: {invoice_id}"
        )
```

### Step 2: Implement CEO Briefing

```python
# scripts/ceo_briefing.py
def generate_ceo_briefing():
    vault_path = Path(os.getenv('VAULT_PATH'))
    
    # Read Business_Goals.md
    goals = read_file(vault_path / 'Business_Goals.md')
    
    # Get completed tasks from last week
    completed = get_completed_tasks(
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now()
    )
    
    # Get bank transactions
    transactions = get_bank_transactions(last_7_days=True)
    
    # Calculate revenue
    revenue = sum(t['amount'] for t in transactions if t['type'] == 'income')
    
    # Identify bottlenecks
    bottlenecks = identify_bottlenecks(completed)
    
    # Generate briefing
    briefing = f'''---
generated: {datetime.now().isoformat()}
period: {last_week_start} to {datetime.now().strftime('%Y-%m-%d')}
---

# Monday Morning CEO Briefing

## Executive Summary
{"Strong" if revenue > target else "Needs improvement"} week with revenue {"ahead of" if revenue > target else "behind"} target.

## Revenue
- **This Week**: ${revenue:,.2f}
- **MTD**: ${month_to_date:,.2f} ({mtd_percentage}% of ${monthly_target:,.2f} target)
- **Trend**: {"On track" if on_track else "Behind"}

## Completed Tasks
{format_completed_tasks(completed)}

## Bottlenecks
{format_bottlenecks(bottlenecks)}

## Proactive Suggestions
{generate_suggestions(transactions, completed)}
'''
    
    # Write briefing
    briefing_file = vault_path / 'OUTPUT' / 'Reports' / f'{datetime.now().strftime("%Y-%m-%d")}_CEO_Briefing.md'
    write_atomic(str(briefing_file), briefing)
    
    return briefing_file
```

### Gold Tier Testing

```bash
# Test OdooMCP
python mcp_servers/odoo_mcp.py --test

# Test CEO Briefing
python scripts/ceo_briefing.py --dry-run

# Test hash chain audit logs
python scripts/test_audit_logs.py
```

---

## 💎 PLATINUM TIER IMPLEMENTATION

### Required Features (All Gold +)

- [ ] Cloud deployment (Oracle/AWS VM)
- [ ] Cloud/Local split architecture
- [ ] Git-based vault sync
- [ ] Health monitoring dashboard
- [ ] 24/7 operation with watchdog

### Step 1: Deploy to Cloud VM

```bash
# Oracle Cloud Free Tier setup
# 1. Create VM instance (Ubuntu 22.04)
# 2. SSH into VM
ssh ubuntu@<vm-ip>

# 3. Install dependencies
sudo apt update
sudo apt install -y python3.13 python3-pip nodejs npm

# 4. Clone repository
git clone <your-repo>
cd personal_assistant

# 5. Setup virtual environment
uv venv
source .venv/bin/activate
uv pip install -e .

# 6. Configure for cloud deployment
export CLOUD_MODE=true
export LOCAL_VAULT_SYNC_PATH=/home/ubuntu/vault-sync

# 7. Start with PM2
pm2 start orchestrator.py --interpreter python3
pm2 start gmail_watcher.py --interpreter python3
pm2 save
pm2 startup
```

### Step 2: Configure Vault Sync

```bash
# Setup Git-based sync
cd AI_Employee_Vault

# Initialize git repo
git init
git remote add origin <your-git-repo>

# Create .gitignore for secrets
cat > .gitignore << EOF
SECURITY/.env
SECURITY/*.json
SECURITY/audit_logs/
*.pid
EOF

# Initial commit
git add .
git commit -m "Initial vault commit"
git push -u origin main

# Setup sync script
cat > sync_vault.sh << EOF
#!/bin/bash
cd AI_Employee_Vault
git pull origin main
git add .
git commit -m "Sync $(date)"
git push origin main
EOF

chmod +x sync_vault.sh

# Run sync every 5 minutes
crontab -e
*/5 * * * * /home/ubuntu/personal_assistant/sync_vault.sh
```

### Platinum Tier Testing

```bash
# Test cloud/local split
python scripts/test_cloud_split.py

# Test vault sync
python scripts/test_vault_sync.py

# Test health monitoring
curl http://<vm-ip>:8080/health
```

---

## 🧪 TESTING CHECKLIST

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

## 📋 SUBMISSION REQUIREMENTS

### GitHub Repository

- [ ] Public repository (or private with judge access)
- [ ] README.md with setup instructions
- [ ] ARCHITECTURE.md with system design
- [ ] LICENSE file (MIT recommended)
- [ ] .gitignore (never commit secrets!)

### Documentation

- [ ] README.md includes:
  - Project overview
  - Setup instructions
  - Architecture diagram
  - Usage examples
  - Tier declaration

- [ ] Security disclosure:
  - How credentials are handled
  - HITL safeguards implemented
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

### Submission Form

- [ ] Complete submission form: https://forms.gle/JR9T1SJq5rmQyGkGA
- [ ] Include GitHub repo URL
- [ ] Include demo video URL (YouTube/unlisted)
- [ ] Declare tier (Bronze/Silver/Gold/Platinum)

---

## 🏆 JUDGING CRITERIA ALIGNMENT

| Criterion | Weight | How We Score High |
|-----------|--------|-------------------|
| **Functionality** | 30% | Complete Bronze + Silver features, working end-to-end |
| **Innovation** | 25% | Auto-skip promotional, mark-as-read on pending, Qwen Skills integration |
| **Practicality** | 20% | Daily use ready, solves real email overload problem |
| **Security** | 15% | HITL enforced, rate limiting, audit logging, secret isolation |
| **Documentation** | 10% | Complete ARCHITECTURE.md, MCP_SPEC.md, IMPLEMENTATION_GUIDE.md |

---

## 📞 GETTING HELP

### Wednesday Research Meetings

- **When:** Every Wednesday at 10:00 PM PKT
- **Where:** [Zoom Link](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **Meeting ID:** 871 8870 7642
- **Passcode:** 744832

### Learning Resources

- [Claude Code Fundamentals](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
- [MCP Introduction](https://modelcontextprotocol.io/introduction)
- [Obsidian Help](https://help.obsidian.md/Getting+started)

### Troubleshooting

See [Troubleshooting FAQ](#troubleshooting-faq) section below.

---

## ❓ TROUBLESHOOTING FAQ

### Q: Gmail Watcher not detecting emails?

**A:** Check:
1. OAuth token valid? Run `python scripts/gmail_auth.py`
2. Emails marked as unread?
3. Gmail API enabled in Google Cloud Console?

### Q: Ralph Loop timing out?

**A:** Check:
1. Qwen CLI installed? Run `qwen --version`
2. Prompt file created? Check `SYSTEM/state/prompt.md`
3. Timeout too short? Increase `ITERATION_TIMEOUT` in `.env`

### Q: Approval files not created?

**A:** Check:
1. Ralph Loop completing successfully?
2. Draft content extracted?
3. Folder permissions correct?

### Q: Emails not sending?

**A:** Check:
1. Gmail API scopes include `gmail.send`?
2. Approval moved to `Approved/` folder?
3. Rate limit exceeded? Check logs

---

**Ready to build your AI Employee? Start with Bronze Tier and iterate!** 🚀
