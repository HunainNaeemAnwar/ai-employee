"""
Path constants for AI Employee system.

All file system paths are defined here for easy maintenance.
"""

import os
from pathlib import Path


class Paths:
    """Centralized path management."""
    
    # Base directories
    BASE_DIR = Path(__file__).parent.parent
    VAULT_DIR = BASE_DIR / "AI_Employee_Vault"
    
    # Vault subdirectories
    INPUT_QUEUES = VAULT_DIR / "INPUT_QUEUES"
    PROCESSING = VAULT_DIR / "PROCESSING"
    OUTPUT = VAULT_DIR / "OUTPUT"
    KNOWLEDGE = VAULT_DIR / "KNOWLEDGE"
    SECURITY = VAULT_DIR / "SECURITY"
    SYSTEM = VAULT_DIR / "SYSTEM"
    
    # Processing folders
    PENDING = PROCESSING / "Pending"
    IN_PROGRESS = PROCESSING / "In_Progress"
    PENDING_APPROVAL = PROCESSING / "Pending_Approval"
    APPROVED = PROCESSING / "Approved"
    REJECTED = PROCESSING / "Rejected"
    FAILED = PROCESSING / "Failed"
    
    # Output folders
    COMPLETED = OUTPUT / "Completed"
    REPORTS = OUTPUT / "Reports"
    ARCHIVE = OUTPUT / "Archive"
    
    # System folders
    STATE_DIR = SYSTEM / "state"
    CONFIG_DIR = SYSTEM / "config"
    LOGS_DIR = SYSTEM / "logs"
    AUDIT_LOGS = SECURITY / "audit_logs"
    
    # Key files
    STATE_FILE = STATE_DIR / "current_task.json"
    HISTORY_FILE = STATE_DIR / "task_history.jsonl"
    DASHBOARD = VAULT_DIR / "Dashboard.md"
    HANDBOOK = VAULT_DIR / "Company_Handbook.md"
    GOALS = VAULT_DIR / "Business_Goals.md"
    
    # Security files
    ENV_FILE = SECURITY / ".env"
    GMAIL_TOKEN = SECURITY / "gmail_token.json"
    GMAIL_CREDENTIALS = SECURITY / "credentials.json"
    
    # Qwen skills
    SKILLS_DIR = BASE_DIR / ".qwen" / "skills"
    
    # Test files
    TEST_FILES_DIR = BASE_DIR / "test_files"
    
    @classmethod
    def ensure_directories(cls):
        """Create all necessary directories if they don't exist."""
        dirs = [
            cls.INPUT_QUEUES / "Gmail",
            cls.INPUT_QUEUES / "WhatsApp",
            cls.INPUT_QUEUES / "Banking",
            cls.INPUT_QUEUES / "Files",
            cls.PENDING,
            cls.IN_PROGRESS,
            cls.PENDING_APPROVAL,
            cls.APPROVED,
            cls.REJECTED,
            cls.FAILED,
            cls.COMPLETED / "approvals",
            cls.REPORTS,
            cls.ARCHIVE,
            cls.STATE_DIR,
            cls.CONFIG_DIR,
            cls.LOGS_DIR,
            cls.AUDIT_LOGS,
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_input_queue(cls, source: str) -> Path:
        """Get input queue folder for a source."""
        return cls.INPUT_QUEUES / source.capitalize()
    
    @classmethod
    def get_approval_file(cls, approval_id: str) -> Path:
        """Get path to approval file."""
        return cls.PENDING_APPROVAL / f"APPROVAL_{approval_id}.md"
    
    @classmethod
    def get_audit_log(cls, date: str = None) -> Path:
        """Get path to audit log file."""
        from datetime import datetime
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return cls.AUDIT_LOGS / f"{date}.jsonl"
