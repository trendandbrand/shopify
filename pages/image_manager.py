import streamlit as st
from database.db import get_db_session, ShopifyProduct
from services.csv_exporter import parse_images_list
from services.validator import validate_product_record

def show_image_manager():
    st.title("🖼️ Image Manager")
    st.markdown("Add, edit, delete, and validate product images. Ensure your URLs are secure and compliant.")

    # Copyright Warning Box
    st.warning("⚠️ **Copyright Warning:** Use only images you own, or those you are authorized to use by the manufacturer/supplier. Do not use copyrighted images from competitor sites.")

    session = get_db_session()
    
    # Check if there are products
    products = session.query(ShopifyProduct).order_by(ShopifyProduct.id.asc()).all()
    if not products:
        st.info("No products found in the database. Head to **Product Link Importer** to get started.")
        session.close()
        return

    # Select product
    prod_options = {p.id: f"#{p.id} - {p.title[:60]}" for p in products}
    selected_id = st.selectbox("Select Product to Manage Images:", list(prod_options.keys()), format_func=lambda x: prod_options[x])

    if selected_id:
        product = session.query(ShopifyProduct).filter(ShopifyProduct.id == selected_id).first()
        
        st.markdown(f"**Selected Product SKU:** `{product.variant_sku or 'N/A'}`")
        
        # Get list of current image URLs
        current_images = parse_images_list(product.image_src)
        
        # Display current images in a gallery format
        st.subheader("📷 Current Images Gallery")
        if current_images:
            cols = st.columns(min(len(current_images), 4))
            for idx, img_url in enumerate(current_images):
                col_idx = idx % 4
                with cols[col_idx]:
                    # Draw a nice thumbnail with options to delete/reorder
                    st.image(img_url, width=180, caption=f"Position {idx + 1}")
                    # Show truncated url
                    st.caption(f"URL: ...{img_url[-25:]}")
                    
                    # Delete or position control
                    if st.button(f"🗑️ Delete #{idx+1}", key=f"del_{idx}"):
                        current_images.pop(idx)
                        product.image_src = ", ".join(current_images)
                        
                        # Re-run validation
                        val_res = validate_product_record(product, db_session=session)
                        product.validation_status = val_res["status"]
                        
                        session.commit()
                        st.success(f"Image {idx+1} deleted!")
                        st.rerun()
        else:
            st.warning("⚠️ This product currently has no images. Shopify requires at least one image for display.")

        # Input fields to manage list of URLs
        st.subheader("✏️ Edit Image Links & Alt Text")
        
        # We can display the links in a text area, one per line, and let them edit
        images_text = st.text_area("Image URLs (one per line, secure HTTPS only):", 
                                   value="\n".join(current_images), height=150)
                                   
        col1, col2 = st.columns(2)
        with col1:
            image_position = st.number_input("Primary Image Position:", min_value=1, value=int(product.image_position or 1))
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            auto_alt = st.button("✨ Auto-Generate Alt Text from Title")
            if auto_alt:
                product.image_alt_text = f"Buy {product.title}"
                session.commit()
                st.success("Alt text generated!")
                st.rerun()
                
        image_alt_text = st.text_input("Image Alt Text:", value=product.image_alt_text or "")
        
        # Action Buttons
        col_btn1, col_btn2 = st.columns([2, 8])
        with col_btn1:
            save_images_btn = st.button("💾 Save Image Settings", type="primary")

        if save_images_btn:
            # Parse entered images
            entered_urls = [url.strip() for url in images_text.split("\n") if url.strip()]
            
            # Validate URLs starts with https://
            invalid_urls = []
            for url in entered_urls:
                if not url.startswith("https://"):
                    invalid_urls.append(url)
                    
            if invalid_urls:
                st.error("❌ All image URLs must start with 'https://'. Please fix the following invalid URLs:\n" + 
                         "\n".join([f"- {u}" for u in invalid_urls]))
            else:
                # Save to database
                product.image_src = ", ".join(entered_urls)
                product.image_position = image_position
                product.image_alt_text = image_alt_text
                
                # Re-run validation
                val_res = validate_product_record(product, db_session=session)
                product.validation_status = val_res["status"]
                
                session.commit()
                st.success("Image configurations saved and validated successfully!")
                st.rerun()
                
    session.close()

if __name__ == "__main__":
    show_image_manager()
