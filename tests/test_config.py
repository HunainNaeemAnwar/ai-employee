"""
Unit tests for configuration module.
"""

import pytest
from pathlib import Path
from config.settings import Settings, get_settings
from config.paths import Paths


class TestSettings:
    """Test Settings class."""
    
    def test_settings_init(self):
        """Test Settings initialization."""
        settings = Settings()
        
        assert settings.vault_path is not None
        assert settings.gmail_poll_interval > 0
        assert settings.max_iterations > 0
    
    def test_settings_singleton(self):
        """Test get_settings returns same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
    
    def test_gmail_scopes(self):
        """Test Gmail scopes are defined."""
        settings = Settings()
        
        assert len(settings.gmail_scopes) == 4
        assert 'gmail.readonly' in settings.gmail_scopes[0]
        assert 'gmail.send' in settings.gmail_scopes[1]


class TestPaths:
    """Test Paths class."""
    
    def test_paths_init(self):
        """Test Paths initialization."""
        paths = Paths()
        
        assert paths.BASE_DIR is not None
        assert paths.VAULT_DIR is not None
        assert paths.STATE_DIR is not None
    
    def test_paths_ensure_directories(self):
        """Test ensure_directories creates folders."""
        paths = Paths()
        paths.ensure_directories()
        
        assert paths.PENDING.exists()
        assert paths.IN_PROGRESS.exists()
        assert paths.PENDING_APPROVAL.exists()
        assert paths.COMPLETED.exists()
    
    def test_get_input_queue(self):
        """Test get_input_queue returns correct path."""
        paths = Paths()
        
        gmail_queue = paths.get_input_queue("gmail")
        assert "Gmail" in str(gmail_queue)
    
    def test_get_audit_log(self):
        """Test get_audit_log returns correct path."""
        paths = Paths()
        
        log_file = paths.get_audit_log("2026-02-20")
        assert "2026-02-20.jsonl" in str(log_file)
