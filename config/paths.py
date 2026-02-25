"""
Path constants for AI Employee system.

All file system paths are defined here for easy maintenance.
Aligned with Hackathon Specification folder names.
"""

import os
from pathlib import Path


class Paths:
    """Centralized path management."""

    # Base directories
    BASE_DIR = Path(__file__).parent.parent
    VAULT_DIR = BASE_DIR / "AI_Employee_Vault"

    # Vault subdirectories (Hackathon Standard Names)
    INBOX = VAULT_DIR / "Inbox"
    NEEDS_ACTION = VAULT_DIR / "Needs_Action"
    PLANS = VAULT_DIR / "Plans"
    DONE = VAULT_DIR / "Done"
    PENDING_APPROVAL = VAULT_DIR / "Pending_Approval"
    APPROVED = VAULT_DIR / "Approved"
    REJECTED = VAULT_DIR / "Rejected"
    LOGS = VAULT_DIR / "Logs"
    KNOWLEDGE = VAULT_DIR / "Knowledge"
    ACCOUNTING = VAULT_DIR / "Accounting"

    # Inbox subfolders (for different sources)
    INBOX_GMAIL = INBOX / "Gmail"
    INBOX_WHATSAPP = INBOX / "WhatsApp"
    INBOX_BANKING = INBOX / "Banking"
    INBOX_FILES = INBOX / "Files"

    # Processing folders
    PENDING = NEEDS_ACTION
    IN_PROGRESS = VAULT_DIR / "In_Progress"
    FAILED = VAULT_DIR / "Failed"

    # Output folders
    COMPLETED = DONE
    REPORTS = VAULT_DIR / "Reports"
    ARCHIVE = VAULT_DIR / "Archive"

    # System folders (internal use - hidden)
    STATE_DIR = VAULT_DIR / ".system" / "state"
    CONFIG_DIR = VAULT_DIR / ".system" / "config"

    # Key files
    STATE_FILE = STATE_DIR / "current_task.json"
    HISTORY_FILE = STATE_DIR / "task_history.jsonl"
    DASHBOARD = VAULT_DIR / "Dashboard.md"
    HANDBOOK = VAULT_DIR / "Company_Handbook.md"
    GOALS = VAULT_DIR / "Business_Goals.md"

    # Security files (in .env, never committed)
    ENV_FILE = BASE_DIR / ".env"

    # Qwen skills
    SKILLS_DIR = BASE_DIR / ".qwen" / "skills"

    # Test files
    TEST_FILES_DIR = BASE_DIR / "test_files"

    @classmethod
    def ensure_directories(cls):
        """Create all necessary directories if they don't exist."""
        dirs = [
            cls.INBOX_GMAIL,
            cls.INBOX_WHATSAPP,
            cls.INBOX_BANKING,
            cls.INBOX_FILES,
            cls.PENDING,
            cls.IN_PROGRESS,
            cls.PENDING_APPROVAL,
            cls.APPROVED,
            cls.REJECTED,
            cls.FAILED,
            cls.COMPLETED,
            cls.REPORTS,
            cls.ARCHIVE,
            cls.STATE_DIR,
            cls.CONFIG_DIR,
            cls.LOGS,
            cls.ACCOUNTING,
            cls.KNOWLEDGE / "Contexts",
            cls.KNOWLEDGE / "Procedures",
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_input_queue(cls, source: str) -> Path:
        """Get inbox folder for a source."""
        source_map = {
            "gmail": cls.INBOX_GMAIL,
            "whatsapp": cls.INBOX_WHATSAPP,
            "banking": cls.INBOX_BANKING,
            "files": cls.INBOX_FILES,
        }
        return source_map.get(source.lower(), cls.INBOX_FILES)

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
        return cls.LOGS / f"{date}.jsonl"
