"""
Application settings for AI Employee.

Loads configuration from environment variables and .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Settings:
    """Application configuration."""
    
    def __init__(self):
        """Load settings from environment."""
        # Load .env file (check multiple locations for migration compatibility)
        env_locations = [
            Path(__file__).parent.parent / ".env",
            Path(__file__).parent.parent / "AI_Employee_Vault" / ".env",
            Path(__file__).parent.parent / "AI_Employee_Vault" / "SECURITY" / ".env",
        ]
        
        for env_file in env_locations:
            if env_file.exists():
                load_dotenv(env_file)
                break
        
        # Vault configuration
        self.vault_path = Path(
            os.getenv("VAULT_PATH", os.path.join(os.getcwd(), "AI_Employee_Vault"))
        )
        
        # Watcher settings
        self.gmail_poll_interval = int(os.getenv("GMAIL_POLL_INTERVAL", "120"))
        self.whatsapp_poll_interval = int(os.getenv("WHATSAPP_POLL_INTERVAL", "30"))
        
        # Ralph Loop settings (increased for better reliability)
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", "10"))
        self.iteration_timeout = int(os.getenv("ITERATION_TIMEOUT", "120"))
        self.no_progress_threshold = int(os.getenv("NO_PROGRESS_THRESHOLD", "2"))
        
        # Email settings
        self.max_emails_per_hour = int(os.getenv("MAX_EMAILS_PER_HOUR", "10"))
        self.max_emails_per_day = int(os.getenv("MAX_EMAILS_PER_DAY", "100"))
        
        # HITL settings
        self.auto_approve_max_length = int(os.getenv("AUTO_APPROVE_MAX_LENGTH", "1000"))
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_to_file = os.getenv("LOG_TO_FILE", "true").lower() == "true"
        
        # Gmail API
        self.gmail_client_id = os.getenv("GMAIL_CLIENT_ID")
        self.gmail_client_secret = os.getenv("GMAIL_CLIENT_SECRET")
        self.gmail_redirect_uri = os.getenv("GMAIL_REDIRECT_URI", "http://localhost:8080")
        
        # Feature flags
        self.enable_web_ui = os.getenv("ENABLE_WEB_UI", "false").lower() == "true"
        self.enable_notifications = os.getenv("ENABLE_NOTIFICATIONS", "true").lower() == "true"
    
    @property
    def credentials_file(self) -> Path:
        """Path to Gmail credentials file."""
        return self.vault_path / "SECURITY" / "credentials.json"
    
    @property
    def token_file(self) -> Path:
        """Path to Gmail token file."""
        return self.vault_path / "SECURITY" / "gmail_token.json"
    
    @property
    def state_file(self) -> Path:
        """Path to current state file."""
        return self.vault_path / "SYSTEM" / "state" / "current_task.json"
    
    @property
    def gmail_scopes(self) -> list:
        """Required Gmail API scopes."""
        return [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.labels'
        ]
    
    def has_gmail_credentials(self) -> bool:
        """Check if Gmail credentials are configured."""
        return bool(self.gmail_client_id and self.gmail_client_secret)
    
    def is_gmail_authenticated(self) -> bool:
        """Check if Gmail is authenticated."""
        return self.token_file.exists()


# Global settings instance
_settings: Settings = None


def get_settings() -> Settings:
    """Get or create global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
