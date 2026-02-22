"""
Actions package for AI Employee.

MCP servers for executing actions (email, browser, etc).
"""

from .email import EmailMCP

__all__ = ['EmailMCP']
