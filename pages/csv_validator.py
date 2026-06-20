import streamlit as st
from database.db import get_db_session, ShopifyProduct
from services.validator import validate_product_record

def show_csv_validator():
    st.title("✅ CSV Validator")
    st.markdown("Verify your product catalog integrity. Validate all mandatory Shopify fields and detect duplicates before file export.")

    session = get_db_session()
    
    products = session.query(ShopifyProduct).order_by(ShopifyProduct.id.asc()).all()
    
    if not products:
        st.info("No products found to validate. Import products first.")
        session.close()
        return

    # Count database items
    total_products = len(products)
    ready_count = 0
    needs_fixing_count = 0
    
    # Store validation results
    validation_reports = []
    
    # We pass all products to check for duplicates in the current batch
    for p in products:
        report = validate_product_record(p, db_session=session, all_products_in_batch=products)
        
        # Update database validation status if it changed
        if p.validation_status != report["status"]:
            p.validation_status = report["status"]
            session.commit()
            
        if report["status"] == "Ready":
            ready_count += 1
        else:
            needs_fixing_count += 1
            
        validation_reports.append({
            "product": p,
            "status": report["status"],
            "errors": report["errors"],
            "warnings": report["warnings"]
        })
        
    # Metrics
    st.subheader("📋 Catalog Health Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Products", total_products)
    with col2:
        st.metric("Ready to Export", ready_count, delta=f"+{ready_count}" if ready_count else None)
    with col3:
        st.metric("Needs Fixing", needs_fixing_count, delta=f"-{needs_fixing_count}" if needs_fixing_count else None, delta_color="inverse")
        
    if needs_fixing_count == 0:
        st.success("🎉 All products are valid! Your catalog is ready for Shopify import.")
    else:
        st.error(f"❌ {needs_fixing_count} products have validation errors. Please resolve them before exporting.")

    # Validation Actions
    if st.button("🔄 Force Re-Run All Validations"):
        # Just reload page to trigger logic
        st.rerun()

    # Detailed report per product
    st.subheader("🔍 Detailed Validation Reports")
    
    # Filter selection
    filter_status = st.selectbox("Show products:", ["All", "Needs Fixing", "Ready"])
    
    for r in validation_reports:
        p = r["product"]
        status = r["status"]
        errors = r["errors"]
        warnings = r["warnings"]
        
        # Apply filter
        if filter_status == "Needs Fixing" and status == "Ready":
            continue
        if filter_status == "Ready" and status == "Needs Fixing":
            continue
            
        # Display header
        title_summary = f"#{p.id} - {p.title[:60]} (SKU: {p.variant_sku or 'N/A'})"
        
        if status == "Ready":
            label = f"🟢 {title_summary}"
        else:
            label = f"🔴 {title_summary}"
            
        with st.expander(label):
            st.markdown(f"**Handle:** `{p.handle}` | **Price:** `${p.variant_price:.2f}` | **Status:** `{p.status}`")
            
            if errors:
                st.markdown("##### ❌ Errors (Must Fix)")
                for err in errors:
                    st.markdown(f"- <span style='color:red'>{err}</span>", unsafe_allow_html=True)
            else:
                st.markdown("##### 🟢 No Errors")
                
            if warnings:
                st.markdown("##### ⚠️ Warnings (Review Recommended)")
                for warn in warnings:
                    st.markdown(f"- <span style='color:orange'>{warn}</span>", unsafe_allow_html=True)
            else:
                st.markdown("##### 🟢 No Warnings")
                
            # Quick Link Info
            st.info("💡 Edit this product inside the **Product Editor** page to resolve these validation items.")

    session.close()

if __name__ == "__main__":
    show_csv_validator()
