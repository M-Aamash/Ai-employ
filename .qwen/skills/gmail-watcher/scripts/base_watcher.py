"""
Base Watcher - Abstract base class for all watcher scripts.

All watchers (Gmail, WhatsApp, LinkedIn) inherit from this base class.
Provides common functionality for vault management, logging, and action file creation.
"""

import logging
import json
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional


class BaseWatcher(ABC):
    """Base class for all watcher scripts."""
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks
        """
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs_path = self.vault_path / 'Logs'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
        self.logger.info(f'Initialized {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {check_interval}s')
    
    def _setup_logging(self):
        """Setup logging to file and console."""
        log_file = self.logs_path / f'{self.__class__.__name__.lower()}_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Setup logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    @abstractmethod
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new items.
        
        Returns:
            List of new items to process
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create an action file in Needs_Action folder.
        
        Args:
            item: Item data to create action file for
            
        Returns:
            Path to created action file
        """
        pass
    
    def run(self):
        """Main run loop - continuously checks for updates."""
        import time
        
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info('Press Ctrl+C to stop')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s)')
                        
                        for item in items:
                            try:
                                action_file = self.create_action_file(item)
                                self.logger.info(f'Created action file: {action_file.name}')
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('Watcher stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
    
    def sanitize_filename(self, name: str) -> str:
        """
        Sanitize a string for use as a filename.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized filename
        """
        import re
        # Remove or replace invalid characters
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Remove leading/trailing spaces and dots
        name = name.strip(' .')
        # Limit length
        return name[:200]
    
    def get_today_date(self) -> str:
        """Get current date in ISO format."""
        return datetime.now().strftime('%Y-%m-%d')
    
    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def _log_action(self, action_type: str, target: str, filepath: Path, details: Dict = None):
        """Log action to JSON log file."""
        log_entry = {
            'timestamp': self.get_timestamp(),
            'action_type': action_type,
            'actor': self.__class__.__name__.lower(),
            'target': target,
            'filepath': str(filepath),
            'result': 'created',
            'details': details or {}
        }

        log_file = self.logs_path / f'{self.get_today_date()}.json'

        # Read existing logs with error handling
        logs = []
        if log_file.exists():
            try:
                content = log_file.read_text(encoding='utf-8')
                if content.strip():  # Only parse if not empty
                    logs = json.loads(content)
            except (json.JSONDecodeError, UnicodeDecodeError):
                # File is corrupted, start fresh
                logs = []
                self.logger.warning(f"Log file corrupted, starting fresh: {log_file}")

        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding='utf-8')
