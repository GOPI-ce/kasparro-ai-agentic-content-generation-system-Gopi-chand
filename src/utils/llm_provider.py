"""
LLM Provider Module

Provides a unified interface for multiple LLM providers:
- Groq (recommended - generous free tier)
- Google Gemini
- Mock mode (for testing)
"""

import os
import json
import re
from typing import Dict, Any, Optional
from utils import get_config, get_logger

logger = get_logger("LLMProvider")


class LLMProvider:
    """Unified LLM provider interface supporting multiple backends."""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        
        if self.mock_mode:
            logger.info("Running in MOCK MODE - no API calls will be made")
            self.client = None
            return
        
        if self.provider == "groq":
            self._init_groq()
        elif self.provider == "gemini":
            self._init_gemini()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    def _init_groq(self):
        """Initialize Groq client."""
        try:
            from langchain_groq import ChatGroq
            
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY is required. Get one free at: https://console.groq.com")
            
            self.client = ChatGroq(
                api_key=api_key,
                model_name=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                temperature=0.7
            )
            logger.info(f"Initialized Groq with model: {os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')}")
            
        except ImportError:
            raise ImportError("Please install langchain-groq: pip install langchain-groq")
    
    def _init_gemini(self):
        """Initialize Gemini client."""
        import google.generativeai as genai
        
        api_key = get_config().get_gemini_api_key()
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
            
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(get_config().gemini_model)
        logger.info(f"Initialized Gemini with model: {get_config().gemini_model}")

    def generate(self, prompt: str, max_retries: int = 3) -> str:
        """Generate text from a prompt."""
        if self.mock_mode:
            return self._mock_response(prompt)
        
        import time
        
        for attempt in range(max_retries):
            try:
                if self.provider == "groq":
                    response = self.client.invoke(prompt)
                    return response.content
                else:  # gemini
                    response = self.client.generate_content(prompt)
                    return response.text
                    
            except Exception as e:
                error_str = str(e).lower()
                
                if "rate" in error_str or "quota" in error_str or "429" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = 30 * (attempt + 1)
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 2}/{max_retries}")
                        time.sleep(wait_time)
                        continue
                
                logger.error(f"LLM generation failed: {e}")
                raise
        
        raise ValueError("LLM generation failed after max retries")

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """
        Generate JSON from a prompt with robust parsing.
        Handles extra text, multiple JSON objects, and markdown.
        """
        text = self.generate(prompt)
        
        # Clean markdown code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            parts = text.split("```")
            if len(parts) >= 2:
                text = parts[1]
        
        text = text.strip()
        
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON object using regex
        # Match from first { to last matching }
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try finding JSON between first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
        
        # If all else fails, try to find any valid JSON object
        for i in range(len(text)):
            if text[i] == '{':
                depth = 0
                for j in range(i, len(text)):
                    if text[j] == '{':
                        depth += 1
                    elif text[j] == '}':
                        depth -= 1
                        if depth == 0:
                            try:
                                return json.loads(text[i:j+1])
                            except json.JSONDecodeError:
                                break
        
        raise ValueError(f"Could not parse JSON from response: {text[:200]}...")
    
    def _mock_response(self, prompt: str) -> str:
        """Return mock response for testing."""
        return '{"mock": true, "message": "This is a mock response"}'


# Global provider instance
_provider: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    """Get the global LLM provider instance."""
    global _provider
    if _provider is None:
        _provider = LLMProvider()
    return _provider
