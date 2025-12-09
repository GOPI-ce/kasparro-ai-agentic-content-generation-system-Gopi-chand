"""
Logging utilities for the multi-agent system.

Provides structured logging with agent decision tracking and execution tracing.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json


class AgentLogger:
    """Centralized logging for agent decisions and execution traces."""
    
    def __init__(self, name: str, log_level: str = "INFO", log_file: Optional[str] = None):
        """
        Initialize the agent logger.
        
        Args:
            name: Logger name (typically agent class name)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional log file path
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)
    
    def agent_decision(self, agent_name: str, decision: str, context: dict):
        """
        Log an agent decision with context.
        
        Args:
            agent_name: Name of the agent making the decision
            decision: Description of the decision
            context: Additional context as a dictionary
        """
        decision_log = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "decision": decision,
            "context": context
        }
        self.logger.info(f"[AGENT DECISION] {json.dumps(decision_log, indent=2)}")
    
    def execution_trace(self, agent_name: str, action: str, status: str, duration_ms: Optional[float] = None):
        """
        Log an execution trace.
        
        Args:
            agent_name: Name of the agent
            action: Action being performed
            status: Status (started, completed, failed)
            duration_ms: Optional execution duration in milliseconds
        """
        trace_log = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "status": status
        }
        if duration_ms is not None:
            trace_log["duration_ms"] = duration_ms
        
        self.logger.debug(f"[EXECUTION TRACE] {json.dumps(trace_log)}")


def get_logger(name: str, config: Optional[dict] = None) -> AgentLogger:
    """
    Factory function to get a configured logger.
    
    Args:
        name: Logger name
        config: Optional configuration dictionary
    
    Returns:
        Configured AgentLogger instance
    """
    if config:
        log_level = config.get("logging", {}).get("level", "INFO")
        log_file = config.get("logging", {}).get("file", None)
    else:
        log_level = "INFO"
        log_file = None
    
    return AgentLogger(name, log_level, log_file)
