import streamlit as st
import pandas as pd
import time
from database.db import get_db_session, ShopifyProduct, RawProduct
from services.product_cleaner import rewrite_product_data
from services.validator import validate_product_record
from services.sku_service import create_handle

def load_products_as_df(session):
    products = session.query(ShopifyProduct).order_by(ShopifyProduct.id.asc()).all()
    if not products:
        return pd.DataFrame()
    
    # Map SQLAlchemy objects to list of dicts
    data = []
    for p in products:
        p_dict = {c.name: getattr(p, c.name) for c in p.__table__.columns}
        # Convert numeric types to float/int for pandas
        if p_dict["variant_price"]:
            p_dict["variant_price"] = float(p_dict["variant_price"])
        if p_dict["variant_compare_at_price"]:
            p_dict["variant_compare_at_price"] = float(p_dict["variant_compare_at_price"])
        if p_dict["cost_per_item"]:
            p_dict["cost_per_item"] = float(p_dict["cost_per_item"])
        data.append(p_dict)
        
    return pd.DataFrame(data)

def show_product_editor():
    st.title("✏️ Product Editor")
    st.markdown("Edit your product details, check validation errors, and clean description copies before exporting.")

    session = get_db_session()
    
    # Count products
    total_products = session.query(ShopifyProduct).count()
    if total_products == 0:
        st.info("No products found in the database. Go to **Product Link Importer** to import products or add them.")
        session.close()
        return

    # Tabs for Single Product Form Edit and Bulk Dataframe Edit
    tab_single, tab_bulk = st.tabs(["📋 Detailed Form Editor", "📊 Bulk Grid Editor"])
    
    # --- TAB 1: SINGLE PRODUCT FORM EDITOR ---
    with tab_single:
        st.subheader("Select Product to Edit")
        
        # Load products list for dropdown
        products_list = session.query(ShopifyProduct.id, ShopifyProduct.title, ShopifyProduct.variant_sku).order_by(ShopifyProduct.id.asc()).all()
        options = {p.id: f"#{p.id} - {p.title[:50]} (SKU: {p.variant_sku or 'N/A'})" for p in products_list}
        
        selected_id = st.selectbox("Choose Product:", options=list(options.keys()), format_func=lambda x: options[x])
        
        if selected_id:
            # Fetch full product record
            product = session.query(ShopifyProduct).filter(ShopifyProduct.id == selected_id).first()
            
            # Fetch raw product if available for rewriting
            raw_product = None
            if product.source_url:
                raw_product = session.query(RawProduct).filter(RawProduct.source_url == product.source_url).first()
            
            st.markdown("---")
            
            # Main Save/Rewrite/Delete Action Buttons
            col_act1, col_act2, col_act3 = st.columns([2, 2, 4])
            with col_act1:
                save_btn = st.button("💾 Save Product Details", key="save_single")
            with col_act2:
                # Rewrite Button
                rewrite_btn = st.button("✨ Auto-Rewrite (AI/Rule Copy)", key="rewrite_single", 
                                        help="Paraphrase Title & clean description into standard Shopify HTML. Requires raw scraper data.")
            with col_act3:
                delete_btn = st.button("🗑️ Delete Product", key="delete_single", type="primary")

            if delete_btn:
                session.delete(product)
                session.commit()
                st.success(f"Product #{selected_id} deleted successfully!")
                time.sleep(1)
                st.rerun()

            # If rewrite button clicked
            if rewrite_btn:
                if raw_product and raw_product.raw_description:
                    rewritten_title, rewritten_body = rewrite_product_data(
                        raw_product.raw_title,
                        raw_product.raw_description,
                        product.vendor
                    )
                    product.title = rewritten_title
                    product.body_html = rewritten_body
                    product.handle = create_handle(rewritten_title)
                    product.seo_title = rewritten_title[:70]
                    session.commit()
                    st.success("✨ Title, Handle, and Body HTML rewritten successfully! Form updated below.")
                else:
                    st.warning("Could not rewrite: No raw source description found for this product. Enter details manually.")

            # Layout fields in logical categories
            with st.form("product_form"):
                st.markdown("### 🏷️ Basic Information")
                col1, col2 = st.columns(2)
                with col1:
                    title_val = st.text_input("Product Title:", value=product.title)
                    handle_val = st.text_input("Handle (URL Friendly):", value=product.handle)
                    source_url_val = st.text_input("Source URL:", value=product.source_url or "", disabled=True)
                with col2:
                    vendor_val = st.text_input("Vendor / Brand:", value=product.vendor or "")
                    cat_val = st.text_input("Product Category (Shopify Standard):", value=product.product_category or "")
                    type_val = st.text_input("Product Type:", value=product.product_type or "")
                    tags_val = st.text_input("Tags (comma separated):", value=product.tags or "")
                
                st.markdown("### 📝 Product Description (HTML)")
                body_val = st.text_area("Body HTML:", value=product.body_html, height=200)
                
                st.markdown("### 💰 Pricing & Inventory")
                col3, col4, col5 = st.columns(3)
                with col3:
                    price_val = st.number_input("Variant Price ($):", min_value=0.00, value=float(product.variant_price or 0.00), step=0.01)
                    compare_val = st.number_input("Compare At Price ($):", min_value=0.00, value=float(product.variant_compare_at_price or 0.00), step=0.01)
                with col4:
                    sku_val = st.text_input("Variant SKU:", value=product.variant_sku or "")
                    barcode_val = st.text_input("Variant Barcode (GTIN/UPC):", value=product.variant_barcode or "")
                with col5:
                    qty_val = st.number_input("Inventory Qty:", min_value=0, value=int(product.variant_inventory_qty or 0))
                    grams_val = st.number_input("Weight (Grams):", min_value=0, value=int(product.variant_grams or 0))
                
                st.markdown("### 📐 Options & Toggles")
                col6, col7, col8 = st.columns(3)
                with col6:
                    opt1_name = st.text_input("Option 1 Name:", value=product.option1_name or "Title")
                    opt1_val = st.text_input("Option 1 Value:", value=product.option1_value or "Default Title")
                with col7:
                    opt2_name = st.text_input("Option 2 Name:", value=product.option2_name or "")
                    opt2_val = st.text_input("Option 2 Value:", value=product.option2_value or "")
                with col8:
                    published_val = st.selectbox("Published:", ["true", "false"], index=0 if product.published == "true" else 1)
                    status_val = st.selectbox("Status:", ["draft", "active", "archived"], index=["draft", "active", "archived"].index(product.status or "draft"))
                
                st.markdown("### 🖼️ Images & SEO")
                col9, col10 = st.columns(2)
                with col9:
                    img_src_val = st.text_area("Image Source URLs (one per line or comma separated):", value=product.image_src or "", height=80)
                    img_pos_val = st.number_input("Image Position:", min_value=1, value=int(product.image_position or 1))
                    img_alt_val = st.text_input("Image Alt Text:", value=product.image_alt_text or "")
                with col10:
                    seo_title_val = st.text_input("SEO Title (max 70 chars):", value=product.seo_title or "")
                    seo_desc_val = st.text_area("SEO Description (max 160 chars):", value=product.seo_description or "", height=80)
                    g_cat_val = st.text_input("Google Shopping Category:", value=product.google_shopping_category or "")

                # Extra Google fields
                col11, col12, col13 = st.columns(3)
                with col11:
                    g_gender = st.text_input("Google Gender:", value=product.google_shopping_gender or "")
                    g_age = st.text_input("Google Age Group:", value=product.google_shopping_age_group or "")
                with col12:
                    g_mpn = st.text_input("Google MPN:", value=product.google_shopping_mpn or "")
                    g_cond = st.text_input("Google Condition:", value=product.google_shopping_condition or "new")
                with col13:
                    cost_val = st.number_input("Cost Per Item ($):", min_value=0.00, value=float(product.cost_per_item or 0.00), step=0.01)
                    shipping_val = st.number_input("Product Shipping Cost ($):", min_value=0.00, value=float(product.shipping_cost or 0.00), step=0.01)
                    fee_val = st.number_input("Platform Fee ($):", min_value=0.00, value=float(product.platform_fee or 0.00), step=0.01)

                submit_btn = st.form_submit_form = False
                
                # Check submission
                if save_btn:
                    # Update model properties
                    product.title = title_val
                    product.handle = handle_val
                    product.vendor = vendor_val
                    product.product_category = cat_val
                    product.product_type = type_val
                    product.tags = tags_val
                    product.body_html = body_val
                    product.variant_price = price_val
                    product.variant_compare_at_price = compare_val
                    product.variant_sku = sku_val
                    product.variant_barcode = barcode_val
                    product.variant_inventory_qty = qty_val
                    product.variant_grams = grams_val
                    product.option1_name = opt1_name
                    product.option1_value = opt1_val
                    product.option2_name = opt2_name
                    product.option2_value = opt2_val
                    product.published = published_val
                    product.status = status_val
                    product.image_src = img_src_val
                    product.image_position = img_pos_val
                    product.image_alt_text = img_alt_val
                    product.seo_title = seo_title_val
                    product.seo_description = seo_desc_val
                    product.google_shopping_category = g_cat_val
                    product.google_shopping_gender = g_gender
                    product.google_shopping_age_group = g_age
                    product.google_shopping_mpn = g_mpn
                    product.google_shopping_condition = g_cond
                    product.cost_per_item = cost_val
                    product.shipping_cost = shipping_val
                    product.platform_fee = fee_val
                    
                    # Validate product and set validation_status
                    val_res = validate_product_record(product, db_session=session)
                    product.validation_status = val_res["status"]
                    
                    session.commit()
                    st.success(f"Product #{selected_id} details updated successfully!")
                    
                    # Display errors/warnings
                    if val_res["errors"]:
                        st.error("Validation Errors to fix:\n" + "\n".join([f"- {e}" for e in val_res["errors"]]))
                    if val_res["warnings"]:
                        st.warning("Validation Warnings:\n" + "\n".join([f"- {w}" for e in val_res["warnings"]]))
                        
                    time.sleep(1)
                    st.rerun()

    # --- TAB 2: BULK GRID EDITOR ---
    with tab_bulk:
        st.subheader("Bulk Edit Product Records")
        st.markdown("Use the spreadsheet grid below to quickly edit key fields. Double-click cells to modify, then click 'Apply Bulk Changes'.")
        
        # Load products into DataFrame
        df = load_products_as_df(session)
        
        if not df.empty:
            # Columns to display in grid (we hide internal columns to keep it clean)
            grid_cols = ["id", "variant_sku", "title", "variant_price", "variant_compare_at_price", "vendor", "status", "validation_status", "handle"]
            display_df = df[grid_cols].copy()
            
            # Edit grid
            edited_df = st.data_editor(
                display_df,
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "variant_sku": st.column_config.TextColumn("SKU"),
                    "title": st.column_config.TextColumn("Product Title", width="medium"),
                    "variant_price": st.column_config.NumberColumn("Price ($)", step=0.01, format="$%.2f"),
                    "variant_compare_at_price": st.column_config.NumberColumn("Compare At ($)", step=0.01, format="$%.2f"),
                    "vendor": st.column_config.TextColumn("Vendor"),
                    "status": st.column_config.SelectboxColumn("Status", options=["draft", "active", "archived"]),
                    "validation_status": st.column_config.TextColumn("Validation", disabled=True),
                    "handle": st.column_config.TextColumn("Handle")
                },
                disabled=["id", "validation_status"],
                hide_index=True,
                width="stretch",
                key="bulk_grid_editor"
            )
            
            if st.button("💾 Apply Bulk Changes"):
                # Save changes back to database
                any_change = False
                for idx, row in edited_df.iterrows():
                    p_id = int(row["id"])
                    db_prod = session.query(ShopifyProduct).filter(ShopifyProduct.id == p_id).first()
                    
                    if db_prod:
                        # Check if changed to optimize
                        if (db_prod.variant_sku != row["variant_sku"] or
                            db_prod.title != row["title"] or
                            float(db_prod.variant_price or 0.0) != float(row["variant_price"]) or
                            float(db_prod.variant_compare_at_price or 0.0) != float(row["variant_compare_at_price"]) or
                            db_prod.vendor != row["vendor"] or
                            db_prod.status != row["status"] or
                            db_prod.handle != row["handle"]):
                            
                            db_prod.variant_sku = row["variant_sku"]
                            db_prod.title = row["title"]
                            db_prod.variant_price = row["variant_price"]
                            db_prod.variant_compare_at_price = row["variant_compare_at_price"]
                            db_prod.vendor = row["vendor"]
                            db_prod.status = row["status"]
                            db_prod.handle = row["handle"]
                            
                            # Validate
                            val_res = validate_product_record(db_prod, db_session=session)
                            db_prod.validation_status = val_res["status"]
                            any_change = True
                
                if any_change:
                    session.commit()
                    st.success("Bulk changes applied and validated successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.info("No modifications detected.")
        else:
            st.info("No products available to edit.")

    session.close()

if __name__ == "__main__":
    show_product_editor()
