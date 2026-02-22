"""
Task models for AI Employee system.

Defines task structure and status enums.
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime


class TaskStatus(str, Enum):
    """Task status values."""
    NEW = "new"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    """Represents a task in the AI Employee system."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize task from dictionary."""
        self.id = data.get('id', '')
        self.source = data.get('source', 'unknown')
        self.type = data.get('type', 'unknown')
        self.priority = data.get('priority', 'low')
        self.status = TaskStatus(data.get('status', TaskStatus.PENDING.value))
        self.data = data.get('data', {})
        self.draft_content = data.get('draft_content', '')
        self.hitl_required = data.get('hitl_required', False)
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.claimed_at = data.get('claimed_at')
        self.completed_at = data.get('completed_at')
        self.raw_data = data
    
    @property
    def email_id(self) -> str:
        """Get email ID from task data."""
        return self.data.get('email_id', '')
    
    @property
    def sender(self) -> str:
        """Get sender email address."""
        return self.data.get('from', '')
    
    @property
    def subject(self) -> str:
        """Get email subject."""
        return self.data.get('subject', '')
    
    @property
    def recipient(self) -> str:
        """Get recipient email (for replies, this is the sender)."""
        recipient = self.data.get('from', '')
        # Clean up recipient
        if '<' in recipient:
            recipient = recipient.split('<')[1].split('>')[0].strip()
        # Remove spaces
        return recipient.replace(' ', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'source': self.source,
            'type': self.type,
            'priority': self.priority,
            'status': self.status.value,
            'data': self.data,
            'draft_content': self.draft_content,
            'hitl_required': self.hitl_required,
            'created_at': self.created_at,
            'claimed_at': self.claimed_at,
            'completed_at': self.completed_at,
        }
    
    def __repr__(self) -> str:
        return f"Task(id={self.id}, type={self.type}, status={self.status.value})"
