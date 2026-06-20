import streamlit as st
from database.db import get_db_session, ExportHistory, RawProduct
from sqlalchemy import func

def show_import_history():
    st.title("⏳ Import & Export History")
    st.markdown("Monitor history of URL extractions and Shopify sheet generations.")

    session = get_db_session()
    
    tab_exports, tab_imports = st.tabs(["📤 Export Batches", "📥 Raw URL Import Logs"])
    
    # --- TAB 1: EXPORT BATCHES ---
    with tab_exports:
        st.subheader("Generated Export Sheets")
        
        exports = session.query(ExportHistory).order_by(ExportHistory.created_at.desc()).all()
        
        if exports:
            export_data = []
            for e in exports:
                export_data.append({
                    "Batch ID": e.id,
                    "Date & Time": e.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "File Name": e.export_file_name,
                    "Export Type": e.export_type,
                    "Products Count": e.total_products,
                    "Status": e.export_status
                })
            st.dataframe(export_data, width="stretch", hide_index=True)
        else:
            st.info("No export batches have been generated yet.")
            
    # --- TAB 2: RAW IMPORT LOGS ---
    with tab_imports:
        st.subheader("Raw Scraper Extraction Logs")
        
        # Summary counts
        total_scraped = session.query(RawProduct).count()
        success_scraped = session.query(RawProduct).filter(RawProduct.extraction_status == "Success").count()
        manual_scraped = session.query(RawProduct).filter(RawProduct.extraction_status != "Success").count()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Extracted URLs", total_scraped)
        with col2:
            st.metric("Successful Scrapes", success_scraped)
        with col3:
            st.metric("Manual Entry Flagged", manual_scraped)
            
        raw_items = session.query(RawProduct).order_by(RawProduct.created_at.desc()).limit(50).all()
        
        if raw_items:
            raw_data = []
            for r in raw_items:
                raw_data.append({
                    "ID": r.id,
                    "Date": r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "Source URL": r.source_url,
                    "Scraped Title": r.raw_title or "(Empty)",
                    "Extraction Status": r.extraction_status
                })
            st.dataframe(raw_data, width="stretch", hide_index=True)
        else:
            st.info("No URLs have been scraped yet. Use the **Product Link Importer** to scrape links.")

    session.close()

if __name__ == "__main__":
    show_import_history()
