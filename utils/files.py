"""
File operations utility module.

Provides atomic file operations for safe concurrent access.
"""

import json
import os
import shutil
import tempfile
from typing import Any


def write_atomic(filepath: str, content: str) -> None:
    """
    Write file atomically using temp file + rename pattern.
    
    Ensures readers never see partial writes.
    """
    dir_path = os.path.dirname(filepath)
    os.makedirs(dir_path, exist_ok=True)
    
    # Create temp file in same directory
    fd, temp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        os.rename(temp_path, filepath)
    except Exception:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def read_json(filepath: str) -> Any:
    """Read and parse JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(filepath: str, data: Any, indent: int = 2) -> None:
    """Write data as JSON atomically."""
    content = json.dumps(data, indent=indent, ensure_ascii=False)
    write_atomic(filepath, content)


def read_file(filepath: str) -> str:
    """Read entire file content as string."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def file_exists(filepath: str) -> bool:
    """Check if file exists."""
    return os.path.exists(filepath)


def move_file(src: str, dst: str) -> None:
    """Move file from src to dst."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)


def list_files(directory: str, extension: str = None) -> list:
    """List files in directory, optionally filtered by extension."""
    if not os.path.exists(directory):
        return []
    
    files = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            if extension is None or filename.endswith(extension):
                files.append(filepath)
    
    return files
