"""
CLI commands for AI Employee.
"""

import os
import sys
import time
import signal
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from config.paths import Paths
from core.state import StateManager
from agents.ralph import RalphLoop
from mcp_servers.email_mcp import EmailMCP
from watchers.gmail import GmailWatcher


def run_command(command: str, vault_path: str):
    """Run CLI command."""
    if command == 'start':
        cmd_start(vault_path)
    elif command == 'status':
        cmd_status(vault_path)
    elif command == 'stop':
        cmd_stop()
    elif command == 'test':
        cmd_test(vault_path)
    elif command == 'help':
        cmd_help()


def cmd_start(vault_path: str):
    """Start the orchestrator."""
    print("🚀 Starting AI Employee Orchestrator...")
    print(f"📂 Vault: {vault_path}")
    print("=" * 50)
    
    settings = Settings()
    paths = Paths()
    paths.ensure_directories()
    
    state_manager = StateManager(vault_path)
    ralph_loop = RalphLoop(vault_path)
    email_mcp = EmailMCP(vault_path)
    gmail_watcher = GmailWatcher(vault_path)
    
    # Authenticate Gmail
    if gmail_watcher.authenticate():
        print("✅ Gmail Watcher authenticated")
    else:
        print("⚠️ Gmail Watcher running in test mode")
    
    # Main loop
    print("\n🔄 Main loop started (checking every 10 seconds)")
    print("Press Ctrl+C to stop\n")
    
    running = True
    last_gmail_poll = 0
    gmail_poll_interval = settings.gmail_poll_interval
    
    def signal_handler(sig, frame):
        nonlocal running
        print("\n🛑 Shutting down...")
        running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    
    while running:
        try:
            # Poll Gmail every 2 minutes
            current_time = time.time()
            if current_time - last_gmail_poll >= gmail_poll_interval:
                print("\n📧 Polling Gmail...")
                emails = gmail_watcher.check_for_new_items()
                print(f"📬 Found {len(emails)} new emails")
                
                for email in emails:
                    gmail_watcher.create_action_file(email)
                
                last_gmail_poll = current_time
            
            # Check approved tasks
            _check_approved_tasks(state_manager, email_mcp, vault_path)
            
            # Check pending tasks
            _process_pending_tasks(state_manager, ralph_loop, email_mcp, vault_path)
            
        except Exception as e:
            print(f"⚠️ Error in main loop: {e}")
        
        time.sleep(10)
    
    print("\n✅ Orchestrator stopped")


def _check_approved_tasks(state_manager, email_mcp, vault_path: str):
    """Check for approved tasks and execute emails."""
    approved_folder = Path(vault_path) / "Approved"

    if not approved_folder.exists():
        return

    for filepath in approved_folder.glob("*.md"):
        if filepath.name.startswith('APPROVAL_'):
            _process_markdown_approval(filepath, state_manager, email_mcp, vault_path)


def _process_markdown_approval(filepath, state_manager, email_mcp, vault_path: str):
    """Process markdown approval file."""
    from utils.files import read_file
    from pathlib import Path
    import shutil
    
    content = read_file(str(filepath))
    
    # Parse approval data
    import re
    task_id_match = re.search(r'task_id:\s*(\S+)', content)
    draft_match = re.search(r'## Draft Content\s*```\s*([\s\S]*?)```', content)
    from_match = re.search(r'From:\s*([^\n]+)', content)
    subject_match = re.search(r'Subject:\s*([^\n]+)', content)
    
    # Try to extract email_id from approval file
    email_id_match = re.search(r'email_id:\s*(\S+)', content)
    
    if not task_id_match or not draft_match:
        print(f"⚠️ Invalid approval file: {filepath.name}")
        return
    
    task_id = task_id_match.group(1)
    draft_content = draft_match.group(1).strip()
    email_id = email_id_match.group(1) if email_id_match else None
    
    # Extract recipient - look for email pattern in "From:" line
    recipient = ''
    if from_match:
        from_line = from_match.group(1)
        # Try to extract email from "Name <email@domain.com>" format
        import re
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        email_matches = re.findall(email_pattern, from_line)
        if email_matches:
            recipient = email_matches[0]
        else:
            recipient = from_line
    
    subject = subject_match.group(1).strip() if subject_match else 'Re: Your Email'
    
    # Clean recipient
    recipient = recipient.replace(' ', '').replace('*', '')  # Remove spaces and markdown
    
    # Expanded no-reply/marketing address patterns
    no_reply_patterns = [
        'no-reply', 'noreply', 'donotreply', 'do-not-reply',
        'mailer-daemon', 'mailer', 'delivery-status',
        'bounce', 'postmaster', 'abuse',
        'newsletter', 'notifications', 'updates',
        'noreply-', 'no_reply', 'donotreply'
    ]
    
    marketing_domain_patterns = [
        '@mail.', '@newsletter.', '@notifications.',
        'mail.replit.com', 'notifications.github.com',
        'amazonses.com', 'sendgrid.net', 'mailchimp.com'
    ]
    
    # Check if it's a no-reply or marketing address
    is_no_reply = any(p in recipient.lower() for p in no_reply_patterns)
    is_marketing = any(p in recipient.lower() for p in marketing_domain_patterns)
    
    if is_no_reply or is_marketing:
        address_type = "no-reply" if is_no_reply else "marketing"
        print(f"\n⚠️ Skipping {address_type} address: {recipient}")
        # Mark original as read if we have email_id
        if email_id:
            try:
                email_mcp.mark_as_read(email_id)
                print(f"   ✅ Marked original email as read")
            except Exception as e:
                print(f"   ⚠️ Could not mark as read: {e}")
        # Move to completed (can't reply to these addresses)
        completed_folder = Path(vault_path) / "Done" / "approvals"
        completed_folder.mkdir(parents=True, exist_ok=True)
        filepath.rename(completed_folder / filepath.name)
        print(f"   📁 Moved to: Done/approvals/ ({address_type})")
        return
    
    if not subject.lower().startswith('re:'):
        subject = f"Re: {subject}"
    
    # Move file to processing folder first (prevent re-processing)
    processing_folder = Path(vault_path) / "PROCESSING" / "Sending"
    processing_folder.mkdir(parents=True, exist_ok=True)
    temp_filepath = processing_folder / filepath.name
    shutil.move(str(filepath), str(temp_filepath))
    
    print(f"\n✅ Found approval: {filepath.name}")
    print(f"📧 Executing email send...")
    print(f"   To: {recipient}")
    print(f"   Subject: {subject}")
    
    try:
        success = email_mcp.send_email(
            to=recipient,
            subject=subject,
            body=draft_content,
            in_reply_to=email_id
        )
        
        if success:
            print(f"✅ Email sent successfully")
            # Mark original email as read
            if email_id:
                try:
                    email_mcp.mark_as_read(email_id)
                    print(f"   ✅ Marked original email as read (ID: {email_id})")
                except Exception as e:
                    print(f"   ⚠️ Could not mark as read: {e}")
            # Move to completed
            completed_folder = Path(vault_path) / "Done" / "approvals"
            completed_folder.mkdir(parents=True, exist_ok=True)
            temp_filepath.rename(completed_folder / temp_filepath.name)
            print(f"   📁 Moved to: Done/approvals/")
        else:
            print(f"❌ Email send failed")
            # Move to failed
            failed_folder = Path(vault_path) / "Failed"
            failed_folder.mkdir(parents=True, exist_ok=True)
            temp_filepath.rename(failed_folder / temp_filepath.name)
            print(f"   📁 Moved to: Failed/")
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        # Move to failed
        failed_folder = Path(vault_path) / "Failed"
        failed_folder.mkdir(parents=True, exist_ok=True)
        temp_filepath.rename(failed_folder / temp_filepath.name)
        print(f"   📁 Moved to: Failed/")


def _process_pending_tasks(state_manager, ralph_loop, email_mcp, vault_path: str):
    """Process pending tasks."""
    from pathlib import Path
    from utils.files import write_atomic
    import uuid
    from datetime import datetime
    
    task = state_manager.claim_next_pending()

    if not task:
        return

    print(f"\n📋 Processing task: {task.id} (type: {task.type})")
    
    # Auto-skip promotional and no-reply emails (no approval needed)
    no_reply_patterns = ['no-reply', 'noreply', 'donotreply', 'newsletter', 'notifications', 'updates']
    is_no_reply = any(p in task.sender.lower() for p in no_reply_patterns)
    is_promotional = task.type == 'promotional'
    
    if is_no_reply or is_promotional:
        print(f"   ⏭️ Auto-skipped (type: {task.type}, sender: {task.sender})")
        # Mark email as read
        email_id = task.data.get('email_id')
        if email_id:
            try:
                email_mcp.mark_as_read(email_id)
                print(f"   ✅ Marked email as read")
            except Exception as e:
                print(f"   ⚠️ Could not mark as read: {e}")
        
        # Move directly from Needs_Action to Done (auto-skipped emails are not claimed)
        needs_action_path = Path(vault_path) / "Needs_Action" / f"{task.id}.json"
        done_path = Path(vault_path) / "Done" / f"{task.id}.json"
        
        if needs_action_path.exists():
            needs_action_path.rename(done_path)
            print(f"   📁 Moved to: Done/ (auto-skipped)")
        else:
            # Fallback: use state_manager if file was already claimed
            state_manager.complete_task(task.id, f"Auto-skipped ({task.type})")
            print(f"   📁 Moved to: Done/ (auto-skipped)")
        
        return
    
    # Mark email as read when claimed (user has seen it by moving to Pending/)
    email_id = task.data.get('email_id')
    if email_id:
        try:
            email_mcp.mark_as_read(email_id)
            print(f"   ✅ Marked email as read (ID: {email_id})")
        except Exception as e:
            print(f"   ⚠️ Could not mark as read: {e}")
    
    print("🧠 Running Ralph Loop...")

    result = ralph_loop.run(task)

    if result.success:
        print(f"✅ Ralph Loop completed in {result.iterations} iterations")

        # Extract draft from Qwen output
        draft_content = _extract_draft_from_output(result.output)

        if draft_content:
            print(f"📝 Draft created ({len(draft_content)} chars)")
            
            # Create Plan.md file
            try:
                plan_file = ralph_loop.create_plan_file(task, draft_content)
                print(f"📋 Plan created: {plan_file.name}")
            except Exception as e:
                print(f"⚠️ Could not create Plan.md: {e}")

            # Create approval request
            approval_id = _create_approval_request(
                task=task,
                draft_content=draft_content,
                vault_path=vault_path
            )
            print(f"📋 Approval created: APPROVAL_{approval_id}.md")
            print(f"   Move to Approved/ to send")
        else:
            # No draft - task might be categorization only
            print(f"⚠️ No draft created - task may be categorization only")
            state_manager.complete_task(task.id, "Categorized")

    elif result.error:
        print(f"❌ Ralph Loop failed: {result.error}")
        state_manager.fail_task(task.id, result.error)


def _extract_draft_from_output(output: str) -> str:
    """Extract draft email from Qwen output."""
    import re
    
    draft = ""
    
    # Try multiple patterns
    
    # Pattern 1: ## DRAFT EMAIL with code blocks
    pattern = r'## DRAFT EMAIL\s*```\s*([\s\S]*?)```'
    match = re.search(pattern, output, re.IGNORECASE)
    if match:
        draft = match.group(1).strip()
    
    # Pattern 2: Content between --- markers (Qwen's default format)
    if not draft:
        pattern = r'---\s*\n([\s\S]*?)\n\s*---'
        match = re.search(pattern, output)
        if match:
            draft = match.group(1).strip()
    
    # Pattern 3: **Draft Email Response:** followed by content
    if not draft:
        pattern = r'\*\*Draft Email Response:\*\*\s*[-–—]+\s*([\s\S]*?)(?:\n\n|\n---|\Z)'
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            draft = match.group(1).strip()
    
    # Pattern 4: Look for content between "To:" and signature
    if not draft:
        pattern = r'\*\*To:\*\*.*?\n([\s\S]*?)(?:Best regards|Regards|Thanks|Sincerely)'
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            draft = match.group(0).strip()
    
    # Clean up the draft
    if draft:
        # Remove header lines like "**DRAFT EMAIL RESPONSE**"
        draft = re.sub(r'^\*\*DRAFT EMAIL RESPONSE\*\*\s*\n', '', draft, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove metadata lines (**To:**, **From:**, **Subject:**)
        draft = re.sub(r'^\*\*(To|From|Subject):\*\*.*?\n', '', draft, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove lines that are just markdown headers (not part of email body)
        lines = draft.split('\n')
        clean_lines = []
        for line in lines:
            # Skip lines that are all-caps headers (except actual email content)
            if line.strip().isupper() and len(line.strip()) < 50 and not line.strip().startswith('Dear') and not line.strip().startswith('Hi') and not line.strip().startswith('Hello'):
                continue
            # Skip lines that are just "**" or markdown artifacts
            if line.strip() in ['**', '---', '***']:
                continue
            clean_lines.append(line)
        
        draft = '\n'.join(clean_lines)
        
        # Remove leading empty lines
        draft = draft.lstrip('\n')
    
    return draft


def _create_approval_request(task, draft_content: str, vault_path: str) -> str:
    """Create approval request file."""
    from pathlib import Path
    from utils.files import write_atomic
    import uuid
    from datetime import datetime

    approval_id = str(uuid.uuid4())
    approval_folder = Path(vault_path) / "Pending_Approval"
    approval_folder.mkdir(parents=True, exist_ok=True)

    approval_file = approval_folder / f"APPROVAL_{approval_id}.md"
    
    # Get email data
    sender = task.data.get('from', 'Unknown')
    subject = task.data.get('subject', 'No Subject')
    email_id = task.data.get('email_id', '')
    
    content = f"""---
approval_id: {approval_id}
task_id: {task.id}
email_id: {email_id}
created_at: {datetime.now().isoformat()}
action_type: email_reply
reason: Email reply requires human approval
status: pending
---

# Approval Request

## Action
Send email reply

## Draft Content
```
{draft_content}
```

## Context
- Source: {task.source}
- From: {sender}
- Subject: {subject}
- Priority: {task.priority}

## Instructions
Move this file to:
- `../Approved/` to execute the action (send email)
- `../Rejected/` to discard

---
**DO NOT EDIT THIS FILE** - Only move to Approved/ or Rejected/
"""
    write_atomic(str(approval_file), content)
    
    return approval_id


def cmd_status(vault_path: str):
    """Show system status."""
    print("📊 AI Employee System Status")
    print("=" * 50)
    
    state_manager = StateManager(vault_path)
    counts = state_manager.get_queue_counts()
    
    print(f"\n📥 Task Queues:")
    print(f"  - Pending: {counts.get('pending', 0)}")
    print(f"  - In Progress: {counts.get('in_progress', 0)}")
    print(f"  - Pending Approval: {counts.get('pending_approval', 0)}")
    print(f"  - Completed: {counts.get('completed', 0)}")
    
    state = state_manager.get_state()
    print(f"\n🔄 Current State:")
    print(f"  - Task ID: {state.get('task_id', 'None')}")
    print(f"  - Status: {state.get('status', 'idle')}")


def cmd_stop():
    """Stop the orchestrator."""
    print("🛑 Stop command received. Press Ctrl+C in the running terminal.")


def cmd_test(vault_path: str):
    """List test files."""
    test_dir = Path(__file__).parent.parent / "test_files"
    
    if not test_dir.exists():
        print("⚠️ No test files found")
        return
    
    print("📧 Available test files:")
    for f in test_dir.glob("*.json"):
        print(f"  - {f.name}")


def cmd_help():
    """Show help."""
    print("""
AI Employee - Personal AI Assistant

Usage:
  ai-employee <command> [options]

Commands:
  start     Start the orchestrator
  status    Show system status
  stop      Stop the orchestrator
  test      List test files
  help      Show this help

Examples:
  ai-employee start
  ai-employee status
  ai-employee test
""")
