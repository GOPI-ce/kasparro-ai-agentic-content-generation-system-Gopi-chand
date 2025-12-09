"""
Agents Package

Exports all agent classes for the marketing content generation system.

Agent Hierarchy:
- BaseAgent (abstract base class with Template Method pattern)
  ├── CoordinatorAgent (orchestrator)
  ├── DataExtractionAgent (no LLM)
  ├── QuestionGeneratorAgent (LLM)
  ├── ProductCreatorAgent (LLM)
  ├── ContentGenerationAgent (LLM + templates + content_blocks)
  └── QualityValidationAgent (no LLM)
"""

from agents.base_agent import BaseAgent
from agents.coordinator import CoordinatorAgent
from agents.data_extractor import DataExtractionAgent
from agents.question_generator import QuestionGeneratorAgent
from agents.product_creator import ProductCreatorAgent
from agents.content_generator import ContentGenerationAgent
from agents.quality_validator import QualityValidationAgent

__all__ = [
    "BaseAgent",
    "CoordinatorAgent",
    "DataExtractionAgent",
    "QuestionGeneratorAgent",
    "ProductCreatorAgent",
    "ContentGenerationAgent",
    "QualityValidationAgent"
]
