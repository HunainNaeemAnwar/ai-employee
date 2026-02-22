"""
State management for AI Employee system.

Handles task lifecycle, state persistence, and approval workflow.
"""

import os
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from config.paths import Paths
from config.settings import Settings
from utils.files import read_json, write_json, write_atomic
from utils.logger import AuditLogger
from core.task import Task, TaskStatus


class StateManager:
    """Manages task state and lifecycle."""
    
    def __init__(self, vault_path: str = None):
        """Initialize state manager."""
        settings = Settings()
        self.vault_path = Path(vault_path) if vault_path else settings.vault_path
        self.logger = AuditLogger(str(self.vault_path))
        
        # Initialize paths
        self.paths = Paths()
        self.paths.ensure_directories()
        
        # State file
        self.state_file = self.paths.STATE_FILE
    
    def claim_next_pending(self) -> Optional[Task]:
        """Claim the highest priority pending task."""
        pending_folder = self.paths.PENDING
        
        if not pending_folder.exists():
            return None
        
        # Get all pending tasks
        tasks = []
        for filename in pending_folder.glob("*.json"):
            try:
                data = read_json(str(filename))
                tasks.append((Task(data), filename))
            except Exception:
                continue
        
        if not tasks:
            return None
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        tasks.sort(key=lambda x: priority_order.get(x[0].priority, 3))
        
        # Claim first task
        task, filepath = tasks[0]
        return self._claim_task(task, filepath)
    
    def _claim_task(self, task: Task, filepath: Path) -> Task:
        """Move task from Pending to In_Progress."""
        # Atomic move
        in_progress_path = self.paths.IN_PROGRESS / filepath.name
        shutil.move(str(filepath), str(in_progress_path))
        
        # Update task
        task.status = TaskStatus.IN_PROGRESS
        task.claimed_at = datetime.now().isoformat()
        
        # Update state
        self._update_current_state(task)
        
        # Log
        self.logger.log_task_claimed(task.id, task.type)
        
        return task
    
    def _update_current_state(self, task: Task) -> None:
        """Update SYSTEM/state/current_task.json."""
        state = {
            "task_id": task.id,
            "status": task.status.value,
            "iteration": 0,
            "last_iteration_at": None,
            "claimed_at": task.claimed_at,
            "context": {
                "last_action": None,
                "next_step": "start_ralph_loop",
                "notes": f"Processing {task.type} task"
            },
            "history": []
        }
        write_json(str(self.state_file), state)
    
    def update_state(self, task_id: str, iteration: int = None,
                     last_action: str = None, next_step: str = None) -> None:
        """Update current task state."""
        if not self.state_file.exists():
            return
        
        state = read_json(str(self.state_file))
        
        if iteration is not None:
            state["iteration"] = iteration
        if last_action is not None:
            state["context"]["last_action"] = last_action
        if next_step is not None:
            state["context"]["next_step"] = next_step
        
        state["last_iteration_at"] = datetime.now().isoformat()
        write_json(str(self.state_file), state)
    
    def complete_task(self, task_id: str, result: str) -> None:
        """Move task to OUTPUT/Completed/."""
        task = self._find_task_in_progress(task_id)
        
        if not task:
            return
        
        # Update task
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()
        
        # Move to completed
        in_progress_path = self.paths.IN_PROGRESS / f"{task_id}.json"
        completed_path = self.paths.COMPLETED / f"{task_id}.json"
        
        if in_progress_path.exists():
            shutil.move(str(in_progress_path), str(completed_path))
        
        # Append to history
        self._append_history(task.to_dict())
        
        # Log
        self.logger.log_task_completed(task_id, result)
        
        # Reset state
        self._reset_state()
    
    def fail_task(self, task_id: str, error: str) -> None:
        """Move task to PROCESSING/Failed/."""
        task = self._find_task_in_progress(task_id)
        
        if not task:
            return
        
        # Update task
        task.status = TaskStatus.FAILED
        
        # Move to failed
        in_progress_path = self.paths.IN_PROGRESS / f"{task_id}.json"
        failed_path = self.paths.FAILED / f"{task_id}.json"
        
        if in_progress_path.exists():
            shutil.move(str(in_progress_path), str(failed_path))
        
        # Append to history
        self._append_history(task.to_dict())
        
        # Log
        self.logger.log_task_failed(task_id, error)
        
        # Reset state
        self._reset_state()
    
    def _find_task_in_progress(self, task_id: str) -> Optional[Task]:
        """Find task in In_Progress folder."""
        filepath = self.paths.IN_PROGRESS / f"{task_id}.json"
        
        if filepath.exists():
            data = read_json(str(filepath))
            return Task(data)
        
        return None
    
    def request_approval(self, task: Task, reason: str) -> str:
        """Create approval request in PROCESSING/Pending_Approval/."""
        approval_id = str(uuid.uuid4())
        approval_file = self.paths.PENDING_APPROVAL / f"APPROVAL_{approval_id}.md"
        
        content = f"""---
approval_id: {approval_id}
task_id: {task.id}
created_at: {datetime.now().isoformat()}
action_type: email_reply
reason: {reason}
status: pending
---

# Approval Request

## Action
Send email reply

## Draft Content
```
{task.draft_content if task.draft_content else 'No draft content'}
```

## Context
- Source: {task.source}
- From: {task.sender}
- Subject: {task.subject}
- Priority: {task.priority}

## Instructions
Move this file to:
- `../Approved/` to execute the action
- `../Rejected/` to discard

---
**DO NOT EDIT THIS FILE** - Only move to Approved/ or Rejected/
"""
        write_atomic(str(approval_file), content)
        
        # Log
        self.logger.log_approval_requested(task.id, approval_id, reason)
        
        return approval_id
    
    def _append_history(self, task_data: Dict[str, Any]) -> None:
        """Append task to history log."""
        with open(self.paths.HISTORY_FILE, "a", encoding='utf-8') as f:
            f.write(json.dumps(task_data) + "\n")
    
    def _reset_state(self) -> None:
        """Reset current state to idle."""
        state = {
            "task_id": None,
            "status": "idle",
            "iteration": 0,
            "last_iteration_at": None,
            "claimed_at": None,
            "context": {
                "last_action": None,
                "next_step": "claim_next_pending_task",
                "notes": "System ready, waiting for tasks"
            },
            "history": []
        }
        write_json(str(self.state_file), state)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state."""
        if not self.state_file.exists():
            return {}
        return read_json(str(self.state_file))
    
    def get_queue_counts(self) -> Dict[str, int]:
        """Get counts for all queues."""
        return {
            "pending": len(list(self.paths.PENDING.glob("*.json"))),
            "in_progress": len(list(self.paths.IN_PROGRESS.glob("*.json"))),
            "pending_approval": len(list(self.paths.PENDING_APPROVAL.glob("*.md"))),
            "approved": len(list(self.paths.APPROVED.glob("*.md"))),
            "rejected": len(list(self.paths.REJECTED.glob("*.md"))),
            "completed": len(list(self.paths.COMPLETED.glob("*.json"))),
            "failed": len(list(self.paths.FAILED.glob("*.json")))
        }
