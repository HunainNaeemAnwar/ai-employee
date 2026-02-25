"""
Secrets Management Module

Loads sensitive credentials from .env file.
Never hardcode secrets in code - always use this module.
"""

import os
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv


class SecretsManager:
    """
    Manages secrets for AI Employee system.
    
    Secrets are loaded from SECURITY/.env file.
    This file should never be committed to Git.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize secrets manager.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vault_path = vault_path
        
        # Check multiple .env locations (migration compatibility)
        env_locations = [
            os.path.join(vault_path, ".env"),
            os.path.join(vault_path, "SECURITY", ".env"),
            os.path.join(os.path.dirname(vault_path), ".env"),
        ]
        
        self.env_file = None
        for location in env_locations:
            if os.path.exists(location):
                self.env_file = location
                break
        
        self._load_secrets()
    
    def _load_secrets(self) -> None:
        """Load secrets from .env file."""
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
    
    def get(self, key: str, required: bool = False) -> Optional[str]:
        """
        Get a secret value by key.
        
        Args:
            key: Environment variable name
            required: If True, raise error if not found
            
        Returns:
            Secret value or None (if not found and not required)
            
        Raises:
            ValueError: If required secret is not found
        """
        value = os.getenv(key)
        
        if value is None and required:
            raise ValueError(
                f"Required secret '{key}' not found in {self.env_file}. "
                f"Please add it to SECURITY/.env"
            )
        
        return value
    
    def get_gmail_credentials(self) -> dict:
        """
        Get Gmail API credentials.
        
        Returns:
            Dictionary with client_id, client_secret, redirect_uri
            
        Raises:
            ValueError: If any required credential is missing
        """
        return {
            "client_id": self.get("GMAIL_CLIENT_ID", required=True),
            "client_secret": self.get("GMAIL_CLIENT_SECRET", required=True),
            "redirect_uri": self.get("GMAIL_REDIRECT_URI", required=True)
        }
    
    def get_vault_path(self) -> str:
        """
        Get vault path from environment.
        
        Returns:
            Vault path string
        """
        return self.get("VAULT_PATH") or self.vault_path
    
    def get_log_level(self) -> str:
        """
        Get configured log level.
        
        Returns:
            Log level string (default: INFO)
        """
        return self.get("LOG_LEVEL") or "INFO"
    
    def get_max_iterations(self) -> int:
        """
        Get max iterations for Ralph Loop.
        
        Returns:
            Max iterations integer (default: 5)
        """
        try:
            return int(self.get("MAX_ITERATIONS") or "5")
        except ValueError:
            return 5
    
    def has_gmail_credentials(self) -> bool:
        """
        Check if Gmail credentials are configured.
        
        Returns:
            True if all required credentials exist
        """
        try:
            self.get_gmail_credentials()
            return True
        except ValueError:
            return False


# Convenience function for quick access
_secrets_manager: Optional[SecretsManager] = None


def get_secrets(vault_path: str) -> SecretsManager:
    """
    Get or create secrets manager instance.
    
    Args:
        vault_path: Path to AI_Employee_Vault
        
    Returns:
        SecretsManager instance
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager(vault_path)
    return _secrets_manager


def get_secret(key: str, vault_path: str = None, required: bool = False) -> Optional[str]:
    """
    Quick access to a single secret.
    
    Args:
        key: Environment variable name
        vault_path: Path to vault (optional)
        required: If True, raise error if not found
        
    Returns:
        Secret value or None
    """
    if vault_path is None:
        vault_path = os.environ.get("VAULT_PATH", "/home/hunain/personal_assistant/AI_Employee_Vault")
    
    manager = get_secrets(vault_path)
    return manager.get(key, required=required)
