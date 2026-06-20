import re
from sqlalchemy import func
from database.db import ShopifyProduct

COLOR_MAP = {
    "black": "BLK",
    "white": "WHT",
    "pink": "PNK",
    "blue": "BLU",
    "red": "RED",
    "green": "GRN",
    "yellow": "YLW",
    "orange": "ORG",
    "purple": "PRP",
    "silver": "SLV",
    "gold": "GLD",
    "grey": "GRY",
    "gray": "GRY",
    "brown": "BRN",
    "beige": "BGE",
    "navy": "NVY",
    "copper": "CPR",
    "bronze": "BRZ",
    "multicolor": "MUL",
    "rainbow": "RNB",
    "transparent": "CLR",
    "clear": "CLR"
}

def create_handle(title):
    """
    Converts product title into lowercase URL handle.
    Removes special characters, replaces spaces with hyphens, and avoids double hyphens.
    """
    if not title:
        return ""
    # Lowercase
    cleaned = title.lower()
    # Remove apostrophes
    cleaned = cleaned.replace("'", "").replace("’", "")
    # Replace non-alphanumeric characters with spaces
    cleaned = re.sub(r'[^a-z0-9\-]', ' ', cleaned)
    # Replace spaces with hyphens
    cleaned = re.sub(r'\s+', '-', cleaned)
    # Remove leading/trailing and consecutive hyphens
    cleaned = re.sub(r'-+', '-', cleaned).strip("-")
    return cleaned

def get_category_abbrev(category):
    """Derives a 3-5 character uppercase category abbreviation."""
    if not category:
        return "GEN"
    # Clean category (keep alphanumeric, space, etc.)
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', category).upper()
    if not cleaned:
        return "GEN"
    # Take first 4 characters, or full length if shorter
    return cleaned[:4]

def get_color_abbrev(color):
    """Derives a 3 character uppercase color abbreviation."""
    if not color:
        return "GEN"
    color_cleaned = re.sub(r'[^a-zA-Z]', '', color).strip().lower()
    if not color_cleaned:
        return "GEN"
        
    # Check lookup map
    if color_cleaned in COLOR_MAP:
        return COLOR_MAP[color_cleaned]
        
    # Fallback: remove vowels and take first 3 letters, or just take first 3 letters
    vowels = "aeiou"
    consonants = "".join([c for c in color_cleaned if c not in vowels])
    if len(consonants) >= 3:
        return consonants[:3].upper()
    return color_cleaned[:3].upper().ljust(3, "X")

def generate_sku(title, category, color, prefix="TNB", db_session=None):
    """
    Generates a unique SKU in format PREFIX-CATEGORY-COLOR-001.
    Checks the database to find the next available sequence number.
    """
    # 1. Clean inputs
    prefix = re.sub(r'[^a-zA-Z0-9]', '', prefix).upper()
    if not prefix:
        prefix = "TNB"
        
    cat_abbrev = get_category_abbrev(category)
    color_abbrev = get_color_abbrev(color)
    
    sku_pattern_prefix = f"{prefix}-{cat_abbrev}-{color_abbrev}-"
    
    # Default sequence starts at 1
    next_num = 1
    
    if db_session:
        # Query database to find existing SKUs matching this pattern
        try:
            # We search for SKUs starting with sku_pattern_prefix
            query = db_session.query(ShopifyProduct.variant_sku).filter(
                ShopifyProduct.variant_sku.like(f"{sku_pattern_prefix}%")
            ).all()
            
            nums = []
            for row in query:
                sku_str = row[0]
                if not sku_str:
                    continue
                # Extract sequence number from the end (e.g. TNB-HEAD-BLK-002 -> 2)
                parts = sku_str.split("-")
                if parts and parts[-1].isdigit():
                    nums.append(int(parts[-1]))
            
            if nums:
                next_num = max(nums) + 1
        except Exception as e:
            # Fallback in case of database issue
            pass
            
    # Format sequence number as 3 digits
    sku_val = f"{sku_pattern_prefix}{str(next_num).zfill(3)}"
    return sku_val
