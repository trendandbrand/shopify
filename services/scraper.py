import re
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger("scraper")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def clean_html(html_content):
    """Remove script, style, and iframe tags from html."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "lxml")
    for script in soup(["script", "style", "iframe"]):
        script.decompose()
    return str(soup)

def parse_price(price_str):
    """Clean and extract float value from a price string."""
    if not price_str:
        return 0.0
    # Remove currency symbols and comma separators
    cleaned = re.sub(r'[^\d\.]', '', price_str)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def scrape_product_url(url, delay=1.0):
    """
    Attempts to scrape product details from a given URL using requests and BeautifulSoup.
    Enforces a delay to avoid rate limiting.
    """
    time.sleep(delay)
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    result = {
        "source_url": url,
        "raw_title": "",
        "raw_price": 0.0,
        "raw_description": "",
        "raw_images": [],
        "raw_vendor": "",
        "raw_category": "",
        "extraction_status": "Needs Manual Entry"
    }

    # Basic URL validation
    try:
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            logger.warning(f"Invalid URL: {url}")
            return result
    except Exception:
        logger.warning(f"Error parsing URL: {url}")
        return result

    # Check for Amazon or other known protected sites to set warning early
    is_amazon = "amazon.com" in parsed_url.netloc or "amazon." in parsed_url.netloc
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch {url}. Status code: {response.status_code}")
            return result
            
        soup = BeautifulSoup(response.content, "lxml")
        
        # 1. Title Extraction
        title = ""
        # Try og:title
        og_title = soup.find("meta", property="og:title") or soup.find("meta", name="twitter:title")
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        # Fallback to page title tag
        if not title and soup.title:
            title = soup.title.string.strip()
        # Fallback to first h1
        if not title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text().strip()
        
        # 2. Price Extraction
        price = 0.0
        price_candidates = []
        # Try metadata
        meta_price = (
            soup.find("meta", property="product:price:amount") or 
            soup.find("meta", property="og:price:amount") or 
            soup.find("meta", itemprop="price")
        )
        if meta_price and meta_price.get("content"):
            price = parse_price(meta_price["content"])
        
        if price == 0.0:
            # Look in page text using common selectors
            for selector in [
                ".price", "#price", ".product-price", ".current-price", 
                "[itemprop='price']", ".a-price-whole", ".price-item--sale"
            ]:
                el = soup.select_one(selector)
                if el:
                    price_candidates.append(el.get_text())
            
            for candidate in price_candidates:
                parsed = parse_price(candidate)
                if parsed > 0.0:
                    price = parsed
                    break

        # 3. Images Extraction
        images = []
        # Try og:image
        og_image = soup.find("meta", property="og:image") or soup.find("meta", name="twitter:image")
        if og_image and og_image.get("content"):
            images.append(og_image["content"])
            
        # Try scanning image tags with product hints
        img_tags = soup.find_all("img")
        for img in img_tags:
            src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            if not src:
                continue
            # Resolve relative URLs
            src = urllib.parse.urljoin(url, src)
            
            # Skip tiny images / icons / indicators
            alt = (img.get("alt") or "").lower()
            src_lower = src.lower()
            if any(term in src_lower or term in alt for term in ["logo", "icon", "spinner", "badge", "cart", "arrow"]):
                continue
            
            if src not in images and src.startswith("https://"):
                images.append(src)
                
        # Limit to first 10 images
        images = images[:10]

        # 4. Description Extraction
        description = ""
        # Try og:description
        og_desc = soup.find("meta", property="og:description") or soup.find("meta", name="description")
        if og_desc and og_desc.get("content"):
            description = og_desc["content"].strip()
            
        # Try finding standard description blocks
        desc_div = (
            soup.find("div", class_="product-description") or 
            soup.find("div", id="description") or 
            soup.find("div", class_="description") or
            soup.find("div", itemprop="description")
        )
        if desc_div:
            # We preserve some basic layout or text
            desc_text = desc_div.get_text(separator="\n").strip()
            if len(desc_text) > len(description):
                description = desc_text
                
        # 5. Vendor Extraction
        vendor = ""
        # Try og:brand or brand name
        og_brand = soup.find("meta", property="product:brand") or soup.find("meta", property="og:brand")
        if og_brand and og_brand.get("content"):
            vendor = og_brand["content"].strip()
        if not vendor:
            # Try to infer vendor from domain name
            vendor = parsed_url.netloc.replace("www.", "").split(".")[0].capitalize()

        # 6. Category Extraction
        category = ""
        breadcrumbs = soup.select(".breadcrumb, .breadcrumbs, .breadcrumb-item, .nav-breadcrumb")
        if breadcrumbs:
            category = " > ".join([b.get_text().strip() for b in breadcrumbs if b.get_text().strip()][:3])
            
        # Compile result
        if title:
            result["raw_title"] = title
            result["raw_price"] = price
            result["raw_description"] = description
            result["raw_images"] = images
            result["raw_vendor"] = vendor
            result["raw_category"] = category
            
            if is_amazon:
                # Flag amazon explicitly, as details might be incomplete or blocky
                result["extraction_status"] = "Partial (Amazon - Review Needed)"
            else:
                result["extraction_status"] = "Success"
        else:
            if is_amazon:
                result["extraction_status"] = "Blocked (Amazon Protected)"
            else:
                result["extraction_status"] = "Needs Manual Entry"
                
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        result["extraction_status"] = "Needs Manual Entry"

    return result


def extract_product_links_from_page(url):
    """
    Scrapes a page (like a collection or grid page) and finds all product-like links.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    product_links = set()
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch page for link extraction: {url}. Code: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.content, "lxml")
        
        # Find all anchors
        anchors = soup.find_all("a", href=True)
        for a in anchors:
            href = a["href"].strip()
            # Resolve relative links
            full_url = urllib.parse.urljoin(url, href)
            
            # Simple heuristics to identify product pages:
            url_lower = full_url.lower()
            
            # Heuristics filters
            is_product = False
            if "/products/" in url_lower or "/product/" in url_lower or "/dp/" in url_lower or "/gp/product/" in url_lower:
                is_product = True
            elif "item" in url_lower or "detail" in url_lower:
                if re.search(r'\d{4,}', url_lower):
                    is_product = True
            
            # Blacklist filters
            is_blacklisted = False
            for term in ["/collections/", "/category/", "/categories/", "/cart", "/checkout", "/account", "/blogs/", "/pages/", "?sort_by", "contact", "about"]:
                if term in url_lower:
                    is_blacklisted = True
                    break
                    
            if is_product and not is_blacklisted:
                # Clean query parameters
                cleaned_url = full_url.split("?")[0]
                product_links.add(cleaned_url)
                
    except Exception as e:
        logger.error(f"Error extracting links from page {url}: {e}")
        
    return list(product_links)


def extract_product_links_from_sitemap(sitemap_url):
    """
    Fetches a sitemap XML URL and extracts all product-like links.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/xml,application/xml,application/xhtml+xml,*/*;q=0.8"
    }
    product_links = set()
    try:
        response = requests.get(sitemap_url, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch sitemap: {sitemap_url}. Code: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.content, "xml") # Parse as XML
        locs = soup.find_all("loc")
        for loc in locs:
            full_url = loc.get_text().strip()
            url_lower = full_url.lower()
            
            # Apply product heuristics
            is_product = False
            if "/products/" in url_lower or "/product/" in url_lower or "/dp/" in url_lower or "/gp/product/" in url_lower:
                is_product = True
                
            is_blacklisted = False
            for term in ["/collections/", "/category/", "/categories/", "/cart", "/checkout", "/account", "/blogs/", "/pages/"]:
                if term in url_lower:
                    is_blacklisted = True
                    break
                    
            if is_product and not is_blacklisted:
                product_links.add(full_url.split("?")[0])
                
    except Exception as e:
        logger.error(f"Error parsing sitemap {sitemap_url}: {e}")
        
    return list(product_links)

