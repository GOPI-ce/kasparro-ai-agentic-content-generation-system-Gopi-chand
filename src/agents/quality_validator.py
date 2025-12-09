"""
Quality Validation Agent

Validates the structure and content of all generated marketing pages.
Checks against assignment requirements (15+ FAQs, required fields, etc.)
"""

from typing import Dict, Any, List
from schemas import FAQPage, ProductPage, ComparisonPage
from utils import StateManager
from agents.base_agent import BaseAgent


class QualityValidationAgent(BaseAgent):
    """
    Agent that validates final output against requirements:
    - FAQ: Must have 15+ Q&As
    - ProductPage: Must have tagline, benefits, specifications
    - ComparisonPage: Must have 4+ comparison rows and verdict
    """
    
    # Validation thresholds (based on assignment requirements)
    MIN_FAQ_ITEMS = 15
    MIN_BENEFITS = 2
    MIN_COMPARISON_ROWS = 4
    
    def __init__(self, state_manager: StateManager, config: Dict[str, Any] = None):
        super().__init__("QualityValidator", state_manager, config)

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates the 3 generated pages against requirements.
        
        Returns:
            Dict with status (PASSED/FAILED), errors, and warnings
        """
        faq = input_data.get("faq")
        product_page = input_data.get("product_page")
        comparison = input_data.get("comparison")
        
        errors = []
        warnings = []
        
        # =====================================================================
        # 1. Validate FAQ Page
        # =====================================================================
        if not isinstance(faq, FAQPage):
            errors.append("FAQ content is not a valid FAQPage object")
        else:
            # Check minimum FAQ count (requirement: 15+)
            faq_count = len(faq.faqs)
            if faq_count < self.MIN_FAQ_ITEMS:
                errors.append(f"FAQ has only {faq_count} items, requirement is {self.MIN_FAQ_ITEMS}+")
            elif faq_count < 20:
                warnings.append(f"FAQ has {faq_count} items (good, but 20+ is excellent)")
            
            # Check all FAQs have both question and answer
            for i, item in enumerate(faq.faqs):
                if not item.question or len(item.question.strip()) < 5:
                    warnings.append(f"FAQ item {i+1} has empty/short question")
                if not item.answer or len(item.answer.strip()) < 10:
                    warnings.append(f"FAQ item {i+1} has empty/short answer")
        
        # =====================================================================
        # 2. Validate Product Page
        # =====================================================================
        if not isinstance(product_page, ProductPage):
            errors.append("Product Page content is not a valid ProductPage object")
        else:
            # Check required creative fields
            if not product_page.tagline or len(product_page.tagline) < 5:
                errors.append("Tagline is missing or too short")
            
            if not product_page.description or len(product_page.description) < 20:
                warnings.append("Description is missing or too short")
            
            # Check benefits count
            benefits_count = len(product_page.key_benefits)
            if benefits_count < self.MIN_BENEFITS:
                errors.append(f"Only {benefits_count} key benefits, need {self.MIN_BENEFITS}+")
            
            # Check specifications
            if len(product_page.specifications) < 2:
                warnings.append("Less than 2 specifications listed")
            
            # Check usage guide
            if not product_page.usage_guide:
                warnings.append("Usage guide is empty")
        
        # =====================================================================
        # 3. Validate Comparison Page
        # =====================================================================
        if not isinstance(comparison, ComparisonPage):
            errors.append("Comparison content is not a valid ComparisonPage object")
        else:
            # Check comparison table
            rows_count = len(comparison.comparison_table)
            if rows_count < self.MIN_COMPARISON_ROWS:
                errors.append(f"Comparison has only {rows_count} rows, need {self.MIN_COMPARISON_ROWS}+")
            
            # Check verdict exists
            if not comparison.verdict or len(comparison.verdict) < 10:
                errors.append("Verdict is missing or too short")
            
            # Check summary
            if not comparison.summary:
                warnings.append("Comparison summary is empty")
            
            # Check product names are different
            if comparison.product_a_name == comparison.product_b_name:
                errors.append("Product A and B have the same name")
        
        # =====================================================================
        # Determine status
        # =====================================================================
        status = "PASSED" if not errors else "FAILED"
        
        self.log_decision("Validation completed", {
            "status": status,
            "error_count": len(errors),
            "warning_count": len(warnings)
        })
        
        return {
            "status": status,
            "errors": errors,
            "warnings": warnings,
            "stats": {
                "faq_count": len(faq.faqs) if isinstance(faq, FAQPage) else 0,
                "benefits_count": len(product_page.key_benefits) if isinstance(product_page, ProductPage) else 0,
                "comparison_rows": len(comparison.comparison_table) if isinstance(comparison, ComparisonPage) else 0
            }
        }

    def validate_input(self, input_data: Any) -> None:
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary containing the 3 pages")
        
        required_keys = ["faq", "product_page", "comparison"]
        for key in required_keys:
            if key not in input_data:
                raise ValueError(f"Missing required key: {key}")
