import re
from database.db import ShopifyProduct

def validate_product_record(product, db_session=None, all_products_in_batch=None):
    """
    Validates a single product record (either dict or SQLAlchemy model).
    Checks for required Shopify fields, duplicates, and warning conditions.
    """
    errors = []
    warnings = []
    
    # 1. Convert product to dict if it's an SQLAlchemy model
    if hasattr(product, '__dict__'):
        p_dict = {c.name: getattr(product, c.name) for c in product.__table__.columns}
    else:
        p_dict = dict(product)
        
    p_id = p_dict.get("id")
    title = p_dict.get("title", "")
    handle = p_dict.get("handle", "")
    sku = p_dict.get("variant_sku", "")
    price = p_dict.get("variant_price")
    image_src = p_dict.get("image_src", "")
    tags = p_dict.get("tags", "")
    status = p_dict.get("status", "draft")
    
    # 2. Check Empty Required Fields
    if not title or not str(title).strip():
        errors.append("Title is required and cannot be empty.")
        
    if not handle or not str(handle).strip():
        errors.append("Handle is required and cannot be empty.")
        
    if not sku or not str(sku).strip():
        errors.append("Variant SKU is required and cannot be empty.")
        
    if price is None or str(price).strip() == "":
        errors.append("Price is required.")
    else:
        try:
            p_val = float(price)
            if p_val <= 0:
                warnings.append("Variant Price is 0 or negative. Verify pricing.")
        except (ValueError, TypeError):
            errors.append("Price must be a valid number.")

    # 3. Check Image URL Format
    if image_src:
        image_src_str = str(image_src).strip()
        if not image_src_str.startswith("https://"):
            errors.append("Image URL must be secure and start with 'https://'.")
    else:
        warnings.append("Missing product image URL. Shopify products without images may not display correctly.")

    # 4. Check Tags Separator
    if tags:
        tags_str = str(tags).strip()
        # If tag contains semicolons or pipes, warn
        if ";" in tags_str or "|" in tags_str:
            warnings.append("Tags should be separated by commas, not semicolons or pipes.")

    # 5. Check Product Status
    status_str = str(status).strip().lower()
    if status_str not in ["active", "draft", "archived"]:
        errors.append(f"Status must be 'active', 'draft', or 'archived' (got '{status}').")

    # 6. Check Duplicate Handle and SKU
    if db_session:
        try:
            # Check duplicate SKU in DB (excluding this product's ID)
            if sku:
                sku_query = db_session.query(ShopifyProduct).filter(
                    ShopifyProduct.variant_sku == sku
                )
                if p_id:
                    sku_query = sku_query.filter(ShopifyProduct.id != p_id)
                if sku_query.first():
                    errors.append(f"Duplicate SKU found in database: '{sku}'.")
                    
            # Check duplicate Handle in DB (excluding this product's ID)
            if handle:
                handle_query = db_session.query(ShopifyProduct).filter(
                    ShopifyProduct.handle == handle
                )
                if p_id:
                    handle_query = handle_query.filter(ShopifyProduct.id != p_id)
                if handle_query.first():
                    errors.append(f"Duplicate Handle found in database: '{handle}'.")
        except Exception as e:
            # If DB validation fails, log it
            pass

    # Check duplicate SKU/Handle in the current batch
    if all_products_in_batch:
        sku_count = 0
        handle_count = 0
        for other in all_products_in_batch:
            # Standardize checking whether list contains dicts or models
            if hasattr(other, '__dict__'):
                o_sku = getattr(other, "variant_sku", "")
                o_handle = getattr(other, "handle", "")
                o_id = getattr(other, "id", None)
            else:
                o_sku = other.get("variant_sku", "")
                o_handle = other.get("handle", "")
                o_id = other.get("id", None)
                
            # Skip checking against self
            if p_id and o_id and p_id == o_id:
                continue
                
            if sku and o_sku == sku:
                sku_count += 1
            if handle and o_handle == handle:
                handle_count += 1
                
        if sku_count > 0:
            errors.append(f"Duplicate SKU found in the current batch: '{sku}'.")
        if handle_count > 0:
            errors.append(f"Duplicate Handle found in the current batch: '{handle}'.")

    # Determine status
    validation_status = "Ready" if len(errors) == 0 else "Needs Fixing"
    
    return {
        "status": validation_status,
        "errors": errors,
        "warnings": warnings
    }
