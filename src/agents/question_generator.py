"""
Question Generator Agent

Automatically generates 15+ categorized user questions from product data.
Categories: Informational, Safety, Usage, Purchase, Comparison

Uses the unified LLM provider for multi-backend support (Groq/Gemini) and mock mode.
"""

from typing import Dict, Any, List
import json
import os
from schemas import ProductData
from utils import StateManager, get_config
from agents.base_agent import BaseAgent


class QuestionGeneratorAgent(BaseAgent):
    """
    Agent that generates categorized user questions from product data.
    Produces at least 15 questions across 5 categories.
    """
    
    # Question categories as per assignment requirements
    CATEGORIES = [
        "Informational",  # What is it, how does it work
        "Safety",         # Side effects, allergies, warnings
        "Usage",          # How to apply, when, frequency
        "Purchase",       # Price, availability, value
        "Comparison"      # vs other products, alternatives
    ]
    
    def __init__(self, state_manager: StateManager, config: Dict[str, Any] = None):
        super().__init__("QuestionGenerator", state_manager, config)
        
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        
        if not self.mock_mode:
            from utils.llm_provider import get_llm_provider
            self.llm = get_llm_provider()
        else:
            self.llm = None
            self.logger.info("Running in MOCK MODE")

    def execute(self, input_data: ProductData) -> Dict[str, List[Dict[str, str]]]:
        """
        Generates categorized questions from product data.
        
        Args:
            input_data: ProductData object for the main product
            
        Returns:
            Dict with categories as keys and lists of question dicts as values
        """
        self.log_decision("Generating categorized questions", {
            "product": input_data.product_name,
            "categories": self.CATEGORIES
        })
        
        if self.mock_mode:
            return self._mock_questions(input_data)
        
        prompt = f"""
        Generate user questions for this product. Return JSON with 5 categories, 3 questions each.

        PRODUCT: {input_data.model_dump_json(indent=2)}

        FORMAT:
        {{"Informational": [{{"question": "...", "answer": "..."}}], "Safety": [...], "Usage": [...], "Purchase": [...], "Comparison": [...]}}
        """
        
        questions = self.llm.generate_json(prompt)
        
        # Log summary
        total_questions = sum(len(q_list) for q_list in questions.values())
        self.logger.info(f"Generated {total_questions} questions across {len(questions)} categories")
        
        return questions

    def _mock_questions(self, product: ProductData) -> Dict[str, List[Dict[str, str]]]:
        """Generate mock categorized questions."""
        return {
            "Informational": [
                {"question": f"What is {product.product_name}?", "answer": f"A skincare serum with {product.concentration}."},
                {"question": "What are the key ingredients?", "answer": f"Contains {product.key_ingredients}."},
                {"question": "What are the main benefits?", "answer": f"Benefits include {product.benefits}."}
            ],
            "Safety": [
                {"question": "Are there any side effects?", "answer": f"{product.side_effects or 'Minimal side effects.'}"},
                {"question": "Is it safe for sensitive skin?", "answer": "Perform a patch test before first use."},
                {"question": "Can I use it if I have allergies?", "answer": "Check ingredients list and consult a dermatologist."}
            ],
            "Usage": [
                {"question": "How do I apply it?", "answer": product.how_to_use},
                {"question": "When should I use it in my routine?", "answer": "Apply after cleansing, before moisturizer."},
                {"question": "How often should I use it?", "answer": "Once daily in the morning for best results."}
            ],
            "Purchase": [
                {"question": f"What is the price?", "answer": f"Priced at {product.price}."},
                {"question": "Where can I buy it?", "answer": "Available online and at select retailers."},
                {"question": "Is it good value for money?", "answer": f"Excellent value at {product.price}."}
            ],
            "Comparison": [
                {"question": "How does it compare to other serums?", "answer": f"With {product.concentration}, offers optimal concentration."},
                {"question": "Is it better than drugstore options?", "answer": "Premium formulation provides superior results."},
                {"question": "Can I layer it with other products?", "answer": "Yes, layer with water-based serums."}
            ]
        }

    def validate_input(self, input_data: Any) -> None:
        if not isinstance(input_data, ProductData):
            raise ValueError("Input must be a ProductData object")
