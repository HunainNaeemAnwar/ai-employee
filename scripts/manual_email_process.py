#!/usr/bin/env python3
"""
Manual Email Processor

Manually move emails from Inbox/ to Needs_Action/ for processing.

Usage:
    python scripts/manual_email_process.py --email-id <gmail_email_id>
    python scripts/manual_email_process.py --list    # List emails in Inbox
    python scripts/manual_email_process.py --all     # Move all emails to Needs_Action
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from config.paths import Paths


def list_inbox_emails(vault_path: Path):
    """List all emails in Inbox/Gmail/"""
    inbox_folder = vault_path / "Inbox" / "Gmail"
    
    if not inbox_folder.exists():
        print("📭 Inbox/Gmail/ folder is empty or doesn't exist")
        return []
    
    files = list(inbox_folder.glob("*.json"))
    
    if not files:
        print("📭 No emails in Inbox/Gmail/")
        return []
    
    print(f"📬 Found {len(files)} email(s) in Inbox/Gmail/:")
    print("=" * 60)
    
    emails = []
    for file in sorted(files):
        data = json.loads(file.read_text())
        email_id = data.get('id', 'unknown')
        email_type = data.get('type', 'unknown')
        priority = data.get('priority', 'unknown')
        sender = data.get('data', {}).get('from', 'unknown')
        subject = data.get('data', {}).get('subject', 'no subject')
        
        print(f"\n📧 {email_id}")
        print(f"   Type: {email_type} | Priority: {priority}")
        print(f"   From: {sender}")
        print(f"   Subject: {subject}")
        print(f"   File: {file.name}")
        
        emails.append({
            'id': email_id,
            'file': file,
            'data': data
        })
    
    print("=" * 60)
    return emails


def move_email_to_needs_action(email_file: Path, vault_path: Path):
    """Move a single email from Inbox to Needs_Action"""
    needs_action_folder = vault_path / "Needs_Action"
    needs_action_folder.mkdir(parents=True, exist_ok=True)
    
    # Read email data
    data = json.loads(email_file.read_text())
    
    # Update status
    data['status'] = 'pending'
    data['moved_at'] = datetime.now().isoformat()
    
    # Generate new filename
    new_filename = f"task_{datetime.now():%Y%m%d_%H%M%S}_{data.get('id', 'unknown')[:8]}.json"
    new_file = needs_action_folder / new_filename
    
    # Write to Needs_Action
    with open(new_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Remove from Inbox
    email_file.unlink()
    
    print(f"✅ Moved to Needs_Action/: {new_filename}")
    return new_file


def move_all_emails(vault_path: Path):
    """Move all emails from Inbox to Needs_Action"""
    inbox_folder = vault_path / "Inbox" / "Gmail"
    
    if not inbox_folder.exists():
        print("📭 Inbox/Gmail/ folder doesn't exist")
        return 0
    
    files = list(inbox_folder.glob("*.json"))
    
    if not files:
        print("📭 No emails to move")
        return 0
    
    print(f"🔄 Moving {len(files)} email(s) to Needs_Action/...")
    print("=" * 60)
    
    moved = 0
    for file in files:
        move_email_to_needs_action(file, vault_path)
        moved += 1
    
    print("=" * 60)
    print(f"✅ Moved {moved} email(s)")
    return moved


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manually process emails from Inbox"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List emails in Inbox/Gmail/"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Move all emails to Needs_Action/"
    )
    parser.add_argument(
        "--email-id",
        type=str,
        help="Move specific email by ID"
    )
    parser.add_argument(
        "--vault",
        type=str,
        default=None,
        help="Path to vault (default: from settings)"
    )
    
    args = parser.parse_args()
    
    settings = Settings()
    vault_path = Path(args.vault) if args.vault else settings.vault_path
    
    if args.list:
        list_inbox_emails(vault_path)
    
    elif args.all:
        move_all_emails(vault_path)
    
    elif args.email_id:
        inbox_folder = vault_path / "Inbox" / "Gmail"
        
        # Find email by ID
        found = False
        for file in inbox_folder.glob("*.json"):
            data = json.loads(file.read_text())
            if data.get('id') == args.email_id:
                print(f"📧 Found email: {args.email_id}")
                move_email_to_needs_action(file, vault_path)
                found = True
                break
        
        if not found:
            print(f"❌ Email not found: {args.email_id}")
            print("   Run with --list to see available emails")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
