"""
Email MCP Server

Provides email sending capabilities via Gmail API.
Bronze Tier Implementation.
"""

import os
import base64
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

from .base_mcp import BaseMCP, ValidationResult, ExecutionResult


class EmailMCP(BaseMCP):
    """
    Email MCP for Gmail API operations.
    
    Actions:
    - send_email: Send email via Gmail API
    - draft_email: Create draft only
    - search_emails: Search inbox
    
    Rate Limit: 10 emails/hour
    HITL: Required for unknown recipients, payment-related, contains links
    """
    
    def __init__(self, vault_path: str, dry_run: bool = False):
        """
        Initialize Email MCP.
        
        Args:
            vault_path: Path to AI_Employee_Vault
            dry_run: If True, log actions without executing
        """
        super().__init__(vault_path, dry_run)
        self.rate_limit = 10  # 10 emails per hour
        self.vault_path = Path(vault_path)
        self.service: Optional[object] = None
    
    def validate(self, action: dict) -> ValidationResult:
        """
        Validate email action.
        
        Args:
            action: Action dictionary
        
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
        valid_actions = ['send_email', 'draft_email', 'search_emails']
        if action_type not in valid_actions:
            return ValidationResult(
                success=False,
                error=f"Invalid action: {action_type}. Must be one of: {valid_actions}"
            )
        
        # Check rate limit
        if action_type in ['send_email', 'draft_email']:
            if self._rate_limit_exceeded():
                return ValidationResult(
                    success=False,
                    error=f"Rate limit exceeded: {self.rate_limit}/hour"
                )
        
        # Check required parameters for send_email
        if action_type == 'send_email':
            if not action.get('to'):
                return ValidationResult(
                    success=False,
                    error="Missing required parameter: 'to'"
                )
            
            if not action.get('subject'):
                return ValidationResult(
                    success=False,
                    error="Missing required parameter: 'subject'"
                )
            
            # Check HITL requirements
            if self._requires_hitl(action):
                hitl_result = self.check_hitl_approval(action)
                if not hitl_result.success:
                    return hitl_result
        
        return ValidationResult(success=True)
    
    def execute(self, action: dict) -> ExecutionResult:
        """
        Execute email action.
        
        Args:
            action: Action dictionary
        
        Returns:
            ExecutionResult with success/output/error
        """
        try:
            # Check dry-run mode
            if self._check_dry_run(f"email:{action.get('action')}"):
                return ExecutionResult(
                    success=True,
                    output=f"[DRY RUN] Would execute: {action.get('action')}"
                )
            
            action_type = action.get('action')
            
            if action_type == 'send_email':
                return self._send_email(action)
            elif action_type == 'draft_email':
                return self._draft_email(action)
            elif action_type == 'search_emails':
                return self._search_emails(action)
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
    
    def _authenticate(self) -> bool:
        """
        Authenticate with Gmail API.
        
        Returns:
            True if authenticated, False otherwise
        """
        if self.service:
            return True
        
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            token_file = self.vault_path / "SECURITY" / "gmail_token.json"
            
            if not token_file.exists():
                return False
            
            creds = Credentials.from_authorized_user_file(str(token_file))
            
            # Refresh if needed
            if not creds.valid and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            
            if not creds.valid:
                return False
            
            self.service = build('gmail', 'v1', credentials=creds)
            return True
            
        except Exception:
            return False
    
    def _requires_hitl(self, action: dict) -> bool:
        """
        Check if HITL approval required.
        
        Args:
            action: Action dictionary
        
        Returns:
            True if HITL required, False otherwise
        """
        # Unknown recipient (not in clients.md)
        if not self._is_known_recipient(action.get('to', '')):
            return True
        
        # Payment-related
        subject = action.get('subject', '').lower()
        if any(kw in subject for kw in ['payment', 'invoice', 'bill', 'receipt']):
            return True
        
        # Contains links
        body = action.get('body', '')
        if 'http://' in body or 'https://' in body:
            return True
        
        return False
    
    def _is_known_recipient(self, email: str) -> bool:
        """
        Check if recipient is known client.
        
        Args:
            email: Recipient email address
        
        Returns:
            True if known, False otherwise
        """
        # Check clients.md
        clients_file = self.vault_path / "KNOWLEDGE" / "Contexts" / "clients.md"
        
        if not clients_file.exists():
            return False
        
        content = clients_file.read_text(encoding='utf-8')
        
        # Simple check - look for email domain in file
        if '@' in email:
            domain = email.split('@')[1]
            return domain in content
        
        return False
    
    def _send_email(self, action: dict) -> ExecutionResult:
        """Send email via Gmail API"""
        if not self._authenticate():
            return ExecutionResult(
                success=False,
                error="Gmail authentication failed. Run: python scripts/gmail_auth.py"
            )
        
        to = action['to']
        subject = action['subject']
        body = action.get('body', '')
        in_reply_to = action.get('in_reply_to')
        
        # Create message
        message = MIMEText(body)
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject
        
        if in_reply_to:
            message['In-Reply-To'] = in_reply_to
            message['References'] = in_reply_to
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send
        result = self.service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        message_id = result.get('id')
        
        return ExecutionResult(
            success=True,
            output=f"Email sent to {to}: {subject} (ID: {message_id})"
        )
    
    def _draft_email(self, action: dict) -> ExecutionResult:
        """Create email draft"""
        if not self._authenticate():
            return ExecutionResult(
                success=False,
                error="Gmail authentication failed"
            )
        
        to = action['to']
        subject = action['subject']
        body = action.get('body', '')
        
        # Create message
        message = MIMEText(body)
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Create draft
        result = self.service.users().drafts().create(
            userId='me',
            body={'message': {'raw': raw_message}}
        ).execute()
        
        draft_id = result.get('id')
        
        return ExecutionResult(
            success=True,
            output=f"Draft created: {to} - {subject} (ID: {draft_id})"
        )
    
    def _search_emails(self, action: dict) -> ExecutionResult:
        """Search inbox"""
        if not self._authenticate():
            return ExecutionResult(
                success=False,
                error="Gmail authentication failed"
            )
        
        query = action.get('q', 'is:unread')
        max_results = action.get('max_results', 10)
        
        # Search
        result = self.service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = result.get('messages', [])
        
        return ExecutionResult(
            success=True,
            output=f"Found {len(messages)} messages matching: {query}"
        )
