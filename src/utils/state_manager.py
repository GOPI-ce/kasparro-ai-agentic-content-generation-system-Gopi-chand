"""
State management for multi-agent workflow.

Manages agent communication, intermediate results, and workflow progress.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Status of an agent in the workflow."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StateManager:
    """Manages state across agents in the workflow."""
    
    def __init__(self):
        """Initialize the state manager."""
        self._state: Dict[str, Any] = {}
        self._agent_status: Dict[str, AgentStatus] = {}
        self._agent_results: Dict[str, Any] = {}
        self._execution_log: List[Dict[str, Any]] = []
        self._workflow_start: Optional[datetime] = None
        self._workflow_end: Optional[datetime] = None
    
    def start_workflow(self):
        """Mark workflow as started."""
        self._workflow_start = datetime.now()
        self._log_event("workflow_started", {"timestamp": self._workflow_start.isoformat()})
    
    def end_workflow(self):
        """Mark workflow as ended."""
        self._workflow_end = datetime.now()
        if self._workflow_start:
            duration = (self._workflow_end - self._workflow_start).total_seconds()
            self._log_event("workflow_completed", {
                "timestamp": self._workflow_end.isoformat(),
                "duration_seconds": duration
            })
    
    def set_agent_status(self, agent_name: str, status: AgentStatus):
        """
        Set the status of an agent.
        
        Args:
            agent_name: Name of the agent
            status: New status
        """
        self._agent_status[agent_name] = status
        self._log_event("agent_status_change", {
            "agent": agent_name,
            "status": status.value,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_agent_status(self, agent_name: str) -> AgentStatus:
        """
        Get the status of an agent.
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            Agent status
        """
        return self._agent_status.get(agent_name, AgentStatus.PENDING)
    
    def set_agent_result(self, agent_name: str, result: Any):
        """
        Store the result from an agent.
        
        Args:
            agent_name: Name of the agent
            result: Result data
        """
        self._agent_results[agent_name] = result
        self._log_event("agent_result_stored", {
            "agent": agent_name,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_agent_result(self, agent_name: str) -> Optional[Any]:
        """
        Get the result from an agent.
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            Agent result or None if not found
        """
        return self._agent_results.get(agent_name)
    
    def set(self, key: str, value: Any):
        """
        Set a value in the shared state.
        
        Args:
            key: State key
            value: Value to store
        """
        self._state[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the shared state.
        
        Args:
            key: State key
            default: Default value if key not found
        
        Returns:
            Value or default
        """
        return self._state.get(key, default)
    
    def has(self, key: str) -> bool:
        """
        Check if a key exists in the state.
        
        Args:
            key: State key
        
        Returns:
            True if key exists
        """
        return key in self._state
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log an event to the execution log.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        self._execution_log.append({
            "event_type": event_type,
            "data": data
        })
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """
        Get the execution log.
        
        Returns:
            List of execution events
        """
        return self._execution_log.copy()
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the workflow execution.
        
        Returns:
            Summary dictionary
        """
        summary = {
            "workflow_start": self._workflow_start.isoformat() if self._workflow_start else None,
            "workflow_end": self._workflow_end.isoformat() if self._workflow_end else None,
            "agent_statuses": {name: status.value for name, status in self._agent_status.items()},
            "total_events": len(self._execution_log)
        }
        
        if self._workflow_start and self._workflow_end:
            summary["total_duration_seconds"] = (self._workflow_end - self._workflow_start).total_seconds()
        
        return summary
    
    def clear(self):
        """Clear all state (for testing or reset)."""
        self._state.clear()
        self._agent_status.clear()
        self._agent_results.clear()
        self._execution_log.clear()
        self._workflow_start = None
        self._workflow_end = None
