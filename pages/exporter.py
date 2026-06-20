import streamlit as st
import os
from database.db import get_db_session, ShopifyProduct, ExportHistory
from services.csv_exporter import generate_csv_export, generate_excel_export
from services.validator import validate_product_record

def show_exporter():
    st.title("📤 Shopify CSV Exporter")
    st.markdown("Generate and download Shopify import-ready CSVs and Excel backups.")

    session = get_db_session()
    
    # Check products
    products = session.query(ShopifyProduct).all()
    if not products:
        st.info("No products available to export. Import products first.")
        session.close()
        return

    # Count database items
    total_products = len(products)
    ready_count = session.query(ShopifyProduct).filter(ShopifyProduct.validation_status == 'Ready').count()
    
    st.subheader("📦 Select Export Target")
    export_option = st.radio(
        "Which products do you want to export?",
        [
            f"(Recommended) Export only validated 'Ready' products ({ready_count} of {total_products})",
            f"Export all products ({total_products} products, may contain warnings or empty fields)"
        ]
    )

    # Determine products to export
    is_ready_only = "(Recommended)" in export_option
    if is_ready_only:
        export_list = session.query(ShopifyProduct).filter(ShopifyProduct.validation_status == 'Ready').all()
    else:
        export_list = products
        
    export_count = len(export_list)
    
    st.markdown(f"**Selected for Export:** `{export_count}` products.")
    
    if export_count == 0:
        st.warning("⚠️ No products are matching your export criteria.")
        session.close()
        return

    st.subheader("🚀 Generate Export Sheets")
    
    # Custom filename input
    default_name = f"shopify_import_{os.getpid()}"
    custom_filename = st.text_input("Base File Name (without extension):", value=default_name)
    
    if st.button("📤 Generate Shopify Sheets", type="primary"):
        if not custom_filename.strip():
            st.error("Please enter a valid file name.")
        else:
            try:
                csv_filename = f"{custom_filename}.csv"
                excel_filename = f"{custom_filename}.xlsx"
                
                # Generate files
                csv_path, csv_df = generate_csv_export(export_list, csv_filename)
                excel_path = generate_excel_export(export_list, excel_filename)
                
                # Save to Database Export History
                history = ExportHistory(
                    export_file_name=csv_filename,
                    total_products=export_count,
                    export_type="CSV & Excel Export" if not is_ready_only else "Validated CSV & Excel Export",
                    export_status="Success"
                )
                session.add(history)
                session.commit()
                
                st.success("🎉 Files generated successfully!")
                
                # Download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    with open(csv_path, "rb") as f:
                        csv_data = f.read()
                    st.download_button(
                        label="📥 Download Shopify CSV",
                        data=csv_data,
                        file_name=csv_filename,
                        mime="text/csv",
                        width="stretch"
                    )
                    st.caption(f"Saved locally: `exports/csv/{csv_filename}`")
                    
                with col2:
                    with open(excel_path, "rb") as f:
                        excel_data = f.read()
                    st.download_button(
                        label="📥 Download Excel Backup",
                        data=excel_data,
                        file_name=excel_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width="stretch"
                    )
                    st.caption(f"Saved locally: `exports/excel/{excel_filename}`")
                    
                # Show instructions on Shopify import
                st.markdown("---")
                st.markdown("### 🛍️ How to import this CSV into Shopify:")
                st.markdown("""
                1. Log in to your **Shopify Admin** panel.
                2. Navigate to **Products**.
                3. Click **Import** at the top right of the screen.
                4. Click **Add file** and select the downloaded CSV file (`.csv`).
                5. Check **'Publish new products to all sales channels'** if desired.
                6. Click **Upload and preview**.
                7. Review the sample product mapping, then click **Import products**.
                """)
                
            except Exception as e:
                st.error(f"Error during sheet generation: {e}")

    session.close()

if __name__ == "__main__":
    show_exporter()
