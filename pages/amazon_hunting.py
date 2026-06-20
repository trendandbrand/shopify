import streamlit as st
import requests
import re
import time
import urllib.parse
from bs4 import BeautifulSoup
from database.db import get_db_session, RawProduct, ShopifyProduct
from services.sku_service import create_handle, generate_sku
from services.product_cleaner import rewrite_product_data
from services.validator import validate_product_record

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def search_amazon_products(keyword, page=1):
    """
    Queries Amazon search results and returns product data list.
    Returns a list of dicts with title, price, rating, image, url.
    """
    query = urllib.parse.quote_plus(keyword)
    url = f"https://www.amazon.com/s?k={query}&page={page}"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.amazon.com/"
    }

    products = []
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code != 200:
            return products, f"Amazon returned status {resp.status_code}. Try again later."

        soup = BeautifulSoup(resp.content, "lxml")

        # Amazon product cards
        cards = soup.select('[data-component-type="s-search-result"]')
        for card in cards:
            try:
                # Title
                title_el = card.select_one("h2 span") or card.select_one(".a-size-base-plus")
                title = title_el.get_text().strip() if title_el else ""
                if not title:
                    continue

                # Price
                price = 0.0
                price_el = card.select_one(".a-price .a-offscreen") or card.select_one(".a-price-whole")
                if price_el:
                    raw_p = re.sub(r'[^\d\.]', '', price_el.get_text())
                    try:
                        price = float(raw_p)
                    except Exception:
                        price = 0.0

                # Rating
                rating = ""
                rating_el = card.select_one(".a-icon-star-small .a-icon-alt") or card.select_one(".a-icon-star .a-icon-alt")
                if rating_el:
                    rating = rating_el.get_text().strip()

                # Reviews count
                reviews = ""
                reviews_el = card.select_one('[aria-label*="ratings"]') or card.select_one(".a-size-small .a-color-secondary")
                if reviews_el:
                    reviews = re.sub(r'[^\d,]', '', reviews_el.get("aria-label", reviews_el.get_text())).strip()

                # Image
                img = ""
                img_el = card.select_one(".s-image") or card.select_one("img.product-image")
                if img_el:
                    img = img_el.get("src", "")

                # Product URL
                link = ""
                link_el = card.select_one("a.a-link-normal[href*='/dp/']") or card.select_one("h2 a")
                if link_el:
                    href = link_el.get("href", "")
                    link = urllib.parse.urljoin("https://www.amazon.com", href).split("?")[0]

                # ASIN
                asin = card.get("data-asin", "")

                products.append({
                    "asin": asin,
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "reviews": reviews,
                    "image": img,
                    "url": link
                })
            except Exception:
                continue

    except Exception as e:
        return products, str(e)

    return products, None


def import_amazon_product(product_data, vendor="Amazon Supplier", sku_prefix="TNB"):
    """Saves an Amazon product (from hunt results) into our Shopify products table."""
    session = get_db_session()
    try:
        title = product_data["title"]
        price = float(product_data["price"] or 0.0)
        image = product_data["image"]
        url = product_data["url"]

        # Save raw
        raw_prod = RawProduct(
            source_url=url,
            raw_title=title,
            raw_price=price,
            raw_description=f"Amazon ASIN: {product_data['asin']}. Rating: {product_data['rating']}",
            raw_images=image,
            raw_vendor=vendor,
            extraction_status="Amazon Hunt (Review Needed)"
        )
        session.add(raw_prod)
        session.flush()

        handle = create_handle(title)
        _, body_html = rewrite_product_data(title, f"Amazon ASIN: {product_data['asin']}", vendor)
        sku = generate_sku(title=title, category="Amazon", color="", prefix=sku_prefix, db_session=session)

        shopify_prod = ShopifyProduct(
            source_url=url,
            handle=handle,
            title=title,
            body_html=body_html,
            vendor=vendor,
            product_category="Amazon Hunt",
            product_type="General",
            tags=f"amazon, hunt, {sku_prefix.lower()}",
            published="true",
            option1_name="Title",
            option1_value="Default Title",
            variant_sku=sku,
            variant_price=price,
            variant_compare_at_price=round(price * 1.3, 2),
            variant_requires_shipping=True,
            variant_taxable=True,
            image_src=image,
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
        return True, sku
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def show_amazon_hunting():
    st.title("🔎 Amazon Product Hunting")
    st.markdown("Discover high-demand products on Amazon by keyword. Review listings and import promising products directly to your Shopify catalog with one click.")

    st.warning("⚠️ **Copyright Notice:** Amazon product images are copyrighted. Do not use Amazon images directly on Shopify. Use only manufacturer-supplied or authorized images. Descriptions will be auto-rewritten.")

    # Search panel
    col_search, col_page, col_vendor = st.columns([3, 1, 2])
    with col_search:
        keyword = st.text_input("🔍 Search Keyword / Niche:", placeholder="e.g. wireless earbuds, phone stand, gym bag")
    with col_page:
        page_num = st.number_input("Page:", min_value=1, max_value=10, value=1)
    with col_vendor:
        vendor_name = st.text_input("Vendor Label:", value="Trend & Brand")

    col_btn, col_prefix = st.columns([2, 2])
    with col_btn:
        search_btn = st.button("🚀 Hunt Products on Amazon", type="primary", width="stretch")
    with col_prefix:
        sku_prefix = st.text_input("SKU Prefix:", value="TNB")

    if search_btn:
        if not keyword.strip():
            st.error("Please enter a search keyword.")
            return

        with st.spinner(f"Hunting Amazon for: **{keyword}**..."):
            products, error = search_amazon_products(keyword, page=page_num)
            time.sleep(1)

        if error:
            st.error(f"Search failed: {error}")
            st.info("Amazon may be blocking automated requests. Try again later or use a VPN. You can still manually paste Amazon URLs in the **Product Link Importer**.")
            return

        if not products:
            st.warning("No products found. Amazon may have blocked this request or changed its layout. Try a different keyword or wait a moment.")
            return

        st.session_state["hunt_results"] = products
        st.session_state["hunt_vendor"] = vendor_name
        st.session_state["hunt_prefix"] = sku_prefix

    # Display results
    hunt_results = st.session_state.get("hunt_results", [])
    if hunt_results:
        vendor_label = st.session_state.get("hunt_vendor", vendor_name)
        prefix_label = st.session_state.get("hunt_prefix", sku_prefix)

        st.markdown("---")
        st.subheader(f"🛒 Hunt Results — {len(hunt_results)} Products Found")
        st.caption("Click **Import to Catalog** to add a product to your Shopify editor. Remember to replace Amazon images with authorized supplier images.")

        imported_keys = st.session_state.get("imported_asins", set())

        for i, prod in enumerate(hunt_results):
            with st.container():
                col_img, col_info, col_action = st.columns([1, 4, 2])

                with col_img:
                    if prod["image"] and prod["image"].startswith("http"):
                        st.image(prod["image"], width=120)
                    else:
                        st.markdown("🖼️ *No image*")

                with col_info:
                    st.markdown(f"#### {prod['title'][:90]}{'...' if len(prod['title']) > 90 else ''}")
                    cols_meta = st.columns(3)
                    with cols_meta[0]:
                        st.metric("Price", f"${prod['price']:.2f}" if prod["price"] else "N/A")
                    with cols_meta[1]:
                        st.metric("Rating", prod["rating"] or "N/A")
                    with cols_meta[2]:
                        st.metric("Reviews", prod["reviews"] or "N/A")
                    if prod["url"]:
                        st.markdown(f"[🔗 View on Amazon]({prod['url']})", unsafe_allow_html=False)
                    st.caption(f"ASIN: `{prod['asin']}`")

                with col_action:
                    asin_key = prod.get("asin", f"prod_{i}")
                    if asin_key in imported_keys:
                        st.success("✅ Imported!")
                    else:
                        if st.button(f"📥 Import to Catalog", key=f"import_{i}_{asin_key}", width="stretch"):
                            ok, info = import_amazon_product(prod, vendor=vendor_label, sku_prefix=prefix_label)
                            if ok:
                                imported_keys.add(asin_key)
                                st.session_state["imported_asins"] = imported_keys
                                st.success(f"✅ Imported! SKU: `{info}`")
                                st.rerun()
                            else:
                                st.error(f"Import failed: {info}")

                st.markdown("---")

        st.info("👉 After importing, go to **Image Manager** to replace Amazon images with authorized supplier images, then validate and export.")


if __name__ == "__main__":
    show_amazon_hunting()
