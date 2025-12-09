"""
Configuration management for the multi-agent system.

Loads configuration from config.yaml and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the agent system."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config.yaml file
        """
        # Load environment variables
        load_dotenv()
        
        # Load YAML configuration
        self.config_path = Path(config_path)
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config_data = yaml.safe_load(f)
        else:
            self.config_data = {}
        
        # Override with environment variables
        self._load_env_overrides()
    
    def _load_env_overrides(self):
        """Override config with environment variables."""
        # Gemini API Key (required)
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            if "llm" not in self.config_data:
                self.config_data["llm"] = {}
            self.config_data["llm"]["api_key"] = gemini_key
        
        # Model name
        model = os.getenv("GEMINI_MODEL")
        if model:
            self.config_data["llm"]["model"] = model
        
        # Temperature
        temp = os.getenv("TEMPERATURE")
        if temp:
            self.config_data["llm"]["temperature"] = float(temp)
        
        # Log level
        log_level = os.getenv("LOG_LEVEL")
        if log_level:
            if "logging" not in self.config_data:
                self.config_data["logging"] = {}
            self.config_data["logging"]["level"] = log_level
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path (e.g., 'llm.model')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        
        Example:
            >>> config.get('llm.temperature', 0.7)
            0.7
        """
        keys = key_path.split('.')
        value = self.config_data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.config_data.get("llm", {})
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific agent.
        
        Args:
            agent_name: Name of the agent (e.g., 'coordinator', 'data_extractor')
        
        Returns:
            Agent configuration dictionary
        """
        return self.config_data.get("agents", {}).get(agent_name, {})
    
    def get_template_config(self) -> Dict[str, Any]:
        """Get template configuration."""
        return self.config_data.get("templates", {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration."""
        return self.config_data.get("output", {})
    
    @property
    def gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key."""
        return self.get("llm.api_key")
    
    @property
    def gemini_model(self) -> str:
        """Get Gemini model name."""
        return self.get("llm.model", "gemini-pro")
    
    @property
    def temperature(self) -> float:
        """Get LLM temperature."""
        return self.get("llm.temperature", 0.7)
    
    @property
    def max_tokens(self) -> int:
        """Get max tokens."""
        return self.get("llm.max_tokens", 2048)
    
    def get_gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key (alias for property)."""
        return self.gemini_api_key

    def validate(self) -> bool:
        """
        Validate required configuration.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is required. Set it in .env file or environment variable."
            )
        
        return True


# Global config instance
_config_instance: Optional[Config] = None


def get_config(config_path: str = "config.yaml") -> Config:
    """
    Get or create global config instance.
    
    Args:
        config_path: Path to config file
    
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance
