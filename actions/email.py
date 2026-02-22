"""
Email MCP (Model Context Protocol) server.

Provides email actions: send, mark as read, label.
"""

import os
import base64
from email.mime.text import MIMEText
from typing import Optional
from pathlib import Path

from config.settings import Settings
from utils.logger import AuditLogger


class EmailMCP:
    """Email MCP server for Gmail API."""
    
    def __init__(self, vault_path: str = None):
        """Initialize Email MCP."""
        settings = Settings()
        self.vault_path = Path(vault_path) if vault_path else settings.vault_path
        self.logger = AuditLogger(str(self.vault_path))
        self.service = None
        self._authenticated = False
    
    def authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
        except ImportError:
            return False

        token_file = self.vault_path / "SECURITY" / "gmail_token.json"

        if not token_file.exists():
            return False

        try:
            # Load credentials (don't pass scopes - use scopes from token)
            creds = Credentials.from_authorized_user_file(str(token_file))

            # Refresh if needed
            if not creds.valid and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                print('🔄 Refreshing expired token...')
                creds.refresh(Request())

            if not creds.valid:
                print('⚠️  Credentials not valid after refresh')
                return False

            self.service = build('gmail', 'v1', credentials=creds)
            self._authenticated = True

            return True

        except Exception as e:
            print(f'⚠️  Authentication error: {e}')
            return False
    
    def send_email(self, to: str, subject: str, body: str,
                   in_reply_to: Optional[str] = None) -> bool:
        """Send email via Gmail API."""
        if not self._authenticated:
            if not self.authenticate():
                return False
        
        try:
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['from'] = 'me'
            message['subject'] = subject
            
            if in_reply_to:
                message['In-Reply-To'] = in_reply_to
                message['References'] = in_reply_to
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            # Log
            self.logger.log_email_sent(
                task_id=in_reply_to or 'unknown',
                to=to,
                subject=subject
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def mark_as_read(self, email_id: str) -> bool:
        """Mark email as read."""
        if not self._authenticated:
            if not self.authenticate():
                return False
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to mark as read: {e}")
            return False
    
    def label_email(self, email_id: str, label: str) -> bool:
        """Add label to email."""
        if not self._authenticated:
            if not self.authenticate():
                return False
        
        try:
            # Find or create label
            label_id = self._get_or_create_label(label)
            
            if label_id:
                self.service.users().messages().modify(
                    userId='me',
                    id=email_id,
                    body={'addLabelIds': [label_id]}
                ).execute()
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to label email: {e}")
            return False
    
    def _get_or_create_label(self, label: str) -> Optional[str]:
        """Get or create Gmail label."""
        try:
            # Find existing
            results = self.service.users().labels().list(userId='me').execute()
            for lbl in results.get('labels', []):
                if lbl['name'].lower() == label.lower():
                    return lbl['id']
            
            # Create new
            new_label = self.service.users().labels().create(
                userId='me',
                body={'name': label}
            ).execute()
            return new_label['id']
            
        except Exception:
            return None
