import re
from bs4 import BeautifulSoup

SPAM_TERMS = [
    r"free shipping", r"in stock", r"buy now", r"best seller", r"amazon\.com", 
    r"eligible for refund", r"warranty included", r"click here", r"order today",
    r"top rated", r"lowest price", r"save \d+%", r"off discount"
]

def clean_text_of_spam(text):
    """Remove promotional spam phrases from text."""
    if not text:
        return ""
    cleaned = text
    for term in SPAM_TERMS:
        cleaned = re.sub(term, "", cleaned, flags=re.IGNORECASE)
    # Remove double spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def clean_description_html(raw_html_or_text):
    """
    Cleans messy HTML or plain text into a clean HTML format.
    Ensures no scripts or styling tags remain, and formats spacing.
    """
    if not raw_html_or_text:
        return ""
        
    # Check if input is HTML or plain text
    if "<" in raw_html_or_text and ">" in raw_html_or_text:
        soup = BeautifulSoup(raw_html_or_text, "lxml")
        # Remove script and style tags
        for element in soup(["script", "style", "iframe", "noscript"]):
            element.decompose()
        text = soup.get_text(separator="\n")
    else:
        text = raw_html_or_text

    # Split lines and clean them
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # Remove spam lines
    cleaned_lines = []
    for line in lines:
        cleaned_line = clean_text_of_spam(line)
        if cleaned_line and len(cleaned_line) > 3:
            cleaned_lines.append(cleaned_line)

    return "\n".join(cleaned_lines)

def rewrite_product_data(raw_title, raw_description, vendor=""):
    """
    Rewrites the title and description to make them unique and Shopify-ready.
    Converts plain/dirty text descriptions into rich HTML paragraphs and lists.
    """
    # 1. Clean Title
    cleaned_title = clean_text_of_spam(raw_title)
    # Reformat Title (e.g. Title Case, remove brackets/parentheses which often contain shipping info)
    cleaned_title = re.sub(r'\[.*?\]|\(.*?\)', '', cleaned_title)  # Remove brackets and parens
    cleaned_title = re.sub(r'\s+', ' ', cleaned_title).strip()
    
    # Capitalize title correctly
    words = cleaned_title.split(" ")
    title_words = []
    for i, w in enumerate(words):
        if i == 0 or len(w) > 3 or w.lower() not in ["and", "or", "but", "for", "with", "the", "a", "an", "in", "on", "at", "to", "by", "of"]:
            title_words.append(w.capitalize())
        else:
            title_words.append(w.lower())
    rewritten_title = " ".join(title_words)
    if not rewritten_title:
        rewritten_title = "New Shopify Product"

    # 2. Clean and Rewrite Description to HTML
    clean_desc_text = clean_description_html(raw_description)
    paragraphs = [p.strip() for p in clean_desc_text.split("\n") if p.strip()]

    # Construct premium HTML
    html_out = []
    
    # Intro sentence
    intro_words = f"Introducing the premium {rewritten_title}."
    if vendor:
        intro_words = f"Brought to you by {vendor}, the {rewritten_title} is designed to elevate your experience."
        
    html_out.append(f"<p>{intro_words}</p>")

    # Group remaining lines into paragraphs and features
    features = []
    other_paragraphs = []
    
    for p in paragraphs:
        # Check if line looks like a bullet feature (short, contains dash, bullet, or colon)
        if len(p) < 120 and (p.startswith("-") or p.startswith("*") or p.startswith("•") or ":" in p or "feature" in p.lower()):
            # Clean bullet indicator
            feat = re.sub(r'^[\-\*•\s]+', '', p).strip()
            if feat:
                features.append(feat)
        else:
            other_paragraphs.append(p)

    # Output details
    if other_paragraphs:
        # Take the longest paragraph as the main body description
        main_desc = max(other_paragraphs, key=len)
        html_out.append(f"<p>{main_desc}</p>")
        
        # Add another paragraph if available
        for p in other_paragraphs:
            if p != main_desc and len(p) > 50:
                html_out.append(f"<p>{p}</p>")
                break
    else:
        html_out.append(f"<p>Discover high-quality craftsmanship and exceptional performance. Ideal for daily use, this product is built to last and exceed expectations.</p>")

    # Add Features section if found
    if features:
        html_out.append("<h3>Key Features & Benefits</h3>")
        html_out.append("<ul>")
        for feat in features[:6]: # Limit to 6 key features
            html_out.append(f"  <li>{feat}</li>")
        html_out.append("</ul>")
    else:
        # Default features
        html_out.append("<h3>Product Features</h3>")
        html_out.append("<ul>")
        html_out.append("  <li>Premium quality materials for long-lasting durability</li>")
        html_out.append("  <li>Designed with utility and style in mind</li>")
        html_out.append("  <li>Easy to use and integrate into your routine</li>")
        html_out.append("</ul>")

    # Add Shopify standard closing info
    html_out.append("<h3>Why Choose This?</h3>")
    html_out.append(f"<p>Upgrade your collection today. The {rewritten_title} offers unmatched reliability, visual appeal, and value, making it a perfect choice for smart shoppers.</p>")

    rewritten_body_html = "\n".join(html_out)

    return rewritten_title, rewritten_body_html
