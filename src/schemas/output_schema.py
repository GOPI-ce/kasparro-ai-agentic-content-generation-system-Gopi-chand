"""
JSON Schema Definitions for Product Marketing Content System

Defines Pydantic models for:
1. Product Data (Input)
2. FAQ Page (Output)
3. Product Page (Output)
4. Comparison Page (Output)
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ============================================================================
# INPUT SCHEMA (Product Data)
# ============================================================================

class ProductData(BaseModel):
    """Schema for product input data (e.g., GlowBoost)."""
    
    product_name: str = Field(..., alias="Product Name")
    concentration: Optional[str] = Field(None, alias="Concentration")
    skin_type: str = Field(..., alias="Skin Type")
    key_ingredients: str = Field(..., alias="Key Ingredients")
    benefits: str = Field(..., alias="Benefits")
    how_to_use: str = Field(..., alias="How to Use")
    side_effects: Optional[str] = Field(None, alias="Side Effects")
    price: str = Field(..., alias="Price")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "Product Name": "GlowBoost Vitamin C Serum",
                "Concentration": "10% Vitamin C",
                "Skin Type": "Oily, Combination",
                "Key Ingredients": "Vitamin C, Hyaluronic Acid",
                "Benefits": "Brightening, Fades dark spots",
                "How to Use": "Apply 2-3 drops in morning",
                "Side Effects": "Mild tingling",
                "Price": "₹699"
            }
        }

# ============================================================================
# OUTPUT SCHEMAS
# ============================================================================

# 1. FAQ Page
class FAQItem(BaseModel):
    question: str
    answer: str

class FAQPage(BaseModel):
    product_name: str
    faqs: List[FAQItem]

# 2. Product Page
class ProductSpec(BaseModel):
    name: str
    value: str

class ProductPage(BaseModel):
    title: str
    price: str
    tagline: str
    description: str
    key_benefits: List[str]
    specifications: List[ProductSpec]
    usage_guide: str
    safety_info: Optional[str] = None

# 3. Comparison Page
class ComparisonRow(BaseModel):
    feature: str
    product_a_value: str
    product_b_value: str
    winner: Optional[str] = None  # "A", "B", or "Tie"

class ComparisonPage(BaseModel):
    product_a_name: str
    product_b_name: str
    summary: str
    comparison_table: List[ComparisonRow]
    verdict: str
