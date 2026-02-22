"""
Utilities package for AI Employee.

File operations, logging, and secrets management.
"""

from .files import read_json, write_json, write_atomic
from .logger import AuditLogger
from .secrets import SecretsManager, get_secrets

__all__ = [
    'read_json', 'write_json', 'write_atomic',
    'AuditLogger',
    'SecretsManager', 'get_secrets'
]
