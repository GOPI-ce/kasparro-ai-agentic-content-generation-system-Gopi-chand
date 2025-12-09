"""
Data Extraction Agent

Responsible for parsing and validating product data.
"""

from typing import List, Dict, Any
from schemas import ProductData
from utils import StateManager
from agents.base_agent import BaseAgent


class DataExtractionAgent(BaseAgent):
    """
    Agent that extracts and validates product data from input.
    """
    
    def __init__(self, state_manager: StateManager, config: Dict[str, Any] = None):
        super().__init__("DataExtractor", state_manager, config)

    def execute(self, input_data: Dict[str, Any]) -> ProductData:
        """
         Parses and validates the input dictionary into a ProductData object.
        """
        self.log_decision("Extracting product data", {
            "keys_present": list(input_data.keys())
        })
        
        try:
            # Pydantic does the heavy lifting of validation
            product_data = ProductData(**input_data)
            
            self.logger.info(f"Successfully extracted data for: {product_data.product_name}")
            return product_data
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            raise ValueError(f"Input data validation failed: {e}")

    def validate_input(self, input_data: Any) -> None:
        if not isinstance(input_data, dict):
            raise ValueError("Input data must be a dictionary")
