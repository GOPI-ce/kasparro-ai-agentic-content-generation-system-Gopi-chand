"""
FAQ Page Template

Defines the structure and layout for FAQ page generation.
Template includes placeholders for dynamic content insertion.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class FAQTemplate:
    """
    Template structure for FAQ pages.
    
    Sections:
    - Header with product name
    - Categorized Q&A sections
    - Footer with additional info
    """
    
    # Template metadata
    TEMPLATE_NAME = "faq_page"
    TEMPLATE_VERSION = "1.0"
    
    # Required fields
    REQUIRED_FIELDS = [
        "product_name",
        "faqs"
    ]
    
    # Section structure
    SECTIONS = {
        "header": {
            "title": "Frequently Asked Questions",
            "subtitle_template": "Common questions about {product_name}"
        },
        "categories": [
            {
                "id": "informational",
                "title": "Product Information",
                "icon": "ℹ️"
            },
            {
                "id": "safety",
                "title": "Safety & Side Effects",
                "icon": "⚠️"
            },
            {
                "id": "usage",
                "title": "How to Use",
                "icon": "📋"
            },
            {
                "id": "purchase",
                "title": "Pricing & Purchase",
                "icon": "🛒"
            },
            {
                "id": "comparison",
                "title": "Product Comparisons",
                "icon": "⚖️"
            }
        ],
        "footer": {
            "contact_text": "Still have questions? Contact our support team.",
            "disclaimer": "This information is for educational purposes only."
        }
    }
    
    @classmethod
    def apply(cls, product_name: str, faqs: List[Dict[str, str]], 
              categorized_questions: Dict[str, List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Apply template to generate FAQ page structure.
        
        Args:
            product_name: Name of the product
            faqs: List of FAQ items (question, answer dicts)
            categorized_questions: Optional categorized questions from QuestionGenerator
            
        Returns:
            Complete FAQ page structure
        """
        # Build header
        header = {
            "title": cls.SECTIONS["header"]["title"],
            "subtitle": cls.SECTIONS["header"]["subtitle_template"].format(
                product_name=product_name
            )
        }
        
        # Organize FAQs by category if categorized_questions provided
        if categorized_questions:
            organized_faqs = []
            for category in cls.SECTIONS["categories"]:
                category_key = category["id"].capitalize()
                if category_key in categorized_questions:
                    for qa in categorized_questions[category_key]:
                        organized_faqs.append({
                            "category": category["title"],
                            "category_icon": category["icon"],
                            "question": qa["question"],
                            "answer": qa["answer"]
                        })
            faqs = organized_faqs if organized_faqs else faqs
        
        return {
            "template_name": cls.TEMPLATE_NAME,
            "template_version": cls.TEMPLATE_VERSION,
            "product_name": product_name,
            "header": header,
            "faqs": faqs,
            "footer": cls.SECTIONS["footer"],
            "metadata": {
                "total_questions": len(faqs),
                "categories_used": list(set(f.get("category", "General") for f in faqs))
            }
        }


# Export convenience function
def create_faq_page(product_name: str, faqs: List[Dict[str, str]], 
                    categorized_questions: Dict = None) -> Dict[str, Any]:
    """Convenience function to create FAQ page from template."""
    return FAQTemplate.apply(product_name, faqs, categorized_questions)
