# Personal AI Employee - Architecture Design Document

**Version:** 1.0  
**Tier:** Bronze → Silver → Gold → Platinum  
**Last Updated:** 2026-02-17  
**Hackathon Compliance:** ✅ All requirements met

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Folder Structure](#folder-structure)
4. [Component Design](#component-design)
5. [Agent Skills Framework](#agent-skills-framework)
6. [Data Contracts](#data-contracts)
7. [State Machine](#state-machine)
8. [Security Model](#security-model)
9. [Error Handling](#error-handling)
10. [Implementation Roadmap](#implementation-roadmap)
11. [Common Utilities](#common-utilities)

---

## 🎯 System Overview

### What We're Building

A **Digital FTE (Full-Time Equivalent)** - an AI agent that autonomously manages personal and business tasks 24/7:

- ✉️ **Email Triage**: Auto-categorize, draft replies, flag urgent
- 💬 **WhatsApp Monitoring**: Keyword detection, reply drafting (HITL required)
- 🏦 **Finance Tracking**: Bank transaction sync, invoice generation
- 📱 **Social Media**: LinkedIn, Twitter/X, Instagram management
- 📊 **Weekly Audits**: CEO Briefing every Monday 7 AM

### Core Philosophy

- **Local-First**: All processing on local machine, no cloud dependency for Bronze/Silver
- **Privacy-Focused**: Secrets never sync, WhatsApp/banking LOCAL ONLY
- **Human-in-the-Loop**: Sensitive actions require approval
- **File-Based State**: JSON files in Obsidian vault (migrate to SQLite in Gold)
- **Agent Skills**: All AI functionality modularized as reusable skills

### Hackathon Requirements Compliance

| Requirement | Implementation |
|-------------|----------------|
| Local-first, agent-driven | ✅ JSON state in vault, Qwen subprocess |
| Obsidian dashboard | ✅ Root-level handbook + goals, vault structure |
| Ralph Wiggum loop | ✅ RalphLoop class with 3 completion signals |
| Agent Skills | ✅ Qwen Code Skills in `.qwen/skills/` with SKILL.md format |
| Handbook at root | ✅ Company_Handbook.md at vault root |
| Gmail first | ✅ Bronze tier starts with Gmail Watcher |
| HITL workflow | ✅ File-based approval system |
| MCP servers | ✅ Modular MCP architecture |
| Tiered roadmap | ✅ Bronze→Silver→Gold→Platinum |

---

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                         │
│  Gmail API │ WhatsApp Web │ Bank CSV │ File System Drop    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  PERCEPTION LAYER (Watchers)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Gmail Watcher │  │WhatsApp Watch│  │File Watcher  │      │
│  │(2 min poll)  │  │(30s poll)    │  │(realtime)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│                           ▼                                 │
│              INPUT_QUEUES/{Gmail,WhatsApp,Files}/           │
│                 action_YYYYMMDD_HHMMSS.json                 │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR (Main Loop)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Async Event Loop (asyncio)                          │  │
│  │  - Watcher lifecycle management                      │  │
│  │  - Task claiming from PROCESSING/Pending/            │  │
│  │  - Ralph Loop execution (spawn Qwen subprocess)      │  │
│  │  - Scheduled jobs (CEO Briefing @ Mon 7AM)           │  │
│  │  - Error recovery & circuit breakers                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    BRAIN LAYER (Qwen + Vault)               │
│  ┌─────────────────┐         ┌─────────────────────────┐   │
│  │  Qwen CLI       │         │  Obsidian Vault         │   │
│  │  (subprocess)   │◄───────►│  - Company_Handbook.md  │   │
│  │                 │         │  - Business_Goals.md    │   │
│  │  --file prompt  │         │  - PROCESSING/          │   │
│  └─────────────────┘         │  - SYSTEM/state/        │   │
│                              └─────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Qwen Code Skills (auto-loaded)                     │   │
│  │  - ~/.qwen/skills/ (personal)                       │   │
│  │  - .qwen/skills/ (project)                          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   ACTION LAYER (MCP Servers)                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │Email MCP   │  │Browser MCP │  │WhatsApp MCP│            │
│  │(SMTP/IMAP) │  │(Playwright)│  │(Playwright)│            │
│  └────────────┘  └────────────┘  └────────────┘            │
│                                                             │
│  HITL Check:                                                │
│  - Auto-approve: Known contacts, <1000 chars               │
│  - Require approval: Payments, WhatsApp, new payees        │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                           │
│  ✅ OUTPUT/Completed/    - Finished tasks                  │
│  📊 OUTPUT/Reports/      - CEO Briefings, audits           │
│  🗄️ OUTPUT/Archive/      - Monthly archival                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
AI_Employee_Vault/
├── 📋 Company_Handbook.md          # AI behavior rules, autonomy levels (ROOT LEVEL)
├── 📋 Business_Goals.md            # KPIs, targets, metrics (ROOT LEVEL)
│
├── 📥 INPUT_QUEUES/
│   ├── Gmail/                      # Gmail Watcher drops action files here
│   ├── WhatsApp/                   # WhatsApp Watcher drops action files here
│   ├── Banking/                    # Finance Watcher drops transaction files
│   └── Files/                      # File system drop folder
│
├── 🔄 PROCESSING/
│   ├── Pending/                    # Tasks waiting to be claimed
│   ├── In_Progress/                # Currently being worked on
│   ├── Plans/                      # Generated execution plans
│   ├── Pending_Approval/           # HITL queue (sensitive actions)
│   ├── Approved/                   # Human-approved actions ready to execute
│   ├── Rejected/                   # Human-rejected actions
│   └── Failed/                     # Dead Letter Queue
│
├── ✅ OUTPUT/
│   ├── Completed/                  # Finished tasks (archived here)
│   ├── Reports/                    # CEO Briefings, weekly audits
│   └── Archive/                    # Monthly archival (YYYY-MM/)
│
├── 🧠 KNOWLEDGE/
│   ├── Contexts/                   # Client profiles & history
│   │   └── clients.md
│   └── Procedures/                 # Reusable SOPs
│       ├── email_response.md
│       └── invoice_creation.md

├── 🤖 QWEN SKILLS/ (Qwen Code Skills - auto-loaded)
│   ├── ~/.qwen/skills/             # Personal skills (global)
│   └── .qwen/skills/               # Project skills (git-shareable)
│       ├── email-triage/
│       │   └── SKILL.md
│       ├── email-reply-draft/
│       │   └── SKILL.md
│       └── client-lookup/
│           └── SKILL.md
│
├── 🛡️ SECURITY/
│   ├── .env                        # API keys (NEVER COMMIT, chmod 600)
│   └── audit_logs/                 # Action logs (YYYY-MM-DD.jsonl)
│
└── ⚙️ SYSTEM/
    ├── state/                      # Current task states (JSON)
    │   ├── current_task.json
    │   ├── task_history.jsonl
    │   └── complete.flag           # Ralph Loop completion signal
    ├── config/                     # Watcher configurations
    │   ├── watchers.yaml
    │   └── mcp_config.yaml
    └── logs/
        ├── error.log
        └── performance.log
```

### Root Level Files (Hackathon Requirement)

**Company_Handbook.md** - AI behavior rules and autonomy levels:
- Decision-making authority matrix
- HITL thresholds
- Escalation policies
- Communication style guidelines

**Business_Goals.md** - KPIs, targets, metrics:
- Revenue targets
- Response time SLAs
- Task completion rates
- Cost optimization goals

---

## 🧩 Component Design

### 1. State Manager (`scripts/state_manager.py`)

**Responsibility**: Task lifecycle tracking with atomic file operations

```python
class StateManager:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.state_file = os.path.join(vault_path, "SYSTEM/state/current_task.json")
        self.history_file = os.path.join(vault_path, "SYSTEM/state/task_history.jsonl")
    
    def claim_task(self, task_id: str) -> dict:
        """Move task from Pending to In_Progress (atomic operation)"""
        pending_path = os.path.join(self.vault_path, "PROCESSING/Pending", f"{task_id}.json")
        in_progress_path = os.path.join(self.vault_path, "PROCESSING/In_Progress", f"{task_id}.json")
        
        # Atomic move
        shutil.move(pending_path, in_progress_path)
        
        # Update state
        task = read_json(in_progress_path)
        task["status"] = "in_progress"
        task["claimed_at"] = datetime.now().isoformat()
        write_atomic(self.state_file, json.dumps(task, indent=2))
        
        return task
    
    def claim_next_pending(self) -> Optional[dict]:
        """Claim highest priority pending task"""
        pending_folder = os.path.join(self.vault_path, "PROCESSING/Pending")
        
        # Get all pending tasks
        tasks = []
        for filename in os.listdir(pending_folder):
            if filename.endswith('.json'):
                filepath = os.path.join(pending_folder, filename)
                task = read_json(filepath)
                tasks.append((task, filepath))
        
        # Sort by priority (high > medium > low)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        tasks.sort(key=lambda x: priority_order.get(x[0].get('priority', 'low'), 3))
        
        # Claim first available
        for task, filepath in tasks:
            try:
                self.claim_task(task['id'])
                return task
            except Exception:
                continue  # Task might have been claimed by another process
        
        return None
    
    def update_state(self, task: dict) -> None:
        """Write task state to SYSTEM/state/current_task.json"""
        task["updated_at"] = datetime.now().isoformat()
        write_atomic(self.state_file, json.dumps(task, indent=2))
    
    def complete_task(self, task_id: str, result: str) -> None:
        """Move to OUTPUT/Completed/, update history"""
        in_progress_path = os.path.join(self.vault_path, "PROCESSING/In_Progress", f"{task_id}.json")
        completed_path = os.path.join(self.vault_path, "OUTPUT/Completed", f"{task_id}.json")
        
        task = read_json(in_progress_path)
        task["status"] = "completed"
        task["completed_at"] = datetime.now().isoformat()
        task["result"] = result
        
        shutil.move(in_progress_path, completed_path)
        self._append_history(task)
    
    def fail_task(self, task_id: str, error: str) -> None:
        """Move to PROCESSING/Failed/ (Dead Letter Queue)"""
        in_progress_path = os.path.join(self.vault_path, "PROCESSING/In_Progress", f"{task_id}.json")
        failed_path = os.path.join(self.vault_path, "PROCESSING/Failed", f"{task_id}.json")
        
        task = read_json(in_progress_path)
        task["status"] = "failed"
        task["error"] = error
        task["failed_at"] = datetime.now().isoformat()
        
        shutil.move(in_progress_path, failed_path)
        self._append_history(task)
    
    def request_approval(self, task: dict, reason: str) -> str:
        """Create file in PROCESSING/Pending_Approval/"""
        approval_id = str(uuid4())
        approval_file = os.path.join(
            self.vault_path, 
            "PROCESSING/Pending_Approval",
            f"APPROVAL_{approval_id}.md"
        )
        
        content = f"""---
approval_id: {approval_id}
task_id: {task['id']}
created_at: {datetime.now().isoformat()}
action_type: {task.get('action_required', 'unknown')}
reason: {reason}
---

# Approval Request

## Action
{task.get('action_required', 'Unknown action')}

## Draft Content
```
{task.get('draft_content', 'No draft content')}
```

## Context
- Source: {task.get('source', 'Unknown')}
- Created: {task.get('created_at', 'Unknown')}
- Priority: {task.get('priority', 'normal')}

## Instructions
Move this file to:
- `../Approved/` to execute the action
- `../Rejected/` to discard

---
**DO NOT EDIT THIS FILE** - Only move to Approved/ or Rejected/
"""
        write_atomic(approval_file, content)
        return approval_id
    
    def check_approval_status(self, task_id: str) -> str:
        """Check if file moved to Approved/ or Rejected/"""
        # Check Approved folder
        approved_folder = os.path.join(self.vault_path, "PROCESSING/Approved")
        for filename in os.listdir(approved_folder):
            if task_id in filename:
                return "approved"
        
        # Check Rejected folder
        rejected_folder = os.path.join(self.vault_path, "PROCESSING/Rejected")
        for filename in os.listdir(rejected_folder):
            if task_id in filename:
                return "rejected"
        
        return "pending"
    
    def _append_history(self, task: dict) -> None:
        """Append task to history log"""
        with open(self.history_file, "a") as f:
            f.write(json.dumps(task) + "\n")
```

**Atomic Operations**: Write to temp file → `os.rename()` (atomic on POSIX)

```python
def write_atomic(filepath: str, content: str) -> None:
    """Write file atomically using temp file + rename pattern"""
    dir_path = os.path.dirname(filepath)
    fd, temp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        os.rename(temp_path, filepath)
    except:
        os.unlink(temp_path)
        raise
```

---

### 2. Ralph Loop Orchestrator (`scripts/ralph_loop.py`)

**Responsibility**: Run Qwen in iterations until task completion

```python
class RalphLoop:
    MAX_ITERATIONS = 50
    NO_PROGRESS_THRESHOLD = 3
    COMPLETION_SIGNALS = [
        "<status>TASK_COMPLETE</status>",
        "<promise>COMPLETE</promise>",
        "DONE"
    ]
    
    def __init__(self, vault_path: str, qwen_cmd: str = "qwen"):
        self.vault_path = vault_path
        self.qwen_cmd = qwen_cmd
        self.state_file = os.path.join(vault_path, "SYSTEM/state/current_task.json")
        self.complete_flag = os.path.join(vault_path, "SYSTEM/state/complete.flag")
    
    def run(self, task: dict) -> TaskResult:
        """Execute Ralph Loop until completion or failure"""
        iteration = 0
        no_progress_count = 0
        last_state_hash = self._hash_state_file()
        
        while iteration < self.MAX_ITERATIONS:
            # Build prompt for this iteration
            prompt_path = self._build_prompt(task, iteration)
            
            try:
                # Spawn Qwen subprocess
                result = subprocess.run(
                    [self.qwen_cmd, "--file", prompt_path, "--cwd", self.vault_path],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes
                )
                
                # Check for completion signals
                for signal in self.COMPLETION_SIGNALS:
                    if signal in result.stdout:
                        self._cleanup()
                        return TaskResult(
                            success=True,
                            output=result.stdout,
                            iterations=iteration + 1
                        )
                
                # Check for complete.flag file
                if os.path.exists(self.complete_flag):
                    self._cleanup()
                    return TaskResult(
                        success=True,
                        output=result.stdout,
                        iterations=iteration + 1
                    )
                
                # Check for progress (state file changed)
                current_hash = self._hash_state_file()
                if current_hash == last_state_hash:
                    no_progress_count += 1
                    if no_progress_count >= self.NO_PROGRESS_THRESHOLD:
                        return TaskResult(
                            success=False,
                            error=f"No progress detected after {iteration + 1} iterations"
                        )
                else:
                    no_progress_count = 0
                    last_state_hash = current_hash
                
                iteration += 1
                
            except subprocess.TimeoutExpired:
                return TaskResult(success=False, error="Qwen timeout (5 min)")
            except Exception as e:
                return TaskResult(success=False, error=str(e))
        
        return TaskResult(success=False, error="Max iterations reached")
    
    def _build_prompt(self, task: dict, iteration: int) -> str:
        """Build prompt.md for Qwen iteration"""
        prompt_path = os.path.join(self.vault_path, "SYSTEM/prompt.md")
        
        prompt = f"""# AI Employee - Iteration {iteration + 1}

You are an autonomous AI Employee working in iterations (Ralph Loop pattern).

## CURRENT STATE
Read these files to understand context:
- SYSTEM/state/current_task.json - Current task state
- PROCESSING/In_Progress/{task['id']}.json - Task details
- Company_Handbook.md - Your behavior rules and autonomy levels

## YOUR TASK
{task.get('action_required', 'Process the task')}

## TASK DATA
```json
{json.dumps(task.get('data', {}), indent=2)}
```

## RULES
1. Read state files to understand previous progress
2. Take ONE concrete action (not planning, actual doing)
3. Update SYSTEM/state/current_task.json with what you did
4. If task complete, create SYSTEM/state/complete.flag OR output <status>TASK_COMPLETE</status>
5. If approval needed, create file in PROCESSING/Pending_Approval/ using StateManager
6. Never ask questions, just act
7. Log all actions to SYSTEM/logs/audit/

## COMPLETION SIGNAL
Output <status>TASK_COMPLETE</status> when done, or create complete.flag file.

BEGIN ITERATION {iteration + 1}:
"""
        write_atomic(prompt_path, prompt)
        return prompt_path
    
    def _hash_state_file(self) -> str:
        """Hash state file to detect changes"""
        if not os.path.exists(self.state_file):
            return ""
        with open(self.state_file, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _cleanup(self) -> None:
        """Clean up temporary files"""
        prompt_path = os.path.join(self.vault_path, "SYSTEM/prompt.md")
        if os.path.exists(prompt_path):
            os.unlink(prompt_path)
```

**Completion Signals** (3 methods):
1. `<status>TASK_COMPLETE</status>` in stdout
2. `<promise>COMPLETE</promise>` in stdout
3. `SYSTEM/state/complete.flag` file created

---

### 3. Watchers (`watchers/*.py`)

**Base Class**:
```python
class BaseWatcher:
    def __init__(self, vault_path: str, queue_folder: str, poll_interval: int):
        self.vault_path = vault_path
        self.queue_folder = os.path.join(vault_path, "INPUT_QUEUES", queue_folder)
        self.poll_interval = poll_interval
        self.state_manager = StateManager(vault_path)
    
    async def watch(self):
        """Main watch loop"""
        while True:
            try:
                items = self.check_for_new_items()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.log_error(e)
            await asyncio.sleep(self.poll_interval)
    
    def check_for_new_items(self) -> list:
        """Override: Check source for new items"""
        raise NotImplementedError
    
    def create_action_file(self, item: dict) -> str:
        """Create JSON action file in INPUT_QUEUES/{source}/"""
        filename = f"action_{datetime.now():%Y%m%d_%H%M%S}_{uuid4()}.json"
        filepath = os.path.join(self.queue_folder, filename)
        
        action = {
            "id": str(uuid4()),
            "source": self.__class__.__name__,
            "timestamp": datetime.now().isoformat(),
            "type": self.detect_type(item),
            "priority": self.calculate_priority(item),
            "data": item,
            "status": "new",
            "hitl_required": self.check_hitl_required(item)
        }
        
        write_atomic(filepath, json.dumps(action, indent=2))
        return filepath
    
    def detect_type(self, item: dict) -> str:
        """Override: Detect action type from item"""
        raise NotImplementedError
    
    def calculate_priority(self, item: dict) -> str:
        """Override: Calculate priority (high/medium/low)"""
        raise NotImplementedError
    
    def check_hitl_required(self, item: dict) -> bool:
        """Override: Check if HITL approval required"""
        raise NotImplementedError
    
    def log_error(self, error: Exception) -> None:
        """Log error to SYSTEM/logs/error.log"""
        log_path = os.path.join(self.vault_path, "SYSTEM/logs/error.log")
        with open(log_path, "a") as f:
            f.write(f"{datetime.now().isoformat()} - {self.__class__.__name__}: {error}\n")
```

**Implementations**:

#### Gmail Watcher (`watchers/gmail_watcher.py`)

```python
class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, poll_interval: int = 120):
        super().__init__(vault_path, "Gmail", poll_interval)
        self.gmail_service = self._authenticate()
        self.seen_ids = set()  # Track seen email IDs
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2"""
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        creds = Credentials.from_authorized_user_file(
            os.path.join(self.vault_path, "SECURITY/gmail_token.json")
        )
        return build('gmail', 'v1', credentials=creds)
    
    def check_for_new_items(self) -> list:
        """Check Gmail for new unread messages"""
        results = self.gmail_service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=10
        ).execute()
        
        messages = results.get('messages', [])
        new_items = []
        
        for msg in messages:
            if msg['id'] not in self.seen_ids:
                full_msg = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                new_items.append({
                    "email_id": msg['id'],
                    "from": self._extract_email(full_msg),
                    "subject": self._extract_subject(full_msg),
                    "body": self._extract_body(full_msg),
                    "labels": full_msg.get('labelIds', []),
                    "snippet": full_msg.get('snippet', '')
                })
                self.seen_ids.add(msg['id'])
        
        return new_items
    
    def detect_type(self, item: dict) -> str:
        """Detect email type"""
        subject = item.get('subject', '').lower()
        body = item.get('body', '').lower()
        
        if any(kw in subject or kw in body for kw in ['invoice', 'payment', 'bill']):
            return "invoice_related"
        elif any(kw in subject or kw in body for kw in ['urgent', 'asap', 'priority']):
            return "urgent"
        elif 'CATEGORY_PROMOTIONS' in item.get('labels', []):
            return "promotional"
        else:
            return "general"
    
    def calculate_priority(self, item: dict) -> str:
        """Calculate priority based on sender, keywords, labels"""
        score = 0
        
        # Known client check
        if self._is_known_client(item['from']):
            score += 30
        
        # Keywords
        keywords = ['urgent', 'asap', 'invoice', 'payment', 'deadline', 'important']
        for kw in keywords:
            if kw in item.get('subject', '').lower() or kw in item.get('body', '').lower():
                score += 10
        
        # Labels
        if 'IMPORTANT' in item.get('labels', []):
            score += 20
        if 'STARRED' in item.get('labels', []):
            score += 15
        
        if score >= 50:
            return "high"
        elif score >= 25:
            return "medium"
        else:
            return "low"
    
    def check_hitl_required(self, item: dict) -> bool:
        """Check if HITL approval required for reply"""
        # Unknown sender requires approval
        if not self._is_known_client(item['from']):
            return True
        
        # Payment-related requires approval
        if 'payment' in item.get('subject', '').lower() or 'invoice' in item.get('subject', '').lower():
            return True
        
        # Contains links requires approval
        if 'http' in item.get('body', ''):
            return True
        
        return False
    
    def _is_known_client(self, email: str) -> bool:
        """Check if sender is known client"""
        # Load from KNOWLEDGE/Contexts/clients.md
        clients_file = os.path.join(self.vault_path, "KNOWLEDGE/Contexts/clients.md")
        if not os.path.exists(clients_file):
            return False
        
        with open(clients_file, 'r') as f:
            content = f.read().lower()
        
        return email.lower() in content or email.split('@')[0].lower() in content
```

#### WhatsApp Watcher (`watchers/whatsapp_watcher.py`)

```python
class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, poll_interval: int = 30):
        super().__init__(vault_path, "WhatsApp", poll_interval)
        self.session_path = os.path.join(vault_path, "SECURITY/.whatsapp_session")
        self.browser = None
        self.page = None
    
    async def initialize(self):
        """Initialize Playwright browser for WhatsApp Web"""
        from playwright.async_api import async_playwright
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch_persistent_context(
            user_data_dir=self.session_path,
            headless=False  # Must be visible for QR scan
        )
        self.page = await self.browser.new_page()
        await self.page.goto("https://web.whatsapp.com")
    
    def check_for_new_items(self) -> list:
        """Check WhatsApp Web for new messages with keywords"""
        # This is simplified - actual implementation needs DOM selectors
        keywords = ['urgent', 'asap', 'invoice', 'payment', 'bhejo']
        
        # JavaScript to extract messages
        messages = self.page.evaluate("""
            () => {
                const chats = document.querySelectorAll('[data-testid="chat"]');
                return Array.from(chats).map(chat => ({
                    contact: chat.querySelector('[data-testid="info"]')?.textContent,
                    last_message: chat.querySelector('[data-testid="message"]')?.textContent,
                    timestamp: chat.querySelector('[data-testid="message-timestamp"]')?.textContent
                }));
            }
        """)
        
        new_items = []
        for msg in messages:
            if any(kw in (msg.get('last_message') or '').lower() for kw in keywords):
                new_items.append({
                    "contact": msg.get('contact', 'Unknown'),
                    "message": msg.get('last_message', ''),
                    "timestamp": msg.get('timestamp', '')
                })
        
        return new_items
    
    def detect_type(self, item: dict) -> str:
        """Detect message type"""
        message = item.get('message', '').lower()
        
        if any(kw in message for kw in ['invoice', 'bill', 'payment']):
            return "finance_related"
        elif any(kw in message for kw in ['urgent', 'asap', 'important']):
            return "urgent"
        else:
            return "general"
    
    def calculate_priority(self, item: dict) -> str:
        """All WhatsApp messages are high priority (user expectation)"""
        return "high"
    
    def check_hitl_required(self, item: dict) -> bool:
        """ALL WhatsApp messages require HITL (privacy policy)"""
        return True
```

---

### 4. Orchestrator (`scripts/orchestrator.py`)

**Responsibility**: Main event loop coordinating all components

```python
class Orchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.state_manager = StateManager(vault_path)
        self.ralph_loop = RalphLoop(vault_path)
        self.watchers = []
        self.mcp_servers = {}
        self.running = False
    
    def add_watcher(self, watcher: BaseWatcher):
        """Add watcher to the list"""
        self.watchers.append(watcher)
    
    def add_mcp(self, name: str, mcp: BaseMCP):
        """Add MCP server"""
        self.mcp_servers[name] = mcp
    
    async def start(self):
        """Main event loop"""
        self.running = True
        
        # Start watchers as background tasks
        watcher_tasks = [
            asyncio.create_task(watcher.watch())
            for watcher in self.watchers
        ]
        
        # Initialize input queue processor
        input_queues = ["Gmail", "WhatsApp", "Files"]
        
        # Main processing loop
        while self.running:
            try:
                # 1. Move new action files from INPUT_QUEUES to PROCESSING/Pending
                for queue in input_queues:
                    await self.process_input_queue(queue)
                
                # 2. Check for approved actions ready to execute
                await self.process_approved_actions()
                
                # 3. Claim next pending task
                task = self.state_manager.claim_next_pending()
                if task:
                    # 4. Run Ralph Loop
                    result = self.ralph_loop.run(task)
                    
                    # 5. Handle result
                    if result.success:
                        self.state_manager.complete_task(task['id'], result.output)
                    else:
                        self.state_manager.fail_task(task['id'], result.error)
                
                # 6. Check scheduled jobs (CEO Briefing @ Mon 7AM)
                await self.check_scheduled_jobs()
                
                # 7. Sleep to avoid busy-waiting
                await asyncio.sleep(5)
                
            except Exception as e:
                self.log_error(e)
                await asyncio.sleep(30)  # Back off on error
    
    async def process_input_queue(self, queue_name: str):
        """Move action files from INPUT_QUEUES to PROCESSING/Pending"""
        queue_path = os.path.join(self.vault_path, "INPUT_QUEUES", queue_name)
        pending_path = os.path.join(self.vault_path, "PROCESSING/Pending")
        
        for filename in os.listdir(queue_path):
            if filename.endswith('.json'):
                src = os.path.join(queue_path, filename)
                dst = os.path.join(pending_path, filename)
                shutil.move(src, dst)
    
    async def process_approved_actions(self):
        """Execute actions that human has approved"""
        approved_folder = os.path.join(self.vault_path, "PROCESSING/Approved")
        
        for filename in os.listdir(approved_folder):
            if filename.endswith('.json'):
                filepath = os.path.join(approved_folder, filename)
                action = read_json(filepath)
                
                mcp_type = action.get('mcp_type', 'email')
                mcp = self.mcp_servers.get(mcp_type)
                
                if mcp and mcp.validate(action):
                    result = mcp.execute(action)
                    if result.success:
                        # Archive action
                        archive_path = os.path.join(
                            self.vault_path,
                            "OUTPUT/Completed",
                            filename
                        )
                        shutil.move(filepath, archive_path)
                        
                        # Log to audit
                        self.log_audit(mcp.audit_log(action, result))
                    else:
                        # Move to Failed
                        failed_path = os.path.join(
                            self.vault_path,
                            "PROCESSING/Failed",
                            filename
                        )
                        shutil.move(filepath, failed_path)
    
    async def check_scheduled_jobs(self):
        """Check and run scheduled jobs (CEO Briefing @ Mon 7AM)"""
        now = datetime.now()
        
        # CEO Briefing: Every Monday at 7 AM
        if now.weekday() == 0 and now.hour == 7 and now.minute == 0:
            await self.generate_ceo_briefing()
    
    async def generate_ceo_briefing(self):
        """Generate weekly CEO Briefing report"""
        from scripts.ceo_briefing import generate_briefing
        
        report_path = os.path.join(
            self.vault_path,
            "OUTPUT/Reports",
            f"{datetime.now():%Y-%m-%d}_CEO_Briefing.md"
        )
        
        generate_briefing(self.vault_path, report_path)
    
    def log_audit(self, entry: dict):
        """Log to audit trail"""
        audit_path = os.path.join(
            self.vault_path,
            "SECURITY/audit_logs",
            f"{datetime.now():%Y-%m-%d}.jsonl"
        )
        
        with open(audit_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def log_error(self, error: Exception):
        """Log error"""
        log_path = os.path.join(self.vault_path, "SYSTEM/logs/error.log")
        with open(log_path, "a") as f:
            f.write(f"{datetime.now().isoformat()} - Orchestrator: {error}\n")
```

---

### 5. MCP Servers (`mcp_servers/*.py`)

**Interface**:
```python
class BaseMCP:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
    
    def validate(self, action: dict) -> ValidationResult:
        """Check if action can be executed (returns success, error_message)"""
        raise NotImplementedError
    
    def execute(self, action: dict) -> ExecutionResult:
        """Perform the action (returns success, output, error)"""
        raise NotImplementedError
    
    def audit_log(self, action: dict, result: ExecutionResult) -> dict:
        """Return log entry for audit trail"""
        return {
            "timestamp": datetime.now().isoformat(),
            "mcp": self.__class__.__name__,
            "action": action,
            "result": result.__dict__,
        }
```

**Email MCP (`mcp_servers/email_mcp.py`)**:
```python
class EmailMCP(BaseMCP):
    def __init__(self, vault_path: str):
        super().__init__(vault_path)
        self.rate_limit = 10  # 10 emails per hour
        self.sent_count = 0
        self.rate_limit_reset = datetime.now() + timedelta(hours=1)
    
    def validate(self, action: dict) -> ValidationResult:
        """Validate email action"""
        if self.sent_count >= self.rate_limit:
            return ValidationResult(
                success=False,
                error="Rate limit exceeded (10 emails/hour)"
            )
        
        if not action.get('to'):
            return ValidationResult(success=False, error="Missing 'to' field")
        
        if not action.get('subject'):
            return ValidationResult(success=False, error="Missing 'subject' field")
        
        return ValidationResult(success=True)
    
    def execute(self, action: dict) -> ExecutionResult:
        """Send email via Gmail API"""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError
            
            # Authenticate
            creds = Credentials.from_authorized_user_file(
                os.path.join(self.vault_path, "SECURITY/gmail_token.json")
            )
            service = build('gmail', 'v1', credentials=creds)
            
            # Create message
            message = self._create_message(
                action['to'],
                action['subject'],
                action.get('body', '')
            )
            
            # Send
            sent_message = service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            self.sent_count += 1
            
            return ExecutionResult(
                success=True,
                output=f"Email sent: {sent_message['id']}",
                error=None
            )
            
        except HttpError as e:
            return ExecutionResult(success=False, output=None, error=str(e))
    
    def _create_message(self, to: str, subject: str, body: str) -> dict:
        """Create Gmail API message"""
        from email.mime.text import MIMEText
        import base64
        
        message = MIMEText(body)
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject
        
        return {
            'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
        }
```

---

## 🎯 Agent Skills Framework

### Qwen Code Skills

Skills are stored in `.qwen/skills/{skill_name}/SKILL.md` (project-level, git-shareable) or `~/.qwen/skills/` (personal).

**How Skills Work:**
- Qwen Code auto-discovers skills at startup
- Model triggers skills based on description keyword matching
- Each skill contains: trigger conditions, input/output schemas, decision rules, examples

**Bronze Tier Skills:**
- `email-triage` - Categorize and prioritize emails
- `email-reply-draft` - Draft email replies
- `client-lookup` - Check if sender is known client

Each skill in `.qwen/skills/{skill_name}/SKILL.md`:
```markdown
---
name: skill-name
description: Brief description with trigger keywords. Use when X, Y, Z.
---

# Skill Name

## When to Use
- Condition 1
- Condition 2

## Input Schema
```json
{
  "email_id": "string",
  "from": "string", 
  "subject": "string",
  "body": "string",
  "labels": ["string"]
}
```

## Processing Steps
1. [READ] email content from INPUT_QUEUES/Gmail/
2. [ANALYZE] classify priority using Company_Handbook rules
3. [DECIDE] if reply needed → draft reply
4. [CHECK] if HITL required (unknown sender, payment, links)
5. [WRITE] result to PROCESSING/Plans/ or request approval

## Tools Allowed
- read_file: INPUT_QUEUES/, KNOWLEDGE/Clients/
- write_file: PROCESSING/Plans/, PROCESSING/Pending_Approval/
- draft_email: create but don't send
- request_approval: if HITL threshold met

## Output Schema
```json
{
  "action": "draft_reply|archive|flag_for_human",
  "draft_path": "PROCESSING/Plans/PLAN_{id}.md",
  "approval_required": true|false,
  "reason": "string"
}
```

## Examples

### Example 1: Urgent Invoice Email
**Input:**
```json
{
  "from": "client@abc.com",
  "subject": "Urgent: Payment pending",
  "body": "Hi, your invoice #12345 is overdue. Please pay ASAP.",
  "labels": ["IMPORTANT", "INBOX"]
}
```

**Output:**
```json
{
  "action": "draft_reply",
  "draft_path": "PROCESSING/Plans/PLAN_abc123.md",
  "approval_required": true,
  "reason": "Payment-related email requires approval"
}
```

### Example 2: Newsletter
**Input:**
```json
{
  "from": "newsletter@company.com",
  "subject": "Weekly Updates",
  "body": "Check out our latest features...",
  "labels": ["CATEGORY_PROMOTIONS"]
}
```

**Output:**
```json
{
  "action": "archive",
  "approval_required": false,
  "reason": "Promotional email, no action needed"
}
```
```

### Skill Templates to Create

| Skill | File | Tier |
|-------|------|------|
| Email Triage | `.qwen/skills/email-triage/SKILL.md` | Bronze |
| Email Reply Draft | `.qwen/skills/email-reply-draft/SKILL.md` | Bronze |
| Client Lookup | `.qwen/skills/client-lookup/SKILL.md` | Bronze |
| Invoice Generation | `.qwen/skills/invoice-generation/SKILL.md` | Silver |
| WhatsApp Reply | `.qwen/skills/whatsapp-reply/SKILL.md` | Silver |
| Social Media Post | `.qwen/skills/social-media-post/SKILL.md` | Gold |

---

## 📐 Data Contracts

### Task Schema (`PROCESSING/Pending/*.json`)

```json
{
  "id": "uuid4-string",
  "created_at": "2026-02-17T10:30:00Z",
  "updated_at": "2026-02-17T10:30:00Z",
  "source": "GmailWatcher",
  "type": "email_triage",
  "priority": "high",
  "status": "pending",
  "data": {
    "email_id": "gmail-msg-id",
    "from": "client@example.com",
    "subject": "Urgent: Invoice Payment",
    "body": "Email body text...",
    "labels": ["important", "inbox"]
  },
  "action_required": "draft_reply",
  "metadata": {
    "sender_known": true,
    "keywords": ["urgent", "invoice", "payment"],
    "priority_score": 85
  },
  "hitl_required": false
}
```

### State Schema (`SYSTEM/state/current_task.json`)

```json
{
  "task_id": "uuid4-string",
  "status": "in_progress",
  "iteration": 3,
  "started_at": "2026-02-17T10:35:00Z",
  "last_iteration_at": "2026-02-17T10:40:00Z",
  "context": {
    "last_action": "read_email_and_analyzed_intent",
    "next_step": "draft_reply_for_approval",
    "notes": "Client asking about invoice #12345"
  },
  "history": [
    {"iteration": 1, "action": "read_email", "timestamp": "..."},
    {"iteration": 2, "action": "check_client_history", "timestamp": "..."},
    {"iteration": 3, "action": "draft_reply", "timestamp": "..."}
  ]
}
```

### Approval Request Schema (`PROCESSING/Pending_Approval/APPROVAL_xxx.md`)

```markdown
---
approval_id: uuid4-string
task_id: uuid4-string
created_at: 2026-02-17T10:45:00Z
action_type: send_email
reason: Reply to client requires approval (company policy)
---

# Approval Request

## Action
Send email reply to client@example.com

## Draft Content
```
Subject: Re: Urgent: Invoice Payment

Dear Client,

Thank you for reaching out. Your invoice #12345 is being processed...
```

## Context
- Original email received: 2026-02-17T10:30:00Z
- Client: ABC Corp (known contact)
- Keywords: urgent, invoice, payment

## Instructions
Move this file to:
- `../Approved/` to execute the action
- `../Rejected/` to discard

---
**DO NOT EDIT THIS FILE** - Only move to Approved/ or Rejected/
```

### Audit Log Schema (`SECURITY/audit_logs/YYYY-MM-DD.jsonl`)

```json
{"timestamp": "2026-02-17T10:30:00Z", "event": "task_created", "task_id": "uuid", "source": "GmailWatcher", "details": {...}}
{"timestamp": "2026-02-17T10:35:00Z", "event": "task_claimed", "task_id": "uuid", "orchestrator": "main", "details": {...}}
{"timestamp": "2026-02-17T10:40:00Z", "event": "iteration_complete", "task_id": "uuid", "iteration": 3, "details": {...}}
{"timestamp": "2026-02-17T10:45:00Z", "event": "approval_requested", "task_id": "uuid", "approval_id": "uuid", "reason": "send_email", "details": {...}}
```

---

## 🔄 State Machine

### Task Lifecycle

```
                    ┌─────────────┐
                    │   CREATED   │ (Watcher creates action file)
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
          ┌────────│   PENDING   │◄───────┐
          │        └──────┬──────┘        │
          │               │               │
          │               ▼               │
          │        ┌─────────────┐        │
          │        │   CLAIMED   │        │ (Orchestrator claims task)
          │        └──────┬──────┘        │
          │               │               │
          │               ▼               │
          │        ┌─────────────┐        │
          │        │ IN_PROGRESS │────────┤ (Ralph Loop iterations)
          │        └──────┬──────┘        │
          │               │               │
          │               ▼               │
          │        ┌─────────────┐        │
          │        │  AWAITING   │        │ (HITL approval needed)
          │        │  APPROVAL   │        │
          │        └──────┬──────┘        │
          │               │               │
          │       ┌───────┴───────┐       │
          │       ▼               ▼       │
          │ ┌──────────┐    ┌──────────┐ │
          │ │ APPROVED │    │ REJECTED │─┘
          │ └────┬─────┘    └──────────┘
          │      │
          │      ▼
          │ ┌─────────────┐
          │ │  EXECUTING  │ (MCP server action)
          │ └──────┬──────┘
          │        │
          │        ▼
          │ ┌─────────────┐
          └│  COMPLETED  │
           └─────────────┘
                 │
                 ▼
           ┌─────────────┐
           │   FAILED    │ (Dead Letter Queue)
           └─────────────┘
```

### State Transitions

| From | To | Trigger |
|------|-----|---------|
| CREATED | PENDING | Watcher creates action file in INPUT_QUEUES |
| PENDING | CLAIMED | Orchestrator claims task |
| CLAIMED | IN_PROGRESS | Task moved to PROCESSING/In_Progress |
| IN_PROGRESS | IN_PROGRESS | Ralph Loop iteration (state update) |
| IN_PROGRESS | AWAITING_APPROVAL | Qwen determines HITL required |
| IN_PROGRESS | COMPLETED | Task finished (no approval needed) |
| IN_PROGRESS | FAILED | Error during Ralph Loop |
| AWAITING_APPROVAL | APPROVED | Human moves file to Approved/ |
| AWAITING_APPROVAL | REJECTED | Human moves file to Rejected/ |
| APPROVED | EXECUTING | MCP server starts action |
| EXECUTING | COMPLETED | MCP action successful |
| EXECUTING | FAILED | MCP action failed |
| REJECTED | COMPLETED | Task archived as rejected |
| FAILED | PENDING | Human retries task (manual) |

---

## 🛡️ Security Model

### Credential Management

```
SECURITY/.env  (chmod 600, gitignored)

# Gmail API
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REFRESH_TOKEN=...

# Bank API (if applicable)
BANK_API_KEY=...
BANK_API_SECRET=...

# Odoo ERP (Gold tier)
ODOO_URL=...
ODOO_DB=...
ODOO_USERNAME=...
ODOO_PASSWORD=...

# WhatsApp Session (LOCAL ONLY, encrypted)
WHATSAPP_SESSION_PATH=/home/hunain/.whatsapp_session
```

**Never stored in vault, never synced to cloud.**

### HITL Thresholds

| Action Type | Auto-Approve | Require Approval |
|-------------|--------------|------------------|
| Email reply | Known contact, <1000 chars | Unknown sender, >1000 chars, contains links |
| WhatsApp reply | NEVER (always HITL) | All messages |
| Payment | NEVER | All payments |
| New payee | NEVER | All new payees |
| File organization | Yes | No |
| Data entry (local) | Yes | No |
| Social media post | Draft only | Publishing |
| Data deletion | NEVER | All deletions |
| Contract signing | NEVER | All contracts |

### Rate Limiting

| Action | Limit | Window |
|--------|-------|--------|
| Email sending | 10 emails | Per hour |
| WhatsApp messages | 20 messages | Per hour |
| Payment attempts | 3 attempts | Per hour |
| API calls (Gmail) | 100 calls | Per minute |

### Audit Logging

**Bronze/Silver**: Simple JSONL logging
```json
{"timestamp": "...", "event": "email_sent", "to": "client@example.com", "actor": "EmailMCP"}
```

**Gold/Platinum**: Hash chain for tamper evidence
```json
{"timestamp": "...", "event": "email_sent", "to": "client@example.com", "actor": "EmailMCP", "prev_hash": "abc123...", "current_hash": "def456..."}
```

---

## ⚠️ Error Handling

### Retry Strategy

| Error Type | Retries | Backoff | Circuit Breaker |
|------------|---------|---------|-----------------|
| Transient (network, timeout) | 3 | Exponential (1s, 5s, 30s) | Pause 10 min after 3 failures |
| Auth failure | 0 | None | Immediate alert to human |
| Logic error (AI mistake) | 0 | None | Move to Dead Letter Queue |
| Rate limit | 3 | Exponential (60s, 300s, 900s) | Pause 1 hour |
| File system error | 3 | Fixed (1s) | Alert human |

### Circuit Breaker States

```
┌─────────────┐
│   CLOSED    │ (Normal operation, requests flow through)
└──────┬──────┘
       │
       │ Failure count >= threshold
       ▼
┌─────────────┐
│   OPEN    │ (Requests blocked, wait for timeout)
└──────┬──────┘
       │
       │ Timeout expired
       ▼
┌─────────────┐
│  HALF-OPEN  │ (Test with single request)
└──────┬──────┘
       │
       ├─ Success → CLOSED
       └─ Failure → OPEN
```

### Dead Letter Queue

Failed tasks moved to `PROCESSING/Failed/`:
- Human reviews manually
- Can retry (move back to Pending) or archive
- Audit log preserved

---

## 🔧 Common Utilities

### Data Classes

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class TaskResult:
    """Result from Ralph Loop execution"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    iterations: int = 0

@dataclass
class ValidationResult:
    """Result from MCP validation"""
    success: bool
    error: Optional[str] = None

@dataclass
class ExecutionResult:
    """Result from MCP execution"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
```

### Helper Functions

```python
import json
import os
import tempfile

def read_json(filepath: str) -> dict:
    """Read and parse JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def write_atomic(filepath: str, content: str) -> None:
    """Write file atomically using temp file + rename pattern"""
    dir_path = os.path.dirname(filepath)
    fd, temp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        os.rename(temp_path, filepath)
    except:
        os.unlink(temp_path)
        raise
```

---

## 📅 Implementation Roadmap

### Phase 1: Bronze (Week 1, 8-12 hours)

**Goal**: Working MVP with Gmail automation

| Task | File | Hours |
|------|------|-------|
| Create vault structure | `AI_Employee_Vault/` | 0.5 |
| Company_Handbook.md (root) | `Company_Handbook.md` | 1 |
| Business_Goals.md (root) | `Business_Goals.md` | 0.5 |
| Qwen Skills (email-triage, reply-draft, client-lookup) | `.qwen/skills/*/SKILL.md` | 1 |
| State Manager | `scripts/state_manager.py` | 2 |
| Ralph Loop | `scripts/ralph_loop.py` | 2 |
| **Gmail Watcher** | `watchers/gmail_watcher.py` | 3 |
| Gmail OAuth setup | `scripts/gmail_auth.py` | 1.5 |
| Orchestrator (basic) | `scripts/orchestrator.py` | 2 |
| Email MCP (Gmail API) | `mcp_servers/email_mcp.py` | 1.5 |
| Test end-to-end | Manual testing | 1 |

**Success Criteria**:
- [ ] New email arrives in Gmail → Watcher detects → Action file created
- [ ] Qwen reads email → Drafts reply (or archives) → Updates state
- [ ] If HITL required: Approval file created in Pending_Approval/
- [ ] Human moves to Approved/ → Email MCP sends reply
- [ ] Task completes → Moved to OUTPUT/Completed/ → Audit logged
- [ ] Ralph Loop handles multi-step tasks (read → analyze → draft → send)

---

### Phase 2: Silver (Week 2, +20-30 hours)

**Goal**: WhatsApp automation with HITL approval

| Task | File | Hours |
|------|------|-------|
| WhatsApp Watcher | `watchers/whatsapp_watcher.py` | 4 |
| HITL Approval Workflow | `scripts/hitl_manager.py` | 2 |
| Browser MCP | `mcp_servers/browser_mcp.py` | 3 |
| WhatsApp MCP | `mcp_servers/whatsapp_mcp.py` | 2 |
| Orchestrator (full) | `scripts/orchestrator.py` | 3 |
| Scheduled Jobs | `scripts/scheduler.py` | 2 |
| Error Recovery | Circuit breaker implementation | 2 |

**Success Criteria**:
- [ ] WhatsApp message detected → Always requires approval
- [ ] Scheduled CEO Briefing runs Monday 7 AM
- [ ] Circuit breaker triggers on repeated failures

---

### Phase 3: Gold (Week 3-4, +40+ hours)

**Goal**: Full cross-domain integration with Odoo

| Task | File | Hours |
|------|------|-------|
| Finance Watcher | `watchers/finance_watcher.py` | 4 |
| Odoo MCP | `mcp_servers/odoo_mcp.py` | 6 |
| LinkedIn MCP | `mcp_servers/linkedin_mcp.py` | 4 |
| Twitter MCP | `mcp_servers/twitter_mcp.py` | 3 |
| Instagram MCP | `mcp_servers/instagram_mcp.py` | 3 |
| CEO Briefing Generator | `scripts/ceo_briefing.py` | 4 |
| Hash Chain Audit Logs | `scripts/audit_logger.py` | 2 |
| SQLite Migration | `scripts/state_manager.py` (SQLite version) | 4 |

**Success Criteria**:
- [ ] Bank transactions synced daily
- [ ] Invoices auto-generated from completed tasks
- [ ] Weekly CEO Briefing in OUTPUT/Reports/
- [ ] Tamper-evident audit logs

---

### Phase 4: Platinum (Week 5-6, +60+ hours)

**Goal**: Production 24/7 deployment with cloud/local split

| Task | File | Hours |
|------|------|-------|
| Oracle Cloud VM Setup | Infrastructure | 4 |
| Docker Containerization | `Dockerfile`, `docker-compose.yml` | 3 |
| Git Vault Sync | `scripts/vault_sync.py` | 4 |
| Health Monitoring | Prometheus + Grafana | 4 |
| Alerting (PagerDuty/Slack) | `scripts/alerting.py` | 2 |
| Secrets Management | HashiCorp Vault integration | 3 |
| Backup Strategy | Automated backups | 2 |

**Success Criteria**:
- [ ] Cloud agent drafts, local agent approves
- [ ] Vault syncs via Git (secrets excluded)
- [ ] Health dashboard shows system status
- [ ] Alerts on critical failures

---

## 🎯 Next Steps

1. **Review this architecture** - Confirm all design decisions
2. **Start Bronze Phase** - Create vault structure and core components
3. **Test end-to-end** - Gmail watcher → Qwen → State update → Email sent
4. **Iterate** - Add WhatsApp, HITL, scheduling in Silver phase

---

**Architecture complete. Ready to implement?**
