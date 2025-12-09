"""
Comparison Page Template

Defines the structure for product comparison pages.
Includes comparison table, feature analysis, and verdict.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ComparisonTemplate:
    """
    Template structure for product comparison pages.
    
    Sections:
    - Header with product names
    - Comparison table
    - Feature-by-feature analysis
    - Verdict/recommendation
    """
    
    # Template metadata
    TEMPLATE_NAME = "comparison_page"
    TEMPLATE_VERSION = "1.0"
    
    # Required fields
    REQUIRED_FIELDS = [
        "product_a_name",
        "product_b_name",
        "comparison_table",
        "verdict"
    ]
    
    # Comparison features to include
    COMPARISON_FEATURES = [
        {"id": "price", "label": "Price", "icon": "💰"},
        {"id": "concentration", "label": "Active Concentration", "icon": "🧪"},
        {"id": "ingredients", "label": "Key Ingredients", "icon": "🌿"},
        {"id": "skin_type", "label": "Skin Type", "icon": "👤"},
        {"id": "benefits", "label": "Benefits", "icon": "✨"},
        {"id": "side_effects", "label": "Side Effects", "icon": "⚠️"}
    ]
    
    # Winner indicators
    WINNER_ICONS = {
        "A": "🏆",
        "B": "🏆",
        "Tie": "🤝"
    }
    
    @classmethod
    def apply(cls, product_a_name: str, product_b_name: str,
              comparison_table: List[Dict[str, str]], summary: str,
              verdict: str) -> Dict[str, Any]:
        """
        Apply template to generate comparison page structure.
        
        Args:
            product_a_name: Name of Product A
            product_b_name: Name of Product B
            comparison_table: List of comparison rows
            summary: Executive summary of comparison
            verdict: Final recommendation/verdict
            
        Returns:
            Complete comparison page structure
        """
        # Enhance comparison rows with icons
        enhanced_rows = []
        for row in comparison_table:
            feature = row.get("feature", "")
            winner = row.get("winner", "Tie")
            
            # Find matching feature config
            feature_config = next(
                (f for f in cls.COMPARISON_FEATURES if f["label"].lower() in feature.lower()),
                {"icon": "📊"}
            )
            
            enhanced_rows.append({
                "feature": feature,
                "feature_icon": feature_config.get("icon", "📊"),
                "product_a_value": row.get("product_a_value", "N/A"),
                "product_b_value": row.get("product_b_value", "N/A"),
                "winner": winner,
                "winner_icon": cls.WINNER_ICONS.get(winner, "")
            })
        
        # Calculate overall scores
        a_wins = sum(1 for row in comparison_table if row.get("winner") == "A")
        b_wins = sum(1 for row in comparison_table if row.get("winner") == "B")
        ties = sum(1 for row in comparison_table if row.get("winner") == "Tie")
        
        return {
            "template_name": cls.TEMPLATE_NAME,
            "template_version": cls.TEMPLATE_VERSION,
            "header": {
                "title": f"{product_a_name} vs {product_b_name}",
                "subtitle": "Side-by-Side Product Comparison"
            },
            "products": {
                "product_a": {"name": product_a_name, "position": "left"},
                "product_b": {"name": product_b_name, "position": "right"}
            },
            "summary": {
                "title": "Comparison Summary",
                "content": summary
            },
            "comparison_table": {
                "headers": ["Feature", product_a_name, product_b_name, "Winner"],
                "rows": enhanced_rows
            },
            "scores": {
                "product_a_wins": a_wins,
                "product_b_wins": b_wins,
                "ties": ties,
                "total_features": len(comparison_table)
            },
            "verdict": {
                "title": "Our Verdict",
                "content": verdict,
                "recommendation": product_a_name if a_wins > b_wins else (
                    product_b_name if b_wins > a_wins else "Either product"
                )
            },
            "metadata": {
                "features_compared": len(comparison_table),
                "comparison_type": "product_vs_product"
            }
        }


# Export convenience function
def create_comparison_page(product_a_name: str, product_b_name: str,
                           comparison_table: List[Dict[str, str]], 
                           summary: str, verdict: str) -> Dict[str, Any]:
    """Convenience function to create comparison page from template."""
    return ComparisonTemplate.apply(
        product_a_name, product_b_name, comparison_table, summary, verdict
    )
