#!/usr/bin/env python3
"""
Cleanup In_Progress Folder

Moves stuck tasks from In_Progress/ to appropriate folders based on their type.

Usage:
    python scripts/cleanup_in_progress.py [--vault PATH]
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.paths import Paths
from config.settings import Settings
from mcp_servers.email_mcp import EmailMCP


def cleanup_in_progress(vault_path: str = None):
    """Clean up stuck tasks in In_Progress folder."""
    settings = Settings()
    vault = Path(vault_path) if vault_path else settings.vault_path
    paths = Paths()
    
    in_progress_folder = vault / "In_Progress"
    done_folder = vault / "Done"
    
    if not in_progress_folder.exists():
        print("✅ In_Progress folder is empty")
        return
    
    # Get all JSON files
    files = list(in_progress_folder.glob("*.json"))
    
    if not files:
        print("✅ No tasks to clean up")
        return
    
    print(f"📁 Found {len(files)} tasks in In_Progress/\n")
    
    # Initialize email MCP for marking emails as read
    email_mcp = EmailMCP(str(vault))
    
    # Counters
    auto_skipped = 0
    moved_to_pending = 0
    errors = 0
    
    no_reply_patterns = ['no-reply', 'noreply', 'donotreply', 'newsletter', 'notifications', 'updates']
    
    for filepath in files:
        try:
            with open(filepath, 'r') as f:
                task = json.load(f)
            
            task_id = task.get('id', filepath.stem)
            task_type = task.get('type', 'unknown')
            sender = task.get('data', {}).get('from', '')
            email_id = task.get('data', {}).get('email_id', '')
            
            # Check if auto-skip (promotional or no-reply)
            is_no_reply = any(p in sender.lower() for p in no_reply_patterns)
            is_promotional = task_type == 'promotional'
            
            if is_no_reply or is_promotional:
                # Auto-skip: move to Done/
                print(f"⏭️  Auto-skip: {task_id} ({task_type})")
                
                # Mark email as read
                if email_id:
                    try:
                        email_mcp.mark_as_read(email_id)
                        print(f"   ✅ Marked email as read")
                    except Exception as e:
                        print(f"   ⚠️ Could not mark as read: {e}")
                
                # Move to Done/
                done_path = done_folder / filepath.name
                filepath.rename(done_path)
                print(f"   📁 Moved to: Done/")
                auto_skipped += 1
                
            else:
                # Needs processing: move back to Needs_Action/
                print(f"📋 Needs processing: {task_id} ({task_type})")
                needs_action_path = paths.NEEDS_ACTION / filepath.name
                filepath.rename(needs_action_path)
                print(f"   📁 Moved to: Needs_Action/")
                moved_to_pending += 1
                
        except Exception as e:
            print(f"❌ Error processing {filepath.name}: {e}")
            errors += 1
    
    print("\n" + "=" * 60)
    print("📊 Cleanup Summary")
    print("=" * 60)
    print(f"   Auto-skipped (Done/): {auto_skipped}")
    print(f"   Needs processing: {moved_to_pending}")
    print(f"   Errors: {errors}")
    print(f"   Total: {auto_skipped + moved_to_pending + errors}")
    print("=" * 60)
    
    if moved_to_pending > 0:
        print(f"\n💡 {moved_to_pending} tasks moved to Needs_Action/")
        print("   Run 'python main.py start' to process them")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cleanup stuck In_Progress tasks")
    parser.add_argument(
        '--vault',
        default=str(Path.home() / "personal_assistant" / "AI_Employee_Vault"),
        help='Path to AI_Employee_Vault'
    )
    
    args = parser.parse_args()
    cleanup_in_progress(args.vault)


if __name__ == "__main__":
    main()
