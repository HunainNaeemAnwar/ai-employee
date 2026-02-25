"""
State MCP Server

Provides read/write access to vault state files.
Bronze Tier Implementation.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import List

from .base_mcp import BaseMCP, ValidationResult, ExecutionResult


class StateMCP(BaseMCP):
    """
    State MCP for vault file operations.

    Actions:
    - read_file: Read any file in vault
    - write_file: Write file (atomic: temp + rename)
    - move_file: Move file between folders
    - list_directory: List files in folder

    Validation Rules:
    - Cannot write to Logs/ (protected - audit logs)
    - Cannot delete files (only move to Archive)
    - Must use atomic writes
    """
    
    def __init__(self, vault_path: str, dry_run: bool = False):
        """
        Initialize State MCP.
        
        Args:
            vault_path: Path to AI_Employee_Vault
            dry_run: If True, log actions without executing
        """
        super().__init__(vault_path, dry_run)
        self.vault_path = Path(vault_path)
    
    def validate(self, action: dict) -> ValidationResult:
        """
        Validate state action.
        
        Args:
            action: Action dictionary with 'action' and parameters
        
        Returns:
            ValidationResult with success/error
        """
        action_type = action.get('action')
        
        # Check required parameter
        if not action_type:
            return ValidationResult(
                success=False,
                error="Missing required parameter: 'action'"
            )
        
        # Check action type
        valid_actions = ['read_file', 'write_file', 'move_file', 'list_directory']
        if action_type not in valid_actions:
            return ValidationResult(
                success=False,
                error=f"Invalid action: {action_type}. Must be one of: {valid_actions}"
            )
        
        # Cannot write to Logs/ (protected - audit logs)
        path = action.get('path', '')
        if action_type in ['write_file', 'move_file'] and path.startswith('Logs/'):
            return ValidationResult(
                success=False,
                error="Cannot write to Logs/ folder (protected - audit logs)"
            )
        
        # Cannot delete files (only move to Archive)
        if action.get('action') == 'delete':
            return ValidationResult(
                success=False,
                error="Cannot delete files. Move to Archive/ instead."
            )
        
        # Must use atomic writes for write_file
        if action_type == 'write_file' and not action.get('atomic', False):
            return ValidationResult(
                success=False,
                error="Must use atomic writes (atomic=True)"
            )
        
        return ValidationResult(success=True)
    
    def execute(self, action: dict) -> ExecutionResult:
        """
        Execute state action.
        
        Args:
            action: Action dictionary
        
        Returns:
            ExecutionResult with success/output/error
        """
        try:
            # Check dry-run mode
            if self._check_dry_run(f"state:{action.get('action')}"):
                return ExecutionResult(
                    success=True,
                    output=f"[DRY RUN] Would execute: {action.get('action')}"
                )
            
            action_type = action.get('action')
            
            if action_type == 'read_file':
                return self._read_file(action)
            elif action_type == 'write_file':
                return self._write_file(action)
            elif action_type == 'move_file':
                return self._move_file(action)
            elif action_type == 'list_directory':
                return self._list_directory(action)
            else:
                return ExecutionResult(
                    success=False,
                    error=f"Unknown action: {action_type}"
                )
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e)
            )
    
    def _read_file(self, action: dict) -> ExecutionResult:
        """Read file content"""
        path = action.get('path')
        if not path:
            return ExecutionResult(
                success=False,
                error="Missing required parameter: 'path'"
            )
        
        full_path = self.vault_path / path
        if not full_path.exists():
            return ExecutionResult(
                success=False,
                error=f"File not found: {path}"
            )
        
        content = full_path.read_text(encoding='utf-8')
        return ExecutionResult(
            success=True,
            output=content
        )
    
    def _write_file(self, action: dict) -> ExecutionResult:
        """Write file atomically (temp file + rename)"""
        path = action.get('path')
        content = action.get('content')
        
        if not path:
            return ExecutionResult(
                success=False,
                error="Missing required parameter: 'path'"
            )
        
        if content is None:
            return ExecutionResult(
                success=False,
                error="Missing required parameter: 'content'"
            )
        
        full_path = self.vault_path / path
        
        # Create directory if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Atomic write: temp file + rename
        dir_path = full_path.parent
        fd, temp_path = tempfile.mkstemp(dir=str(dir_path), suffix='.tmp')
        
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
            os.rename(temp_path, str(full_path))
            
            return ExecutionResult(
                success=True,
                output=f"Written: {path}"
            )
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    
    def _move_file(self, action: dict) -> ExecutionResult:
        """Move file from src to dst"""
        src = action.get('src')
        dst = action.get('dst')
        
        if not src:
            return ExecutionResult(
                success=False,
                error="Missing required parameter: 'src'"
            )
        
        if not dst:
            return ExecutionResult(
                success=False,
                error="Missing required parameter: 'dst'"
            )
        
        src_path = self.vault_path / src
        dst_path = self.vault_path / dst
        
        if not src_path.exists():
            return ExecutionResult(
                success=False,
                error=f"Source file not found: {src}"
            )
        
        # Create destination directory if needed
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move file
        shutil.move(str(src_path), str(dst_path))
        
        return ExecutionResult(
            success=True,
            output=f"Moved: {src} → {dst}"
        )
    
    def _list_directory(self, action: dict) -> ExecutionResult:
        """List files in directory"""
        path = action.get('path', '.')
        full_path = self.vault_path / path
        
        if not full_path.exists():
            return ExecutionResult(
                success=False,
                error=f"Directory not found: {path}"
            )
        
        if not full_path.is_dir():
            return ExecutionResult(
                success=False,
                error=f"Not a directory: {path}"
            )
        
        files = [f.name for f in full_path.iterdir()]
        return ExecutionResult(
            success=True,
            output='\n'.join(files)
        )
