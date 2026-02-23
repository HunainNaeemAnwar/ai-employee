# 🖥️ MCP SERVER SPECIFICATIONS

**Version:** 1.0  
**Last Updated:** 2026-02-23  
**Status:** Ready for Implementation

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Base Framework](#base-framework)
3. [MCP Server Specifications](#mcp-server-specifications)
4. [Security Requirements](#security-requirements)
5. [Implementation Guide](#implementation-guide)
6. [Testing Pattern](#testing-pattern)

---

## 🎯 OVERVIEW

### What Are MCP Servers?

**MCP (Model Context Protocol) Servers** are Python modules that provide validated action execution for the AI Employee system.

### Key Characteristics

- **NOT separate processes** - Imported classes called directly by orchestrator
- **Validation first** - Every action validated before execution
- **Rate limiting** - Per-MCP rate limits enforced
- **HITL enforcement** - Human-in-the-Loop checks built-in
- **Audit logging** - Every action logged automatically
- **Error handling** - Graceful failure with proper error messages

### MCP Server Tiers

| Tier | MCPs | Purpose |
|------|------|---------|
| **Bronze** | StateMCP, EmailMCP | Core functionality |
| **Silver** | + BrowserMCP, WhatsAppMCP | Web automation |
| **Gold** | + OdooMCP, SocialMCP | Business integration |
| **Platinum** | + SyncMCP | Cloud deployment |

---

## 🏗️ BASE FRAMEWORK

### File Structure

```
mcp_servers/
├── __init__.py              # Export all MCPs
├── base_mcp.py              # BaseMCP class + dataclasses
├── email_mcp.py             # EmailMCP (Bronze)
├── state_mcp.py             # StateMCP (Bronze)
├── browser_mcp.py           # BrowserMCP (Silver)
├── whatsapp_mcp.py          # WhatsAppMCP (Silver)
├── odoo_mcp.py              # OdooMCP (Gold)
├── social_mcp.py            # SocialMCP (Gold)
└── sync_mcp.py              # SyncMCP (Platinum)
```

### Base Classes (`mcp_servers/base_mcp.py`)

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ValidationResult:
    """Result of action validation"""
    success: bool
    error: Optional[str] = None

@dataclass
class ExecutionResult:
    """Result of action execution"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None

class BaseMCP:
    """Base class for all MCP servers"""
    
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.rate_limit: Optional[int] = None
        self.rate_limit_count: int = 0
        self.rate_limit_reset: Optional[datetime] = None
    
    def validate(self, action: dict) -> ValidationResult:
        """
        Check if action can be executed.
        
        Override in subclass to implement:
        - Rate limit checks
        - HITL approval checks
        - Parameter validation
        
        Returns:
            ValidationResult(success=True) if valid
            ValidationResult(success=False, error="reason") if invalid
        """
        raise NotImplementedError
    
    def execute(self, action: dict) -> ExecutionResult:
        """
        Perform the action.
        
        Override in subclass to implement actual functionality.
        
        Returns:
            ExecutionResult(success=True, output="result")
            ExecutionResult(success=False, error="error")
        """
        raise NotImplementedError
    
    def audit_log(self, action: dict, result: ExecutionResult) -> dict:
        """
        Generate audit log entry.
        
        Called automatically after every execution.
        
        Returns:
            Dictionary with timestamp, MCP name, action, result
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "mcp": self.__class__.__name__,
            "action": action,
            "result": {
                "success": result.success,
                "output": result.output,
                "error": result.error
            }
        }
    
    def _rate_limit_exceeded(self) -> bool:
        """Check if rate limit exceeded. Override in subclass."""
        if self.rate_limit is None:
            return False
        
        # Reset if hour passed
        if (self.rate_limit_reset and 
            datetime.now() > self.rate_limit_reset):
            self.rate_limit_count = 0
            self.rate_limit_reset = None
        
        # Check limit
        if self.rate_limit_count >= self.rate_limit:
            return True
        
        # Increment counter
        self.rate_limit_count += 1
        
        # Set reset time
        if not self.rate_limit_reset:
            self.rate_limit_reset = datetime.now().replace(
                minute=0, second=0, microsecond=0
            )
            self.rate_limit_reset = self.rate_limit_reset.replace(hour=datetime.now().hour + 1)
        
        return False
    
    def _requires_hitl(self, action: dict) -> bool:
        """
        Check if action requires HITL approval.
        
        Override in subclass with MCP-specific logic.
        
        Returns:
            True if HITL required, False otherwise
        """
        return False
```

---

## 📦 MCP SERVER SPECIFICATIONS

### 1. StateMCP (Bronze Tier)

**File:** `mcp_servers/state_mcp.py`  
**Purpose:** Read/write vault state files  
**Dependencies:** None (pure Python)

#### Actions

| Action | Description | HITL Required |
|--------|-------------|---------------|
| `read_file` | Read any file in vault | No |
| `write_file` | Write file (atomic: temp + rename) | No |
| `move_file` | Move file between folders | No |
| `list_directory` | List files in folder | No |

#### Validation Rules

```python
def validate(self, action: dict) -> ValidationResult:
    # Cannot write to SECURITY/ (protected)
    if action['path'].startswith('SECURITY/'):
        return ValidationResult(
            success=False,
            error="Cannot write to SECURITY/ folder"
        )
    
    # Cannot delete files (only move to Archive)
    if action.get('action') == 'delete':
        return ValidationResult(
            success=False,
            error="Cannot delete files. Move to Archive/ instead."
        )
    
    # Must use atomic writes
    if not action.get('atomic', False):
        return ValidationResult(
            success=False,
            error="Must use atomic writes (atomic=True)"
        )
    
    return ValidationResult(success=True)
```

#### Implementation Example

```python
class StateMCP(BaseMCP):
    def execute(self, action: dict) -> ExecutionResult:
        try:
            action_type = action.get('action')
            
            if action_type == 'read_file':
                with open(action['path'], 'r') as f:
                    return ExecutionResult(
                        success=True,
                        output=f.read()
                    )
            
            elif action_type == 'write_file':
                # Atomic write: temp file + rename
                dir_path = os.path.dirname(action['path'])
                fd, temp_path = tempfile.mkstemp(dir=dir_path)
                
                try:
                    with os.fdopen(fd, 'w') as f:
                        f.write(action['content'])
                    os.rename(temp_path, action['path'])
                    
                    return ExecutionResult(
                        success=True,
                        output=f"Written: {action['path']}"
                    )
                except:
                    os.unlink(temp_path)
                    raise
            
            elif action_type == 'move_file':
                shutil.move(action['src'], action['dst'])
                return ExecutionResult(
                    success=True,
                    output=f"Moved: {action['src']} → {action['dst']}"
                )
            
            elif action_type == 'list_directory':
                files = os.listdir(action['path'])
                return ExecutionResult(
                    success=True,
                    output='\n'.join(files)
                )
            
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
```

---

### 2. EmailMCP (Bronze Tier)

**File:** `mcp_servers/email_mcp.py`  
**Purpose:** Send emails via Gmail API  
**Dependencies:** `google-api-python-client`, `google-auth-httplib2`

#### Actions

| Action | Description | HITL Required |
|--------|-------------|---------------|
| `send_email` | Send email via Gmail API | Unknown recipients, payment-related, contains links |
| `draft_email` | Create draft only | No |
| `search_emails` | Search inbox | No |

#### Rate Limit

**10 emails/hour**

#### Validation Rules

```python
def validate(self, action: dict) -> ValidationResult:
    # Check rate limit
    if self._rate_limit_exceeded():
        return ValidationResult(
            success=False,
            error=f"Rate limit exceeded: {self.rate_limit}/hour"
        )
    
    # Check required parameters
    if not action.get('to'):
        return ValidationResult(
            success=False,
            error="Missing required parameter: 'to'"
        )
    
    if not action.get('subject'):
        return ValidationResult(
            success=False,
            error="Missing required parameter: 'subject'"
        )
    
    # Check HITL requirements
    if self._requires_hitl(action):
        if not action.get('hitl_approved'):
            return ValidationResult(
                success=False,
                error="HITL approval required. Move approval file to Approved/ folder."
            )
    
    return ValidationResult(success=True)

def _requires_hitl(self, action: dict) -> bool:
    """Check if HITL approval required"""
    # Unknown recipient
    if not self._is_known_recipient(action['to']):
        return True
    
    # Payment-related
    if 'payment' in action.get('subject', '').lower():
        return True
    if 'invoice' in action.get('subject', '').lower():
        return True
    
    # Contains links
    if 'http://' in action.get('body', '') or 'https://' in action.get('body', ''):
        return True
    
    return False
```

---

### 3. BrowserMCP (Silver Tier)

**File:** `mcp_servers/browser_mcp.py`  
**Purpose:** Browser automation via Playwright  
**Dependencies:** `playwright`

#### Actions

| Action | Description | HITL Required |
|--------|-------------|---------------|
| `navigate` | Go to URL | Payment pages, login pages |
| `click` | Click element | Payment pages |
| `fill_form` | Fill input field | Login forms |
| `screenshot` | Take screenshot | No |
| `get_text` | Extract text | No |

#### Rate Limit

**60 actions/hour**

---

### 4. WhatsAppMCP (Silver Tier)

**File:** `mcp_servers/whatsapp_mcp.py`  
**Purpose:** WhatsApp Web automation  
**Dependencies:** `playwright`

#### Actions

| Action | Description | HITL Required |
|--------|-------------|---------------|
| `send_message` | Send WhatsApp message | **ALWAYS** |
| `read_chat` | Read recent messages | No |
| `scan_qr` | Display QR for auth | No |

#### Rate Limit

**20 messages/hour**

#### Special Requirements

- **ALWAYS HITL required** (privacy policy)
- **LOCAL ONLY** - never run on cloud
- Session stored in `SECURITY/.whatsapp_session/`

---

### 5. OdooMCP (Gold Tier)

**File:** `mcp_servers/odoo_mcp.py`  
**Purpose:** Odoo ERP integration  
**Dependencies:** `requests`

#### Actions

| Action | Description | HITL Required |
|--------|-------------|---------------|
| `create_invoice` | Create customer invoice | **ALWAYS** |
| `record_payment` | Record payment received | **ALWAYS** |
| `get_report` | Generate P&L, balance sheet | No |
| `reconcile` | Match transactions | **ALWAYS** |

#### Rate Limit

**50 API calls/hour**

---

### 6. SocialMCP (Gold Tier)

**File:** `mcp_servers/social_mcp.py`  
**Purpose:** Social media posting  
**Dependencies:** `requests`

#### Actions

| Action | Description | HITL Required |
|--------|-------------|---------------|
| `post_linkedin` | Post to LinkedIn | Yes |
| `post_twitter` | Post to Twitter/X | Yes |
| `post_instagram` | Post to Instagram | Yes |
| `schedule_post` | Schedule for later | Yes |

#### Rate Limit

**5 posts/hour per platform**

---

### 7. SyncMCP (Platinum Tier)

**File:** `mcp_servers/sync_mcp.py`  
**Purpose:** Cloud-local vault synchronization  
**Dependencies:** `gitpython`

#### Actions

| Action | Description | HITL Required |
|--------|-------------|---------------|
| `sync_vault` | Push/pull vault changes | No |
| `resolve_conflict` | Handle file conflicts | No |
| `health_check` | Check sync status | No |

#### Special Requirements

- Never sync `SECURITY/` folder
- Git-based sync only
- Conflict resolution: timestamp-based

---

## 🔒 SECURITY REQUIREMENTS

### All MCPs Must Implement

| Requirement | Implementation |
|-------------|----------------|
| **Rate Limiting** | Track counts per hour, reset hourly |
| **HITL Enforcement** | Check `action['hitl_approved']` before sensitive actions |
| **Audit Logging** | Call `self.audit_log()` after every execution |
| **Secret Isolation** | Load from `SECURITY/.env`, never log secrets |
| **Error Handling** | Catch exceptions, return `ExecutionResult(success=False, error=str(e))` |

### HITL Check Pattern

```python
def validate(self, action: dict) -> ValidationResult:
    # Check if HITL required
    if self._requires_hitl(action):
        if not action.get('hitl_approved'):
            return ValidationResult(
                success=False,
                error="HITL approval required. Move approval file to Approved/ folder."
            )
    
    # Check rate limit
    if self._rate_limit_exceeded():
        return ValidationResult(
            success=False,
            error=f"Rate limit exceeded: {self.rate_limit}/hour"
        )
    
    return ValidationResult(success=True)
```

---

## 🛠️ IMPLEMENTATION GUIDE

### Build Order

1. **First:** `base_mcp.py` (foundation)
2. **Bronze:** `state_mcp.py` + `email_mcp.py`
3. **Silver:** `browser_mcp.py` + `whatsapp_mcp.py`
4. **Gold:** `odoo_mcp.py` + `social_mcp.py`
5. **Platinum:** `sync_mcp.py`

### Implementation Steps for Each MCP

1. **Create file** in `mcp_servers/`
2. **Inherit from BaseMCP**
3. **Implement `__init__`** - Set rate limits, initialize clients
4. **Implement `validate()`** - Add validation rules
5. **Implement `execute()`** - Add actual functionality
6. **Override `_requires_hitl()`** - Add HITL logic
7. **Test** - Use testing pattern below

---

## 🧪 TESTING PATTERN

### Test Each MCP

```python
def test_email_mcp():
    """Test EmailMCP"""
    mcp = EmailMCP("/path/to/vault")
    
    # Test validation
    action = {
        "to": "test@example.com",
        "subject": "Test",
        "body": "Test body"
    }
    result = mcp.validate(action)
    assert result.success
    
    # Test execution (dry run)
    result = mcp.execute(action)
    assert result.success or result.error
    
    # Test audit log
    log = mcp.audit_log(action, result)
    assert "timestamp" in log
    assert "mcp" in log
    assert log["mcp"] == "EmailMCP"

def test_state_mcp():
    """Test StateMCP"""
    mcp = StateMCP("/path/to/vault")
    
    # Test read
    action = {"action": "read_file", "path": "test.txt"}
    result = mcp.validate(action)
    assert result.success
    
    # Test write (atomic)
    action = {
        "action": "write_file",
        "path": "test.txt",
        "content": "test",
        "atomic": True
    }
    result = mcp.validate(action)
    assert result.success
    
    # Test protected folder
    action = {
        "action": "write_file",
        "path": "SECURITY/secret.txt",
        "content": "test",
        "atomic": True
    }
    result = mcp.validate(action)
    assert not result.success
    assert "SECURITY" in result.error
```

---

## 📚 REFERENCES

- [Architecture Document](ARCHITECTURE.md#mcp-server-specifications)
- [Constitution](CONSTITUTION.md#section-41-bronze-tier-mvp)
- [Agents Guide](AGENTS.md#mcp-server-usage-guide)

---

**Ready to implement MCP framework?** 🚀
