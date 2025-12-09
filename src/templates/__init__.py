"""
Template Package

Provides explicit template definitions for all generated pages:
- FAQ Page Template
- Product Page Template  
- Comparison Page Template
"""

from templates.faq_template import FAQTemplate, create_faq_page
from templates.product_page_template import ProductPageTemplate, create_product_page
from templates.comparison_template import ComparisonTemplate, create_comparison_page

__all__ = [
    "FAQTemplate",
    "ProductPageTemplate", 
    "ComparisonTemplate",
    "create_faq_page",
    "create_product_page",
    "create_comparison_page"
]
