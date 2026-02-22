"""
Audit Logger Module

Provides tamper-evident logging for all AI actions.
Logs are stored in JSONL format (one JSON per line) per day.
"""

import json
import os
from datetime import datetime
from typing import Any, Optional
from .files import write_atomic


class AuditLogger:
    """
    Audit logger for AI Employee system.
    
    Logs are stored in SECURITY/audit_logs/YYYY-MM-DD.jsonl
    Each log entry is a single JSON line with timestamp, actor, action, result.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize audit logger.
        
        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vault_path = vault_path
        self.logs_dir = os.path.join(vault_path, "SECURITY/audit_logs")
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def _get_log_file(self) -> str:
        """Get today's log file path."""
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.logs_dir, f"{today}.jsonl")
    
    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        return datetime.now().isoformat()
    
    def log(
        self,
        action: str,
        actor: str,
        result: str,
        task_id: Optional[str] = None,
        details: Optional[dict] = None,
        hitl: bool = False
    ) -> None:
        """
        Log an action to the audit trail.
        
        Args:
            action: What action was taken (e.g., "email_sent", "task_completed")
            actor: Who took the action (e.g., "GmailWatcher", "EmailMCP", "Human")
            result: Outcome of the action (e.g., "success", "failed", "pending_approval")
            task_id: Optional task identifier
            details: Optional additional details (will be JSON serialized)
            hitl: Whether this action required human-in-the-loop approval
        """
        log_entry = {
            "timestamp": self._get_timestamp(),
            "action": action,
            "actor": actor,
            "result": result,
            "hitl": hitl
        }
        
        if task_id:
            log_entry["task_id"] = task_id
        
        if details:
            log_entry["details"] = details
        
        # Append to log file (atomic write)
        log_file = self._get_log_file()
        log_line = json.dumps(log_entry) + "\n"
        
        # Read existing content (if any) and append
        existing = ""
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                existing = f.read()
        
        # Write atomically
        write_atomic(log_file, existing + log_line)
    
    def log_task_claimed(self, task_id: str, task_type: str) -> None:
        """Log that a task was claimed for processing."""
        self.log(
            action="task_claimed",
            actor="Orchestrator",
            result="success",
            task_id=task_id,
            details={"task_type": task_type}
        )
    
    def log_task_completed(self, task_id: str, result: str) -> None:
        """Log that a task was completed."""
        self.log(
            action="task_completed",
            actor="Orchestrator",
            result="success",
            task_id=task_id,
            details={"outcome": result}
        )
    
    def log_task_failed(self, task_id: str, error: str) -> None:
        """Log that a task failed."""
        self.log(
            action="task_failed",
            actor="Orchestrator",
            result="failed",
            task_id=task_id,
            details={"error": error}
        )
    
    def log_approval_requested(self, task_id: str, approval_id: str, reason: str) -> None:
        """Log that human approval was requested."""
        self.log(
            action="approval_requested",
            actor="Orchestrator",
            result="pending_approval",
            task_id=task_id,
            details={"approval_id": approval_id, "reason": reason},
            hitl=True
        )
    
    def log_approval_granted(self, task_id: str, approval_id: str) -> None:
        """Log that human approval was granted."""
        self.log(
            action="approval_granted",
            actor="Human",
            result="approved",
            task_id=task_id,
            details={"approval_id": approval_id},
            hitl=True
        )
    
    def log_approval_rejected(self, task_id: str, approval_id: str) -> None:
        """Log that human approval was rejected."""
        self.log(
            action="approval_rejected",
            actor="Human",
            result="rejected",
            task_id=task_id,
            details={"approval_id": approval_id},
            hitl=True
        )
    
    def log_email_sent(self, task_id: str, to: str, subject: str) -> None:
        """Log that an email was sent."""
        self.log(
            action="email_sent",
            actor="EmailMCP",
            result="success",
            task_id=task_id,
            details={"to": to, "subject": subject}
        )
    
    def log_email_detected(self, email_id: str, from_addr: str, subject: str) -> None:
        """Log that a new email was detected."""
        self.log(
            action="email_detected",
            actor="GmailWatcher",
            result="success",
            task_id=email_id,
            details={"from": from_addr, "subject": subject}
        )
    
    def get_today_logs(self) -> list:
        """
        Get all log entries for today.
        
        Returns:
            List of log entry dictionaries
        """
        log_file = self._get_log_file()
        if not os.path.exists(log_file):
            return []
        
        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    logs.append(json.loads(line))
        
        return logs
    
    def get_stats(self) -> dict:
        """
        Get statistics for today's logs.
        
        Returns:
            Dictionary with counts by action type
        """
        logs = self.get_today_logs()
        
        stats = {
            "total_actions": len(logs),
            "by_actor": {},
            "by_result": {},
            "hitl_count": 0
        }
        
        for log in logs:
            # Count by actor
            actor = log.get("actor", "unknown")
            stats["by_actor"][actor] = stats["by_actor"].get(actor, 0) + 1
            
            # Count by result
            result = log.get("result", "unknown")
            stats["by_result"][result] = stats["by_result"].get(result, 0) + 1
            
            # Count HITL actions
            if log.get("hitl"):
                stats["hitl_count"] += 1
        
        return stats
