import streamlit as st
import time
from database.db import get_db_session, RawProduct, ShopifyProduct
from services.scraper import scrape_product_url, extract_product_links_from_page, extract_product_links_from_sitemap
from services.sku_service import create_handle, generate_sku
from services.product_cleaner import rewrite_product_data
from services.validator import validate_product_record

def show_link_importer():
    st.title("📥 Product Link Importer")
    st.markdown("Import products using direct URLs, scan entire store collection pages, or parse sitemap XML files.")

    st.warning("⚠️ **Safety Notice:** Do not use copyrighted Amazon or competitor descriptions/images. Use authorized supplier content only. The rewriter helps you create unique copy.")

    # --- Import Mode Selector ---
    mode = st.radio(
        "Choose your import method:",
        ["🔗 Direct Product URLs", "🌐 Scan Seller Page / Collection URL", "🗺️ Parse Sitemap XML"],
        horizontal=True
    )

    st.markdown("---")

    # ---- MODE 1: Direct Product URLs ----
    if "Direct" in mode:
        st.subheader("🔗 Paste Direct Product Links")
        st.markdown("One product URL per line. Supports any store: Shopify, WooCommerce, AliExpress, supplier pages, etc.")
        urls_input = st.text_area("Product URLs (one per line):", height=180,
                                   placeholder="https://example.com/products/wireless-headphones\nhttps://supplier.com/item/12345")
        urls = [u.strip() for u in urls_input.strip().split("\n") if u.strip()]
        st.info(f"**{len(urls)}** URLs ready to process.")

    # ---- MODE 2: Collection Page / Grid Scan ----
    elif "Scan" in mode:
        st.subheader("🌐 Scan a Seller / Collection Page")
        st.markdown("""
        Paste a **single collection or store category page** URL. The tool will crawl all discovered product links on that page automatically.

        **Works great with:**
        - Shopify: `https://store.com/collections/all`
        - WooCommerce: `https://store.com/shop`
        - Any product grid/listing page
        """)
        collection_url = st.text_input("Collection / Seller Page URL:", placeholder="https://example.com/collections/all")
        max_links = st.slider("Max products to extract from page:", min_value=5, max_value=200, value=50)
        urls = []

        if st.button("🔍 Discover Product Links", key="discover_btn"):
            if not collection_url.strip():
                st.error("Please enter a valid page URL.")
            else:
                with st.spinner("Scanning page for product links..."):
                    found = extract_product_links_from_page(collection_url)
                    urls = found[:max_links]
                if urls:
                    st.success(f"✅ Found **{len(urls)}** product links on that page!")
                    with st.expander("Preview discovered links"):
                        for u in urls:
                            st.text(u)
                    st.session_state["bulk_urls"] = urls
                else:
                    st.error("No product links found on that page. Try a different URL or use Direct mode.")
                    return

        # Retrieve from session state if already discovered
        if "bulk_urls" in st.session_state and not urls:
            urls = st.session_state.get("bulk_urls", [])
            if urls:
                st.info(f"Using **{len(urls)}** previously discovered links. Click **Extract Product Data** below to import.")

    # ---- MODE 3: Sitemap XML ----
    else:
        st.subheader("🗺️ Parse Sitemap XML")
        st.markdown("""
        Paste a sitemap XML URL to extract all product links automatically.

        **Common sitemap patterns:**
        - `https://example.com/sitemap.xml`
        - `https://example.com/sitemap_products_1.xml`
        """)
        sitemap_url = st.text_input("Sitemap XML URL:", placeholder="https://example.com/sitemap_products_1.xml")
        max_sitemap = st.slider("Max products from sitemap:", min_value=10, max_value=500, value=100)
        urls = []

        if st.button("🗺️ Parse Sitemap", key="parse_sitemap_btn"):
            if not sitemap_url.strip():
                st.error("Please enter a valid sitemap URL.")
            else:
                with st.spinner("Parsing sitemap XML..."):
                    found = extract_product_links_from_sitemap(sitemap_url)
                    urls = found[:max_sitemap]
                if urls:
                    st.success(f"✅ Extracted **{len(urls)}** product URLs from sitemap!")
                    with st.expander("Preview extracted links"):
                        for u in urls:
                            st.text(u)
                    st.session_state["sitemap_urls"] = urls
                else:
                    st.error("No product URLs found in sitemap. Verify the sitemap URL contains product links.")
                    return

        if "sitemap_urls" in st.session_state and not urls:
            urls = st.session_state.get("sitemap_urls", [])
            if urls:
                st.info(f"Using **{len(urls)}** URLs from parsed sitemap.")

    # ---- Shared Import Settings ----
    if urls:
        st.markdown("---")
        st.subheader("⚙️ Import Settings")
        col1, col2, col3 = st.columns(3)
        with col1:
            default_vendor = st.text_input("Default Brand / Vendor:", value="TNB Store")
        with col2:
            sku_prefix = st.text_input("SKU Prefix:", value="TNB")
        with col3:
            scrape_delay = st.slider("Delay between requests (sec):", 0.5, 5.0, 1.0, 0.5)

        if st.button("🚀 Extract & Import Product Data", type="primary"):
            _run_import(urls, default_vendor, sku_prefix, scrape_delay)


def _run_import(urls, default_vendor, sku_prefix, scrape_delay):
    """Internal function to scrape and save products."""
    st.subheader("📋 Extraction Progress")
    progress_bar = st.progress(0)
    status_text = st.empty()
    session = get_db_session()
    success_count = 0
    failed_count = 0
    results_preview = []

    for idx, url in enumerate(urls):
        status_text.text(f"⏳ Processing {idx+1}/{len(urls)}: {url[:60]}...")
        scraped = scrape_product_url(url, delay=scrape_delay)

        images_str = ",".join(scraped["raw_images"]) if scraped["raw_images"] else ""
        raw_prod = RawProduct(
            source_url=scraped["source_url"],
            raw_title=scraped["raw_title"],
            raw_price=scraped["raw_price"],
            raw_description=scraped["raw_description"],
            raw_images=images_str,
            raw_vendor=scraped["raw_vendor"] or default_vendor,
            extraction_status=scraped["extraction_status"]
        )
        session.add(raw_prod)
        session.flush()

        title = scraped["raw_title"] or f"Manual Entry Required - Product {raw_prod.id}"
        handle = create_handle(title) or f"manual-entry-{raw_prod.id}"
        sku = generate_sku(
            title=title,
            category=scraped["raw_category"] or "Uncategorized",
            color="",
            prefix=sku_prefix,
            db_session=session
        ) if scraped["raw_title"] else ""

        body_html = ""
        if scraped["raw_description"]:
            _, body_html = rewrite_product_data(title, scraped["raw_description"], scraped["raw_vendor"] or default_vendor)

        shopify_prod = ShopifyProduct(
            source_url=url,
            handle=handle,
            title=title,
            body_html=body_html,
            vendor=scraped["raw_vendor"] or default_vendor,
            product_category=scraped["raw_category"] or "Uncategorized",
            product_type="General",
            tags="",
            published="true",
            option1_name="Title",
            option1_value="Default Title",
            variant_sku=sku,
            variant_grams=0,
            variant_inventory_qty=1,
            variant_inventory_policy="deny",
            variant_fulfillment_service="manual",
            variant_price=scraped["raw_price"],
            variant_compare_at_price=round(float(scraped["raw_price"] or 0) * 1.3, 2),
            variant_requires_shipping=True,
            variant_taxable=True,
            image_src=images_str,
            image_position=1,
            image_alt_text=title,
            status="draft",
            validation_status="Needs Validation"
        )
        session.add(shopify_prod)
        session.flush()

        val_res = validate_product_record(shopify_prod, db_session=session)
        shopify_prod.validation_status = val_res["status"]
        session.commit()

        results_preview.append({
            "Source URL": url[:60],
            "Status": scraped["extraction_status"],
            "Extracted Title": (scraped["raw_title"] or "(Empty)")[:50],
            "Price": f"${float(scraped['raw_price'] or 0):.2f}",
            "SKU": sku or "(Pending)"
        })

        if "Success" in scraped["extraction_status"]:
            success_count += 1
        else:
            failed_count += 1

        progress_bar.progress((idx + 1) / len(urls))

    status_text.text("✅ Import complete!")
    session.close()

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ **{success_count}** products scraped successfully")
    with col2:
        st.warning(f"⚠️ **{failed_count}** products flagged for manual entry")

    st.dataframe(results_preview, width="stretch")
    st.info("👉 Go to **Product Editor** to review and complete manually-flagged products before exporting.")


if __name__ == "__main__":
    show_link_importer()
