#!/usr/bin/env python3
"""
Vault Folder Migration Script

Migrates vault folder structure from internal names to Hackathon Spec names.

BEFORE (Internal Names):
- INPUT_QUEUES/ → Inbox/
- PROCESSING/Pending/ → Needs_Action/
- OUTPUT/Completed/ → Done/
- SECURITY/audit_logs/ → Logs/
- KNOWLEDGE/ → Knowledge/
- SYSTEM/ → .system/

AFTER (Hackathon Spec Names):
- Inbox/
- Needs_Action/
- Plans/
- Done/
- Pending_Approval/
- Approved/
- Rejected/
- Logs/
- Knowledge/
- Accounting/ (new)
- .system/ (hidden)

Usage:
    python scripts/migrate_vault_folders.py [--vault AI_Employee_Vault]
"""

import os
import shutil
from pathlib import Path


def migrate_vault(vault_path: Path):
    """Migrate vault folder structure."""
    print(f"🔄 Starting vault migration: {vault_path}")
    print("=" * 60)
    
    # Step 1: Remove symlinks
    print("\n📋 Step 1: Removing symlinks...")
    symlinks = ["Inbox", "Needs_Action", "Plans", "Done", 
                "Pending_Approval", "Approved", "Rejected", "Logs"]
    for symlink in symlinks:
        path = vault_path / symlink
        if path.is_symlink():
            path.unlink()
            print(f"   ✅ Removed symlink: {symlink}")
        elif path.exists():
            print(f"   ⚠️  {symlink} is not a symlink, skipping")
        else:
            print(f"   ⚠️  {symlink} doesn't exist, skipping")
    
    # Step 2: Move INPUT_QUEUES → Inbox
    print("\n📋 Step 2: Moving INPUT_QUEUES → Inbox...")
    input_queues = vault_path / "INPUT_QUEUES"
    inbox = vault_path / "Inbox"
    if input_queues.exists() and not inbox.exists():
        input_queues.rename(inbox)
        print(f"   ✅ Renamed INPUT_QUEUES → Inbox")
    elif inbox.exists():
        print(f"   ✅ Inbox already exists")
    else:
        inbox.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created Inbox/")
    
    # Step 3: Move PROCESSING subfolders to root
    print("\n📋 Step 3: Moving PROCESSING folders to root...")
    processing = vault_path / "PROCESSING"
    if processing.exists():
        # Move subfolders
        for subfolder in ["Pending", "Plans", "Pending_Approval", "Approved", "Rejected", "In_Progress", "Failed"]:
            src = processing / subfolder
            if subfolder == "Pending":
                dst = vault_path / "Needs_Action"
            else:
                dst = vault_path / subfolder
            
            if src.exists() and not dst.exists():
                src.rename(dst)
                print(f"   ✅ Moved {subfolder} → {dst.name}")
            elif dst.exists():
                print(f"   ✅ {dst.name} already exists")
        
        # Remove PROCESSING if empty
        if not any(processing.iterdir()):
            processing.rmdir()
            print(f"   ✅ Removed empty PROCESSING/ folder")
    else:
        # Create folders if they don't exist
        for folder in ["Needs_Action", "Plans", "Pending_Approval", "Approved", "Rejected", "In_Progress", "Failed"]:
            (vault_path / folder).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created processing folders")
    
    # Step 4: Move OUTPUT subfolders to root
    print("\n📋 Step 4: Moving OUTPUT folders to root...")
    output = vault_path / "OUTPUT"
    if output.exists():
        # Move Completed → Done
        completed = output / "Completed"
        done = vault_path / "Done"
        if completed.exists() and not done.exists():
            completed.rename(done)
            print(f"   ✅ Moved Completed → Done")
        elif done.exists():
            print(f"   ✅ Done already exists")
        
        # Move Reports, Archive
        for subfolder in ["Reports", "Archive"]:
            src = output / subfolder
            dst = vault_path / subfolder
            if src.exists() and not dst.exists():
                src.rename(dst)
                print(f"   ✅ Moved {subfolder} → root")
            elif dst.exists():
                print(f"   ✅ {subfolder} already exists")
        
        # Remove OUTPUT if empty
        if not any(output.iterdir()):
            output.rmdir()
            print(f"   ✅ Removed empty OUTPUT/ folder")
    else:
        # Create folders if they don't exist
        for folder in ["Done", "Reports", "Archive"]:
            (vault_path / folder).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created output folders")
    
    # Step 5: Move SECURITY/audit_logs → Logs
    print("\n📋 Step 5: Moving SECURITY/audit_logs → Logs...")
    security = vault_path / "SECURITY"
    logs = vault_path / "Logs"
    if security.exists():
        audit_logs = security / "audit_logs"
        if audit_logs.exists() and not logs.exists():
            audit_logs.rename(logs)
            print(f"   ✅ Moved audit_logs → Logs")
        elif logs.exists():
            print(f"   ✅ Logs already exists")
        
        # Move .env to root
        env_file = security / ".env"
        if env_file.exists():
            env_file.rename(vault_path / ".env")
            print(f"   ✅ Moved .env to root")
        
        # Remove SECURITY if empty
        if not any(security.iterdir()):
            security.rmdir()
            print(f"   ✅ Removed empty SECURITY/ folder")
    else:
        logs.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created Logs/")
    
    # Step 6: Rename KNOWLEDGE → Knowledge
    print("\n📋 Step 6: Renaming KNOWLEDGE → Knowledge...")
    knowledge_old = vault_path / "KNOWLEDGE"
    knowledge_new = vault_path / "Knowledge"
    if knowledge_old.exists() and not knowledge_new.exists():
        knowledge_old.rename(knowledge_new)
        print(f"   ✅ Renamed KNOWLEDGE → Knowledge")
    elif knowledge_new.exists():
        print(f"   ✅ Knowledge already exists")
    else:
        knowledge_new.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created Knowledge/")
    
    # Step 7: Move SYSTEM → .system (hidden)
    print("\n📋 Step 7: Moving SYSTEM → .system (hidden)...")
    system_old = vault_path / "SYSTEM"
    system_new = vault_path / ".system"
    if system_old.exists() and not system_new.exists():
        system_old.rename(system_new)
        print(f"   ✅ Renamed SYSTEM → .system")
    elif system_new.exists():
        print(f"   ✅ .system already exists")
    else:
        system_new.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created .system/")
    
    # Step 8: Create Accounting/ folder (new)
    print("\n📋 Step 8: Creating Accounting/ folder...")
    accounting = vault_path / "Accounting"
    if not accounting.exists():
        accounting.mkdir(parents=True, exist_ok=True)
        (accounting / "Current_Month.md").write_text("# Current Month Transactions\n")
        print(f"   ✅ Created Accounting/ with Current_Month.md")
    else:
        print(f"   ✅ Accounting already exists")
    
    # Step 9: Create missing subfolders
    print("\n📋 Step 9: Creating missing subfolders...")
    subfolders = [
        inbox / "Gmail",
        inbox / "WhatsApp",
        inbox / "Banking",
        inbox / "Files",
        knowledge_new / "Contexts",
        knowledge_new / "Procedures",
    ]
    for folder in subfolders:
        folder.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ Created all subfolders")
    
    print("\n" + "=" * 60)
    print("✅ Vault migration completed!")
    print("=" * 60)
    
    # Show final structure
    print("\n📊 Final vault structure:")
    for item in sorted(vault_path.iterdir()):
        if item.is_dir():
            print(f"   📁 {item.name}/")
        else:
            print(f"   📄 {item.name}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migrate vault folder structure to Hackathon Spec"
    )
    parser.add_argument(
        "--vault",
        type=str,
        default="AI_Employee_Vault",
        help="Path to vault directory (default: AI_Employee_Vault)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault)
    
    if not vault_path.exists():
        print(f"❌ Vault not found: {vault_path}")
        print("   Please run this script from the project root directory.")
        return
    
    if args.dry_run:
        print(f"🔍 DRY RUN - No changes will be made")
        print(f"   Vault: {vault_path}")
        return
    
    # Backup recommendation
    print("⚠️  IMPORTANT: Before migrating, backup your vault!")
    print(f"   cp -r {vault_path} {vault_path}.backup")
    print()
    
    response = input("Continue with migration? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        return
    
    migrate_vault(vault_path)


if __name__ == "__main__":
    main()
