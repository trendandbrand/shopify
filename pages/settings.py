import streamlit as st
import os
from database.db import using_sqlite, DATABASE_URL

def show_settings():
    st.title("⚙️ App Settings")
    st.markdown("Configure default Shopify values and monitor the database engine status.")

    # Database connection status
    st.subheader("🖥️ Database Connection Status")
    if using_sqlite:
        st.warning("⚠️ **Running in Fallback Mode (SQLite):** The application could not connect to PostgreSQL on port 5432 and is using the local SQLite database (`product2shopify.db`). To use PostgreSQL, verify your connection URI in `.env` and restart the app.")
    else:
        st.success("🟢 **PostgreSQL Connected:** The application is successfully connected to the PostgreSQL database.")
        
    st.code(f"Active Connection URI: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}", language="text")

    # Default values form
    st.subheader("🛍️ Shopify Default Field Configurations")
    st.markdown("These defaults are pre-populated when importing and processing new products.")

    with st.form("settings_defaults_form"):
        col1, col2 = st.columns(2)
        with col1:
            default_published = st.selectbox("Default Published:", ["true", "false"], index=0)
            default_inv_policy = st.selectbox("Default Inventory Policy:", ["deny", "continue"], index=0)
            default_fulfilment = st.text_input("Default Fulfillment Service:", value="manual")
            default_status = st.selectbox("Default Product Status:", ["draft", "active", "archived"], index=0)
        with col2:
            default_shipping = st.selectbox("Default Requires Shipping:", ["true", "false"], index=0)
            default_taxable = st.selectbox("Default Taxable:", ["true", "false"], index=0)
            default_weight_unit = st.selectbox("Default Weight Unit:", ["lb", "oz", "g", "kg"], index=0)
            default_gift_card = st.selectbox("Default Gift Card:", ["true", "false"], index=1)
            
        submitted = st.form_submit_button("💾 Save Default Configurations")
        if submitted:
            # We can save these in session state for dynamic use in scraper / loaders
            st.session_state["default_published"] = default_published
            st.session_state["default_inv_policy"] = default_inv_policy
            st.session_state["default_fulfilment"] = default_fulfilment
            st.session_state["default_shipping"] = default_shipping
            st.session_state["default_taxable"] = default_taxable
            st.session_state["default_weight_unit"] = default_weight_unit
            st.session_state["default_gift_card"] = default_gift_card
            st.session_state["default_status"] = default_status
            
            st.success("Configurations saved to application session!")

    # Help section
    st.subheader("💡 Tips for Shopify CSV Imports")
    st.markdown("""
    * **Handles:** Every unique product must have a unique handle. If you have variants, they must share the exact same handle.
    * **SKUs:** Shopify requires unique SKUs. Use the **SKU Generator** to ensure no duplicates.
    * **Image URLs:** Must be publicly accessible HTTPS links. Private local paths (like `C:/images/...`) will fail to load in Shopify.
    * **Published:** If set to `true`, the product will be visible in your store channels immediately upon import.
    """)

if __name__ == "__main__":
    show_settings()
