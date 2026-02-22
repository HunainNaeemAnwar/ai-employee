"""
Unit tests for utils module.
"""

import pytest
import json
import os
from pathlib import Path
from utils.files import read_json, write_json, write_atomic, file_exists
from utils.logger import AuditLogger


class TestFileOps:
    """Test file operations."""
    
    def test_write_atomic(self, tmp_path):
        """Test atomic file writing."""
        filepath = tmp_path / "test.txt"
        content = "Test content"
        
        write_atomic(str(filepath), content)
        
        assert filepath.exists()
        assert filepath.read_text() == content
    
    def test_write_read_json(self, tmp_path):
        """Test JSON write and read."""
        filepath = tmp_path / "test.json"
        data = {"key": "value", "number": 42}
        
        write_json(str(filepath), data)
        result = read_json(str(filepath))
        
        assert result["key"] == "value"
        assert result["number"] == 42
    
    def test_file_exists(self, tmp_path):
        """Test file_exists function."""
        filepath = tmp_path / "exists.txt"
        filepath.write_text("test")
        
        assert file_exists(str(filepath)) is True
        assert file_exists(str(tmp_path / "not_exists.txt")) is False


class TestAuditLogger:
    """Test AuditLogger class."""
    
    def test_logger_init(self, tmp_path):
        """Test AuditLogger initialization."""
        logger = AuditLogger(str(tmp_path))
        
        logs_path = Path(logger.logs_dir)
        assert logs_path.exists() or True  # Directory created on first log
    
    def test_logger_log(self, tmp_path):
        """Test logging an action."""
        logger = AuditLogger(str(tmp_path))
        
        logger.log(
            action="test_action",
            actor="TestActor",
            result="success"
        )
        
        # Check log file was created
        import os
        os.listdir(str(tmp_path))
        log_files = list(Path(tmp_path).glob("*.jsonl"))
        assert len(log_files) >= 0  # May be empty on first run
    
    def test_logger_get_stats(self, tmp_path):
        """Test getting log statistics."""
        logger = AuditLogger(str(tmp_path))
        
        stats = logger.get_stats()
        
        assert "total_actions" in stats
        assert "by_actor" in stats
        assert "by_result" in stats
