"""
Base watcher class for AI Employee.

Abstract base class for all watchers.
Hackathon Spec Aligned: Uses standard folder names (Inbox, Needs_Action, etc.)
"""

import os
import json
import uuid
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any

from config.paths import Paths
from utils.files import write_atomic
from utils.logger import AuditLogger


class BaseWatcher(ABC):
    """Abstract base class for watchers."""
    
    def __init__(self, vault_path: str, queue_folder: str, poll_interval: int):
        """Initialize base watcher."""
        self.vault_path = Path(vault_path)
        self.queue_folder = self.vault_path / queue_folder
        self.poll_interval = poll_interval
        self.logger = AuditLogger(str(self.vault_path))
        self.running = False
        
        # Ensure queue folder exists
        self.queue_folder.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def check_for_new_items(self) -> List[Dict[str, Any]]:
        """Check source for new items. Override in subclass."""
        pass
    
    @abstractmethod
    def detect_type(self, item: Dict[str, Any]) -> str:
        """Detect item type. Override in subclass."""
        pass
    
    @abstractmethod
    def calculate_priority(self, item: Dict[str, Any]) -> str:
        """Calculate priority. Override in subclass."""
        pass
    
    @abstractmethod
    def check_hitl_required(self, item: Dict[str, Any]) -> bool:
        """Check if HITL required. Override in subclass."""
        pass
    
    def create_action_file(self, item: Dict[str, Any]) -> str:
        """Create JSON action file in queue folder."""
        action = {
            "id": f"{self.__class__.__name__}_{uuid.uuid4().hex[:8]}",
            "source": self.__class__.__name__,
            "timestamp": datetime.now().isoformat(),
            "type": self.detect_type(item),
            "priority": self.calculate_priority(item),
            "data": item,
            "status": "new",
            "hitl_required": self.check_hitl_required(item)
        }
        
        filename = f"action_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}.json"
        filepath = self.queue_folder / filename
        
        write_atomic(str(filepath), json.dumps(action, indent=2))
        
        return str(filepath)
    
    async def watch(self):
        """Main watch loop."""
        import asyncio
        
        self.running = True
        
        while self.running:
            try:
                items = self.check_for_new_items()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.log(
                    action="watcher_error",
                    actor=self.__class__.__name__,
                    result="error",
                    details={"error": str(e)}
                )
            
            await asyncio.sleep(self.poll_interval)
    
    def stop(self):
        """Stop the watcher."""
        self.running = False
