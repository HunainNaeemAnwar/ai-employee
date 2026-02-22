"""
File Operations Utility Module

Provides atomic file operations for safe concurrent access.
All writes use temp file + rename pattern for atomicity.
"""

import json
import os
import tempfile
from typing import Any


def write_atomic(filepath: str, content: str) -> None:
    """
    Write file atomically using temp file + rename pattern.
    
    This ensures that readers never see partial writes.
    On POSIX systems, rename is atomic.
    
    Args:
        filepath: Path to the file to write
        content: Content to write to the file
    """
    dir_path = os.path.dirname(filepath)
    
    # Create directory if it doesn't exist
    os.makedirs(dir_path, exist_ok=True)
    
    # Create temp file in same directory (same filesystem for atomic rename)
    fd, temp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    
    try:
        # Write content to temp file
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Atomic rename (POSIX)
        os.rename(temp_path, filepath)
    except Exception:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def read_json(filepath: str) -> Any:
    """
    Read and parse JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Parsed JSON data (dict, list, or primitive)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(filepath: str, data: Any, indent: int = 2) -> None:
    """
    Write data as JSON atomically.
    
    Args:
        filepath: Path to JSON file
        data: Data to serialize as JSON
        indent: Number of spaces for indentation (default: 2)
    """
    content = json.dumps(data, indent=indent, ensure_ascii=False)
    write_atomic(filepath, content)


def read_file(filepath: str) -> str:
    """
    Read entire file content as string.
    
    Args:
        filepath: Path to file
        
    Returns:
        File content as string
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def file_exists(filepath: str) -> bool:
    """
    Check if file exists.
    
    Args:
        filepath: Path to file
        
    Returns:
        True if file exists, False otherwise
    """
    return os.path.exists(filepath)


def move_file(src: str, dst: str) -> None:
    """
    Move file from src to dst atomically.
    
    Args:
        src: Source file path
        dst: Destination file path
    """
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)


def list_files(directory: str, extension: str = None) -> list:
    """
    List files in directory, optionally filtered by extension.
    
    Args:
        directory: Directory to list
        extension: Optional extension filter (e.g., '.json')
        
    Returns:
        List of file paths
    """
    if not os.path.exists(directory):
        return []
    
    files = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            if extension is None or filename.endswith(extension):
                files.append(filepath)
    
    return files


# Import shutil for move_file
import shutil
