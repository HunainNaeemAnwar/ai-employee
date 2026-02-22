"""
Unit tests for core module.
"""

import pytest
import json
from pathlib import Path
from core.task import Task, TaskStatus
from core.state import StateManager


class TestTask:
    """Test Task class."""
    
    def test_task_init(self):
        """Test Task initialization."""
        data = {
            "id": "test_001",
            "source": "GmailWatcher",
            "type": "email",
            "priority": "high",
            "data": {"from": "test@example.com"}
        }
        
        task = Task(data)
        
        assert task.id == "test_001"
        assert task.source == "GmailWatcher"
        assert task.priority == "high"
        assert task.status == TaskStatus.PENDING
    
    def test_task_email_properties(self):
        """Test Task email property extraction."""
        data = {
            "id": "email_001",
            "data": {
                "from": "john@example.com",
                "subject": "Test Email",
                "email_id": "msg_123"
            }
        }
        
        task = Task(data)
        
        assert task.sender == "john@example.com"
        assert task.subject == "Test Email"
        assert task.email_id == "msg_123"
    
    def test_task_to_dict(self):
        """Test Task to_dict conversion."""
        data = {"id": "test_001", "type": "email"}
        task = Task(data)
        
        result = task.to_dict()
        
        assert result["id"] == "test_001"
        assert result["type"] == "email"
        assert "status" in result


class TestStateManager:
    """Test StateManager class."""
    
    def test_state_manager_init(self):
        """Test StateManager initialization."""
        sm = StateManager()
        
        assert sm.vault_path is not None
        assert sm.state_file.exists()
    
    def test_get_queue_counts(self):
        """Test get_queue_counts returns correct structure."""
        sm = StateManager()
        counts = sm.get_queue_counts()
        
        assert "pending" in counts
        assert "in_progress" in counts
        assert "completed" in counts
        assert isinstance(counts["pending"], int)
    
    def test_get_state(self):
        """Test get_state returns dictionary."""
        sm = StateManager()
        state = sm.get_state()
        
        assert isinstance(state, dict)
        assert "status" in state or len(state) == 0
