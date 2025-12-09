"""
Content Logic Blocks

Reusable transformation functions for converting product data into marketing copy.
These are the building blocks used by templates and content generators.
"""

from typing import Dict, List, Any, Optional
import re


# =============================================================================
# PRICE FORMATTING
# =============================================================================

def format_price(price: str, currency_symbol: str = "₹") -> Dict[str, Any]:
    """
    Parse and format price string consistently.
    
    Args:
        price: Raw price string (e.g., "₹699", "699", "Rs. 699")
        currency_symbol: Desired currency symbol
        
    Returns:
        Dict with formatted price info
    """
    # Extract numeric value
    numeric = re.sub(r'[^\d.]', '', price)
    try:
        value = float(numeric)
    except ValueError:
        value = 0.0
    
    return {
        "display": f"{currency_symbol}{int(value)}" if value == int(value) else f"{currency_symbol}{value}",
        "numeric": value,
        "currency": currency_symbol,
        "original": price
    }


def compare_prices(price_a: str, price_b: str) -> Dict[str, Any]:
    """
    Compare two prices and determine the better value.
    
    Args:
        price_a: Price string for product A
        price_b: Price string for product B
        
    Returns:
        Comparison result with winner
    """
    parsed_a = format_price(price_a)
    parsed_b = format_price(price_b)
    
    diff = parsed_a["numeric"] - parsed_b["numeric"]
    
    return {
        "product_a": parsed_a,
        "product_b": parsed_b,
        "difference": abs(diff),
        "winner": "A" if diff < 0 else ("B" if diff > 0 else "Tie"),
        "winner_reason": "Lower price" if diff != 0 else "Same price"
    }


# =============================================================================
# INGREDIENT FORMATTING
# =============================================================================

def format_ingredients(ingredients_str: str) -> List[Dict[str, str]]:
    """
    Parse ingredient string into structured list.
    
    Args:
        ingredients_str: Comma-separated ingredient string
        
    Returns:
        List of ingredient dicts with name and optional details
    """
    if not ingredients_str:
        return []
    
    # Split by common delimiters
    raw_list = re.split(r'[,;]', ingredients_str)
    
    ingredients = []
    for item in raw_list:
        item = item.strip()
        if not item:
            continue
            
        # Check for concentration notation (e.g., "10% Vitamin C")
        match = re.match(r'(\d+%?)\s+(.+)', item)
        if match:
            ingredients.append({
                "name": match.group(2).strip(),
                "concentration": match.group(1),
                "display": item
            })
        else:
            ingredients.append({
                "name": item,
                "concentration": None,
                "display": item
            })
    
    return ingredients


def compare_ingredients(ingredients_a: str, ingredients_b: str) -> Dict[str, Any]:
    """
    Compare ingredient lists between two products.
    
    Args:
        ingredients_a: Ingredients string for product A
        ingredients_b: Ingredients string for product B
        
    Returns:
        Comparison with common and unique ingredients
    """
    list_a = {i["name"].lower() for i in format_ingredients(ingredients_a)}
    list_b = {i["name"].lower() for i in format_ingredients(ingredients_b)}
    
    common = list_a & list_b
    only_a = list_a - list_b
    only_b = list_b - list_a
    
    return {
        "common": list(common),
        "only_product_a": list(only_a),
        "only_product_b": list(only_b),
        "similarity_score": len(common) / max(len(list_a | list_b), 1)
    }


# =============================================================================
# BENEFITS FORMATTING
# =============================================================================

def generate_benefit_bullets(benefits_str: str, max_bullets: int = 5) -> List[Dict[str, str]]:
    """
    Convert benefits string into formatted bullet points.
    
    Args:
        benefits_str: Raw benefits string (comma-separated or paragraph)
        max_bullets: Maximum number of bullets to generate
        
    Returns:
        List of benefit bullet dicts
    """
    if not benefits_str:
        return []
    
    # Split by common delimiters
    raw_list = re.split(r'[,;•\n]', benefits_str)
    
    bullets = []
    for item in raw_list[:max_bullets]:
        item = item.strip()
        if not item:
            continue
        
        # Capitalize first letter and add period if missing
        formatted = item[0].upper() + item[1:] if item else item
        if formatted and not formatted.endswith(('.', '!', '?')):
            formatted += '.'
        
        bullets.append({
            "text": formatted,
            "icon": "✓",
            "highlight": len(item) < 30  # Short benefits can be highlighted
        })
    
    return bullets


def categorize_benefits(benefits_str: str) -> Dict[str, List[str]]:
    """
    Categorize benefits into skin-related categories.
    
    Args:
        benefits_str: Raw benefits string
        
    Returns:
        Dict with categorized benefits
    """
    bullets = generate_benefit_bullets(benefits_str, max_bullets=10)
    
    categories = {
        "appearance": [],
        "treatment": [],
        "protection": [],
        "other": []
    }
    
    # Keywords for categorization
    appearance_keywords = ["bright", "glow", "radiant", "smooth", "soft", "even tone"]
    treatment_keywords = ["fade", "reduce", "fight", "anti", "heal", "repair", "dark spot"]
    protection_keywords = ["protect", "shield", "barrier", "hydrat", "moisture"]
    
    for bullet in bullets:
        text_lower = bullet["text"].lower()
        
        if any(kw in text_lower for kw in appearance_keywords):
            categories["appearance"].append(bullet["text"])
        elif any(kw in text_lower for kw in treatment_keywords):
            categories["treatment"].append(bullet["text"])
        elif any(kw in text_lower for kw in protection_keywords):
            categories["protection"].append(bullet["text"])
        else:
            categories["other"].append(bullet["text"])
    
    return categories


# =============================================================================
# COMPARISON TABLE BUILDING
# =============================================================================

def create_comparison_row(feature: str, value_a: str, value_b: str, 
                          winner_logic: str = "auto") -> Dict[str, str]:
    """
    Build a comparison table row with automatic winner detection.
    
    Args:
        feature: Feature being compared
        value_a: Product A's value
        value_b: Product B's value
        winner_logic: "auto", "lower_better", "higher_better", or explicit "A"/"B"/"Tie"
        
    Returns:
        Comparison row dict
    """
    winner = "Tie"
    
    if winner_logic in ["A", "B", "Tie"]:
        winner = winner_logic
    elif winner_logic == "lower_better":
        # Extract numbers and compare
        num_a = float(re.sub(r'[^\d.]', '', value_a) or 0)
        num_b = float(re.sub(r'[^\d.]', '', value_b) or 0)
        winner = "A" if num_a < num_b else ("B" if num_b < num_a else "Tie")
    elif winner_logic == "higher_better":
        num_a = float(re.sub(r'[^\d.]', '', value_a) or 0)
        num_b = float(re.sub(r'[^\d.]', '', value_b) or 0)
        winner = "A" if num_a > num_b else ("B" if num_b > num_a else "Tie")
    
    return {
        "feature": feature,
        "product_a_value": value_a,
        "product_b_value": value_b,
        "winner": winner
    }


def build_comparison_table(product_a: Dict[str, Any], product_b: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Build complete comparison table from two product data dicts.
    
    Handles both Pydantic field names (snake_case) and aliases (Title Case).
    
    Args:
        product_a: Product A data
        product_b: Product B data
        
    Returns:
        List of comparison rows
    """
    def get_value(product: Dict, *keys: str) -> str:
        """Get value by trying multiple key formats."""
        for key in keys:
            if key in product and product[key]:
                return str(product[key])
        return "N/A"
    
    rows = []
    
    # Price comparison (lower is better)
    rows.append(create_comparison_row(
        "Price",
        get_value(product_a, "price", "Price"),
        get_value(product_b, "price", "Price"),
        "lower_better"
    ))
    
    # Concentration (higher is often better for serums)
    rows.append(create_comparison_row(
        "Concentration",
        get_value(product_a, "concentration", "Concentration"),
        get_value(product_b, "concentration", "Concentration"),
        "higher_better"
    ))
    
    # Ingredients (no clear winner)
    rows.append(create_comparison_row(
        "Key Ingredients",
        get_value(product_a, "key_ingredients", "Key Ingredients"),
        get_value(product_b, "key_ingredients", "Key Ingredients"),
        "Tie"
    ))
    
    # Skin Type (no clear winner)
    rows.append(create_comparison_row(
        "Suitable For",
        get_value(product_a, "skin_type", "Skin Type"),
        get_value(product_b, "skin_type", "Skin Type"),
        "Tie"
    ))
    
    return rows


# =============================================================================
# TEMPLATE APPLICATION
# =============================================================================

def apply_template(template_struct: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generic template application - fills placeholders in template with data.
    
    Args:
        template_struct: Template structure with {placeholder} markers
        data: Data dict with values to fill
        
    Returns:
        Filled template structure
    """
    import copy
    result = copy.deepcopy(template_struct)
    
    def fill_placeholders(obj, data):
        if isinstance(obj, str):
            # Replace {key} patterns with data values
            for key, value in data.items():
                obj = obj.replace(f"{{{key}}}", str(value))
            return obj
        elif isinstance(obj, dict):
            return {k: fill_placeholders(v, data) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [fill_placeholders(item, data) for item in obj]
        return obj
    
    return fill_placeholders(result, data)


# =============================================================================
# SKIN TYPE PARSING
# =============================================================================

def parse_skin_types(skin_type_str: str) -> List[str]:
    """
    Parse skin type string into clean list.
    
    Args:
        skin_type_str: Raw skin type string (e.g., "Oily, Combination")
        
    Returns:
        List of skin types
    """
    if not skin_type_str:
        return []
    
    types = re.split(r'[,;&/]', skin_type_str)
    return [t.strip().title() for t in types if t.strip()]


def skin_type_match(type_a: str, type_b: str) -> Dict[str, Any]:
    """
    Check overlap between two skin type specifications.
    
    Args:
        type_a: Skin types for product A
        type_b: Skin types for product B
        
    Returns:
        Match analysis
    """
    list_a = set(t.lower() for t in parse_skin_types(type_a))
    list_b = set(t.lower() for t in parse_skin_types(type_b))
    
    common = list_a & list_b
    all_types = list_a | list_b
    
    return {
        "common_types": list(common),
        "product_a_only": list(list_a - list_b),
        "product_b_only": list(list_b - list_a),
        "overlap_ratio": len(common) / max(len(all_types), 1)
    }
