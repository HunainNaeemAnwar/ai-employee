"""
Watchers package for AI Employee.

Perception layer - monitors external sources (Gmail, WhatsApp, etc).
"""

from .gmail import GmailWatcher
from .base import BaseWatcher

__all__ = ['GmailWatcher', 'BaseWatcher']
