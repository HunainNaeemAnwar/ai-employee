#!/usr/bin/env python3
"""
AI Employee CLI Entry Point

Usage:
    python main.py start
    python main.py status
    python main.py test
    python main.py help
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from cli.main import main

if __name__ == "__main__":
    main()
