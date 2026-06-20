import os
import csv
import pandas as pd
from datetime import datetime

SHOPIFY_COLUMNS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags", "Published",
    "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value", "Option3 Name", "Option3 Value",
    "Variant SKU", "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Qty",
    "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price",
    "Variant Requires Shipping", "Variant Taxable", "Variant Barcode", "Image Src", "Image Position",
    "Image Alt Text", "Gift Card", "SEO Title", "SEO Description", "Google Shopping / Google Product Category",
    "Google Shopping / Gender", "Google Shopping / Age Group", "Google Shopping / MPN",
    "Google Shopping / Condition", "Google Shopping / Custom Product", "Variant Image", "Variant Weight Unit",
    "Variant Tax Code", "Cost per item", "Included / United States", "Price / United States",
    "Compare At Price / United States", "Status"
]

def ensure_export_dirs():
    """Ensure that exports directories exist."""
    os.makedirs(os.path.join("exports", "csv"), exist_ok=True)
    os.makedirs(os.path.join("exports", "excel"), exist_ok=True)

def parse_images_list(image_src):
    """Splits image_src string by comma, newline or whitespace into a list of URLs."""
    if not image_src:
        return []
    # Replace newlines and commas with space, then split
    raw_urls = image_src.replace("\n", " ").replace(",", " ").split()
    urls = []
    for url in raw_urls:
        url = url.strip()
        if url.startswith("http"):
            urls.append(url)
    return urls

def build_shopify_rows(products):
    """
    Transforms products list/query result into Shopify CSV rows.
    Handles multiple images per product by creating supplementary rows with just Handle and Image Src.
    """
    rows = []
    
    for product in products:
        # Convert product to dict if it's an SQLAlchemy model
        if hasattr(product, '__dict__'):
            p = {c.name: getattr(product, c.name) for c in product.__table__.columns}
        else:
            p = dict(product)
            
        handle = p.get("handle", "")
        if not handle:
            continue
            
        images = parse_images_list(p.get("image_src", ""))
        
        # Base product row dictionary
        base_row = {
            "Handle": handle,
            "Title": p.get("title", ""),
            "Body (HTML)": p.get("body_html", ""),
            "Vendor": p.get("vendor", ""),
            "Product Category": p.get("product_category", ""),
            "Type": p.get("product_type", ""),
            "Tags": p.get("tags", ""),
            "Published": str(p.get("published", "true")).upper(),
            "Option1 Name": p.get("option1_name", ""),
            "Option1 Value": p.get("option1_value", ""),
            "Option2 Name": p.get("option2_name", ""),
            "Option2 Value": p.get("option2_value", ""),
            "Option3 Name": p.get("option3_name", ""),
            "Option3 Value": p.get("option3_value", ""),
            "Variant SKU": p.get("variant_sku", ""),
            "Variant Grams": p.get("variant_grams", 0),
            "Variant Inventory Tracker": p.get("variant_inventory_tracker", "shopify"),
            "Variant Inventory Qty": p.get("variant_inventory_qty", 1),
            "Variant Inventory Policy": p.get("variant_inventory_policy", "deny"),
            "Variant Fulfillment Service": p.get("variant_fulfillment_service", "manual"),
            "Variant Price": p.get("variant_price", 0.00),
            "Variant Compare At Price": p.get("variant_compare_at_price", 0.00),
            "Variant Requires Shipping": str(p.get("variant_requires_shipping", True)).upper(),
            "Variant Taxable": str(p.get("variant_taxable", True)).upper(),
            "Variant Barcode": p.get("variant_barcode", ""),
            "Image Src": images[0] if len(images) > 0 else "",
            "Image Position": p.get("image_position") or (1 if len(images) > 0 else ""),
            "Image Alt Text": p.get("image_alt_text", ""),
            "Gift Card": str(p.get("gift_card", "false")).upper(),
            "SEO Title": p.get("seo_title", ""),
            "SEO Description": p.get("seo_description", ""),
            "Google Shopping / Google Product Category": p.get("google_shopping_category", ""),
            "Google Shopping / Gender": p.get("google_shopping_gender", ""),
            "Google Shopping / Age Group": p.get("google_shopping_age_group", ""),
            "Google Shopping / MPN": p.get("google_shopping_mpn", ""),
            "Google Shopping / Condition": p.get("google_shopping_condition", "new"),
            "Google Shopping / Custom Product": str(p.get("google_shopping_custom_product", "true")).upper(),
            "Variant Image": p.get("variant_image", ""),
            "Variant Weight Unit": p.get("variant_weight_unit", "lb"),
            "Variant Tax Code": p.get("variant_tax_code", ""),
            "Cost per item": p.get("cost_per_item", 0.00),
            "Included / United States": "TRUE",
            "Price / United States": p.get("variant_price", 0.00),
            "Compare At Price / United States": p.get("variant_compare_at_price", 0.00),
            "Status": p.get("status", "draft")
        }
        
        rows.append(base_row)
        
        # Add supplementary image rows if there are additional images
        for idx, img_url in enumerate(images[1:], start=2):
            img_row = {col: "" for col in SHOPIFY_COLUMNS}
            img_row["Handle"] = handle
            img_row["Image Src"] = img_url
            img_row["Image Position"] = idx
            img_row["Image Alt Text"] = p.get("image_alt_text", "")
            
            # Shopify expects these defaults to be empty for supplementary image rows
            # but we can copy some values if needed. Standard practice is to leave them blank.
            rows.append(img_row)
            
    return rows

def generate_csv_export(products, filename=None):
    """
    Generates a Shopify-compatible CSV file and saves it.
    Returns the absolute path of the generated file and the pandas DataFrame.
    """
    ensure_export_dirs()
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"shopify_export_{timestamp}.csv"
        
    filepath = os.path.join("exports", "csv", filename)
    rows = build_shopify_rows(products)
    
    df = pd.DataFrame(rows, columns=SHOPIFY_COLUMNS)
    df.to_csv(filepath, index=False, quoting=csv.QUOTE_MINIMAL)
    
    return os.path.abspath(filepath), df

def generate_excel_export(products, filename=None):
    """
    Generates an Excel backup file and saves it.
    Returns the absolute path of the generated file.
    """
    ensure_export_dirs()
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"shopify_backup_{timestamp}.xlsx"
        
    filepath = os.path.join("exports", "excel", filename)
    rows = build_shopify_rows(products)
    
    df = pd.DataFrame(rows, columns=SHOPIFY_COLUMNS)
    df.to_excel(filepath, index=False)
    
    return os.path.abspath(filepath)
