"""
Command-line interface for AI Employee.

Provides start, status, test, and help commands.
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Employee Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-employee start          Start the orchestrator
  ai-employee status         Show system status
  ai-employee test           List test files
  ai-employee stop           Stop the orchestrator
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        choices=['start', 'status', 'stop', 'test', 'help'],
        default='help',
        help='Command to run'
    )
    
    parser.add_argument(
        '--vault',
        default=str(Path.home() / "personal_assistant" / "AI_Employee_Vault"),
        help='Path to AI_Employee_Vault'
    )
    
    args = parser.parse_args()
    
    # Import command handler
    from .commands import run_command
    run_command(args.command, args.vault)


if __name__ == "__main__":
    main()
