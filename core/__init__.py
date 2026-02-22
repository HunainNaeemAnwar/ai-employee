"""
Core business logic package for AI Employee.

Contains state management, task models, and approval workflow.
"""

from .state import StateManager
from .task import Task, TaskStatus

__all__ = ['StateManager', 'Task', 'TaskStatus']
