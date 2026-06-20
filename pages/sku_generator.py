import streamlit as st
from database.db import get_db_session, ShopifyProduct
from services.sku_service import generate_sku, get_category_abbrev, get_color_abbrev
from services.validator import validate_product_record

def show_sku_generator():
    st.title("🏷️ SKU Generator Configuration")
    st.markdown("Configure prefix and categories to automatically structure your product stock-keeping units (SKUs).")

    # Informational box
    st.info("💡 **SKU Format:** `PREFIX-CATEGORY-COLOR-NUMBER` (e.g. `TNB-HEAD-BLK-001`). If a color is not mapped, it uses the first consonants or letters of the color string.")

    session = get_db_session()
    
    # 1. Simulator Card
    st.subheader("🧪 Interactive SKU Simulator")
    with st.expander("Test SKU generation logic", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            sim_prefix = st.text_input("Custom Prefix:", value="TNB", max_chars=10, key="sim_prefix")
        with col2:
            sim_category = st.text_input("Product Category:", value="Headphones", key="sim_category")
        with col3:
            sim_color = st.text_input("Color / Variant:", value="Black", key="sim_color")
            
        # Live preview calculation
        cat_ab = get_category_abbrev(sim_category)
        col_ab = get_color_abbrev(sim_color)
        
        simulated_sku = generate_sku(
            title="", 
            category=sim_category, 
            color=sim_color, 
            prefix=sim_prefix, 
            db_session=session
        )
        
        st.markdown(f"""
        **Calculation Details:**
        * Prefix: `{sim_prefix}`
        * Category Abbreviation: `{cat_ab}`
        * Color Abbreviation: `{col_ab}`
        * **Generated SKU Preview:** `{simulated_sku}`
        """)

    # 2. Bulk Generator Card
    st.subheader("⚙️ Bulk SKU Generation & Correction")
    
    total_products = session.query(ShopifyProduct).count()
    missing_sku_count = session.query(ShopifyProduct).filter(
        (ShopifyProduct.variant_sku == None) | (ShopifyProduct.variant_sku == "")
    ).count()
    
    st.markdown(f"""
    * **Total Products in DB:** {total_products}
    * **Products Missing SKUs:** {missing_sku_count}
    """)
    
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        bulk_prefix = st.text_input("Bulk Prefix:", value="TNB", max_chars=10, key="bulk_prefix")
    with col_opt2:
        overwrite_existing = st.checkbox("Overwrite existing SKUs", value=False, 
                                         help="If checked, this will regenerate SKUs for ALL products. If unchecked, it only fills in missing SKUs.")

    # Color field selection
    st.markdown("Since colors are part of option values in Shopify (e.g. Option1 Value or Option2 Value), the generator will check your Option values for color terms (like 'Black', 'White', etc.) or you can enter a default color below.")
    default_color = st.text_input("Default Color fallback if none found in options:", value="Black")

    if st.button("🏷️ Run Bulk SKU Generator", type="primary"):
        if total_products == 0:
            st.warning("No products found to update.")
        else:
            updated_count = 0
            
            # Fetch products
            if overwrite_existing:
                products_to_update = session.query(ShopifyProduct).all()
            else:
                products_to_update = session.query(ShopifyProduct).filter(
                    (ShopifyProduct.variant_sku == None) | (ShopifyProduct.variant_sku == "")
                ).all()
                
            for p in products_to_update:
                # Deduce color from options
                color_found = ""
                for opt_val in [p.option1_value, p.option2_value]:
                    if opt_val and opt_val.lower() not in ["default title", "default", "none", "title"]:
                        # Standard check if option value is a color name
                        color_found = opt_val
                        break
                if not color_found:
                    color_found = default_color
                    
                # Generate
                new_sku = generate_sku(
                    title=p.title,
                    category=p.product_category or "General",
                    color=color_found,
                    prefix=bulk_prefix,
                    db_session=session
                )
                
                p.variant_sku = new_sku
                
                # Re-validate
                val_res = validate_product_record(p, db_session=session)
                p.validation_status = val_res["status"]
                
                updated_count += 1
                
            session.commit()
            st.success(f"Successfully generated/updated SKUs for {updated_count} products!")
            st.rerun()

    session.close()

if __name__ == "__main__":
    show_sku_generator()
