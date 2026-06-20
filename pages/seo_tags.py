import streamlit as st
from database.db import get_db_session, ShopifyProduct
from services.seo_service import generate_tags, generate_seo_title, generate_seo_description
from services.sku_service import create_handle
from services.validator import validate_product_record

def show_seo_tags():
    st.title("🔍 Tags & SEO Generator")
    st.markdown("Optimize your listings. Automatically generate SEO titles, descriptions, comma-separated tags, and handles from product titles and categories.")

    session = get_db_session()
    
    total_products = session.query(ShopifyProduct).count()
    if total_products == 0:
        st.info("No products found. Import products to begin generating SEO fields.")
        session.close()
        return

    # Fetch stats on missing fields
    missing_tags = session.query(ShopifyProduct).filter((ShopifyProduct.tags == None) | (ShopifyProduct.tags == "")).count()
    missing_handles = session.query(ShopifyProduct).filter((ShopifyProduct.handle == None) | (ShopifyProduct.handle == "")).count()
    missing_seo_titles = session.query(ShopifyProduct).filter((ShopifyProduct.seo_title == None) | (ShopifyProduct.seo_title == "")).count()
    missing_seo_descs = session.query(ShopifyProduct).filter((ShopifyProduct.seo_description == None) | (ShopifyProduct.seo_description == "")).count()

    st.subheader("📊 SEO Optimization Status")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Missing Tags", missing_tags, delta=f"-{missing_tags}" if missing_tags else "0", delta_color="inverse")
    with col2:
        st.metric("Missing Handles", missing_handles, delta=f"-{missing_handles}" if missing_handles else "0", delta_color="inverse")
    with col3:
        st.metric("Missing SEO Titles", missing_seo_titles, delta=f"-{missing_seo_titles}" if missing_seo_titles else "0", delta_color="inverse")
    with col4:
        st.metric("Missing SEO Descs", missing_seo_descs, delta=f"-{missing_seo_descs}" if missing_seo_descs else "0", delta_color="inverse")

    st.subheader("⚙️ Bulk Generation Configuration")
    
    # Checkboxes for actions to take
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        gen_tags = st.checkbox("Generate Tags", value=True, help="Create keyword tags from Title & Category")
        gen_handles = st.checkbox("Generate Handles", value=True, help="Create lowercase URL-friendly handles from Title")
    with col_act2:
        gen_titles = st.checkbox("Generate SEO Titles", value=True, help="Create clean title under 70 characters")
        gen_descs = st.checkbox("Generate SEO Descriptions", value=True, help="Create text description under 160 characters")

    # Scope of generation
    st.markdown("---")
    gen_scope = st.selectbox("Generate for:", ["Only products missing these fields", "All products (overwrite existing)"])

    if st.button("🚀 Run SEO & Tags Generator", type="primary"):
        updated_count = 0
        products = session.query(ShopifyProduct).all()
        
        for p in products:
            made_changes = False
            
            # Tags
            if gen_tags:
                if gen_scope == "All products (overwrite existing)" or not p.tags:
                    p.tags = generate_tags(p.title, p.product_category)
                    made_changes = True
            
            # Handles
            if gen_handles:
                if gen_scope == "All products (overwrite existing)" or not p.handle:
                    new_handle = create_handle(p.title)
                    if new_handle:
                        p.handle = new_handle
                        made_changes = True
            
            # SEO Titles
            if gen_titles:
                if gen_scope == "All products (overwrite existing)" or not p.seo_title:
                    p.seo_title = generate_seo_title(p.title)
                    made_changes = True
                    
            # SEO Descriptions
            if gen_descs:
                if gen_scope == "All products (overwrite existing)" or not p.seo_description:
                    # Look up raw description if possible
                    p.seo_description = generate_seo_description(p.title, p.body_html)
                    made_changes = True
                    
            if made_changes:
                # Re-validate
                val_res = validate_product_record(p, db_session=session)
                p.validation_status = val_res["status"]
                updated_count += 1
                
        session.commit()
        st.success(f"Successfully processed SEO & Tags for {updated_count} products!")
        st.rerun()

    session.close()

if __name__ == "__main__":
    show_seo_tags()
