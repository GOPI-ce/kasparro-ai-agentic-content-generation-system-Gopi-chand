"""
Product Creator Agent

Generates a fictional competitor product (Product B).
Uses the unified LLM provider for multi-backend support.
"""

from typing import Dict, Any
import json
import os
from schemas import ProductData
from utils import StateManager, get_config
from agents.base_agent import BaseAgent


class ProductCreatorAgent(BaseAgent):
    """Agent that generates fictional competitor products."""
    
    def __init__(self, state_manager: StateManager, config: Dict[str, Any] = None):
        super().__init__("ProductCreator", state_manager, config)
        
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        
        if not self.mock_mode:
            from utils.llm_provider import get_llm_provider
            self.llm = get_llm_provider()
        else:
            self.llm = None
            self.logger.info("Running in MOCK MODE")

    def execute(self, input_data: ProductData) -> ProductData:
        """Generates a fictional competitor product."""
        self.log_decision("Generating fictional competitor", {"source_product": input_data.product_name})
        
        if self.mock_mode:
            return self._mock_product_b(input_data)
        
        prompt = f"""Create a fictional competitor Vitamin C serum product.

EXISTING PRODUCT (for reference):
- Name: {input_data.product_name}
- Price: {input_data.price}
- Concentration: {input_data.concentration}

Create a DIFFERENT competing product. Return ONLY a JSON object with these EXACT keys:

{{"Product Name": "Your Product Name Here", "Concentration": "15% Vitamin C", "Skin Type": "All Skin Types", "Key Ingredients": "Vitamin C, Niacinamide", "Benefits": "Brightening, Anti-aging", "How to Use": "Apply 3 drops daily", "Side Effects": "Mild tingling possible", "Price": "₹849"}}

IMPORTANT: Return ONLY the JSON object, no explanation, no markdown, no nesting."""
        
        try:
            response_json = self.llm.generate_json(prompt)
            
            # Handle nested response (some LLMs wrap in extra object)
            if "Product B" in response_json:
                response_json = response_json["Product B"]
            elif "product" in response_json:
                response_json = response_json["product"]
            
            # Convert lowercase keys to expected format
            key_mapping = {
                "product_name": "Product Name",
                "product name": "Product Name", 
                "concentration": "Concentration",
                "skin_type": "Skin Type",
                "skin type": "Skin Type",
                "key_ingredients": "Key Ingredients",
                "key ingredients": "Key Ingredients",
                "benefits": "Benefits",
                "how_to_use": "How to Use",
                "how to use": "How to Use",
                "side_effects": "Side Effects",
                "side effects": "Side Effects",
                "price": "Price"
            }
            
            normalized = {}
            for k, v in response_json.items():
                # Check if key needs normalization
                normalized_key = key_mapping.get(k.lower(), k)
                normalized[normalized_key] = v
            
            product_b = ProductData(**normalized)
            self.logger.info(f"Generated fictional product: {product_b.product_name}")
            return product_b
            
        except Exception as e:
            self.logger.warning(f"LLM generation failed, using fallback: {e}")
            return self._mock_product_b(input_data)

    def _mock_product_b(self, product_a: ProductData) -> ProductData:
        """Generate mock Product B."""
        return ProductData(**{
            "Product Name": "RadiantGlow Vitamin C Complex",
            "Concentration": "15% Vitamin C",
            "Skin Type": "All Skin Types",
            "Key Ingredients": "Vitamin C, Niacinamide, Vitamin E",
            "Benefits": "Brightening, Anti-aging, Reduces fine lines",
            "How to Use": "Apply 3-4 drops morning and evening",
            "Side Effects": "May cause redness for very sensitive skin",
            "Price": "₹849"
        })

    def validate_input(self, input_data: Any) -> None:
        if not isinstance(input_data, ProductData):
            raise ValueError("Input must be a ProductData object")
