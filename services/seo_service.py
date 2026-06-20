import re
from bs4 import BeautifulSoup

STOP_WORDS = {
    "and", "or", "but", "for", "with", "the", "a", "an", "in", "on", "at", "to", 
    "by", "of", "from", "up", "about", "into", "over", "after", "is", "are", 
    "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", 
    "did", "will", "would", "shall", "should", "can", "could", "may", "might", 
    "must", "this", "that", "these", "those", "i", "you", "he", "she", "it", 
    "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "its", 
    "our", "their"
}

def generate_tags(title, category):
    """
    Generates unique, comma-separated tags based on product title and category.
    Filters out common stop words and keeps keywords.
    """
    tags = set()
    
    # Process category
    if category:
        # Split hierarchical categories like "Electronics > Audio > Headphones"
        cat_parts = re.split(r'\s*>\s*', category)
        for part in cat_parts:
            part_cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', part).strip().lower()
            if part_cleaned:
                tags.add(part_cleaned)
                
    # Process title
    if title:
        title_cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', title).strip().lower()
        words = title_cleaned.split()
        for w in words:
            if len(w) > 3 and w not in STOP_WORDS and not w.isdigit():
                tags.add(w)
                
    # Convert to comma separated string
    return ", ".join(sorted(list(tags)))

def generate_seo_title(title):
    """
    Generates a clean SEO title under 70 characters.
    """
    if not title:
        return "Product Detail"
    cleaned = re.sub(r'\s+', ' ', title).strip()
    if len(cleaned) <= 70:
        return cleaned
    # Truncate at word boundary if possible
    truncated = cleaned[:67]
    last_space = truncated.rfind(' ')
    if last_space > 40:
        return truncated[:last_space] + "..."
    return truncated + "..."

def generate_seo_description(title, description):
    """
    Generates a short, clean SEO description under 160 characters.
    Strips HTML tags first.
    """
    if not description:
        if title:
            desc_text = f"Buy {title} online at the best price. Quality guaranteed, fast shipping, and friendly customer support. Order yours today!"
        else:
            desc_text = "Check out our high-quality shop products. Affordable pricing, premium materials, and excellent service. Shop now!"
    else:
        # Clean HTML
        if "<" in description and ">" in description:
            soup = BeautifulSoup(description, "lxml")
            desc_text = soup.get_text(separator=" ")
        else:
            desc_text = description
            
    # Clean spacing and newlines
    desc_text = re.sub(r'\s+', ' ', desc_text).strip()
    
    # Truncate to 157 chars + "..." if longer than 160
    if len(desc_text) <= 160:
        return desc_text
        
    truncated = desc_text[:157]
    last_space = truncated.rfind(' ')
    if last_space > 100:
        return truncated[:last_space] + "..."
    return truncated + "..."
