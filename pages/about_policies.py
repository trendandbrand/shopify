import streamlit as st

def show_about_policies():
    st.title("📄 About, Policies & Sitemap")

    tab_about, tab_privacy, tab_terms, tab_sitemap = st.tabs(["🏢 About", "🔒 Privacy Policy", "📜 Terms of Service", "🗺️ Sitemap"])

    # ---- ABOUT ----
    with tab_about:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                    border-radius: 16px; padding: 40px; text-align: center; margin-bottom: 24px;">
            <h1 style="color: #e94560; margin:0; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px;">
                Product2Shopify AI
            </h1>
            <p style="color: #a0aec0; margin: 12px 0 0 0; font-size: 1.1rem;">
                A flagship product by <a href="https://www.trendandbrands.com/" target="_blank"
                style="color: #e94560; font-weight: 700; text-decoration: none;">Trend & Brand</a>
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### 🎯 What is Product2Shopify AI?
            **Product2Shopify AI** is an intelligent product catalog builder that helps Shopify store owners:
            - Import product data from any supplier or product URL
            - Scan entire seller collection pages and sitemaps
            - Hunt products on Amazon by keyword niche
            - Auto-generate SEO-optimized titles, descriptions, tags & handles
            - Produce Shopify import-ready CSV and Excel files

            It's built to save hours of manual data entry and ensure your catalog is always import-ready.
            """)

        with col2:
            st.markdown("""
            ### 🏢 About Trend & Brand
            [**Trend & Brand**](https://www.trendandbrands.com/) is a digital commerce and brand-building company dedicated to helping entrepreneurs build and scale profitable Shopify stores.

            We build practical tools, automation systems, and strategies that give independent sellers the edge of a full e-commerce team.

            - 🌐 Website: [trendandbrands.com](https://www.trendandbrands.com/)
            - 📧 Support: support@trendandbrands.com
            - 🛍️ Focus: Shopify, Dropshipping, E-commerce Automation
            """)

        st.markdown("---")
        st.markdown("""
        ### 🔑 Key Features
        """)
        cols = st.columns(3)
        features = [
            ("📥", "Bulk Product Import", "Import products from URLs, collection pages, or sitemap XML files in one click"),
            ("🔎", "Amazon Product Hunting", "Search Amazon keywords to discover trending products and import them instantly"),
            ("✨", "Auto Content Rewriter", "Rule-based rewriter creates unique, SEO-optimized Shopify product copy"),
            ("🏷️", "Smart SKU Generator", "Format: PREFIX-CATEGORY-COLOR-001 with duplicate prevention"),
            ("🧮", "Price Calculator", "Built-in margin, markup, and profit calculator to price products correctly"),
            ("📤", "Shopify CSV Export", "Generates 100% Shopify-compatible CSV with multi-image support"),
            ("✅", "CSV Validator", "Pre-export checks for missing titles, SKUs, prices, images & duplicates"),
            ("🖼️", "Image Manager", "Manage image URLs, positions, alt texts with HTTPS validation"),
            ("⏳", "Import History", "Full audit trail of every URL import and export batch"),
        ]
        for i, (icon, title, desc) in enumerate(features):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background: #1a1a2e; border: 1px solid #2d3748; border-radius: 12px;
                            padding: 16px; margin-bottom: 12px; height: 130px;">
                    <div style="font-size: 1.8rem;">{icon}</div>
                    <div style="color: #e2e8f0; font-weight: 700; margin: 4px 0;">{title}</div>
                    <div style="color: #718096; font-size: 0.85rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    # ---- PRIVACY POLICY ----
    with tab_privacy:
        st.markdown("""
        ## 🔒 Privacy Policy
        **Last Updated:** June 2026
        **Operated by:** [Trend & Brand](https://www.trendandbrands.com/)

        ---

        ### 1. Information We Collect
        **Product2Shopify AI** operates entirely on your local machine. We do not collect, store, or transmit any personal data to external servers. All data you enter — product URLs, titles, prices, descriptions — is stored locally in your configured database (PostgreSQL or SQLite).

        ### 2. Web Scraping & Third-Party Sites
        When you scrape a product URL, this tool makes HTTP requests to the target website on your behalf. You are responsible for complying with those websites' Terms of Service. We do not store content from third-party websites on our servers.

        ### 3. Amazon Data
        The Amazon Product Hunting feature queries Amazon's public search results. We do not use the Amazon Product Advertising API. You must not use Amazon product images or descriptions on your store without explicit authorization. Amazon trademarks and content remain the property of Amazon.com, Inc.

        ### 4. Cookies & Analytics
        This application does not use cookies or analytics tracking. Streamlit's standard session state is used only for in-session data management.

        ### 5. Data Storage
        All data is stored in your local database:
        - **PostgreSQL** (if configured via `DATABASE_URL` in `.env`)
        - **SQLite** (`product2shopify.db` in the project directory) as a fallback

        You have full ownership and control of all stored data.

        ### 6. Third-Party Links
        This tool may display links to Amazon, supplier websites, or other third-party URLs. Trend & Brand is not responsible for the privacy practices or content of those sites.

        ### 7. Contact
        For privacy concerns, contact us at: **support@trendandbrands.com**
        or visit [www.trendandbrands.com](https://www.trendandbrands.com/)
        """)

    # ---- TERMS OF SERVICE ----
    with tab_terms:
        st.markdown("""
        ## 📜 Terms of Service
        **Effective Date:** June 2026
        **Provider:** [Trend & Brand](https://www.trendandbrands.com/)

        ---

        ### 1. Acceptance of Terms
        By using **Product2Shopify AI**, you agree to these Terms of Service. If you do not agree, please do not use this tool.

        ### 2. Permitted Use
        This tool is licensed for **personal and commercial use** to:
        - Import and prepare product catalogs for Shopify stores
        - Auto-generate product descriptions using the built-in rewriter
        - Export Shopify import-ready CSV and Excel files

        ### 3. Prohibited Use
        You **must not** use this tool to:
        - Copy, scrape, or reproduce copyrighted product descriptions, images, or brand materials from Amazon, competitors, or any other rights holder without explicit authorization
        - Bypass website security measures, CAPTCHAs, or rate limits
        - Use competitor images or descriptions in your Shopify store
        - Engage in scraping practices that violate third-party websites' Terms of Service

        ### 4. Copyright & Content Responsibility
        You are solely responsible for ensuring that all product content (titles, descriptions, images) you publish to your Shopify store is either:
        - Original content you created
        - Provided by an authorized manufacturer or supplier
        - Properly licensed for commercial use

        **Trend & Brand is not liable** for any copyright infringement resulting from improper use of this tool.

        ### 5. Disclaimer of Warranties
        This tool is provided **"as is"** without warranty of any kind. Trend & Brand does not guarantee uninterrupted access to third-party scraping targets (Amazon, supplier sites) as those platforms may change or block access at any time.

        ### 6. Limitation of Liability
        Trend & Brand shall not be liable for any indirect, incidental, or consequential damages arising from use of this tool, including but not limited to business losses, store suspensions, or legal disputes related to content usage.

        ### 7. Modifications
        We reserve the right to update these terms at any time. Continued use of the tool constitutes acceptance of updated terms.

        ### 8. Contact
        **Trend & Brand** | [www.trendandbrands.com](https://www.trendandbrands.com/)
        📧 support@trendandbrands.com
        """)

    # ---- SITEMAP ----
    with tab_sitemap:
        st.markdown("## 🗺️ Application Sitemap")
        st.markdown("All pages available inside **Product2Shopify AI**:")

        sitemap_items = [
            ("📊", "Dashboard", "Overview metrics: total products, exports, validation status, missing fields"),
            ("📥", "Product Link Importer", "Import via direct URLs, collection page scan, or sitemap XML parsing"),
            ("🔎", "Amazon Product Hunting", "Search Amazon by keyword niche and import products to catalog"),
            ("✏️", "Product Editor", "Form-based and bulk grid editor for all 30+ Shopify product fields"),
            ("🏷️", "SKU Generator", "Auto-generate unique SKUs in PREFIX-CATEGORY-COLOR-001 format"),
            ("🧮", "Price Calculator", "Compute selling prices, margins, profits, and compare-at prices"),
            ("🔍", "Tags & SEO Generator", "Generate handles, comma-separated tags, SEO titles and descriptions"),
            ("🖼️", "Image Manager", "Manage image URLs, positions, alt texts, and validate HTTPS links"),
            ("✅", "CSV Validator", "Pre-export validation with detailed error and warning reports"),
            ("📤", "Shopify CSV Exporter", "Download Shopify-compatible CSV and Excel backup files"),
            ("⏳", "Import History", "Full audit log of all URL imports and export batches"),
            ("⚙️", "Settings", "Database status, default values, and configuration options"),
            ("📄", "About & Policies", "Privacy Policy, Terms of Service, and application sitemap"),
        ]

        cols = st.columns(2)
        for i, (icon, page, desc) in enumerate(sitemap_items):
            with cols[i % 2]:
                st.markdown(f"""
                <div style="background:#1a1a2e; border-left: 3px solid #e94560; border-radius: 8px;
                            padding: 12px 16px; margin-bottom: 10px;">
                    <span style="font-size:1.2rem;">{icon}</span>
                    <span style="color:#e2e8f0; font-weight:700; margin-left:8px;">{page}</span>
                    <div style="color:#718096; font-size:0.82rem; margin-top:4px;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        ### 🌐 External Links
        - [Trend & Brand Website](https://www.trendandbrands.com/)
        - [Shopify Import Documentation](https://help.shopify.com/en/manual/products/import-export/import-products)
        - [Shopify CSV Format Reference](https://help.shopify.com/en/manual/products/import-export/using-csv)
        """)


if __name__ == "__main__":
    show_about_policies()
