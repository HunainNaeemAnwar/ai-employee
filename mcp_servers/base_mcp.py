"""
Base MCP Server

Foundation class for all Model Context Protocol servers.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of action validation"""
    success: bool
    error: Optional[str] = None


@dataclass
class ExecutionResult:
    """Result of action execution"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None


class BaseMCP:
    """
    Base class for all MCP servers.
    
    Provides:
    - Rate limiting
    - Dry-run mode
    - Audit logging
    - HITL enforcement pattern
    """
    
    def __init__(self, vault_path: str, dry_run: bool = False):
        """
        Initialize base MCP.
        
        Args:
            vault_path: Path to AI_Employee_Vault
            dry_run: If True, log actions without executing
        """
        self.vault_path = vault_path
        self.dry_run = dry_run or os.getenv('DRY_RUN', 'false').lower() == 'true'
        self.rate_limit: Optional[int] = None
        self.rate_limit_count: int = 0
        self.rate_limit_reset: Optional[datetime] = None
    
    def validate(self, action: dict) -> ValidationResult:
        """
        Check if action can be executed.
        
        Override in subclass to implement:
        - Rate limit checks
        - HITL approval checks
        - Parameter validation
        
        Returns:
            ValidationResult(success=True) if valid
            ValidationResult(success=False, error="reason") if invalid
        """
        raise NotImplementedError
    
    def execute(self, action: dict) -> ExecutionResult:
        """
        Perform the action.
        
        Override in subclass to implement actual functionality.
        
        Returns:
            ExecutionResult(success=True, output="result")
            ExecutionResult(success=False, error="error")
        """
        raise NotImplementedError
    
    def audit_log(self, action: dict, result: ExecutionResult) -> dict:
        """
        Generate audit log entry.
        
        Called automatically after every execution.
        
        Returns:
            Dictionary with timestamp, MCP name, action, result
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "mcp": self.__class__.__name__,
            "action": action,
            "result": {
                "success": result.success,
                "output": result.output,
                "error": result.error
            }
        }
    
    def _rate_limit_exceeded(self) -> bool:
        """
        Check if rate limit exceeded.
        
        Returns:
            True if rate limit exceeded, False otherwise
        """
        if self.rate_limit is None:
            return False
        
        # Reset if hour passed
        now = datetime.now()
        if (self.rate_limit_reset and now > self.rate_limit_reset):
            self.rate_limit_count = 0
            self.rate_limit_reset = None
        
        # Check limit
        if self.rate_limit_count >= self.rate_limit:
            return True
        
        # Increment counter
        self.rate_limit_count += 1
        
        # Set reset time (1 hour from now)
        if not self.rate_limit_reset:
            self.rate_limit_reset = now + timedelta(hours=1)
        
        return False
    
    def _check_dry_run(self, action: str) -> bool:
        """
        Check if dry-run mode is enabled.
        
        Args:
            action: Name of action being executed
        
        Returns:
            True if dry-run mode, False otherwise
        """
        if self.dry_run:
            logger.info(f'[DRY RUN] Would execute: {action}')
            return True
        return False
    
    def _requires_hitl(self, action: dict) -> bool:
        """
        Check if action requires HITL approval.
        
        Override in subclass with MCP-specific logic.
        
        Args:
            action: Action dictionary
        
        Returns:
            True if HITL required, False otherwise
        """
        return False
    
    def check_hitl_approval(self, action: dict) -> ValidationResult:
        """
        Check if HITL approval has been granted.
        
        Args:
            action: Action dictionary
        
        Returns:
            ValidationResult with success/error
        """
        if self._requires_hitl(action):
            if not action.get('hitl_approved'):
                return ValidationResult(
                    success=False,
                    error="HITL approval required. Move approval file to Approved/ folder."
                )
        return ValidationResult(success=True)
