"""
Base Agent class for the multi-agent system.

All agents inherit from this base class to ensure consistent interface and behavior.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import time

from utils import AgentLogger, get_logger, StateManager, AgentStatus


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    
    Implements Template Method pattern for consistent agent behavior:
    - Input validation
    - Execution with logging
    - Output formatting
    - Error handling
    """
    
    def __init__(self, name: str, state_manager: StateManager, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent.
        
        Args:
            name: Agent name
            state_manager: Shared state manager
            config: Optional agent configuration
        """
        self.name = name
        self.state_manager = state_manager
        self.config = config or {}
        self.logger = get_logger(f"Agent.{name}", self.config)
        
        self.logger.info(f"[{self.name}] Agent initialized")
    
    def run(self, input_data: Any) -> Any:
        """
        Main execution method (Template Method).
        
        Args:
            input_data: Input data for the agent
        
        Returns:
            Agent output
        
        Raises:
            ValueError: If input validation fails
            Exception: If execution fails
        """
        start_time = time.time()
        
        try:
            # Update status to RUNNING
            self.state_manager.set_agent_status(self.name, AgentStatus.RUNNING)
            self.logger.info(f"[{self.name}] Starting execution")
            
            # Validate input
            self.logger.debug(f"[{self.name}] Validating input")
            self.validate_input(input_data)
            
            # Execute agent logic
            self.logger.info(f"[{self.name}] Executing agent logic")
            result = self.execute(input_data)
            
            # Format output
            self.logger.debug(f"[{self.name}] Formatting output")
            formatted_result = self.format_output(result)
            
            # Store result in state
            self.state_manager.set_agent_result(self.name, formatted_result)
            
            # Update status to COMPLETED
            self.state_manager.set_agent_status(self.name, AgentStatus.COMPLETED)
            
            # Log execution time
            duration_ms = (time.time() - start_time) * 1000
            self.logger.execution_trace(
                self.name,
                "execute",
                "completed",
                duration_ms
            )
            self.logger.info(f"[{self.name}] Execution completed in {duration_ms:.2f}ms")
            
            return formatted_result
        
        except Exception as e:
            # Update status to FAILED
            self.state_manager.set_agent_status(self.name, AgentStatus.FAILED)
            self.logger.error(f"[{self.name}] Execution failed: {str(e)}", exc_info=True)
            
            # Log failure
            duration_ms = (time.time() - start_time) * 1000
            self.logger.execution_trace(
                self.name,
                "execute",
                "failed",
                duration_ms
            )
            
            raise
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """
        Execute the agent's core logic. Must be implemented by subclasses.
        
        Args:
            input_data: Input data for the agent
        
        Returns:
            Agent-specific output
        """
        pass
    
    def validate_input(self, input_data: Any) -> None:
        """
        Validate input data. Override in subclasses for custom validation.
        
        Args:
            input_data: Input data to validate
        
        Raises:
            ValueError: If validation fails
        """
        if input_data is None:
            raise ValueError(f"[{self.name}] Input data cannot be None")
    
    def format_output(self, result: Any) -> Any:
        """
        Format output data. Override in subclasses for custom formatting.
        
        Args:
            result: Raw result from execute()
        
        Returns:
            Formatted output
        """
        return result
    
    def log_decision(self, decision: str, context: Dict[str, Any]):
        """
        Log an agent decision.
        
        Args:
            decision: Description of the decision
            context: Additional context
        """
        self.logger.agent_decision(self.name, decision, context)
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
        
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
