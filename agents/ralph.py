"""
Ralph Wiggum Loop executor.

Implements iterative AI execution pattern.
"""

import os
import subprocess
import hashlib
import time
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from config.settings import Settings
from config.paths import Paths
from utils.files import read_json, write_atomic, file_exists
from core.task import Task


class TaskResult:
    """Result of Ralph Loop execution."""
    
    def __init__(self, success: bool, output: str = "", 
                 iterations: int = 0, error: Optional[str] = None):
        self.success = success
        self.output = output
        self.iterations = iterations
        self.error = error


class RalphLoop:
    """Ralph Wiggum Loop executor."""
    
    # Defaults (overridden by Settings)
    DEFAULT_MAX_ITERATIONS = 5
    DEFAULT_NO_PROGRESS_THRESHOLD = 2
    DEFAULT_ITERATION_TIMEOUT = 60
    
    COMPLETION_SIGNALS = [
        "<status>TASK_COMPLETE</status>",
        "<promise>COMPLETE</promise>",
        "DONE",
        "TASK COMPLETE",
        "task complete",
        "Task complete",
        "## DRAFT EMAIL",
        "Draft Email",
        "draft email"
    ]
    
    def __init__(self, vault_path: str = None, qwen_cmd: str = "qwen"):
        """Initialize Ralph Loop."""
        settings = Settings()
        self.vault_path = Path(vault_path) if vault_path else settings.vault_path
        self.qwen_cmd = qwen_cmd
        self.paths = Paths()

        self.state_file = self.paths.STATE_FILE
        self.complete_flag = self.paths.STATE_DIR / "complete.flag"
        self.prompt_file = self.paths.STATE_DIR / "prompt.md"

        # Use settings (with class defaults as fallback)
        self.max_iterations = settings.max_iterations or self.DEFAULT_MAX_ITERATIONS
        self.ITERATION_TIMEOUT = settings.iteration_timeout or self.DEFAULT_ITERATION_TIMEOUT
        self.NO_PROGRESS_THRESHOLD = settings.no_progress_threshold or self.DEFAULT_NO_PROGRESS_THRESHOLD
    
    def run(self, task: Task) -> TaskResult:
        """Execute Ralph Loop until completion or failure."""
        import time
        
        iteration = 0
        no_progress_count = 0
        last_state_hash = self._hash_state_file()
        start_time = time.time()

        print(f"   ⏱️ Starting Ralph Loop (max {self.max_iterations} iterations, {self.ITERATION_TIMEOUT}s timeout)")
        
        # Debug: Check Qwen CLI
        import shutil
        qwen_path = shutil.which(self.qwen_cmd)
        print(f"   🔍 Qwen CLI path: {qwen_path}")
        if not qwen_path:
            print(f"   ❌ ERROR: Qwen CLI '{self.qwen_cmd}' not found in PATH")
            return TaskResult(
                success=False,
                error=f"Qwen CLI not found: {self.qwen_cmd}. Install with: npm install -g @anthropic/claude-code",
                iterations=0
            )

        while iteration < self.max_iterations:
            # Build prompt
            prompt_path = self._build_prompt(task, iteration)
            iter_start = time.time()
            iter_time = 0

            try:
                # Debug: Check prompt file
                print(f"   🔄 Iteration {iteration + 1}/{self.max_iterations}... ", end='', flush=True)
                print(f"(prompt: {prompt_path.name}, size: {prompt_path.stat().st_size if prompt_path.exists() else 0} bytes)")
                
                if not prompt_path.exists():
                    print(f"\n   ❌ ERROR: Prompt file not created: {prompt_path}")
                    iteration += 1
                    continue
                
                with open(prompt_path, 'r') as f:
                    prompt_content = f.read()
                
                # Debug: Show prompt preview
                print(f"\n   📝 Prompt size: {len(prompt_content)} chars")
                
                # Truncate prompt if too large (prevents Qwen hangs)
                max_prompt_size = 3000
                if len(prompt_content) > max_prompt_size:
                    print(f"   ⚠️ Truncating large prompt ({len(prompt_content)} → {max_prompt_size} chars)")
                    prompt_content = prompt_content[:max_prompt_size] + '\n\n[Content truncated for brevity]'
                
                if len(prompt_content) < 100:
                    print(f"   📝 Prompt content: {prompt_content[:200]}")
                else:
                    print(f"   📝 Prompt preview: {prompt_content[:100]}...[truncated]")
                
                # Warn if prompt is very large
                if len(prompt_content) > 2000:
                    print(f"   ⚠️ Large prompt ({len(prompt_content)} chars) may cause timeout")

                # Use qwen with positional prompt (non-interactive mode)
                # Add -y flag to auto-accept (skip interactive confirmations)
                # Add -o text for plain text output (easier to parse)
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        result = subprocess.run(
                            ["qwen", "-y", "-o", "text", prompt_content],  # Non-interactive mode
                            capture_output=True,
                            text=True,
                            timeout=120,  # 2 minutes per iteration (increased for slow responses)
                            cwd=str(self.vault_path)
                        )
                        break  # Success, exit retry loop
                    except subprocess.TimeoutExpired:
                        if attempt < max_retries - 1:
                            print(f"\n   ⏱️ Timeout on attempt {attempt + 1}, retrying...")
                            continue
                        else:
                            print(f"\n   ❌ Timeout after {max_retries} attempts")
                            raise
                
                # Debug: Show return code and stderr
                if result.returncode != 0:
                    print(f"\n   ❌ Qwen exited with code {result.returncode}")
                    if result.stderr:
                        print(f"   ❌ Qwen stderr: {result.stderr[:500]}")

                iter_time = time.time() - iter_start
                print(f" done ({iter_time:.1f}s)")

                # Debug: Show first part of Qwen's output
                if result.stdout:
                    print(f"   📝 Qwen output: {len(result.stdout)} chars")

                    # Show first 200 chars for debugging
                    if len(result.stdout) < 500:
                        print(f"   📄 Output preview: {result.stdout[:200]}...")
                    else:
                        print(f"   📄 Output preview: {result.stdout[:200]}...[truncated]")

                    # Check for ANY content as progress
                    if len(result.stdout.strip()) > 10:
                        no_progress_count = 0  # Any output = progress
                        last_state_hash = "has_output"  # Mark as changed

                    # Check completion signals (expanded patterns)
                    completion_found = False
                    for signal in self.COMPLETION_SIGNALS:
                        if signal in result.stdout:
                            completion_found = True
                            break
                    
                    # Also check for draft patterns
                    if not completion_found:
                        draft_patterns = [
                            '## DRAFT EMAIL',
                            '## EMAIL DRAFT',
                            'Draft Email',
                            'draft email',
                            'Dear ',
                            'Best regards',
                            'Sincerely',
                            'TASK_COMPLETE',
                            'task complete'
                        ]
                        for pattern in draft_patterns:
                            if pattern in result.stdout:
                                completion_found = True
                                print(f"   ✅ Found completion pattern: '{pattern}'")
                                break
                    
                    if completion_found:
                        draft = self._extract_draft(result.stdout)
                        if draft:
                            task.draft_content = draft
                        self._cleanup()
                        total_time = time.time() - start_time
                        print(f"   ✅ Ralph Loop completed in {total_time:.1f}s ({iteration + 1} iterations)")
                        return TaskResult(
                            success=True,
                            output=result.stdout,
                            iterations=iteration + 1
                        )
                    else:
                        print(f"   ⚠️ No completion signal found in output")
                
                # Check progress
                current_hash = self._hash_state_file()
                if current_hash == last_state_hash:
                    no_progress_count += 1
                    if no_progress_count >= self.NO_PROGRESS_THRESHOLD:
                        return TaskResult(
                            success=False,
                            error=f"No progress after {iteration + 1} iterations",
                            iterations=iteration + 1
                        )
                else:
                    no_progress_count = 0
                    last_state_hash = current_hash
                
                iteration += 1
                
            except subprocess.TimeoutExpired:
                total_time = time.time() - start_time
                print(f"   ❌ Timeout after {iter_time:.1f}s (total: {total_time:.1f}s)")
                return TaskResult(
                    success=False,
                    error=f"Qwen timeout ({self.ITERATION_TIMEOUT}s)",
                    iterations=iteration + 1
                )
            except FileNotFoundError:
                return TaskResult(
                    success=False,
                    error=f"Qwen CLI not found: {self.qwen_cmd}",
                    iterations=0
                )
            except Exception as e:
                total_time = time.time() - start_time
                print(f"   ❌ Error after {total_time:.1f}s: {e}")
                return TaskResult(
                    success=False,
                    error=str(e),
                    iterations=iteration + 1
                )

        total_time = time.time() - start_time
        print(f"   ⚠️ Max iterations ({self.max_iterations}) reached in {total_time:.1f}s")
        return TaskResult(
            success=False,
            error=f"Max iterations ({self.max_iterations}) reached",
            iterations=iteration
        )
    
    def _build_prompt(self, task: Task, iteration: int) -> Path:
        """Build prompt for Qwen iteration."""
        # Check if this is an email task (from Gmail Watcher)
        is_email_task = (
            task.type == 'email' or 
            'email' in task.source.lower() or
            'gmail' in task.source.lower()
        )
        
        if is_email_task:
            action_required = f"""
## EMAIL PROCESSING TASK

You are processing an email:
- From: {task.sender}
- Subject: {task.subject}
- Body: {task.data.get('body', '')[:500]}

**CRITICAL INSTRUCTIONS:**
- DO NOT try to move files or create files
- DO NOT try to update state files
- Your ONLY job is to OUTPUT A DRAFT REPLY

**Your task:** Write a professional 2-3 sentence reply.

**REQUIRED OUTPUT FORMAT:**
You MUST output the draft in this EXACT format:

## DRAFT EMAIL
```
Dear Sender,

[Your 2-3 sentence professional reply here]

Best regards,
AI Employee
```

<status>TASK_COMPLETE</status>
"""
        else:
            action_required = "Process the task"

        prompt = f"""# AI Employee - Iteration {iteration + 1}

## CURRENT STATE
- Task ID: {task.id}
- Type: {task.type}
- Priority: {task.priority}

## YOUR TASK
{action_required}

## IMPORTANT RULES
1. DO NOT move files or modify the filesystem
2. DO NOT update state files
3. ONLY output the draft email in the format shown above
4. End with <status>TASK_COMPLETE</status>

BEGIN ITERATION {iteration + 1}:
"""
        write_atomic(str(self.prompt_file), prompt)
        return self.prompt_file
    
    def _hash_state_file(self) -> str:
        """Hash state file to detect changes."""
        if not self.state_file.exists():
            return ""
        with open(self.state_file, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _extract_draft(self, output: str) -> Optional[str]:
        """
        Extract draft email from Qwen output.
        
        Handles multiple output formats including Qwen's actual output.
        """
        import re
        
        # Pattern 1: **Draft Email Response:** (Qwen's default format)
        pattern = r'\*\*Draft Email Response:\*\*\s*\n\s*```\s*([\s\S]*?)```'
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            draft = match.group(1).strip()
            # Remove any "To:" metadata lines
            draft = re.sub(r'^\*\*To:\*\*.*?\n', '', draft, flags=re.MULTILINE)
            if draft and len(draft) > 20:
                return draft
        
        # Pattern 2: **Draft:** (shorter version)
        pattern = r'\*\*Draft:\*\*\s*\n\s*```\s*([\s\S]*?)```'
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            draft = match.group(1).strip()
            if draft and len(draft) > 20:
                return draft
        
        # Pattern 3: Any code block after "draft" keyword (case insensitive)
        pattern = r'[Dd]raft[^`]*?\n\s*```\s*([\s\S]*?)```'
        match = re.search(pattern, output)
        if match:
            draft = match.group(1).strip()
            if draft and len(draft) > 20:
                return draft
        
        # Pattern 4: ## DRAFT EMAIL with code blocks
        pattern = r'## DRAFT EMAIL\s*```\s*([\s\S]*?)```'
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Pattern 5: ## EMAIL DRAFT
        pattern = r'## EMAIL DRAFT\s*```\s*([\s\S]*?)```'
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Pattern 6: Content between --- markers
        pattern = r'---\s*\n([\s\S]*?)\n\s*---'
        match = re.search(pattern, output)
        if match:
            draft = match.group(1).strip()
            # Remove metadata lines
            draft = re.sub(r'^\*\*(To|From|Subject):\*\*.*?\n', '', draft, flags=re.MULTILINE)
            if draft and len(draft) > 20:
                return draft
        
        # Pattern 7: Look for email content (starts with Dear/Salutation)
        pattern = r'(Dear\s+\w+[,\.]?\s*\n[\s\S]*?)(?:Best regards|Regards|Sincerely|Thanks|Best)[\s\S]*$'
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Pattern 8: If output contains email-like content, extract it
        if any(kw in output.lower() for kw in ['dear ', 'best regards', 'sincerely']):
            # Clean up the output
            lines = output.split('\n')
            email_lines = []
            in_email = False
            for line in lines:
                if 'dear ' in line.lower() or in_email:
                    in_email = True
                    email_lines.append(line)
                if 'best regards' in line.lower() or 'sincerely' in line.lower():
                    email_lines.append(line)
                    break

            if email_lines:
                return '\n'.join(email_lines).strip()

        # Pattern 9: Extract any professional reply mentioned in output
        if 'reply' in output.lower() and 'professional' in output.lower():
            # Look for quoted content
            pattern = r'```\s*\n([\s\S]*?)\n\s*```'
            match = re.search(pattern, output)
            if match:
                draft = match.group(1).strip()
                if len(draft) > 20 and ('dear' in draft.lower() or 'regards' in draft.lower()):
                    return draft

        return None
    
    def create_plan_file(self, task: 'Task', draft: str) -> 'Path':
        """
        Create Plan.md file to track progress.
        
        Args:
            task: Task being processed
            draft: Draft content from Qwen
        
        Returns:
            Path to created Plan.md file
        """
        from pathlib import Path
        
        plans_folder = Path(self.vault_path) / "PROCESSING" / "Plans"
        plans_folder.mkdir(parents=True, exist_ok=True)
        
        plan_file = plans_folder / f"PLAN_{task.id}.md"
        
        content = f"""---
task_id: {task.id}
created: {datetime.now().isoformat()}
status: pending_approval
objective: Process {task.type} from {task.sender}
---

## Objective
Process {task.type} email from {task.sender}

## Steps
- [x] Read email
- [x] Categorize email
- [x] Draft reply
- [ ] Send email (requires approval)
- [ ] Log transaction

## Approval Required
Email send requires human approval. See Pending_Approval/

## Draft Content
```
{draft[:500]}{'...' if len(draft) > 500 else ''}
```

## Notes
Draft created by Ralph Loop in {task.iteration if hasattr(task, 'iteration') else 1} iterations
"""
        write_atomic(str(plan_file), content)
        return plan_file
    
    def _cleanup(self) -> None:
        """Clean up temporary files."""
        if self.prompt_file.exists():
            self.prompt_file.unlink()
        if self.complete_flag.exists():
            self.complete_flag.unlink()
