"""
Gmail Watcher for AI Employee.

Monitors Gmail for new unread emails every 2 minutes.
"""

import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from config.settings import Settings
from watchers.base import BaseWatcher


class GmailWatcher(BaseWatcher):
    """Gmail Watcher - polls Gmail API for new emails."""
    
    def __init__(self, vault_path: str = None, poll_interval: int = 120):
        """Initialize Gmail Watcher."""
        settings = Settings()
        vault = Path(vault_path) if vault_path else settings.vault_path
        
        super().__init__(
            vault_path=str(vault),
            queue_folder="INPUT_QUEUES/Gmail",
            poll_interval=poll_interval or settings.gmail_poll_interval
        )
        
        self.service = None
        self.seen_ids_file = vault / "SYSTEM" / "state" / "seen_email_ids.json"
        self.seen_ids = self._load_seen_ids()
    
    def _load_seen_ids(self) -> set:
        """Load seen email IDs from file."""
        try:
            if self.seen_ids_file.exists():
                with open(self.seen_ids_file, 'r') as f:
                    data = json.load(f)
                    seen = set(data.get('seen_ids', []))
                    print(f"📂 Loaded {len(seen)} seen email IDs")
                    return seen
        except Exception as e:
            print(f"⚠️ Could not load seen IDs: {e}")
        return set()
    
    def _save_seen_ids(self) -> None:
        """Save seen email IDs to file."""
        try:
            # Keep only last 1000 IDs to prevent file growing forever
            if len(self.seen_ids) > 1000:
                self.seen_ids = set(list(self.seen_ids)[-1000:])
            
            self.seen_ids_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.seen_ids_file, 'w') as f:
                json.dump({'seen_ids': list(self.seen_ids)}, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save seen IDs: {e}")
    
    def authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
        except ImportError:
            return False
        
        settings = Settings()
        token_file = self.vault_path / "SECURITY" / "gmail_token.json"
        
        if not token_file.exists():
            return False
        
        try:
            creds = Credentials.from_authorized_user_file(
                str(token_file), settings.gmail_scopes
            )
            
            if not creds.valid and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            
            if not creds.valid:
                return False
            
            self.service = build('gmail', 'v1', credentials=creds)
            return True
            
        except Exception:
            return False
    
    def check_for_new_items(self) -> List[Dict[str, Any]]:
        """Check Gmail for new unread messages."""
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            new_items = []
            
            for msg in messages:
                if msg['id'] not in self.seen_ids:
                    full_msg = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()

                    email_data = self._parse_email(full_msg)
                    new_items.append(email_data)
                    self.seen_ids.add(msg['id'])
                    
                    # Save seen_ids to persist across restarts
                    self._save_seen_ids()

                    # Log
                    self.logger.log_email_detected(
                        email_id=msg['id'],
                        from_addr=email_data.get('from', 'unknown'),
                        subject=email_data.get('subject', 'no subject')
                    )

            return new_items
            
        except Exception:
            return []
    
    def _parse_email(self, full_msg: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail API response."""
        payload = full_msg.get('payload', {})
        headers = payload.get('headers', [])
        
        email_data = {
            "email_id": full_msg.get('id'),
            "thread_id": full_msg.get('threadId'),
            "labels": full_msg.get('labelIds', []),
            "received_at": datetime.fromtimestamp(
                int(full_msg.get('internalDate', 0)) / 1000
            ).isoformat()
        }
        
        for header in headers:
            name = header.get('name', '').lower()
            value = header.get('value', '')
            
            if name == 'from':
                email_data['from'] = value
            elif name == 'to':
                email_data['to'] = value
            elif name == 'subject':
                email_data['subject'] = value
        
        email_data['body'] = self._extract_body(payload)
        email_data['has_attachments'] = any(
            part.get('filename') for part in payload.get('parts', [])
        )
        
        return email_data
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body."""
        if payload.get('mimeType', '').startswith('multipart'):
            for part in payload.get('parts', []):
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        body_data = payload.get('body', {})
        if 'data' in body_data:
            return base64.urlsafe_b64decode(body_data['data']).decode('utf-8', errors='ignore')
        
        return payload.get('snippet', '')
    
    def detect_type(self, email: Dict[str, Any]) -> str:
        """Detect email type."""
        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()
        labels = email.get('labels', [])
        
        if any(kw in subject or kw in body for kw in ['invoice', 'payment', 'bill']):
            return "invoice"
        if any(kw in subject or kw in body for kw in ['urgent', 'asap', 'deadline']):
            return "urgent"
        if 'CATEGORY_PROMOTIONS' in labels or 'unsubscribe' in body:
            return "promotional"
        
        return "general"
    
    def calculate_priority(self, email: Dict[str, Any]) -> str:
        """Calculate email priority."""
        score = 0
        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()
        labels = email.get('labels', [])
        
        if any(kw in subject or kw in body for kw in ['urgent', 'asap']):
            score += 20
        if 'IMPORTANT' in labels:
            score += 20
        if 'STARRED' in labels:
            score += 15
        
        if score >= 50:
            return "high"
        elif score >= 25:
            return "medium"
        return "low"
    
    def check_hitl_required(self, email: Dict[str, Any]) -> bool:
        """Check if HITL approval required."""
        from_addr = email.get('from', '')
        body = email.get('body', '')
        subject = email.get('subject', '').lower()
        
        # Unknown sender
        known_domains = ['knownclient.com', 'yourcompany.com']
        if not any(d in from_addr for d in known_domains):
            return True
        
        # Long body
        if len(body) > 1000:
            return True
        
        # Contains links
        if 'http://' in body or 'https://' in body:
            return True
        
        # Payment related
        if any(kw in subject for kw in ['invoice', 'payment', 'bill']):
            return True
        
        return False
