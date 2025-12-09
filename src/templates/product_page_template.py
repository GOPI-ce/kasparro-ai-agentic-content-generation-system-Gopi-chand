"""
Product Page Template

Defines the structure and layout for product description pages.
Includes hero section, benefits, specifications, and usage guide.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ProductPageTemplate:
    """
    Template structure for product description pages.
    
    Sections:
    - Hero (title, tagline, price)
    - Benefits listing
    - Specifications table
    - Usage guide
    - Safety information
    """
    
    # Template metadata
    TEMPLATE_NAME = "product_page"
    TEMPLATE_VERSION = "1.0"
    
    # Required fields
    REQUIRED_FIELDS = [
        "title",
        "price",
        "tagline",
        "description",
        "key_benefits",
        "specifications",
        "usage_guide"
    ]
    
    # Section structure
    SECTIONS = {
        "hero": {
            "layout": "centered",
            "includes": ["title", "tagline", "price", "cta_button"]
        },
        "description": {
            "layout": "full-width",
            "max_length": 500
        },
        "benefits": {
            "layout": "grid",
            "columns": 2,
            "icon_style": "checkmark"
        },
        "specifications": {
            "layout": "table",
            "columns": ["Attribute", "Value"]
        },
        "usage": {
            "layout": "steps",
            "numbered": True
        },
        "safety": {
            "layout": "alert",
            "style": "warning"
        }
    }
    
    @classmethod
    def apply(cls, title: str, price: str, tagline: str, description: str,
              key_benefits: List[str], specifications: List[Dict[str, str]],
              usage_guide: str, safety_info: str = None) -> Dict[str, Any]:
        """
        Apply template to generate product page structure.
        
        Args:
            title: Product title/name
            price: Product price (formatted string)
            tagline: Marketing tagline
            description: Product description
            key_benefits: List of benefit strings
            specifications: List of spec dicts with name/value
            usage_guide: Usage instructions text
            safety_info: Optional safety information
            
        Returns:
            Complete product page structure
        """
        return {
            "template_name": cls.TEMPLATE_NAME,
            "template_version": cls.TEMPLATE_VERSION,
            "hero": {
                "title": title,
                "tagline": tagline,
                "price": price,
                "cta_text": "Add to Cart"
            },
            "description": {
                "text": description,
                "layout": cls.SECTIONS["description"]["layout"]
            },
            "benefits": {
                "title": "Key Benefits",
                "items": [{"text": b, "icon": "✓"} for b in key_benefits],
                "layout": cls.SECTIONS["benefits"]["layout"]
            },
            "specifications": {
                "title": "Product Specifications",
                "rows": specifications,
                "layout": cls.SECTIONS["specifications"]["layout"]
            },
            "usage": {
                "title": "How to Use",
                "instructions": usage_guide,
                "layout": cls.SECTIONS["usage"]["layout"]
            },
            "safety": {
                "title": "Safety Information",
                "content": safety_info or "Please perform a patch test before first use.",
                "style": cls.SECTIONS["safety"]["style"]
            },
            "metadata": {
                "benefits_count": len(key_benefits),
                "specs_count": len(specifications)
            }
        }


# Export convenience function
def create_product_page(title: str, price: str, tagline: str, description: str,
                        key_benefits: List[str], specifications: List[Dict[str, str]],
                        usage_guide: str, safety_info: str = None) -> Dict[str, Any]:
    """Convenience function to create product page from template."""
    return ProductPageTemplate.apply(
        title, price, tagline, description,
        key_benefits, specifications, usage_guide, safety_info
    )
