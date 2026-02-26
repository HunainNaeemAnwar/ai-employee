"""
Dashboard Manager

Updates Dashboard.md with real-time data from state files and logs.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from config.paths import Paths
from config.settings import Settings


class DashboardManager:
    """Manages Dashboard.md updates with real-time data."""

    def __init__(self, vault_path: str = None):
        """Initialize Dashboard Manager."""
        settings = Settings()
        self.vault_path = Path(vault_path) if vault_path else settings.vault_path
        self.paths = Paths()
        self.dashboard_file = self.paths.DASHBOARD

    def get_queue_counts(self) -> Dict[str, int]:
        """Get counts for all task queues with recursive counting."""
        counts = {}
        queue_folders = {
            "Inbox/Gmail": self.paths.INBOX_GMAIL,
            "Inbox/WhatsApp": self.paths.INBOX_WHATSAPP,
            "Inbox/Banking": self.paths.INBOX_BANKING,
            "Needs_Action": self.paths.NEEDS_ACTION,
            "In_Progress": self.paths.IN_PROGRESS,
            "Pending_Approval": self.paths.PENDING_APPROVAL,
            "Approved": self.paths.APPROVED,
            "Rejected": self.paths.REJECTED,
            "Done": self.paths.DONE,
            "Failed": self.paths.FAILED,
            "Plans": self.paths.PLANS,
        }

        for name, folder in queue_folders.items():
            if folder.exists():
                # Count JSON and MD files recursively
                json_count = len(list(folder.rglob("*.json")))
                md_count = len(list(folder.rglob("*.md")))
                counts[name] = json_count + md_count
            else:
                counts[name] = 0

        return counts

    def get_audit_stats(self) -> Dict[str, Any]:
        """Get today's audit log statistics."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.paths.LOGS / f"{today}.jsonl"

        stats = {
            "total_actions": 0,
            "by_actor": {},
            "by_result": {},
            "hitl_count": 0,
        }

        if not log_file.exists():
            return stats

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        stats["total_actions"] += 1

                        # Count by actor
                        actor = entry.get("actor", "unknown")
                        stats["by_actor"][actor] = stats["by_actor"].get(actor, 0) + 1

                        # Count by result
                        result = entry.get("result", "unknown")
                        stats["by_result"][result] = stats["by_result"].get(result, 0) + 1

                        # Count HITL
                        if entry.get("hitl"):
                            stats["hitl_count"] += 1
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass

        return stats

    def get_current_state(self) -> Dict[str, Any]:
        """Get current system state."""
        if not self.paths.STATE_FILE.exists():
            return {"status": "idle", "task_id": None}

        try:
            with open(self.paths.STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"status": "idle", "task_id": None}

    def get_system_health(self) -> Dict[str, Dict[str, str]]:
        """Get system component health status."""
        health = {
            "Gmail Watcher": {"status": "Unknown", "details": "Not running"},
            "Ralph Loop": {"status": "Unknown", "details": "Idle"},
            "Email MCP": {"status": "Unknown", "details": "Not initialized"},
            "Audit Logger": {"status": "Unknown", "details": "Not logging"},
            "State Manager": {"status": "Unknown", "details": "Not initialized"},
            "Plans Folder": {"status": "Unknown", "details": "Not checked"},
        }

        # Check Gmail token
        token_locations = [
            self.vault_path / ".system" / "gmail_token.json",
            self.vault_path / "SECURITY" / "gmail_token.json",
        ]
        token_found = False
        for location in token_locations:
            if location.exists():
                health["Gmail Watcher"] = {"status": "✔ Ready", "details": "Authenticated"}
                token_found = True
                break

        if not token_found:
            health["Gmail Watcher"] = {"status": "⚠️ Not Auth", "details": "Run gmail_auth.py"}

        # Check state file for Ralph Loop status
        state = self.get_current_state()
        if state.get("status") == "in_progress":
            iteration = state.get("iteration", 0)
            task_id = state.get("task_id", "unknown")
            health["Ralph Loop"] = {"status": "🟡 Working", "details": f"Iteration {iteration} on {task_id}"}
        elif state.get("status") == "idle":
            health["Ralph Loop"] = {"status": "✔ Idle", "details": "Ready for tasks"}
        else:
            health["Ralph Loop"] = {"status": "✔ Idle", "details": "No active task"}

        # Check if logs are being written
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.paths.LOGS / f"{today}.jsonl"
        if log_file.exists():
            try:
                log_size = log_file.stat().st_size
                health["Audit Logger"] = {"status": "✔ Active", "details": f"{log_size} bytes today"}
            except Exception:
                health["Audit Logger"] = {"status": "✔ Active", "details": f"Logging to {today}.jsonl"}

        # Email MCP status
        if health["Gmail Watcher"]["status"] == "✔ Ready":
            health["Email MCP"] = {"status": "✔ Ready", "details": "Gmail API"}
        else:
            health["Email MCP"] = {"status": "⚠️ Waiting", "details": "Needs Gmail auth"}

        # State Manager status
        if self.paths.STATE_FILE.exists():
            health["State Manager"] = {"status": "✔ Active", "details": "State file exists"}
        else:
            health["State Manager"] = {"status": "⚠️ Missing", "details": "No state file"}

        # Plans folder status
        if self.paths.PLANS.exists():
            plan_count = len(list(self.paths.PLANS.glob("*.md")))
            health["Plans Folder"] = {"status": "✔ Active", "details": f"{plan_count} plan files"}
        else:
            health["Plans Folder"] = {"status": "⚠️ Missing", "details": "Folder not found"}

        return health

    def generate_dashboard(self) -> str:
        """Generate Dashboard.md content with real-time data."""
        queue_counts = self.get_queue_counts()
        audit_stats = self.get_audit_stats()
        current_state = self.get_current_state()
        health = self.get_system_health()
        recent_activity = self._get_recent_activity()

        # Determine overall status
        if current_state.get("status") == "in_progress":
            overall_status = "🟡 Processing"
        elif queue_counts.get("Needs_Action", 0) > 0:
            overall_status = "🟡 Tasks Pending"
        else:
            overall_status = "🟢 Running"

        # Build actor breakdown
        actor_breakdown = ""
        if audit_stats["by_actor"]:
            for actor, count in sorted(audit_stats["by_actor"].items(), key=lambda x: x[1], reverse=True):
                actor_breakdown += f"- **{actor}**: {count}\n"
        else:
            actor_breakdown = "- *No actions recorded today*\n"

        # Build result breakdown
        result_breakdown = ""
        if audit_stats["by_result"]:
            for result, count in sorted(audit_stats["by_result"].items(), key=lambda x: x[1], reverse=True):
                result_breakdown += f"- **{result}**: {count}\n"
        else:
            result_breakdown = "- *No actions recorded today*\n"

        # Build health table
        health_rows = ""
        for component, info in health.items():
            status = info.get("status", "Unknown")
            details = info.get("details", "")
            health_rows += f"| **{component}** | {status} | {details} |\n"

        # Build pending actions list
        pending_actions = self._get_pending_actions()

        content = f"""# ✔ AI Employee Dashboard

**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Status:** {overall_status}

---

## ✔ Quick Status

| Metric | Value |
|--------|-------|
| **System Status** | {overall_status} |
| **Current Phase** | Bronze (Gmail MVP) |
| **Uptime** | Running since start |
| **Last Sync** | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} |

---

## 📥 Task Queue Status

| Folder | Count | Description |
| ------ | ----- | ----------- |
| **Inbox/Gmail/** | {queue_counts.get('Inbox/Gmail', 0)} | New emails to process |
| **Inbox/WhatsApp/** | {queue_counts.get('Inbox/WhatsApp', 0)} | WhatsApp messages |
| **Inbox/Banking/** | {queue_counts.get('Inbox/Banking', 0)} | Banking notifications |
| **Needs_Action/** | {queue_counts.get('Needs_Action', 0)} | Tasks waiting to be claimed |
| **In_Progress/** | {queue_counts.get('In_Progress', 0)} | Currently being worked on |
| **Pending_Approval/** | {queue_counts.get('Pending_Approval', 0)} | Awaiting human approval |
| **Approved/** | {queue_counts.get('Approved', 0)} | Approved, ready to execute |
| **Rejected/** | {queue_counts.get('Rejected', 0)} | Human-rejected tasks |
| **Done/** | {queue_counts.get('Done', 0)} | Completed tasks |
| **Failed/** | {queue_counts.get('Failed', 0)} | Failed tasks |
| **Plans/** | {queue_counts.get('Plans', 0)} | Execution plan files |

---

## ⚠️ Pending Actions

{pending_actions}

---

## ✔ Today's Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Total Actions | - | {audit_stats['total_actions']} |
| HITL Actions | - | {audit_stats['hitl_count']} |

**By Actor:**
{actor_breakdown}
**By Result:**
{result_breakdown}

---

## 📊 Recent Activity

{recent_activity}

---

## ✔ System Health

| Component | Status | Details |
|-----------|--------|---------|
{health_rows}

---

## ✔ Quick Commands

```bash
# Check status
python main.py status

# Start the system
python main.py start

# Stop the system
python main.py stop
```

---

## ✔ Manual Testing

```bash
# Process pending actions manually
python scripts/ralph_loop.py --vault {self.vault_path}

# Test email categorization
python scripts/test_email_categorization.py
```

---

**Next Scheduled Task:** Monday 7 AM CEO Briefing

---

*Dashboard auto-updates every 10 seconds when orchestrator is running*
"""
        return content

    def _get_pending_actions(self) -> str:
        """Get list of pending actions requiring attention."""
        actions = []

        # Check Pending_Approval folder
        if self.paths.PENDING_APPROVAL.exists():
            approvals = list(self.paths.PENDING_APPROVAL.glob("*.md"))
            for approval in approvals:
                if approval.name.startswith("APPROVAL_"):
                    actions.append(f"- ⚠️ **Approval Waiting:** `{approval.name}`")

        # Check high-priority tasks in Needs_Action
        if self.paths.NEEDS_ACTION.exists():
            for task_file in self.paths.NEEDS_ACTION.glob("*.json"):
                try:
                    with open(task_file, "r", encoding="utf-8") as f:
                        task = json.load(f)
                        if task.get("priority") == "high":
                            actions.append(f"- 🔴 **High Priority:** `{task_file.name}`")
                except Exception:
                    continue

        if not actions:
            return "*No pending actions requiring attention.*"

        return "\n".join(actions)

    def _get_recent_activity(self) -> str:
        """Get recent activity from audit log."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.paths.LOGS / f"{today}.jsonl"

        if not log_file.exists():
            return "*No activity recorded yet*"

        try:
            recent_entries = []
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Get last 10 entries
                for line in lines[-10:]:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        timestamp = entry.get("timestamp", "")[:19]  # Trim to YYYY-MM-DD HH:MM:SS
                        actor = entry.get("actor", "unknown")
                        action = entry.get("action", "unknown")
                        result = entry.get("result", "unknown")
                        recent_entries.append(f"- `{timestamp}` | **{actor}** | {action} → {result}")
                    except json.JSONDecodeError:
                        continue

            if not recent_entries:
                return "*No activity recorded yet*"

            return "\n".join(recent_entries)

        except Exception:
            return "*Unable to read activity log*"

    def update_dashboard(self) -> bool:
        """Update Dashboard.md with real-time data."""
        try:
            content = self.generate_dashboard()
            self.dashboard_file.write_text(content, encoding="utf-8")
            print(f"✅ Dashboard updated: {self.dashboard_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to update dashboard: {e}")
            return False


def update_dashboard(vault_path: str = None) -> bool:
    """Convenience function to update dashboard."""
    manager = DashboardManager(vault_path)
    return manager.update_dashboard()


if __name__ == "__main__":
    import sys

    vault = sys.argv[1] if len(sys.argv) > 1 else None
    success = update_dashboard(vault)
    sys.exit(0 if success else 1)
