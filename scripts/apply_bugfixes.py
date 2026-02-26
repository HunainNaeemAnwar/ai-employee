#!/usr/bin/env python3
"""
Apply bugfix patches to cli/commands.py
"""

import re
from pathlib import Path

# Read the file
commands_file = Path("/home/hunain/personal_assistant/cli/commands.py")
content = commands_file.read_text()

# Fix 1: Add duplicate approval check after Ralph Loop
# Find the approval creation section and add check before it
old_approval_create = '''            # Create approval request
            approval_id = _create_approval_request(
                task=task,
                draft_content=draft_content,
                vault_path=vault_path
            )
            print(f"📋 Approval created: APPROVAL_{approval_id}.md")'''

new_approval_create = '''            # Check if approval already exists (prevent duplicates)
            approval_folder = Path(vault_path) / "Pending_Approval"
            existing_approvals = list(approval_folder.glob("*.md"))
            
            has_approval = False
            for ap in existing_approvals:
                try:
                    ap_content = ap.read_text()
                    if f"task_id: {task.id}" in ap_content:
                        has_approval = True
                        break
                except:
                    continue
            
            if has_approval:
                print(f"   ⚠️ Approval already exists, moving task to Done/")
                done_path = Path(vault_path) / "Done" / f"{task.id}.json"
                if in_progress_path.exists():
                    in_progress_path.rename(done_path)
                    print(f"   📁 Moved to: Done/ (approval exists)")
                return

            # Create approval request
            approval_id = _create_approval_request(
                task=task,
                draft_content=draft_content,
                vault_path=vault_path
            )
            print(f"📋 Approval created: APPROVAL_{approval_id}.md")'''

content = content.replace(old_approval_create, new_approval_create)

# Fix 2: Add file existence check at start of Ralph Loop result handling
old_ralph_success = '''    if result.success:
        print(f"✅ Ralph Loop completed in {result.iterations} iterations")'''

new_ralph_success = '''    # Check if file was already moved (by another process)
    if not in_progress_path.exists():
        print(f"   ⚠️ Task file already processed: {task.id}")
        return

    if result.success:
        print(f"✅ Ralph Loop completed in {result.iterations} iterations")'''

content = content.replace(old_ralph_success, new_ralph_success)

# Write the file
commands_file.write_text(content)
print("✅ Patches applied to cli/commands.py")

# Verify
print("\nVerifying patches...")
if "has_approval = False" in content:
    print("✅ Duplicate approval check added")
else:
    print("❌ Duplicate approval check NOT found")

if "Task file already processed" in content:
    print("✅ File existence check added")
else:
    print("❌ File existence check NOT found")
